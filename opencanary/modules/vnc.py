from opencanary.modules import CanaryService
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet
from opencanary.modules.des import des
import os

# Define VNC protocol versions
RFB_VERSIONS = {
    "3.3": b'003.003',
    "3.7": b'003.007',
    "3.8": b'003.008'
}

# Common passwords for VNC authentication attempts
COMMON_PASSWORDS = [
    '111111', 'password', '123456', '1234',
    'administrator', 'root', 'passw0rd'
]

# Protocol States
PRE_INIT = 0
HANDSHAKE_SEND = 1
SECURITY_SEND = 2
AUTH_SEND = 3
AUTH_OVER = 4

class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass

class UnsupportedVersion(Exception):
    """Custom exception for unsupported protocol versions."""
    pass

class VNCProtocol(Protocol):
    """Implementation of VNC protocol up to authentication."""

    def __init__(self, version: bytes = RFB_VERSIONS["3.8"]):
        self.serv_version = version
        self.state = PRE_INIT
        self.challenge = None

    def _send_handshake(self):
        """Send VNC handshake to the client."""
        self.log_debug('Sending handshake')
        version_string = f'RFB {self.serv_version.decode("utf-8")}\n'
        self.transport.write(version_string.encode('utf-8'))
        self.state = HANDSHAKE_SEND

    def _recv_handshake(self, data: bytes):
        """Receive handshake from the client."""
        self.log_debug('Received handshake')
        if len(data) != 12 or not data.startswith(b'RFB'):
            raise ProtocolError("Invalid handshake response.")

        client_ver = data[4:-1]
        if client_ver not in RFB_VERSIONS.values():
            raise UnsupportedVersion(f"Unsupported version: {client_ver.decode('utf-8')}")

        self._send_security(client_ver)

    def _send_security(self, client_ver: bytes):
        """Send security request to the client."""
        self.log_debug('Sending security request')
        if client_ver == RFB_VERSIONS["3.3"]:
            self.transport.write(b'\x00\x00\x00\x02')
            self._send_auth()
        else:
            self.transport.write(b'\x01\x02')
            self.state = SECURITY_SEND

    def _recv_security(self, data: bytes):
        """Receive security response from the client."""
        self.log_debug('Received security response')
        if len(data) != 1 or data != b'\x02':
            raise ProtocolError("Invalid security response.")

        self._send_auth()

    def _send_auth(self):
        """Send authentication challenge to the client."""
        self.log_debug('Sending authentication challenge')
        self.challenge = os.urandom(16)
        self.transport.write(self.challenge)
        self.state = AUTH_SEND

    def _recv_auth(self, data: bytes):
        """Receive authentication response from the client."""
        self.log_debug('Received authentication response')
        if len(data) != 16:
            raise ProtocolError("Invalid authentication response.")

        logdata = {
            "VNC Server Challenge": self.challenge.hex(),
            "VNC Client Response": data.hex()
        }

        used_password = self._try_decrypt_response(response=data)
        logdata['VNC Password'] = used_password if used_password else '<Password not found in common list>'
        self.factory.log(logdata, transport=self.transport)
        self._send_auth_failed()

    def connectionMade(self):
        """Handle new connection."""
        if self.state != PRE_INIT:
            raise ProtocolError("Connection made in invalid state.")
        self._send_handshake()

    def _send_auth_failed(self):
        """Send authentication failure response to the client."""
        self.transport.write(b'\x00\x00\x00\x01' +
                             b'\x00\x00\x00\x16' +
                             b'Authentication failure')
        self.state = AUTH_OVER
        raise ProtocolError("Authentication failed.")

    def _try_decrypt_response(self, response: bytes) -> str:
        """Attempt to decrypt the response using common passwords."""
        values = bytearray(int(f'{x:08b}'[::-1], 2) for x in response)
        desbox = des(values)

        for password in COMMON_PASSWORDS:
            # Ensure the password is 8 bytes
            pw = (password + '\x00' * (8 - len(password)))[:8].encode('ascii')
            decrypted_challenge = desbox.decrypt(pw)

            if decrypted_challenge == self.challenge:
                return password
        return None

    def dataReceived(self, data: bytes):
        """Handle incoming data based on the current state."""
        try:
            if self.state == HANDSHAKE_SEND:
                self._recv_handshake(data=data)
            elif self.state == SECURITY_SEND:
                self._recv_security(data=data)
            elif self.state == AUTH_SEND:
                self._recv_auth(data=data)
        except (UnsupportedVersion, ProtocolError) as e:
            self.log_debug(f'Error occurred: {e}')
            self.transport.loseConnection()

class CanaryVNC(Factory, CanaryService):
    """Factory for creating VNC service instances."""

    NAME = 'VNC'
    protocol = VNCProtocol

    def __init__(self, config=None, logger=None):
        super().__init__(config, logger)
        self.port = config.getVal("vnc.port", 5900)
        self.logtype = logger.LOG_VNC
        self.debug = config.getVal('vnc.debug', False)

    def log_debug(self, message: str):
        """Log debug messages if debugging is enabled."""
        if self.debug:
            print(message)

    def getService(self):
        """Return the service for the VNC factory."""
        return internet.TCPServer(self.port, self)

CanaryServiceFactory = CanaryVNC
