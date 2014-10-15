import socket

from . import defaults
from . import framing


class HekaConnection(object):

    DEFAULT_ADDRESS = 'localhost:{}'.format(defaults.DEFAULT_PORT)
    SOCKET_FAMILY = socket.SOCK_DGRAM

    def __init__(self, address=DEFAULT_ADDRESS, signer_config=None, lazy=False):
        self.socket = None

        host, port = address.split(':')
        self.host = host
        self.port = int(port)

        self.signer_config = signer_config

        if not lazy:
            self.establish()

    @property
    def address(self):
        return (self.host, self.port)

    def establish(self):
        _socket = socket.socket(
            socket.AF_INET,
            self.SOCKET_FAMILY,
        )
        _socket.connect(self.address)
        self.socket = _socket

    def _send_until_sent(self, payload):
        sent_total = 0
        while sent_total < len(payload):
            sent = self.socket.send(payload[sent_total:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            sent_total = sent_total + sent

    def send(self, payload):
        if not self.socket:
            self.establish()

        framed_payload = framing.frame(payload, self.signer_config)
        print repr(framed_payload)

        # Send until all bytes written
        self._send_until_sent(framed_payload)

    def send_message(self, message):
        self.send(message.encode())


# Ignore this for now
class ReliableConnection(HekaConnection):
    SOCKET_FAMILY = socket.SOCK_STREAM
