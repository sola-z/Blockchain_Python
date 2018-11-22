import socket
import struct
import traceback


class Connection:

    def __init__(self, peer_id, host, port, sock=None):

        self.id = peer_id

        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

    def __make_package(self, message):

        message = message.encode('utf-8')
        length = len(message)
        package = struct.pack("!L%ds" % length, length, message)
        return package

    def send_package(self, message):
        """Send a message through a peer connection."""
        try:
            package = self.__make_package(message)
            self.s.send(package)
        except:
            print("Send Error")
            traceback.print_exc()

    def recv_package(self):
        """Receive a message from a peer connection. Returns None if it was just to debug or there was any error."""
        try:
            package_length = self.s.recv(4)
            length = int(struct.unpack("!L", package_length)[0])
            message = "".encode("utf-8")

            while len(message) != length:
                data = self.s.recv(min(2048, length - len(message)))
                if not len(data):
                    break
                message += data

            if len(message) != length:
                return None
        except:
            print("Receive Error")
            traceback.print_exc()
            return None
        message = str(struct.unpack("%ds" % length, message)[0])[2:-1]
        if message == "PING":
            return None
        else:
            return message

    def close(self):
        """Close the peer connection. The send and recv methods will not work after this call."""
        self.s.close()
        self.s = None
