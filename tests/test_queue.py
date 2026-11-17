import unittest
from backend.structures.queue import Queue


class TestQueue(unittest.TestCase):

    # fila recem-criada deve estar vazia
    def test_new_queue_is_empty(self):
        q = Queue()
        self.assertTrue(q.is_empty())
        self.assertEqual(q.size(), 0)

    # cada enqueue aumenta o tamanho em 1
    def test_enqueue_increases_size(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.size(), 3)
        self.assertFalse(q.is_empty())

    # peek devolve o primeiro da fila sem remover
    def test_peek_returns_front_without_removing(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        self.assertEqual(q.peek(), 1)
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.peek(), 1)  # chamar de novo devolve o mesmo valor

    # o primeiro a entrar e o primeiro a sair (FIFO)
    def test_dequeue_follows_fifo_order(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        self.assertEqual(q.dequeue(), 3)

    # dequeue diminui o tamanho e, ao remover tudo, a fila volta a ficar vazia
    def test_dequeue_decreases_size_until_empty(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.dequeue()
        self.assertEqual(q.size(), 1)
        q.dequeue()
        self.assertEqual(q.size(), 0)
        self.assertTrue(q.is_empty())

    # dequeue na fila vazia deve levantar IndexError
    def test_dequeue_on_empty_queue_raises(self):
        q = Queue()
        with self.assertRaises(IndexError):
            q.dequeue()

    # peek na fila vazia deve levantar IndexError
    def test_peek_on_empty_queue_raises(self):
        q = Queue()
        with self.assertRaises(IndexError):
            q.peek()

    # caso de borda: depois de esvaziar, o _rear precisa ter sido limpo,
    # senao o novo elemento "some" ao ser ligado a um no antigo
    def test_enqueue_after_emptying(self):
        q = Queue()
        q.enqueue(1)
        q.dequeue()
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.peek(), 2)
        self.assertEqual(q.to_list(), [2, 3])

    # enqueue e dequeue intercalados mantem a ordem FIFO
    def test_interleaved_enqueue_and_dequeue(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        self.assertEqual(q.dequeue(), 1)
        q.enqueue(3)
        self.assertEqual(q.dequeue(), 2)
        self.assertEqual(q.dequeue(), 3)
        self.assertTrue(q.is_empty())

    # guardar None nao pode fazer a fila parecer vazia
    def test_enqueue_none_is_a_valid_value(self):
        q = Queue()
        q.enqueue(None)
        self.assertFalse(q.is_empty())
        self.assertEqual(q.size(), 1)
        self.assertIsNone(q.dequeue())
        self.assertTrue(q.is_empty())

    # to_list devolve os valores do inicio para o fim
    def test_to_list_returns_front_to_rear(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(q.to_list(), [1, 2, 3])

    # to_list so le os valores, nao altera a fila
    def test_to_list_does_not_modify_queue(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.to_list()
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.peek(), 1)

    # to_list da fila vazia devolve lista vazia
    def test_to_list_on_empty_queue(self):
        q = Queue()
        self.assertEqual(q.to_list(), [])


if __name__ == "__main__":
    unittest.main()
