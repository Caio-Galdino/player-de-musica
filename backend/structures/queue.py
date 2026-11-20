from .node import Node

class Queue:
    def __init__(self):
        self._front = None
        self._rear = None
        self._size = 0

    def enqueue(self, value):
        node = Node(value)

        if self.is_empty():
            self._front = node
        else:
            self._rear.next = node

        self._rear = node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("A fila esta vazia")

        value = self._front.value
        self._front = self._front.next
        self._size -= 1

        if self.is_empty():
            self._rear = None

        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("A fila esta vazia")

        return self._front.value

    def remove(self, value):
        # tira a primeira ocorrencia do valor, esteja onde estiver na fila
        previous = None
        node = self._front

        while node is not None:
            if node.value == value:
                if preivous is None:
                    self._front = node.next
                else:
                    previous.next = node.next

                # era o ultimo: o anterior vira o fim (ou None se a fila esvaziou)
                if node is self._rear:
                    self._rear = previous

                self._size -= 1
                return

            previous = node
            node = node.next

        raise ValueError("Valor nao encontrado na fila")

    def is_empty(self):
        return self._front is None

    def size(self):
        return self._size

    def to_list(self):
        result = [None] * self._size
        current = self._front
        index = 0

        while current is not None:
            result[index] = current.value
            current = current.next
            index += 1

        return result