from opencanary.modules import CanaryService

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.application import internet

class SIP(Protocol):
    """
    Example SIP Protocol

    $ telnet localhost 5060
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    password:
    password:
    password:
    % Bad passwords
    Connection closed by foreign host.
    """
    def __init__(self):
        self.prompts = 0
        self.buffer = ""

    def connectionMade(self):
        self.transport.write("\xff\xfb\x03\xff\xfb\x01password: ")
        self.prompts += 1

    def dataReceived(self, data):
        """
        Received data is unbuffered so we buffer it for telnet.
        """
        self.buffer += data
        print("Received data: ", repr(data))

        # Discard inital telnet client control chars
        i = self.buffer.find("\x01")
        if i >= 0:
            self.buffer = self.buffer[i+1:]
            return

        if self.buffer.find("\x00") >= 0:
            password = self.buffer.strip("\r\n\x00")
            logdata = {"PASSWORD" : password}
            self.factory.log(logdata, transport=self.transport)
            self.buffer = ""

            if self.prompts < 3:
                self.transport.write("\r\npassword: ")
                self.prompts += 1
            else:
                self.transport.write("\r\n% Bad passwords\r\n")
                self.transport.loseConnection()

class SIP(Factory, CanaryService):
    NAME = 'example1'
    protocol = Example1Protocol

    def __init__(self, config=None, logger=None):
        CanaryService.__init__(self, config, logger)
        self.port = config.getVal("example1.port", 8025)
        self.logtype = logger.LOG_BASE_EXAMPLE

CanaryServiceFactory = SIP
