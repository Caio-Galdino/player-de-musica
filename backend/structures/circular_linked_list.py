from .node import DoublyNode

class CircularLinkedList:
    def __init__(self):
        self._head = None
        self._current = None
        self._size = 0

    def append(self, value):
        node = DoublyNode(value)

        if self.is_empty():
            node.next = node
            node.prev = node
            self._head = node
            self._current = node
        else:
            last = self._head.prev

            node.prev = last
            node.next = self._head
            last.next = node
            self._head.prev = node

        self._size += 1

    def _unlink(self, node):
        # Remove o no e ajusta os vizinhos, o inicio, o atual e o tamanho.
        if self._size == 1:
            self._head = None
            self._current = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

            if node is self._head:
                self._head = node.next

            if node is self._current:
                self._current = node.next

        self._size -= 1

    def remove(self, value):
        if self.is_empty():
            raise ValueError("Valor nao encontrado na lista")

        node = self._head

        while True:
            if node.value == value:
                self._unlink(node)
                return

            node = node.next

            if node is self._head:
                raise ValueError("Valor nao encontrado na lista")

    def remove_current(self):
        if self.is_empty():
            raise IndexError("A lista esta vazia")

        value = self._current.value
        self._unlink(self._current)
        return value

    def next(self):
        if self.is_empty():
            raise IndexError("A lista esta vazia")

        self._current = self._current.next
        return self._current.value

    def prev(self):
        if self.is_empty():
            raise IndexError("A lista esta vazia")

        self._current = self._current.prev
        return self._current.value

    def current(self):
        if self.is_empty():
            raise IndexError("A lista esta vazia")

        return self._current.value

    def is_at_end(self):
        if self.is_empty():
            raise IndexError("A lista esta vazia")

        return self._current is self._head.prev

    def is_empty(self):
        return self._head is None

    def size(self):
        return self._size

    def to_list(self):
        result = [None] * self._size
        node = self._head
        index = 0

        while index < self._size:
            result[index] = node.value
            node = node.next
            index += 1

        return result
