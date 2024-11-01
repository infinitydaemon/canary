from opencanary.modules import CanaryService
from twisted.application import internet
from twisted.protocols.sip import Base
from twisted.internet.address import IPv4Address

class AsteriskServer(Base):
    def handle_request(self, request, addr):
        try:
            logdata = {'HEADERS': request.headers}
            self.transport.getPeer = lambda: IPv4Address('UDP', addr[0], addr[1])
            self.factory.log(logdata=logdata, transport=self.transport)
        except Exception as e:
            self.factory.log(logdata={'ERROR': e}, transport=self.transport)

class AsteriskService(CanaryService):
    NAME = 'asterisk_server'

    def __init__(self, config=None, logger=None):
        CanaryService.__init__(self, config=config, logger=logger)
        self.port = int(config.getVal('asterisk.port', default=5060))
        self.logtype = self.logger.LOG_SIP_REQUEST
        self.listen_addr = config.getVal('device.listen_addr', default='')

    def getService(self):
        f = AsteriskServer()
        f.factory = self
        return internet.UDPServer(self.port, f, interface=self.listen_addr)
