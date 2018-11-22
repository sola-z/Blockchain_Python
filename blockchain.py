import slots
import protocol
import block
import transaction
import hashlist
import pbft
import time
import math
import threading
from tkinter import *


class BlockChain:
    def __init__(self, node, is_pbft, gui):
        self.gui = gui

        self.node = node
        data = {'height': 0, "timestamp": 1462953000, 'previousHash': '',
                'generatorId': 0, 'transactions': [{'amount': 100000000 * 100000000,
                                                    'timestamp': 1462953000, 'recipient': 'neo',
                                                    'sender': ''}]}
        new_blk = block.Block(data)
        self.genesis = new_blk
        self.pendingTransactions = {}
        self.transactionIndex = {}
        self.isPBFT = is_pbft
        self.needHelp = False
        self.targetHeight = 0
        self.needHeight = 1
        self.pbft = pbft.PBFT(self)
        self.lastSlot = 0
        self.lock = threading.Lock()
        self.chain = hashlist.HashList(self)
        self.chain.add(self.genesis.get_hash(), self.genesis)

    def start(self):
        while True:
            self.node.peer.check_peers_alive()
            time.sleep(16)
            self.loop()

    # functions regarding transactions
    def has_transaction(self, trs):
        trans_id = trs.get_hash()
        if (trans_id in self.pendingTransactions) or (trans_id in self.transactionIndex):
            return True
        else:
            return False

    def validate_transaction(self, trs):
        if trs:
            return True
        else:
            return False

    def add_transaction(self, trs):
        self.pendingTransactions[trs.get_hash()] = trs

    # functions regarding blocks
    def has_block(self, block_hash):
        if (self.chain.get(block_hash)) or (self.pbft.has_block(block_hash)):
            return True
        else:
            return False

    def validate_block(self, the_block):
        if not the_block:
            return False
        else:
            last_block = self.chain.last()
            if (the_block.get_height() == last_block.get_height() + 1) and (
                    the_block.get_previous_hash() == last_block.get_hash()):
                return True
            else:
                return False

    def six_blocks_behind(self, the_block):
        if not the_block:
            return False
        else:
            last_block = self.chain.last()
            if the_block.get_height() >= (last_block.get_height() + 6):
                return True
            else:
                return False

    def add_block(self, the_block):
        if self.isPBFT and (not self.node.is_bad):
            slot_number = slots.get_slot_number(slots.get_time(the_block.get_timestamp()))
            self.pbft.add_block(the_block, slot_number)
        else:
            self.commit_block(the_block)
            self.pbft.isBusy = False

    def commit_block(self, the_block):
        self.chain.add(the_block.get_hash(), the_block)
        transactions = the_block.get_transaction()
        for each in transactions:
            self.transactionIndex[each.get_hash()] = each

    def create_block(self):
        last_block = self.chain.last()
        if last_block:
            sec = math.floor(time.time())
            data = {'height': last_block.get_height() + 1, 'timestamp': sec, 'previousHash': last_block.get_hash(),
                    'generatorId': self.node.id}
            new_block = block.Block(data)
            for each in self.pendingTransactions:
                new_block.add_transaction(each)
            self.pendingTransactions = {}
            return new_block

    # functions regarding message
    def process_message(self, msg):
        self.lock.acquire()
        if msg['type'] == protocol.messageType['Transaction']:
            trs = transaction.Transaction(msg['body'])
            if not self.has_transaction(trs):
                if self.validate_transaction(trs):
                    self.node.broadcast(msg)
                    self.add_transaction(trs)
        elif msg['type'] == protocol.messageType['Block']:
            the_block = block.Block(msg['body'])
            if not self.has_block(the_block.get_hash()):
                if self.validate_block(the_block):
                    if self.needHelp:
                        self.needHelp = False
                        self.targetHeight = 0
                        self.needHeight = 1
                    self.node.broadcast(msg)
                    self.add_block(the_block)
                elif not self.needHelp:
                    if self.six_blocks_behind(the_block):
                        self.needHelp = True
                        self.needHeight = 1
                        # helper = the_block.get_generator_id()
                        # message = {'id': self.node.id}
                        self.targetHeight = the_block.get_height()
                        message = {'target': self.needHeight}
                        self.node.broadcast(protocol.help_message(message))
                elif self.needHelp:
                    if the_block.get_height() > self.targetHeight:
                        self.targetHeight = the_block.get_height()
        elif msg['type'] == protocol.messageType['Help']:
            offset = int(msg['body']['target'])
            if offset <= self.chain.last().get_height():
                the_block = self.chain.select(offset, 1, False)[0]
                self.node.broadcast(protocol.answer_message(the_block.get_data()))
        elif (msg['type'] == protocol.messageType['Answer']) and self.needHelp:
            the_block = block.Block(msg['body'])
            if not self.has_block(the_block.get_hash()):
                if self.validate_block(the_block):
                    self.commit_block(the_block)
                    self.needHeight += 1
                    message = {'target': self.needHeight}
                    self.node.broadcast(protocol.help_message(message))
        elif msg['type'] == protocol.messageType['Prepare'] or msg['type'] == protocol.messageType['Commit']:
            if self.isPBFT and (not self.node.is_bad):
                self.pbft.process_message(msg)
        self.lock.release()

    def print_block_chain(self):
        output = ''
        output_format = '({}:{}:{}) ->'
        counter = 0
        node = self.chain.head
        while node is not None:
            the_block = node.data
            output += output_format.format(counter, the_block.get_hash()[:6], the_block.get_generator_id())
            node = node.next
            counter += 1
        myStr = 'node ' + str(self.node.id) + ': ' + output
        # print(myStr)
        self.printToGui(myStr)

    def get_block_chain(self):
        output = ''
        output_format = '({}:{}:{}) ->'
        counter = 0
        node = self.chain.head
        while node is not None:
            the_block = node.data
            output += output_format.format(counter, the_block.get_hash()[:6], the_block.get_generator_id())
            node = node.next
            counter += 1
        myStr = 'node ' + str(self.node.id) + ': ' + output
        return myStr

    def printToGui(self, str):
        theList = self.gui.winfo_children()[2]
        theList.insert(END, str)

    def make_fork(self):
        last_block = self.chain.last()
        if last_block is not None:
            height = last_block.get_height() + 1
            timestamp = math.floor(time.time())
            new_blk = {'height': height, 'timestamp': timestamp, 'previousHash': last_block.get_hash(),
                       'generatorId': self.node.id}
            block1 = block.Block(new_blk)
            new_trs = {'amount': 1000, 'recipient': 'alice', 'sender': 'cracker'}
            new_trs1 = transaction.Transaction(new_trs)
            block1.add_transaction(new_trs1)

            block2 = block.Block(new_blk)
            new_trs = {'amount': 1000, 'recipient': 'bob', 'sender': 'cracker'}
            new_trs2 = transaction.Transaction(new_trs)
            block2.add_transaction(new_trs2)

            forkStr = 'fork on node: {}, height: {}    fork1: {}    fork2: {}'
            forkFormat = forkStr.format(self.node.id, last_block.get_height() + 1, block1.get_hash(), block2.get_hash())
            # print("fork on node: %d, height: %d, fork1: %s, fork2: %s" % (self.node.id,
                  # last_block.get_height() + 1, block1.get_hash(), block2.get_hash()))
            print(forkFormat)
            self.printToGui(forkFormat)
            theList = self.gui.winfo_children()[2]
            listSize = theList.size()
            theList.itemconfig(listSize - 1, bg='red')

            i = 0
            self.add_block(block1)
            for each in self.node.peer.peers:
                if i % 2 == 0:
                    # fork1Str = 'send fork1 to' + str(each)
                    # # print(fork1Str)
                    # self.printToGui(fork1Str)
                    # theList = self.gui.winfo_children()[2]
                    # listSize = theList.size()
                    # theList.itemconfig(listSize - 1, fg='red')
                    self.node.peer.send_to_peer(each, protocol.block_message(block1.get_data()))
                else:
                    # fork2Str = 'send fork2 to' + str(each)
                    # # print(fork2Str)
                    # self.printToGui(fork2Str)
                    # theList = self.gui.winfo_children()[2]
                    # listSize = theList.size()
                    # theList.itemconfig(listSize - 1, fg='red')
                    self.node.peer.send_to_peer(each, protocol.block_message(block2.get_data()))
                i += 1

    def loop(self):
        current_slot = slots.get_slot_number()
        last_block = self.chain.last()
        if last_block is not None:
            last_slot = slots.get_slot_number(slots.get_time(last_block.get_timestamp()))
            sec = math.floor(time.time())
            if current_slot == last_slot or sec % 10 > 5:
                return
            if self.isPBFT and self.lastSlot == current_slot:
                return
            delegate_id = current_slot % slots.delegates
            if self.node.id == delegate_id:
                if not self.node.is_bad:
                    the_block = self.create_block()
                    myStr = 'slots: {}, height: {}, nodeId: {}'
                    str2 = myStr.format(current_slot, the_block.get_height(), self.node.id)
                    # print(str2)
                    self.printToGui(str2)
                    theList = self.gui.winfo_children()[2]
                    listSize = theList.size()
                    theList.itemconfig(listSize-1, bg='green')

                    # print('slots: {}, height: {}, nodeId: {}'.format(current_slot, the_block.get_height(), self.node.id))
                    self.add_block(the_block)
                    self.node.broadcast(protocol.block_message(the_block.get_data()))
                    self.lastSlot = current_slot
                else:
                    self.make_fork()
