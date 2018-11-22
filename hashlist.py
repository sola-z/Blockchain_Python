class ListNode:
    def __init__(self, data):
        self.next = None
        self.prev = None
        self.data = data


class HashList:
    def __init__(self, block_chain):
        self.head = None
        self.tail = None
        self.size = 0
        self.map = {}
        self.block_chain = block_chain

    def size(self):
        return self.size

    # add one extra node to end of list
    def add(self, key, value):
        new_node = ListNode(value)
        self.map[key] = new_node
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        elif self.head == self.tail:
            self.head.next = new_node
            new_node.prev = self.head
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1
        self.block_chain.print_block_chain()

    # return specific node
    def get(self, key):
        if key in self.map:
            return self.map[key]
        else:
            return None

    # delete one node from map and retrieve its data
    def remove(self, key):
        if key in self.map:
            node = self.map[key]
            prev_node = node.prev
            next_node = node.next
            if prev_node:
                prev_node.next = next_node
            if next_node:
                next_node.prev = prev_node
            if node == self.head and node == self.tail:
                self.head = None
                self.tail = None
            elif node == self.head:
                self.head = next_node
            elif node == self.tail:
                self.tail = prev_node

            del self.map[key]
            self.size -= 1
            return node.data
        else:
            return None

    # delete first node and retrieve its data
    def pop(self):
        if not self.head:
            return None
        self.size -= 1
        head = self.head
        if self.head == self.tail:
            self.head = None
            self.tail = None
            return head.data
        else:
            self.head = self.head.next
            self.head.prev = None
            return head.data

    # select an amount of data from all nodes from lists starting specified by offset
    def select(self, offset, limit, reverse):
        result = []
        # nothing to traverse
        if limit < 0:
            return result

        # direction of traversal
        if reverse:
            node = self.tail
        else:
            node = self.head

        # skip to the starting position
        while node and offset > 0:
            if reverse:
                node = node.prev
            else:
                node = node.next
            offset -= 1  # count traversed elements

        while node and limit > 0:
            result.append(node.data)
            if reverse:
                node = node.prev
            else:
                node = node.next
            limit -= 1
        return result

    def first(self):
        if self.head:
            return self.head.data
        else:
            return None

    def last(self):
        if self.tail:
            return self.tail.data
        else:
            return None
