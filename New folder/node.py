import peer
import blockchain
import random
import threading


class Node:
    port_list = [50010, 50011, 50012, 50013, 50014, 50015, 50016, 50017, 50018, 50019,
                 50020, 50021, 50022, 50023, 50024, 50025, 50026, 50027, 50028, 50029]

    def __init__(self, ip, i, num, is_bad, is_pbft, gui):
        self.ip = ip
        self.gui = gui
        self.id = i
        self.num = num
        self.is_bad = is_bad
        self.peer = peer.Peer(self.id, self.ip, self.port_list[self.id], self)

        t = threading.Thread(target=self.peer.listener)
        t.start()
        self.block_chain = blockchain.BlockChain(self, is_pbft, gui)

    def connect(self):
        for i in range(5):
            rand = random.randint(20 - self.num, 19)
            if rand != self.id:
                self.peer.add_peer(str(rand), ip=self.ip, port=self.port_list[rand])
                self.peer.send_to_peer(str(rand), self.pack_self_info())
            # # rand = random.randint(0, 1)
            # rand = random.randint(0, 0)
            # if rand == 0:
            #     # rand = random.randint(0, 9)
            #     rand = random.randint(0, 19)
            #     if rand != self.id:
            #         self.peer.add_peer(str(rand), ip="127.0.0.1", port=self.port_list[rand])
            #         self.peer.send_to_peer(str(rand), self.pack_self_info())
            # if rand == 1:
            #     rand = random.randint(0, 9)
            #     self.peer.add_peer(str(rand), ip="10.13.142.90", port=self.port_list[rand])
            #     # self.peer.add_peer(str(rand), ip="10.13.163.38", port=self.port_list[rand])
            #     self.peer.send_to_peer(str(rand), self.pack_self_info())

    def print_block_chain(self):
        self.block_chain.print_block_chain()

    def start(self):
        self.block_chain.start()

    def broadcast(self, message):
        self.peer.broadcast(message)

    def pack_self_info(self):
        message = {"type": "connection", "id": self.id, "ip": self.ip, "port": self.port_list[self.id]}
        return message

    def handle(self, msg):
        self.block_chain.process_message(msg)

