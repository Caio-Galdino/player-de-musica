import unittest
from backend.structures.stack import Stack


class TestStack(unittest.TestCase):

    # pilha recem-criada deve estar vazia
    def test_new_stack_is_empty(self):
        s = Stack()
        self.assertTrue(s.is_empty())
        self.assertEqual(s.size(), 0)

    # cada push aumenta o tamanho em 1
    def test_push_increases_size(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.size(), 3)
        self.assertFalse(s.is_empty())

    # peek devolve o topo sem remover
    def test_peek_returns_top_without_removing(self):
        s = Stack()
        s.push(1)
        s.push(2)
        self.assertEqual(s.peek(), 2)
        self.assertEqual(s.size(), 2)
        self.assertEqual(s.peek(), 2)  # chamar de novo devolve o mesmo valor

    # o ultimo a entrar e o primeiro a sair (LIFO)
    def test_pop_follows_lifo_order(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)

    # pop diminui o tamanho e, ao remover tudo, a pilha volta a ficar vazia
    def test_pop_decreases_size_until_empty(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.pop()
        self.assertEqual(s.size(), 1)
        s.pop()
        self.assertEqual(s.size(), 0)
        self.assertTrue(s.is_empty())

    # pop na pilha vazia deve levantar IndexError
    def test_pop_on_empty_stack_raises(self):
        s = Stack()
        with self.assertRaises(IndexError):
            s.pop()

    # peek na pilha vazia deve levantar IndexError
    def test_peek_on_empty_stack_raises(self):
        s = Stack()
        with self.assertRaises(IndexError):
            s.peek()

    # a pilha pode ser reutilizada depois de esvaziada
    def test_push_after_emptying(self):
        s = Stack()
        s.push(1)
        s.pop()
        s.push(2)
        self.assertEqual(s.peek(), 2)
        self.assertEqual(s.size(), 1)

    # guardar None nao pode fazer a pilha parecer vazia
    def test_push_none_is_a_valid_value(self):
        s = Stack()
        s.push(None)
        self.assertFalse(s.is_empty())
        self.assertEqual(s.size(), 1)
        self.assertIsNone(s.pop())
        self.assertTrue(s.is_empty())

    # to_list devolve os valores do topo para a base
    def test_to_list_returns_top_to_bottom(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.to_list(), [3, 2, 1])

    # to_list so le os valores, nao altera a pilha
    def test_to_list_does_not_modify_stack(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.to_list()
        self.assertEqual(s.size(), 2)
        self.assertEqual(s.peek(), 2)

    # to_list da pilha vazia devolve lista vazia
    def test_to_list_on_empty_stack(self):
        s = Stack()
        self.assertEqual(s.to_list(), [])


if __name__ == "__main__":
    unittest.main()
