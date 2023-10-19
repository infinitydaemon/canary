from opencanary.modules import CanaryService
from twisted.internet.protocol import Protocol, Factory

from opencanary.modules.des import des
import os

RFB_33  = b'003.003'
RFB_37  = b'003.007'
RFB_38  = b'003.008'

# Common passwords for VNC authentication attempt
COMMON_PASSWORDS = ['111111', 'password', '123456', '111111','1234',
                    'administrator','root','passw0rd']

class ProtocolError(Exception):
    pass

class UnsupportedVersion(Exception):
    pass

class VNCProtocol(Protocol):
    """
        Implementation of VNC up to VNC authentication
    """
    def __init__(self, version=RFB_38):
        self.serv_version = version
        self.state = PRE_INIT

    def _send_handshake(self):
        self.log_debug('send handshake')
        version_string = f'RFB {self.serv_version.decode("utf-8")}\n'
        self.transport.write(version_string.encode('utf-8'))
        self.state = HANDSHAKE_SEND

    def _recv_handshake(self, data=None):
        self.log_debug('got handshake')
        if len(data) != 12 or data[:3] != b'RFB':
            raise ProtocolError()
        client_ver = data[4:-1]

        if client_ver not in [RFB_33, RFB_37, RFB_38]:
            raise UnsupportedVersion()

        self._send_security(client_ver)

    def _send_security(self, client_ver):
        self.log_debug('send security')
        if client_ver == RFB_33:
            self.transport.write(b'\x00\x00\x00\x02')
            self._send_auth()
        else:
            self.transport.write(b'\x01\x02')
            self.state = SECURITY_SEND

    def _recv_security(self, data=None):
        self.log_debug('got security')
        if len(data) != 1 and data != b'\x02':
            raise ProtocolError()
        self._send_auth()

    def _send_auth(self):
        self.log_debug('send auth')
        self.challenge = os.urandom(16)
        self.transport.write(self.challenge)
        self.state = AUTH_SEND

    def _recv_auth(self, data=None):
        self.log_debug('got auth')
        if len(data) != 16:
            raise ProtocolError()

        logdata = {"VNC Server Challenge": self.challenge.hex(),
                   "VNC Client Response": data.hex()}

        used_password = self._try_decrypt_response(response=data)
        if used_password:
            logdata['VNC Password'] = used_password
        else:
            logdata['VNC Password'] = '<Password was not in the common list>'
        self.factory.log(logdata, transport=self.transport)
        self._send_auth_failed()

    def connectionMade(self):
        if self.state != PRE_INIT:
            raise ProtocolError()
        self._send_handshake()

    def _send_auth_failed(self):
        self.transport.write(b'\x00\x00\x00\x01' +
                             b'\x00\x00\x00\x16' +
                             b'Authentication failure')
        self.state = AUTH_OVER
        raise ProtocolError()

    def _try_decrypt_response(self, response=None):
        values = bytearray()
        for x in response:
            values.append(int(f'{x:08b}'[::-1], 2))

        desbox = des(values)

        for password in COMMON_PASSWORDS:
            pw = (password + '\x00' * (8 - len(password)))[:8]
            pw = pw.encode('ascii')
            decrypted_challenge = desbox.decrypt(pw)

            if decrypted_challenge == self.challenge:
                return password
        return None

    def dataReceived(self, data):
        try:
            if self.state == HANDSHAKE_SEND:
                self._recv_handshake(data=data)
            elif self.state == SECURITY_SEND:
                self._recv_security(data=data)
            elif self.state == AUTH_SEND:
                self._recv_auth(data=data)
        except (UnsupportedVersion, ProtocolError):
            self.transport.loseConnection()
            return

class CanaryVNC(Factory, CanaryService):
    NAME = 'VNC'
    protocol = VNCProtocol

    def __init__(self, config=None, logger=None):
        CanaryService.__init__(self, config, logger)
        self.port = config.getVal("vnc.port", 5900)
        self.logtype = logger.LOG_VNC
        self.debug = config.getVal('vnc.debug', False)

    def log_debug(self, message):
        if self.debug:
            print(message)

    def getService(self):
        return internet.TCPServer(self.port, self)

CanaryServiceFactory = CanaryVNC
