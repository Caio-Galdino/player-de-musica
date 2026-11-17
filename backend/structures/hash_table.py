from .node import HashNode

class HashTable:
    def __init__(self, capacity=8):
        if capacity <= 0:
            raise ValueError("A capacidade deve ser maior que zero")

        self._capacity = capacity
        self._buckets = [None] * capacity
        self._size = 0

    def _hash(self, key):
        h = 0

        for character in key:
            h = h * 31 + ord(character)

        return h % self._capacity

    def _find_node(self, key):
        index = self._hash(key)
        node = self._buckets[index]

        while node is not None:
            if node.key == key:
                return node

            node = node.next

        return None

    def put(self, key, value):
        node = self._find_node(key)

        if node is not None:
            node.value = value
            return

        index = self._hash(key)
        #insere no inicio da corrente desse balde
        node = HashNode(key, value)
        node.next = self._buckets[index]
        self._buckets[index] = node
        self._size += 1

        if self._size / self._capacity > 0.75:
            self._rehash()

    def get(self, key):
        node = self._find_node(key)

        if node is None:
            raise KeyError(key)

        return node.value

    def contains(self, key):
        return self._find_node(key) is not None

    def remove(self, key):
        index = self._hash(key)
        node = self._buckets[index]
        previous = None

        while node is not None:
            if node.key == key:
                if previous is None:
                    self._buckets[index] = node.next
                else:
                    previous.next = node.next

                self._size -= 1
                return node.value

            previous = node
            node = node.next

        raise KeyError(key)

    def size(self):
        return self._size

    def is_empty(self):
        return self._size == 0
    
    def _rehash(self):
        old_buckets = self._buckets

        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._size = 0

        # Recalcular os indices usando a nova capacidade
        for bucket in old_buckets:
            node = bucket

            while node is not None:
                self.put(node.key, node.value)
                node = node.next
