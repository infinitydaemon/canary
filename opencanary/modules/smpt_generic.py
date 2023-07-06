from opencanary.modules import CanaryService
from twisted.application import internet
from twisted.internet.protocol import Factory
from twisted.protocols.smtp import SMTP, ESMTP

class SMTPServer(SMTP):
    def __init__(self, *args, **kwargs):
        SMTP.__init__(self, *args, **kwargs)

    def do_UNKNOWN(self, arg):
        """
        Handle unknown SMTP commands
        """
        self.factory.log({"COMMAND": arg})

    def do_EHLO(self, arg):
        """
        Handle EHLO command
        """
        self.factory.log({"COMMAND": "EHLO", "ARGUMENT": arg})
        self.sendLine("250-Hello {}".format(arg))

    # Implement additional SMTP command handlers as needed

class SMTPFactory(Factory):
    protocol = ESMTP

    def __init__(self, logger=None):
        self.logger = logger

    def buildProtocol(self, addr):
        p = SMTPServer()
        p.factory = self
        return p

class SMTPService(CanaryService):
    NAME = 'smtp'

    def __init__(self, config=None, logger=None):
        CanaryService.__init__(self, config=config, logger=logger)
        self.port = int(config.getVal('smtp.port', default=25))
        self.listen_addr = config.getVal('device.listen_addr', default='')

    def getService(self):
        f = SMTPFactory(logger=self.logger)
        return internet.TCPServer(self.port, f, interface=self.listen_addr)
