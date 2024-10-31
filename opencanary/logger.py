import json
import logging.config
import socket
import hpfeeds
import sys
from datetime import datetime
from logging.handlers import SocketHandler
import requests
from twisted.internet import reactor
from opencanary.iphelper import check_ip


class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def getLogger(config):
    logger_config = config.get('logger', {})
    logger_class_name = logger_config.get('class')
    if not logger_class_name:
        raise ValueError("Logger section missing 'class' key.")
    
    LoggerClass = globals().get(logger_class_name)
    if not LoggerClass:
        raise ValueError(f"Logger class '{logger_class_name}' is not defined.")
    
    return LoggerClass(config, **logger_config.get('kwargs', {}))


class LoggerBase:
    LOG_TYPES = {
        'BOOT': 1000,
        'MSG': 1001,
        'DEBUG': 1002,
        'ERROR': 1003,
        'PING': 1004,
        'CONFIG_SAVE': 1005,
        'EXAMPLE': 1006,
        'FTP_LOGIN_ATTEMPT': 2000,
        # Extend as needed
    }

    def sanitizeLog(self, logdata):
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        logdata.update({
            'node_id': self.node_id,
            'local_time': current_time,
            'utc_time': current_time,
            'local_time_adjusted': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            'src_host': logdata.get('src_host', ''),
            'src_port': logdata.get('src_port', -1),
            'dst_host': logdata.get('dst_host', ''),
            'dst_port': logdata.get('dst_port', -1),
            'logtype': logdata.get('logtype', self.LOG_TYPES['MSG']),
            'logdata': logdata.get('logdata', {})
        })
        return logdata


class PyLogger(LoggerBase, metaclass=Singleton):
    def __init__(self, config, handlers, formatters={}):
        self.node_id = config.getVal('device.node_id')
        self.ignorelist = config.getVal('ip.ignorelist', default='')

        for h in handlers:
            handlers[h]["level"] = "NOTSET"
        
        logconfig = {
            "version": 1,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": {self.node_id: {"handlers": list(handlers)}}
        }
        
        logging.config.dictConfig(logconfig)
        self.logger = logging.getLogger(self.node_id)

    def log(self, logdata, retry=True):
        logdata = self.sanitizeLog(logdata)
        if not any(check_ip(logdata['src_host'], ip) for ip in self.ignorelist):
            self.logger.warning(json.dumps(logdata, sort_keys=True))

    def error(self, data):
        data['local_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.logger.error(json.dumps(data, sort_keys=True))


class SocketJSONHandler(SocketHandler):
    def makeSocket(self, timeout=1):
        sock = super().makeSocket(timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return sock

    def send(self, msg, attempt=0):
        if attempt >= 10:
            print("Dropping log message due to too many failed sends")
            return

        if not self.sock:
            self.createSocket()
        
        try:
            self.sock.sendall(msg.encode("utf-8"))
        except socket.error:
            self.sock.close()
            self.sock = None
            reactor.callLater(1.5, lambda: self.send(msg, attempt + 1))


class WebhookHandler(logging.Handler):
    def __init__(self, url, method="POST", data=None, status_code=200, ignore=None, **kwargs):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data
        self.status_code = status_code
        self.ignore = ignore or []
        self.kwargs = kwargs

    def emit(self, record):
        message = self.format(record)
        if any(ignore_word in message for ignore_word in self.ignore):
            return

        payload = map_string(self.data or {"message": message}, {"message": message})
        response = requests.request(method=self.method, url=self.url, json=payload, **self.kwargs)

        if response.status_code != self.status_code:
            print(f"Error {response.status_code} sending Webhook payload:\n{response.text}")


def map_string(data, mapping):
    if isinstance(data, dict):
        return {k: map_string(v, mapping) for k, v in data.items()}
    if isinstance(data, list):
        return [map_string(item, mapping) for item in data]
    if isinstance(data, str):
        return data % mapping
    return data


class HpfeedsHandler(logging.Handler):
    def __init__(self, host, port, ident, secret, channels):
        super().__init__()
        self.hpc = hpfeeds.new(host, int(port), ident, secret)
        self.hpc.subscribe(list(map(str, channels)))

    def emit(self, record):
        try:
            msg = self.format(record)
            self.hpc.publish(self.channels, msg)
        except Exception as e:
            print(f"Error publishing to hpfeeds: {e}")


class SlackHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        data = self.generate_msg(record)
        response = requests.post(self.webhook_url, json=data)
        if response.status_code != 200:
            print(f"Error {response.status_code} sending Slack message:\n{response.text}")

    def generate_msg(self, alert):
        data = json.loads(alert.msg)
        return {
            "attachments": [{
                "pretext": "OpenCanary Alert",
                "fields": [{"title": k, "value": json.dumps(v) if isinstance(v, dict) else v} for k, v in data.items()]
            }]
        }


class TeamsHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        data = json.loads(record.msg)
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "49c176",
            "summary": "OpenCanary Notification",
            "title": "OpenCanary Alert",
            "sections": [{"facts": self.format_facts(data)}]
        }
        response = requests.post(self.webhook_url, headers={'Content-Type': 'application/json'}, json=payload)
        if response.status_code != 200:
            print(f"Error {response.status_code} sending Teams message:\n{response.text}")

    def format_facts(self, data, prefix=""):
        facts = []
        for k, v in data.items():
            key = f"{prefix}__{k.lower()}" if prefix else k.lower()
            if isinstance(v, dict):
                facts.extend(self.format_facts(v, key))
            else:
                facts.append({"name": key, "value": str(v)})
        return facts
