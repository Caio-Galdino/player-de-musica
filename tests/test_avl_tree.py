import random
import unittest
from backend.structures.avl_tree import AVLTree


class TestAVLTree(unittest.TestCase):

    # cria uma arvore inserindo as chaves na ordem dada (valor = chave * 10)
    def make_tree(self, keys):
        t = AVLTree()
        for key in keys:
            t.put(key, key * 10)
        return t

    # percorre a arvore toda conferindo as regras da AVL; devolve a altura do no
    def check_node(self, node, low=None, high=None):
        if node is None:
            return -1

        # regra da BST: chave dentro do intervalo permitido pelos ancestrais
        if low is not None:
            self.assertGreater(node.key, low)
        if high is not None:
            self.assertLess(node.key, high)

        left_height = self.check_node(node.left, low, node.key)
        right_height = self.check_node(node.right, node.key, high)

        # altura guardada no no deve bater com a altura real
        self.assertEqual(node.height, 1 + max(left_height, right_height))
        # fator de balanceamento sempre em {-1, 0, 1}
        self.assertLessEqual(abs(left_height - right_height), 1)

        return node.height

    def assert_valid_avl(self, t):
        self.check_node(t._root)

    # arvore recem-criada deve estar vazia
    def test_new_tree_is_empty(self):
        t = AVLTree()
        self.assertTrue(t.is_empty())
        self.assertEqual(t.size(), 0)
        self.assertEqual(t.height(), -1)
        self.assertEqual(t.to_list(), [])

    # put guarda o valor e get devolve o mesmo valor
    def test_put_and_get(self):
        t = AVLTree()
        t.put("imagine", "John Lennon")
        self.assertEqual(t.get("imagine"), "John Lennon")
        self.assertEqual(t.size(), 1)
        self.assertFalse(t.is_empty())
        self.assertEqual(t.height(), 0)

    # put de chave existente substitui o valor e nao aumenta o tamanho
    def test_put_existing_key_replaces_value(self):
        t = AVLTree()
        t.put("imagine", 1)
        t.put("imagine", 2)
        self.assertEqual(t.get("imagine"), 2)
        self.assertEqual(t.size(), 1)

    # get de chave inexistente deve levantar KeyError
    def test_get_missing_key_raises(self):
        t = AVLTree()
        with self.assertRaises(KeyError):
            t.get("imagine")
        t.put("yesterday", 1)
        with self.assertRaises(KeyError):
            t.get("imagine")

    # contains devolve True/False e nunca levanta erro
    def test_contains(self):
        t = AVLTree()
        t.put("imagine", 1)
        self.assertTrue(t.contains("imagine"))
        self.assertFalse(t.contains("yesterday"))

    # contains olha a chave, nao o valor: guardar None continua contando
    def test_none_is_a_valid_value(self):
        t = AVLTree()
        t.put("silence", None)
        self.assertTrue(t.contains("silence"))
        self.assertIsNone(t.get("silence"))

    # caso esquerda-esquerda: 30, 20, 10 -> rotacao a direita, 20 vira raiz
    def test_left_left_case(self):
        t = self.make_tree([30, 20, 10])
        self.assertEqual(t._root.key, 20)
        self.assertEqual(t._root.left.key, 10)
        self.assertEqual(t._root.right.key, 30)
        self.assertEqual(t.height(), 1)

    # caso direita-direita: 10, 20, 30 -> rotacao a esquerda, 20 vira raiz
    def test_right_right_case(self):
        t = self.make_tree([10, 20, 30])
        self.assertEqual(t._root.key, 20)
        self.assertEqual(t._root.left.key, 10)
        self.assertEqual(t._root.right.key, 30)
        self.assertEqual(t.height(), 1)

    # caso esquerda-direita: 30, 10, 20 -> rotacao dupla, 20 vira raiz
    def test_left_right_case(self):
        t = self.make_tree([30, 10, 20])
        self.assertEqual(t._root.key, 20)
        self.assertEqual(t._root.left.key, 10)
        self.assertEqual(t._root.right.key, 30)
        self.assertEqual(t.height(), 1)

    # caso direita-esquerda: 10, 30, 20 -> rotacao dupla, 20 vira raiz
    def test_right_left_case(self):
        t = self.make_tree([10, 30, 20])
        self.assertEqual(t._root.key, 20)
        self.assertEqual(t._root.left.key, 10)
        self.assertEqual(t._root.right.key, 30)
        self.assertEqual(t.height(), 1)

    # inserir em ordem crescente nao pode virar uma "lista": 7 chaves -> altura 2
    def test_sorted_insertion_stays_balanced(self):
        t = self.make_tree(range(1, 8))
        self.assertEqual(t.height(), 2)
        self.assertEqual(t._root.key, 4)
        self.assert_valid_avl(t)

    # mesmo com muitas chaves em ordem decrescente a altura fica logaritmica
    def test_large_insertion_height_is_logarithmic(self):
        t = self.make_tree(range(1000, 0, -1))
        self.assertEqual(t.size(), 1000)
        # limite teorico da AVL: ~1.44 * log2(n) -> para 1000 chaves, no maximo 14
        self.assertLessEqual(t.height(), 14)
        self.assert_valid_avl(t)

    # to_list devolve os valores em ordem das chaves, qualquer que seja a insercao
    def test_to_list_is_sorted_by_key(self):
        t = self.make_tree([50, 20, 80, 10, 30, 70, 90, 60])
        self.assertEqual(t.to_list(), [100, 200, 300, 500, 600, 700, 800, 900])

    # chaves de texto ficam em ordem alfabetica
    def test_string_keys_in_alphabetical_order(self):
        t = AVLTree()
        for title in ["yesterday", "imagine", "bohemian rhapsody", "hey jude"]:
            t.put(title, title.upper())
        self.assertEqual(
            t.to_list(),
            ["BOHEMIAN RHAPSODY", "HEY JUDE", "IMAGINE", "YESTERDAY"],
        )

    # min e max devolvem os valores das menores e maiores chaves
    def test_min_and_max(self):
        t = self.make_tree([50, 20, 80, 10, 90])
        self.assertEqual(t.min(), 100)
        self.assertEqual(t.max(), 900)

    # min e max em arvore vazia devem levantar IndexError
    def test_min_and_max_on_empty_raise(self):
        t = AVLTree()
        for operation in (t.min, t.max):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(IndexError):
                    operation()

    # remover uma folha
    def test_remove_leaf(self):
        t = self.make_tree([20, 10, 30])
        self.assertEqual(t.remove(10), 100)
        self.assertEqual(t.size(), 2)
        self.assertFalse(t.contains(10))
        self.assertEqual(t.to_list(), [200, 300])
        self.assert_valid_avl(t)

    # remover um no com um filho: o filho sobe para o lugar dele
    def test_remove_node_with_one_child(self):
        t = self.make_tree([20, 10, 30, 40])
        self.assertEqual(t.remove(30), 300)
        self.assertEqual(t.to_list(), [100, 200, 400])
        self.assert_valid_avl(t)

    # remover um no com dois filhos: o sucessor toma o lugar dele
    def test_remove_node_with_two_children(self):
        t = self.make_tree([50, 20, 80, 10, 30, 70, 90])
        self.assertEqual(t.remove(20), 200)
        self.assertEqual(t.size(), 6)
        self.assertEqual(t._root.left.key, 30)
        self.assertEqual(t.to_list(), [100, 300, 500, 700, 800, 900])
        self.assert_valid_avl(t)

    # remover a raiz
    def test_remove_root(self):
        t = self.make_tree([20, 10, 30])
        self.assertEqual(t.remove(20), 200)
        self.assertEqual(t._root.key, 30)
        self.assertEqual(t.to_list(), [100, 300])
        self.assert_valid_avl(t)

    # remover o unico elemento deixa a arvore vazia
    def test_remove_only_element(self):
        t = self.make_tree([10])
        t.remove(10)
        self.assertTrue(t.is_empty())
        self.assertEqual(t.size(), 0)
        self.assertEqual(t.height(), -1)

    # remocao que desbalanceia a arvore deve rebalancear
    def test_remove_triggers_rebalance(self):
        t = self.make_tree([20, 10, 30, 40])
        t.remove(10)  # direita fica pesada em 20 -> rotacao a esquerda
        self.assertEqual(t._root.key, 30)
        self.assert_valid_avl(t)

    # remove de chave inexistente deve levantar KeyError sem alterar a arvore
    def test_remove_missing_key_raises(self):
        t = AVLTree()
        with self.assertRaises(KeyError):
            t.remove(10)
        t = self.make_tree([20, 10, 30])
        with self.assertRaises(KeyError):
            t.remove(99)
        self.assertEqual(t.size(), 3)
        self.assertEqual(t.to_list(), [100, 200, 300])

    # a arvore pode ser reutilizada depois de esvaziada
    def test_put_after_emptying(self):
        t = self.make_tree([10, 20])
        t.remove(10)
        t.remove(20)
        t.put(5, "cinco")
        self.assertEqual(t.get(5), "cinco")
        self.assertEqual(t.size(), 1)

    # muitas insercoes e remocoes aleatorias: a arvore continua uma AVL valida
    def test_random_operations_keep_invariants(self):
        rng = random.Random(42)
        t = AVLTree()
        reference = set()

        for _ in range(2000):
            key = rng.randint(0, 300)
            if rng.random() < 0.6:
                t.put(key, key * 10)
                reference.add(key)
            elif key in reference:
                self.assertEqual(t.remove(key), key * 10)
                reference.remove(key)
            else:
                with self.assertRaises(KeyError):
                    t.remove(key)

        self.assertEqual(t.size(), len(reference))
        self.assertEqual(t.to_list(), [key * 10 for key in sorted(reference)])
        self.assert_valid_avl(t)


if __name__ == "__main__":
    unittest.main()
