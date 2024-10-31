from opencanary.modules import CanaryService
import socket
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet
import logging

class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass

class UnsupportedVersion(Exception):
    """Custom exception for unsupported versions."""
    pass

class TCPBannerProtocol(Protocol):
    """
    Implementation of TCP Banner module - replies with a text banner.
    """
    def __init__(self, factory, banner_id: str, accept_banner: bytes, send_banner: bytes,
                 alert_string_enabled: bool, alert_string: bytes, keep_alive_enabled: bool,
                 keep_alive_secret: bytes, keep_alive_idle: int, keep_alive_interval: int,
                 keep_alive_probes: int):
        self.factory = factory
        self.banner_id = banner_id
        self.accept_banner = accept_banner
        self.send_banner = send_banner
        self.alert_string_enabled = alert_string_enabled
        self.alert_string = alert_string
        self.keep_alive_enabled = keep_alive_enabled
        self.keep_alive_disable_alerting = False
        self.keep_alive_secret = keep_alive_secret
        self.keep_alive_idle = keep_alive_idle
        self.keep_alive_interval = keep_alive_interval
        self.keep_alive_probes = keep_alive_probes

    def connectionMade(self):
        """Handle connection establishment."""
        try:
            # Limit the data sent through to 255 chars
            data = str(self.accept_banner)[:255]
            logdata = {
                'FUNCTION': 'CONNECTION_MADE',
                'DATA': data,
                'BANNER_ID': str(self.banner_id)
            }

            if self.keep_alive_enabled:
                self._set_keep_alive_options()
                self.factory.canaryservice.logtype = self.factory.canaryservice.logger.LOG_TCP_BANNER_KEEP_ALIVE_CONNECTION_MADE
            elif not self.alert_string_enabled:
                self.factory.canaryservice.logtype = self.factory.canaryservice.logger.LOG_TCP_BANNER_CONNECTION_MADE
            
            self.factory.canaryservice.log(logdata, transport=self.transport)
            self.transport.write(self.accept_banner)
        
        except OSError:
            logging.error('Received an OSError. Likely the socket has closed.')
            self.factory.canaryservice.log(logdata, transport=self.transport)

    def _set_keep_alive_options(self):
        """Set TCP keep-alive options for the connection."""
        if hasattr(socket, 'TCP_KEEPIDLE'):
            self.transport.getHandle().setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.keep_alive_idle)
            self.transport.getHandle().setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.keep_alive_interval)
            self.transport.getHandle().setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, self.keep_alive_probes)
            self.transport.setTcpKeepAlive(1)

    def dataReceived(self, data: bytes):
        """
        Handle received data from the TCP connection after the connection has been made.
        """
        try:
            if self.keep_alive_disable_alerting:
                self.transport.write(self.send_banner)
                return

            # Limit the data sent through to 255 chars
            data = data[:255]
            logdata = {'FUNCTION': 'DATA_RECEIVED', 'BANNER_ID': str(self.banner_id)}

            logdata['DATA'] = self._decode_data(data)

            send_log = True

            if self.keep_alive_enabled:
                send_log = self._handle_keep_alive(data, logdata)
            else:
                send_log = self._handle_alert_string(data, logdata)

            if send_log:
                self.factory.canaryservice.log(logdata, transport=self.transport)

            self.transport.write(self.send_banner)
        
        except (UnsupportedVersion, ProtocolError) as e:
            logging.error(f"Protocol error: {e}")
            self.transport.loseConnection()

    def _decode_data(self, data: bytes) -> bytes:
        """Decode received data safely."""
        try:
            return data.rstrip().decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            return data.rstrip().decode('unicode_escape').encode('utf-8')

    def _handle_keep_alive(self, data: bytes, logdata: dict) -> bool:
        """Handle keep-alive functionality."""
        if self.keep_alive_secret and self.keep_alive_secret in data:
            self.keep_alive_disable_alerting = True
            self.factory.canaryservice.logtype = self.factory.canaryservice.logger.LOG_TCP_BANNER_KEEP_ALIVE_SECRET_RECEIVED
            logdata['SECRET_STRING'] = self.keep_alive_secret.decode().encode('utf-8')
            return True
        else:
            self.factory.canaryservice.logtype = self.factory.canaryservice.logger.LOG_TCP_BANNER_KEEP_ALIVE_DATA_RECEIVED
            return True

    def _handle_alert_string(self, data: bytes, logdata: dict) -> bool:
        """Check for alert string presence in received data."""
        if self.alert_string in data:
            logdata['ALERT_STRING'] = self.alert_string.decode().encode('utf-8')
            return True
        return False

class TCPBannerFactory(Factory):
    def __init__(self, config=None, banner_id=1):
        self.banner_id = str(banner_id)
        self.accept_banner = self._load_banner(config, 'initbanner')
        self.send_banner = self._load_banner(config, 'datareceivedbanner')
        self.alert_string_enabled = config.getVal(f'tcpbanner_{self.banner_id}.alertstring.enabled', False)
        self.alert_string = self._load_banner(config, 'alertstring')
        self.keep_alive_enabled = config.getVal(f'tcpbanner_{self.banner_id}.keep_alive.enabled', False)
        self.keep_alive_secret = self._load_banner(config, 'keep_alive_secret')
        self.keep_alive_idle = config.getVal(f'tcpbanner_{self.banner_id}.keep_alive_idle', 300)
        self.keep_alive_interval = config.getVal(f'tcpbanner_{self.banner_id}.keep_alive_interval', 300)
        self.keep_alive_probes = config.getVal(f'tcpbanner_{self.banner_id}.keep_alive_probes', 11)

    def _load_banner(self, config, key: str) -> bytes:
        """Load and clean banner text from configuration."""
        return config.getVal(f'tcpbanner_{self.banner_id}.{key}', '').encode('utf-8').replace(b'\\n', b'\n').replace(b'\\r', b'\r')

    def buildProtocol(self, addr):
        """Build a new instance of the protocol."""
        return TCPBannerProtocol(self, self.banner_id, self.accept_banner, self.send_banner,
                                 self.alert_string_enabled, self.alert_string,
                                 self.keep_alive_enabled, self.keep_alive_secret,
                                 self.keep_alive_idle, self.keep_alive_interval,
                                 self.keep_alive_probes)

class CanaryTCPBanner(CanaryService):
    NAME = 'tcpbanner'
    MAX_TCP_BANNERS = 10

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)

    def getService(self):
        """Return the service for the TCP Banner factory."""
        services = []
        max_banners = self.config.getVal('tcpbanner.maxnum', default=self.MAX_TCP_BANNERS)
        
        for i in range(1, max_banners + 1):
            if self.config.getVal(f'tcpbanner_{i}.enabled', False):
                factory = TCPBannerFactory(config=self.config, banner_id=i)
                factory.canaryservice = self
                port = self.config.getVal(f'tcpbanner_{i}.port', default=8000 + i)
                services.append(internet.TCPServer(port, factory))
        
        return services
