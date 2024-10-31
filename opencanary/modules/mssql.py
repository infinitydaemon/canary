from opencanary.modules import CanaryService
from opencanary.config import ConfigException
from twisted.protocols.policies import TimeoutMixin
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet
from ntlmlib.messages import ChallengeResponse, TargetInfo
import struct
import re
import collections

# Monkeypatch for ntlmlib TargetInfo.getData bug
if not hasattr(TargetInfo, 'getData'):
    TargetInfo.getData = lambda self: self.get_data()

TDSPacket = collections.namedtuple('TDSPacket', 'type status spid packetid window payload')
PreLoginOption = collections.namedtuple('PreLoginOption', 'token data')

class MSSQLProtocol(Protocol, TimeoutMixin):
    """MSSQL TDS Protocol Implementation."""
    
    TDS_HEADER_LEN = 8
    NMAP_PROBE_1 = TDSPacket(type=18, status=1, spid=0, packetid=0, window=0,
                             payload=b'\x00\x00\x15\x00\x06\x01\x00\x1b\x00\x01\x02\x00\x1c\x00\x0c\x03\x00(\x00\x04\xff\x08\x00\x01U\x00\x00\x00MSSQLServer\x00H\x0f\x00\x00')
    NMAP_PROBE_1_RESP = {
        "2008R2": b"\x04\x01\x00.\x00\x00\x01\x00\x00\x00\x15\x00\x06\x01\x00\x1b\x00\x01\x02\x00\x1c\x00\x01\x03\x00\x1d\x00\x00\xff\x0a\x32\x10\xb4",
        "2012": b"\x04\x01\x00\x25\x00\x00\x01\x00\x00\x00\x15\x00\x06\x01\x00\x1b\x00\x01\x02\x00\x1c\x00\x01\x03\x00\x1d\x00\x00\xff\x0b\x00\x0c\x38",
        "2014": b"\x04\x01\x00\x25\x00\x00\x01\x00\x00\x00\x15\x00\x06\x01\x00\x1b\x00\x01\x02\x00\x1c\x00\x01\x03\x00\x1d\x00\x00\xff\x0c\x00\x07\xd0"
    }

    def __init__(self, factory):
        self._busyReceiving = False
        self._buffer = b""
        self.factory = factory
        self.setTimeout(10)

    @staticmethod
    def build_packet(tds):
        """Builds a TDS packet from header and payload."""
        header = struct.pack('>BBHHBB', tds.type, tds.status, len(tds.payload) + MSSQLProtocol.TDS_HEADER_LEN,
                             tds.spid, tds.packetid, tds.window)
        return header + tds.payload

    @staticmethod
    def parse_prelogin(data):
        """Parses the PreLogin packet and returns options."""
        index = data.find(b"\xff")
        if index <= 0:
            return None

        options = data[:index]
        if len(options) % 5 != 0:
            return None

        def get_option(i):
            token, offset, length = struct.unpack(">BHH", options[i:i+5])
            return PreLoginOption._make((token, data[offset:offset + length]))

        return list(map(get_option, range(0, len(options), 5)))

    @staticmethod
    def build_prelogin(preloginopts):
        """Constructs PreLogin packet from options."""
        preloginopts.sort(key=lambda x: x.token)
        dataoffset = len(preloginopts) * 5 + 1
        data, header = b"", b""

        for opt in preloginopts:
            offset = dataoffset + len(data)
            length = len(opt.data)
            header += struct.pack(">BHH", opt.token, offset, length)
            data += opt.data

        return header + b"\xff" + data

    def process(self, tds):
        """Processes incoming TDS packets."""
        if not tds.payload:
            return

        if tds == MSSQLProtocol.NMAP_PROBE_1:
            self.transport.write(MSSQLProtocol.NMAP_PROBE_1_RESP[self.factory.canaryservice.version])
        elif tds.type == MSSQLProtocol.TDS_TYPE_PRELOGIN:
            rPreLogin = [
                PreLoginOption(MSSQLProtocol.PRELOGIN_VERSION, b'\x0c\x00\x10\x04\x00\x00'),
                PreLoginOption(MSSQLProtocol.PRELOGIN_ENCRYPTION, b'\x02'),
                PreLoginOption(MSSQLProtocol.PRELOGIN_INSTOPT, b'\x00'),
                PreLoginOption(MSSQLProtocol.PRELOGIN_THREADID, b''),
                PreLoginOption(MSSQLProtocol.PRELOGIN_MARS, b'\x00'),
                PreLoginOption(MSSQLProtocol.PRELOGIN_TRACEID, b'')
            ]
            payload = self.build_prelogin(rPreLogin)
            self.transport.write(self.build_packet(TDSPacket(MSSQLProtocol.TDS_TYPE_RESPONSE, 0x01, 0, 1, 0, payload)))

        elif tds.type == MSSQLProtocol.TDS_TYPE_LOGIN7:
            login_data = self.parse_login7(tds.payload)
            if not login_data:
                self.transport.abortConnection()
                return
            error_message = self.handle_login(login_data)
            payload = self.build_error(error_message, "")
            payload += b"\xfd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            self.transport.write(self.build_packet(TDSPacket(MSSQLProtocol.TDS_TYPE_RESPONSE, 0x01, 54, 1, 0, payload)))

    def handle_login(self, login_data):
        """Handles the login process based on NTLM or SQL Auth and logs appropriately."""
        ntlm = login_data.pop('NTLM', None)
        if ntlm:
            log_data = {'USERNAME': '', 'PASSWORD': ''}
            logtype = self.factory.canaryservice.logger.LOG_MSSQL_LOGIN_WINAUTH
            self.factory.canaryservice.log(log_data, transport=self.transport, logtype=logtype)
            return "Login failed."
        else:
            logtype = self.factory.canaryservice.logger.LOG_MSSQL_LOGIN_SQLAUTH
            self.factory.canaryservice.log(login_data, transport=self.transport, logtype=logtype)
            username = login_data.get("UserName", "")
            return f"Login failed for user {username}."

    def dataReceived(self, data):
        """Handles incoming data."""
        self._buffer += data
        self.resetTimeout()
        if self._busyReceiving:
            return
        try:
            self._busyReceiving = True
            tds = self.consume_packet()
            if tds:
                self.process(tds)
        finally:
            self._busyReceiving = False

    def consume_packet(self):
        """Consumes a TDS packet from the buffer."""
        if len(self._buffer) < MSSQLProtocol.TDS_HEADER_LEN:
            return None
        try:
            header = list(struct.unpack('>BBHHBB', self._buffer[:MSSQLProtocol.TDS_HEADER_LEN]))
            plen = header[2]
            del header[2]
            if len(self._buffer) >= plen:
                payload = self._buffer[MSSQLProtocol.TDS_HEADER_LEN:plen]
                self._buffer = self._buffer[plen:]
                return TDSPacket._make(header + [payload])
        except Exception as e:
            print(f"Error consuming packet: {e}")
        return None


class SQLFactory(Factory):
    """SQL Factory for building MSSQL Protocol instances."""
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        return MSSQLProtocol(self)


class MSSQL(CanaryService):
    """MSSQL Service Implementation for OpenCanary."""
    NAME = 'mssql'

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)
        self.port = int(config.getVal("mssql.port", default=1433))
        self.version = config.getVal("mssql.version", default="2012")
        self.listen_addr = config.getVal('device.listen_addr', default='')
        if self.version not in MSSQLProtocol.NMAP_PROBE_1_RESP:
            raise ConfigException("mssql.version", "Invalid MSSQL Version")

    def getService(self):
        factory = SQLFactory()
        factory.canaryservice = self
        return internet.TCPServer(self.port, factory, interface=self.listen_addr)
