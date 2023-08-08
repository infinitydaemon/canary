import os
import datetime
from base64 import b64decode

try:
    from urllib.parse import quote, urlparse  # Python 3+
except ImportError:
    from urlparse import urlparse
    from urllib import quote  # Python 2.X

from twisted.application import internet
from twisted.internet.protocol import ServerFactory
from twisted.web.http import HTTPChannel, Request
from twisted.web import http
from twisted.internet import reactor
from jinja2 import Template

from opencanary.modules import CanaryService

PROFILES = {
    "ms-isa": {
        # ... (profile details)
    },
    "squid": {
        # ... (profile details)
    }
}

class AlertProxyRequest(Request):
    FACTORY = None

    def __init__(self, channel, queued):
        super().__init__(channel, queued)

    def logAuth(self):
        auth = self.getHeader("Proxy-Authorization")
        if auth is None:
            return

        factory = AlertProxyRequest.FACTORY

        username, password = "Invalid auth-token submitted", ""
        auth_arr = auth.split(" ")
        if len(auth_arr) != 2:
            return

        atype, token = auth_arr
        if atype == "Basic":
            try:
                username, password = b64decode(token).decode("utf-8").split(":")
            except:
                pass
        elif atype == "NTLM":
            # ... (NTLM handling)
            pass

        logdata = {'USERNAME': username, 'PASSWORD': password}
        factory.log(logdata, transport=self.transport)

    def process(self):
        self.logAuth()

        factory = AlertProxyRequest.FACTORY
        profile = PROFILES[factory.skin]
        # ... (content generation)

        if profile.get("HTTP1.1_always", False):
            self.clientproto = "HTTP/1.1"

        self.setResponseCode(407, profile["status_reason"])
        for (name, value) in profile["headers"]:
            self.responseHeaders.addRawHeader(name, value)

        # ... (response headers)

        self.write(content.encode("utf-8"))
        self.finish()

class AlertProxy(HTTPChannel):
    requestFactory = AlertProxyRequest

class HTTPProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return AlertProxy()

class HTTPProxy(CanaryService):
    NAME = 'httpproxy'

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)
        self.port = int(config.getVal('httpproxy.port', default=8443))
        self.banner = config.getVal('httpproxy.banner', '').encode('utf-8')
        self.skin = config.getVal('httpproxy.skin', default='squid')
        self.skindir = os.path.join(
            HTTPProxy.resource_dir(), 'skin', self.skin)
        self.logtype = logger.LOG_HTTPPROXY_LOGIN_ATTEMPT
        self.listen_addr = config.getVal('device.listen_addr', default='')

        authfilename = os.path.join(self.skindir, 'auth.html')
        try:
            with open(authfilename, 'r') as f:
                self.auth_template = Template(f.read())
        except:
            self.auth_template = Template("")

    def getService(self):
        AlertProxyRequest.FACTORY = self
        f = HTTPProxyFactory()
        return internet.TCPServer(self.port, f, interface=self.listen_addr)
