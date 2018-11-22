import socket
import threading
import traceback
import connection
import json


class Peer:
    """ A peer in a P2P network."""

    def __init__(self, self_id, ip, port, node):
        """ The IP is local IP and the port is randomly chosen"""

        self.id = self_id
        self.ip = ip
        self.port = port
        self.node = node

        self.lock = threading.Lock()
        self.peers = {}
        self.shutdown = False

    def __handle_message(self, sender_socket):
        """ Handle messages from the socket connection"""
        host, port = sender_socket.getpeername()
        p2p_connection = connection.Connection(None, host, port, sender_socket)

        try:
            message = p2p_connection.recv_package()
            if message is not None:
                message = json.loads(message)
                message_type = message["type"]
                if message_type == "connection":
                    self.connection_handler(message)
                else:
                    self.handle(message)
        except:
            traceback.print_exc()
        p2p_connection.close()

    def connection_handler(self, msg):
        peer_id = msg["id"]
        ip = msg["ip"]
        port = msg["port"]
        self.add_peer(peer_id, ip, port)

    def handle(self, message):
        self.node.handle(message)

    def check_id(self, peer_id):
        if peer_id in self.peers:
            return True
        else:
            return False

    def set_id(self, my_id):
        """Choose an id to hide the ip and port information"""
        self.id = my_id

    def get_id(self):
        return self.id

    def get_info(self):
        """Get personal information"""
        print("==== User Information ====")
        print("ID: %s" % self.id)
        print("IP Address: %s" % self.ip)
        print("Port: %s" % self.port)
        print("==========================")

    def add_peer(self, peer_id, ip, port):
        """ Add a peer with its ip and port to the known list of peers."""
        # self.lock.acquire()
        if (peer_id not in self.peers) and (peer_id != self.id):
            self.peers[peer_id] = (ip, int(port))
        # self.lock.release()

    def get_peer(self, peer_id):
        """ Returns the host and port information for a given peer name """
        if peer_id in self.peers:
            return self.peers[peer_id]
        else:
            return None, None

    def remove_peer(self, peer_id):
        """ Removes peer information from the known list of peers. """
        # self.lock.acquire()
        if peer_id in self.peers:
            del self.peers[peer_id]
        # self.lock.release()

    def get_number_of_peers(self):
        """ Return the number of known peer's. """
        return len(self.peers)

    def get_peer_ids(self):
        """ Return a list of all known peer peer_id's. """
        for peer_id in self.peers:
            print(peer_id)

    def make_listener_socket(self, port, backlog=10000):
        """ Make a socket to listen on the given port."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(backlog)
        return s

    def broadcast(self, message):
        """ Broadcast to all the known hosts """
        self.lock.acquire()
        for peer in self.peers:
            self.send_to_peer(peer, message)
        self.lock.release()

    def send_to_peer(self, receiver_id, message):
        """ Send a message to a known host."""
        if receiver_id in self.peers:
            host, port = self.get_peer(receiver_id)
            self.connect_and_send(host, port, message, receiver_id=receiver_id)
        else:
            print("There is no such a host with ID called %s" % receiver_id)

    def connect_and_send(self, host, port, message, receiver_id=None):
        """ Connect and send a message to a known host """
        try:
            connection_for_send = connection.Connection(receiver_id, host, port)
            message = json.dumps(message)
            connection_for_send.send_package(message)
            connection_for_send.close()
        except:
            # self.remove_peer(receiver_id)
            print("---- Cannot Access the Host %s ----" % receiver_id)

    def check_peers_alive(self):
        """ Ping all currently known hosts to ensure they are still active. Removes all the inactive ones."""
        lost_peers = []
        for peer in self.peers:
            try:
                host, port = self.peers[peer]
                test_connection = connection.Connection(peer, host, port)
                test_connection.send_package('PING')
                test_connection.close()
            except:
                lost_peers.append(peer)

        self.lock.acquire()
        try:
            for peer in lost_peers:
                self.remove_peer(peer)
                print("host %s is not alive" % peer)
        finally:
            self.lock.release()

    def listener(self):
        """Always listen to the upcoming messages"""
        s = self.make_listener_socket(self.port)

        while not self.shutdown:
            try:
                sender_socket, sender_address = s.accept()
                sender_socket.settimeout(None)
                t = threading.Thread(target=self.__handle_message, args=[sender_socket])
                t.start()
            except:
                print('Lose Connection')
                traceback.print_exc()
                self.shutdown = True
                continue
        s.close()
