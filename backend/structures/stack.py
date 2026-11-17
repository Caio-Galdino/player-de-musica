from .node import Node

class Stack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, value):
        node = Node(value)
        node.next = self._top
        self._top = node
        self._size += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("A pilha esta vazia")

        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("A pilha esta vazia")

        return self._top.value

    def is_empty(self):
        return self._top is None

    def size(self):
        return self._size

    def to_list(self):
        result = [None] * self._size
        current = self._top
        index = 0

        while current is not None:
            result[index] = current.value
            current = current.next
            index += 1

        return result
    