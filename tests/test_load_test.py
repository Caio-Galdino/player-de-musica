import contextlib
import io
import math
import unittest

import load_test
from backend.services.library_service import LibraryService


class TestLoadTest(unittest.TestCase):

    # build_library insere exatamente a quantidade pedida, sem titulos repetidos
    def test_build_library_size(self):
        library = load_test.build_library(1000)
        self.assertEqual(library.size(), 1000)
        for i in range(1000):
            self.assertEqual(len(library.find_by_title(f"Musica {i:05d}")), 1)

    # a duracao fica sempre entre 60 e 599 segundos
    def test_build_library_durations(self):
        songs = load_test.build_library(1000).list_by_duration()
        self.assertGreaterEqual(songs[0].duration, 60)
        self.assertLessEqual(songs[-1].duration, 599)

    # a listagem por duracao sai em ordem crescente
    def test_build_library_sorted_by_duration(self):
        songs = load_test.build_library(1000).list_by_duration()
        for i in range(1, len(songs)):
            self.assertLessEqual(songs[i - 1].duration, songs[i].duration)

    # a altura fica entre o minimo e o limite teorico da AVL, em todos os tamanhos
    def test_heights_within_avl_bounds(self):
        for total in load_test.SIZES:
            library = load_test.build_library(total)
            minimum = math.floor(math.log2(total))
            maximum = 1.44 * math.log2(total)
            heights = (library.title_tree_height(), library.duration_tree_height())
            for height in heights:
                with self.subTest(total=total, height=height):
                    self.assertGreaterEqual(height, minimum)
                    self.assertLessEqual(height, maximum)

    # o fator de carga da hash nunca passa de 0.75
    def test_hash_load_factor(self):
        for total in load_test.SIZES:
            with self.subTest(total=total):
                library = load_test.build_library(total)
                self.assertLessEqual(total / library.hash_capacity(), 0.75)

    # check_library aceita uma biblioteca correta
    def test_check_library_accepts_valid(self):
        load_test.check_library(load_test.build_library(100), 100)

    # check_library acusa quantidade errada
    def test_check_library_rejects_wrong_size(self):
        with self.assertRaises(AssertionError):
            load_test.check_library(load_test.build_library(100), 101)

    # check_library acusa uma listagem fora de ordem
    def test_check_library_rejects_unsorted(self):
        library = LibraryService()
        first = library.add_song("A", "Artista", 100)
        second = library.add_song("B", "Artista", 100)
        library.list_by_title = lambda: [second, first]
        with self.assertRaises(AssertionError):
            load_test.check_library(library, 2)

    # measure_search devolve um tempo positivo
    def test_measure_search_is_positive(self):
        library = load_test.build_library(100)
        self.assertGreater(load_test.measure_search(library, 100), 0)

    # o relatorio exibe a altura da AVL (exigencia do enunciado)
    def test_run_prints_heights(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            load_test.run(1000)
        text = output.getvalue()
        self.assertRegex(text, r"Altura AVL \(titulo\): +9\n")
        self.assertRegex(text, r"Altura AVL \(duracao\): +10\n")
        self.assertRegex(text, r"Capacidade da hash: +2048\n")


if __name__ == "__main__":
    unittest.main()
