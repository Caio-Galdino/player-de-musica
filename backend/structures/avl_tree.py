from .node import AVLNode

class AVLTree:
    def __init__(self):
        self._root = None
        self._size = 0

    def _height(self, node):
        if node is None:
            return -1

        return node.height

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    def _rotate_right(self, y):
        x = y.left
        b = x.right

        x.right = y
        y.left = b

        # y primeiro pois agora é filho de x
        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x):
        y = x.right
        b = y.left

        y.left = x
        x.right = b

        # x primeiro, pois agora e filho de y
        self._update_height(x)
        self._update_height(y)

        return y

    def _rebalance(self, node):
        self._update_height(node)
        balance = self._balance_factor(node)

        # esquerda pesada
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left) # caso esquerda-direita

            return self._rotate_right(node)

        # direita pesada
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right) # caso direita-esquerda

            return self._rotate_left(node)

        return node

    def put(self, key, value):
        self._root = self._insert(self._root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            self._size += 1
            return AVLNode(key, value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            #chave repetida: so atualizar o valor
            node.value = value
            return node

        return self._rebalance(node)

    def _find_node(self, key):
        node = self._root

        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node

        return None

    def get(self, key):
        node = self._find_node(key)

        if node is None:
            raise KeyError(key)

        return node.value

    def contains(self, key):
        return self._find_node(key) is not None

    def remove(self, key):
        node = self._find_node(key)

        if node is None:
            raise KeyError(key)

        value = node.value
        self._root = self._remove(self._root, key)
        self._size -= 1

        return value

    def _remove(self, node, key):
        # a chave com certeza existe(remove() ja verificou), entao node nunca sera None aqui
        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            # nenhum filho ou so o filho direito
            if node.left is None:
                return node.right

            # so o filho esquerdo
            if node.right is None:
                return node.left

            # dois filhos: copia o sucessor e remove ele da subarvore direita
            sucessor = self._min_node(node.right)
            node.key = sucessor.key
            node.value = sucessor.value
            node.right = self._remove(node.right, sucessor.key)

        return self._rebalance(node)

    def _min_node(self, node):
        while node.left is not None:
            node = node.left

        return node

    def _max_node(self, node):
        while node.right is not None:
            node = node.right

        return node

    def min(self):
        if self.is_empty():
            raise IndexError("A arvore esta vazia")

        return self._min_node(self._root).value

    def max(self):
        if self.is_empty():
            raise IndexError("A arvore esta vazia")

        return self._max_node(self._root).value

    def height(self):
        return self._height(self._root)

    def size(self):
        return self._size

    def is_empty(self):
        return self._root is None

    def to_list(self):
        result = [None] * self._size
        self._in_order(self._root, result, 0)
        return result

    def _in_order(self, node, result, index):
        # devolve o proximo indice livre em result
        if node is None:
            return index

        index = self._in_order(node.left, result, index)
        result[index] = node.value
        index += 1

        return self._in_order(node.right, result, index)