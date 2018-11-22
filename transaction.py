import time
import hashlib
import math


class Transaction:
    """New transaction"""

    def __init__(self, data):
        self.data = {'amount': 0, 'timestamp': math.floor(time.time() / 1000),
                     'recipient': '', 'sender': '', 'hash': None}
        self.size = 0

        if 'amount' in data:
            self.data['amount'] = data['amount']
        if 'timestamp' in data:
            self.data['timestamp'] = data['timestamp']
        if 'recipient' in data:
            self.data['recipient'] = data['recipient']
        if 'sender' in data:
            self.data['sender'] = data['sender']
        if not self.data['hash']:
            self.size, self.data['hash'] = self.calculate_hash()

    def get_data(self):
        return self.data

    def get_size(self):
        return self.size

    def get_hash(self):
        return self.data['hash']

    def get_amount(self):
        return self.data['amount']

    def get_time_stamp(self):
        return self.data['timestamp']

    def get_recipient(self):
        return self.data['recipient']

    def get_sender(self):
        return self.data['sender']

    def get_bytes(self):
        block_string = "{}{}{}{}".format(self.data['amount'], self.data['timestamp'], self.data['recipient'],
                                         self.data['sender'])
        return block_string.encode()

    def calculate_hash(self):
        bytes_data = self.get_bytes()
        size = len(bytes_data)
        return size, hashlib.sha256(bytes_data).hexdigest()
