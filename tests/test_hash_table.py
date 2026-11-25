import unittest
from backend.structures.hash_table import HashTable


class TestHashTable(unittest.TestCase):

    # tabela recem-criada deve estar vazia
    def test_new_table_is_empty(self):
        t = HashTable()
        self.assertTrue(t.is_empty())
        self.assertEqual(t.size(), 0)

    # capacidade invalida deve levantar ValueError
    def test_invalid_capacity_raises(self):
        for capacity in (0, -1):
            with self.subTest(capacity=capacity):
                with self.assertRaises(ValueError):
                    HashTable(capacity=capacity)

    # put guarda o valor e get devolve o mesmo valor
    def test_put_and_get(self):
        t = HashTable()
        t.put("imagine", "John Lennon")
        self.assertEqual(t.get("imagine"), "John Lennon")
        self.assertEqual(t.size(), 1)
        self.assertFalse(t.is_empty())

    # put de chave existente substitui o valor e nao aumenta o tamanho
    def test_put_existing_key_replaces_value(self):
        t = HashTable()
        t.put("imagine", 1)
        t.put("imagine", 2)
        self.assertEqual(t.get("imagine"), 2)
        self.assertEqual(t.size(), 1)

    # get de chave inexistente deve levantar KeyError
    def test_get_missing_key_raises(self):
        t = HashTable()
        t.put("imagine", 1)
        with self.assertRaises(KeyError):
            t.get("yesterday")

    # contains devolve True/False e nunca levanta erro
    def test_contains(self):
        t = HashTable()
        t.put("imagine", 1)
        self.assertTrue(t.contains("imagine"))
        self.assertFalse(t.contains("yesterday"))

    # contains olha a chave, nao o valor: guardar None continua contando
    def test_none_is_a_valid_value(self):
        t = HashTable()
        t.put("silence", None)
        self.assertTrue(t.contains("silence"))
        self.assertIsNone(t.get("silence"))
        self.assertEqual(t.size(), 1)

    # remove devolve o valor, diminui o tamanho e a chave deixa de existir
    def test_remove_returns_value_and_deletes_key(self):
        t = HashTable()
        t.put("imagine", 1)
        t.put("yesterday", 2)
        self.assertEqual(t.remove("imagine"), 1)
        self.assertEqual(t.size(), 1)
        self.assertFalse(t.contains("imagine"))
        self.assertEqual(t.get("yesterday"), 2)

    # remove de chave inexistente deve levantar KeyError sem alterar a tabela
    def test_remove_missing_key_raises(self):
        t = HashTable()
        with self.assertRaises(KeyError):
            t.remove("imagine")
        t.put("yesterday", 2)
        with self.assertRaises(KeyError):
            t.remove("imagine")
        self.assertEqual(t.size(), 1)

    # a tabela pode ser reutilizada depois de esvaziada
    def test_put_after_emptying(self):
        t = HashTable()
        t.put("imagine", 1)
        t.remove("imagine")
        self.assertTrue(t.is_empty())
        t.put("imagine", 2)
        self.assertEqual(t.get("imagine"), 2)
        self.assertEqual(t.size(), 1)

    # _hash: a mesma chave da sempre o mesmo indice, e o indice e valido
    def test_hash_is_stable_and_in_range(self):
        t = HashTable()
        self.assertEqual(t._hash("imagine"), t._hash("imagine"))
        for i in range(200):
            index = t._hash(f"song {i}")
            self.assertTrue(0 <= index < t._capacity)

    # --- colisoes: capacity=1 forca TODAS as chaves no mesmo balde ---

    # varias chaves no mesmo balde continuam acessiveis
    def test_collisions_keep_all_keys(self):
        t = HashTable(capacity=1)
        for key in ("a", "b", "c"):
            t.put(key, key.upper())
        self.assertEqual(t.get("a"), "A")
        self.assertEqual(t.get("b"), "B")
        self.assertEqual(t.get("c"), "C")

    # remover o primeiro, o do meio e o ultimo no da corrente
    def test_collisions_remove_any_position_in_chain(self):
        # put insere no inicio: a corrente fica c -> b -> a
        for removed, remaining in (("c", "ab"), ("b", "ac"), ("a", "bc")):
            with self.subTest(removed=removed):
                t = HashTable(capacity=1)
                for key in ("a", "b", "c"):
                    t.put(key, key.upper())
                self.assertEqual(t.remove(removed), removed.upper())
                self.assertFalse(t.contains(removed))
                for key in remaining:
                    self.assertEqual(t.get(key), key.upper())
                self.assertEqual(t.size(), 2)

    # substituir valor no meio da corrente nao duplica a chave
    def test_collisions_replace_value_in_chain(self):
        t = HashTable(capacity=1)
        for key in ("a", "b", "c"):
            t.put(key, 1)
        t.put("b", 99)
        self.assertEqual(t.get("b"), 99)
        self.assertEqual(t.size(), 3)

    # --- rehash ---

    # o rehash deve dobrar a capacidade quando o fator de carga passa de 0.75
    def test_rehash_grows_capacity(self):
        t = HashTable(capacity=4)
        for i in range(4):  # 4 / 4 = 1.0 > 0.75
            t.put(f"song {i}", i)
        self.assertGreater(t._capacity, 4)

    # depois de varios rehash, todas as chaves continuam encontraveis
    # e o tamanho esta certo (nao foi contado em dobro)
    def test_rehash_keeps_all_keys_and_size(self):
        t = HashTable(capacity=8)
        for i in range(100):
            t.put(f"song {i}", i)
        self.assertEqual(t.size(), 100)
        for i in range(100):
            self.assertEqual(t.get(f"song {i}"), i)

    # o rehash mantem o fator de carga abaixo do limite
    def test_rehash_keeps_load_factor_low(self):
        t = HashTable(capacity=8)
        for i in range(100):
            t.put(f"song {i}", i)
        self.assertLessEqual(t.size() / t._capacity, 0.75)


    # --- capacity ---

    # sem argumento, a tabela comeca com 8 baldes
    def test_default_capacity(self):
        self.assertEqual(HashTable().capacity(), 8)

    # capacity devolve a capacidade pedida na criacao
    def test_custom_capacity(self):
        self.assertEqual(HashTable(capacity=5).capacity(), 5)

    # 6 / 8 = 0.75 ainda nao passa do limite; a 7a chave dispara o rehash
    def test_capacity_doubles_only_after_limit(self):
        t = HashTable(capacity=8)
        for i in range(6):
            t.put(f"song {i}", i)
        self.assertEqual(t.capacity(), 8)
        t.put("song 6", 6)
        self.assertEqual(t.capacity(), 16)

    # substituir o valor de uma chave nao aumenta a tabela
    def test_capacity_unchanged_when_replacing(self):
        t = HashTable(capacity=8)
        for i in range(6):
            t.put(f"song {i}", i)
        for i in range(6):
            t.put(f"song {i}", i * 10)
        self.assertEqual(t.capacity(), 8)

    # remover nao encolhe a tabela
    def test_capacity_unchanged_after_remove(self):
        t = HashTable(capacity=8)
        for i in range(7):
            t.put(f"song {i}", i)
        for i in range(7):
            t.remove(f"song {i}")
        self.assertEqual(t.capacity(), 16)


if __name__ == "__main__":
    unittest.main()
