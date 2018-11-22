import transaction
import hashlib


class Block:
    """Unit in a Block Chain"""

    def __init__(self, data):
        self.data = {'version': 0, 'height': 0, 'size': 0,
                     'timestamp': 0, 'generatorId': 0,
                     'previousHash': '', 'merkle_hash': '',
                     'transactions': [], 'hash': ''}
        self.transactions = []

        if 'version' in data:
            self.data['version'] = data['version']
        if 'height' in data:
            self.data['height'] = data['height']
        if 'size' in data:
            self.data['size'] = data['size']
        if 'timestamp' in data:
            self.data['timestamp'] = data['timestamp']
        if 'generatorId' in data:
            self.data['generatorId'] = data['generatorId']
        if 'previousHash' in data:
            self.data['previousHash'] = data['previousHash']
        if 'merkle_hash' in data:
            self.data['merkle_hash'] = data['merkle_hash']
        if 'transactions' in data:
            self.data['transactions'] = data['transactions']

        size = 0
        for element in self.data['transactions']:
            trans = transaction.Transaction(element)
            size = size + trans.get_size()
            self.transactions.append(trans)

        if len(self.transactions) == 0:
            data = {'amount': 5, 'recipient': 'somebody', 'sender': 'nobody'}
            coin_base_trs = transaction.Transaction(data)
            size = size + coin_base_trs.get_size()
            self.transactions.append(coin_base_trs)

        for element in self.transactions:
            self.data['transactions'].append(element.get_data())

        if not self.data['size']:
            self.data['size'] = size

        if not self.data['merkle_hash']:
            self.data['merkle_hash'] = self.calculate_merkle_hash()

        if not self.data['hash']:
            self.data['hash'] = self.calculate_hash()

    def add_transaction(self, trs):
        self.transactions.append(trs)
        self.data["size"] = self.data["size"] + trs.get_size()
        self.data['transactions'].append(trs.get_data())
        self.data['merkle_hash'] = self.calculate_merkle_hash()
        self.data['hash'] = self.calculate_hash()

    def get_data(self):
        return self.data

    def get_version(self):
        return self.data['version']

    def get_height(self):
        return self.data['height']

    def get_size(self):
        return self.data['size']

    def get_timestamp(self):
        return self.data['timestamp']

    def get_generator_id(self):
        return self.data['generatorId']

    def get_previous_hash(self):
        return self.data['previousHash']

    def get_hash(self):
        return self.data['hash']

    def get_merkle_hash(self):
        return self.data['merkle_hash']

    def get_transaction(self):
        return self.transactions

    def calculate_merkle_hash(self):
        hashes = []
        for trans in self.transactions:
            hashes.append(trans.get_hash())
        while len(hashes) > 1:
            tmp = []
            for i in range(int((len(hashes) + 1) / 2)):
                md = hashlib.sha256()
                md.update(hashes[i * 2].encode())
                md.update(hashes[i * 2 + 1].encode())
                tmp.append(md.hexdigest())
            if len(hashes) % 2 == 1:
                tmp.append(hashes[len(hashes) - 1])
            hashes = tmp
        return hashes[0]

    def calculate_hash(self):
        block_string = "{}{}{}{}{}{}{}".format(self.data['version'], self.data['height'], self.data['size'],
                                               self.data['timestamp'], self.data['previousHash'],
                                               self.data['previousHash'],
                                               self.data['merkle_hash'])
        bytes_data = block_string.encode()
        return hashlib.sha256(bytes_data).hexdigest()
