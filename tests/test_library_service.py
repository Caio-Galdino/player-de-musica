import unittest
from backend.services.library_service import LibraryService


class TestLibraryService(unittest.TestCase):

    # biblioteca com algumas musicas, incluindo dois "Yesterday" de artistas diferentes
    def make_library(self):
        library = LibraryService()
        library.add_song("Yesterday", "The Beatles", 125)
        library.add_song("Imagine", "John Lennon", 183)
        library.add_song("Yesterday", "Boyz II Men", 90)
        library.add_song("Hey Jude", "The Beatles", 431)
        return library

    # devolve so os titulos e artistas, para comparar listas de Song com facilidade
    def describe(self, songs):
        result = [None] * len(songs)
        for index, song in enumerate(songs):
            result[index] = (song.title, song.artist)
        return result

    # biblioteca recem-criada deve estar vazia
    def test_new_library_is_empty(self):
        library = LibraryService()
        self.assertTrue(library.is_empty())
        self.assertEqual(library.size(), 0)
        self.assertEqual(library.list_by_title(), [])
        self.assertEqual(library.list_by_duration(), [])

    # add_song devolve a Song criada e aumenta o tamanho
    def test_add_song_returns_song(self):
        library = LibraryService()
        song = library.add_song("Imagine", "John Lennon", 183)
        self.assertEqual(song.title, "Imagine")
        self.assertEqual(song.artist, "John Lennon")
        self.assertEqual(song.duration, 183)
        self.assertEqual(library.size(), 1)
        self.assertFalse(library.is_empty())

    # dados invalidos sao barrados pela Song e nada entra na biblioteca
    def test_add_invalid_song_raises(self):
        library = LibraryService()
        invalid = [
            (None, "John Lennon", 183),
            ("Imagine", "   ", 183),
            ("Imagine", "John Lennon", 0),
            ("Imagine", "John Lennon", "abc"),
        ]
        for title, artist, duration in invalid:
            with self.subTest(title=title, artist=artist, duration=duration):
                with self.assertRaises(ValueError):
                    library.add_song(title, artist, duration)
        self.assertTrue(library.is_empty())

    # mesmo titulo e mesmo artista nao pode entrar duas vezes
    def test_add_duplicate_raises(self):
        library = self.make_library()
        with self.assertRaises(ValueError):
            library.add_song("Imagine", "John Lennon", 200)
        self.assertEqual(library.size(), 4)

    # a duplicata e detectada mesmo com maiusculas e espacos diferentes
    def test_add_duplicate_is_normalized(self):
        library = self.make_library()
        with self.assertRaises(ValueError):
            library.add_song("  IMAGINE ", "john   lennon", 183)
        self.assertEqual(library.size(), 4)

    # mesmo titulo com artista diferente e permitido
    def test_same_title_different_artist_allowed(self):
        library = LibraryService()
        library.add_song("Yesterday", "The Beatles", 125)
        library.add_song("Yesterday", "Boyz II Men", 90)
        self.assertEqual(library.size(), 2)

    # find devolve exatamente o objeto que foi adicionado
    def test_find_returns_same_object(self):
        library = LibraryService()
        song = library.add_song("Imagine", "John Lennon", 183)
        self.assertIs(library.find("Imagine", "John Lennon"), song)

    # find ignora maiusculas e espacos extras no titulo e no artista
    def test_find_is_normalized(self):
        library = self.make_library()
        song = library.find("  YESTERDAY", "boyz   ii men ")
        self.assertEqual(song.artist, "Boyz II Men")

    # find escolhe o artista certo entre musicas de mesmo titulo
    def test_find_picks_right_artist(self):
        library = self.make_library()
        self.assertEqual(library.find("Yesterday", "The Beatles").duration, 125)
        self.assertEqual(library.find("Yesterday", "Boyz II Men").duration, 90)

    # find de musica inexistente deve levantar KeyError
    def test_find_missing_raises(self):
        library = self.make_library()
        cases = [
            ("Let It Be", "The Beatles"),  # titulo nao existe
            ("Yesterday", "John Lennon"),  # titulo existe, artista nao
        ]
        for title, artist in cases:
            with self.subTest(title=title, artist=artist):
                with self.assertRaises(KeyError):
                    library.find(title, artist)

    # find_by_title devolve todas as musicas com aquele titulo
    def test_find_by_title_returns_all_versions(self):
        library = self.make_library()
        songs = library.find_by_title("yesterday")
        self.assertEqual(
            sorted(self.describe(songs)),
            [("Yesterday", "Boyz II Men"), ("Yesterday", "The Beatles")],
        )

    # find_by_title de titulo inexistente devolve lista vazia, sem erro
    def test_find_by_title_missing_returns_empty(self):
        library = self.make_library()
        self.assertEqual(library.find_by_title("Let It Be"), [])

    # list_by_title ordena por titulo e desempata pelo artista
    def test_list_by_title_order(self):
        library = self.make_library()
        self.assertEqual(
            self.describe(library.list_by_title()),
            [
                ("Hey Jude", "The Beatles"),
                ("Imagine", "John Lennon"),
                ("Yesterday", "Boyz II Men"),
                ("Yesterday", "The Beatles"),
            ],
        )

    # a ordem por titulo ignora maiusculas
    def test_list_by_title_ignores_case(self):
        library = LibraryService()
        library.add_song("bohemian Rhapsody", "Queen", 354)
        library.add_song("Africa", "Toto", 295)
        library.add_song("come Together", "The Beatles", 259)
        titles = [song.title for song in library.list_by_title()]
        self.assertEqual(titles, ["Africa", "bohemian Rhapsody", "come Together"])

    # list_by_duration ordena numericamente (90 vem antes de 125, mesmo como texto)
    def test_list_by_duration_order(self):
        library = self.make_library()
        durations = [song.duration for song in library.list_by_duration()]
        self.assertEqual(durations, [90, 125, 183, 431])

    # musicas com a mesma duracao nao se sobrescrevem
    def test_list_by_duration_with_ties(self):
        library = LibraryService()
        library.add_song("B", "Artista", 200)
        library.add_song("A", "Artista", 200)
        library.add_song("C", "Artista", 100)
        self.assertEqual(
            [song.title for song in library.list_by_duration()],
            ["C", "A", "B"],
        )

    # remove_song devolve a musica e ela some de todas as estruturas
    def test_remove_song(self):
        library = self.make_library()
        removed = library.remove_song("Imagine", "John Lennon")
        self.assertEqual(removed.title, "Imagine")
        self.assertEqual(library.size(), 3)
        with self.assertRaises(KeyError):
            library.find("Imagine", "John Lennon")
        self.assertEqual(library.find_by_title("Imagine"), [])
        self.assertNotIn(removed, library.list_by_title())
        self.assertNotIn(removed, library.list_by_duration())

    # remover uma versao de titulo repetido mantem a outra
    def test_remove_one_of_same_title(self):
        library = self.make_library()
        library.remove_song("Yesterday", "The Beatles")
        self.assertEqual(
            self.describe(library.find_by_title("Yesterday")),
            [("Yesterday", "Boyz II Men")],
        )
        self.assertEqual(library.find("Yesterday", "Boyz II Men").duration, 90)

    # depois de remover todas as versoes, o titulo pode ser adicionado de novo
    def test_remove_all_versions_then_add_again(self):
        library = self.make_library()
        library.remove_song("Yesterday", "The Beatles")
        library.remove_song("Yesterday", "Boyz II Men")
        self.assertEqual(library.find_by_title("Yesterday"), [])
        library.add_song("Yesterday", "The Beatles", 125)
        self.assertEqual(len(library.find_by_title("Yesterday")), 1)
        self.assertEqual(library.size(), 3)

    # remove_song tambem aceita titulo e artista com maiusculas/espacos diferentes
    def test_remove_is_normalized(self):
        library = self.make_library()
        library.remove_song(" hey JUDE", "the beatles")
        self.assertEqual(library.size(), 3)

    # remove_song de musica inexistente levanta KeyError sem alterar nada
    def test_remove_missing_raises(self):
        library = self.make_library()
        with self.assertRaises(KeyError):
            library.remove_song("Let It Be", "The Beatles")
        with self.assertRaises(KeyError):
            library.remove_song("Yesterday", "John Lennon")
        self.assertEqual(library.size(), 4)
        self.assertEqual(len(library.list_by_title()), 4)
        self.assertEqual(len(library.list_by_duration()), 4)

    # remover tudo deixa a biblioteca vazia
    def test_remove_everything(self):
        library = self.make_library()
        for song in library.list_by_title():
            library.remove_song(song.title, song.artist)
        self.assertTrue(library.is_empty())
        self.assertEqual(library.list_by_title(), [])
        self.assertEqual(library.list_by_duration(), [])


if __name__ == "__main__":
    unittest.main()
