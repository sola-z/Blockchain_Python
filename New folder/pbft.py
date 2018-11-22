import slots
import math
import protocol
import time
import threading


PBFT_N = slots.delegates
PBFT_F = math.floor((PBFT_N - 1) / 3)
State = {"None": 0, "Prepare": 1, "Commit": 2}


class PBFT:
    def __init__(self, block_chain):
        self.block_chain = block_chain
        self.node = block_chain.node
        self.pendingBlocks = {}
        self.prepareInfo = None
        self.commitInfo = {}
        self.state = State["None"]
        self.prepareHashCache = {}
        self.commitHashCache = {}
        self.currentSlot = 0

    def has_block(self, block_hash):
        if block_hash in self.pendingBlocks:
            return True
        else:
            return False

    def is_busy(self):
        if self.state == State["None"]:
            return False
        else:
            return True

    def add_block(self, block, slot):
        block_hash = block.get_hash()
        # print('pbft add_block: ' + str(self.node.id) + ' ' + block_hash)
        self.pendingBlocks[block_hash] = block
        if slot > self.currentSlot:
            self.clear_state()

        if self.state == State["None"]:
            self.currentSlot = slot
            self.state = State["Prepare"]
            self.prepareInfo = {
                "height": block.get_height(),
                "hash": block_hash,
                "votesNumber": 1,
                "votes": {}
            }

        # need proof of node signature in formal implementation
        # ?????
            data = protocol.prepare_message({
                'height': block.get_height(),
                'hash': block_hash,
                'signer': self.node.id
            })
            self.prepareInfo['votes'][self.node.id] = True
            t = threading.Thread(target=self.delay_broadcast, args=[data])
            t.start()

    def delay_broadcast(self, data):
        time.sleep(2)
        self.node.broadcast(data)

    def clear_state(self):
        self.state = State["None"]
        self.prepareInfo = None
        self.commitInfo = {}
        self.pendingBlocks = {}

    def commit(self, block_hash):
        if block_hash in self.pendingBlocks:
            block = self.pendingBlocks[block_hash]
            self.block_chain.commit_block(block)
            self.clear_state()

    def process_message(self, msg):
        if msg["type"] == protocol.messageType["Prepare"]:
            d = msg['body']
            key = d['hash'] + ':' + str(d['height']) + ':' + str(d['signer'])
            if key not in self.prepareHashCache:
                self.prepareHashCache[key] = True
                self.node.broadcast(msg)
            else:
                return

            # while True:
            #     if self.state != State["None"]:
            #         break
            #     time.sleep(0.1)
            # if self.state == State["None"]:
            #     self.currentSlot = slot
            #     self.state = State["Prepare"]
            #     self.prepareInfo = {
            #         "height": block.get_height(),
            #         "hash": block_hash,
            #         "votesNumber": 1,
            #         "votes": {}
            #     }
            #
            #     # need proof of node signature in formal implementation
            #     # ?????
            #     self.prepareInfo['votes'][self.node.id] = True
            #     self.node.broadcast(protocol.prepare_message({
            #         'height': block.get_height(),
            #         'hash': block_hash,
            #         'signer': self.node.id
            #     }))

            if self.state == State["Prepare"] and (
                    d['height'] == self.prepareInfo['height']) and (
                    d['hash'] == self.prepareInfo['hash']) and (
                    d['signer'] not in self.prepareInfo['votes']):
                self.prepareInfo['votes'][d['signer']] = True
                self.prepareInfo['votesNumber'] += 1
                # print('pbft %d prepare votes: %d' % (self.node.id, self.prepareInfo['votesNumber']))

                if self.prepareInfo['votesNumber'] > PBFT_F:
                    # print('node %d change state to commit' % self.node.id)
                    self.state = State["Commit"]
                    commit_info = {
                        "height": self.prepareInfo['height'],
                        "hash": self.prepareInfo['hash'],
                        "votesNumber": 1,
                        "votes": {}
                    }
                    commit_info['votes'][self.node.id] = True
                    self.commitInfo[commit_info['hash']] = commit_info
                    self.node.broadcast(protocol.commit_message({
                        "height": self.prepareInfo['height'],
                        "hash": self.prepareInfo['hash'],
                        "signer": self.node.id
                    }))
            return
        elif msg["type"] == protocol.messageType["Commit"]:
            d = msg['body']
            key = d['hash'] + ':' + str(d['height']) + ':' + str(d['signer'])
            if key not in self.commitHashCache:
                self.commitHashCache[key] = True
                self.node.broadcast(msg)
            else:
                return

            if d['hash'] in self.commitInfo:
                commit = self.commitInfo[d['hash']]
                if d['signer'] not in commit['votes']:
                    commit['votes'][d['signer']] = True
                    commit['votesNumber'] += 1
                    # print('pbft %d commit votes: %d' % (self.node.id, commit['votesNumber']))
                    if commit['votesNumber'] > 2 * PBFT_F:
                        self.commit(d['hash'])
            else:
                self.commitInfo[d['hash']] = {
                    "hash": d['hash'],
                    "height": d['height'],
                    "votesNumber": 1,
                    "votes": {}
                }
                self.commitInfo[d['hash']]['votes'][d['signer']] = True
            return
        else:
            return
