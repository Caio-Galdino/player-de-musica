import unittest
from backend.services.library_service import LibraryService
from backend.services.player_service import PlayerService


class TestPlayerService(unittest.TestCase):

    # biblioteca com as musicas A, B, C, D e E (todas do artista "X")
    def setUp(self):
        self.library = LibraryService()
        for title in ("A", "B", "C", "D", "E"):
            self.library.add_song(title, "X", 100)
        self.player = PlayerService(self.library)

    # adiciona varias musicas na playlist pelo titulo
    def add_playlist(self, titles):
        for title in titles:
            self.player.add_to_playlist(title, "X")

    # titulo da musica ou None, para comparar com facilidade
    def title(self, song):
        if song is None:
            return None
        return song.title

    # titulos de uma lista de musicas
    def titles(self, songs):
        result = [None] * len(songs)
        for index, song in enumerate(songs):
            result[index] = song.title
        return result

    # chama next_song varias vezes e devolve os titulos que tocaram
    def next_titles(self, times):
        result = [None] * times
        for index in range(times):
            result[index] = self.title(self.player.next_song())
        return result

    # player novo: nada tocando, tudo vazio, repeat desligado
    def test_new_player_is_empty(self):
        self.assertIsNone(self.player.now_playing())
        self.assertEqual(self.player.playlist(), [])
        self.assertEqual(self.player.up_next(), [])
        self.assertEqual(self.player.history(), [])
        self.assertFalse(self.player.is_repeat())

    # sem playlist e sem fila nao ha nada para tocar
    def test_play_with_nothing_returns_none(self):
        self.assertIsNone(self.player.play())
        self.assertIsNone(self.player.next_song())
        self.assertIsNone(self.player.now_playing())

    # ---------- playlist ----------

    # add_to_playlist devolve o mesmo objeto da biblioteca
    def test_add_to_playlist_uses_library_object(self):
        song = self.player.add_to_playlist("a", "x")
        self.assertIs(song, self.library.find("A", "X"))
        self.assertEqual(self.titles(self.player.playlist()), ["A"])

    # musica que nao existe na biblioteca nao entra na playlist
    def test_add_missing_song_to_playlist_raises(self):
        with self.assertRaises(KeyError):
            self.player.add_to_playlist("Z", "X")
        self.assertEqual(self.player.playlist(), [])

    # a mesma musica pode aparecer mais de uma vez na playlist
    def test_playlist_allows_duplicates(self):
        self.add_playlist(["A", "B", "A"])
        self.assertEqual(self.titles(self.player.playlist()), ["A", "B", "A"])
        self.player.play()
        self.assertEqual(self.next_titles(2), ["B", "A"])

    # remover da playlist uma musica que nao esta nela levanta KeyError
    def test_remove_missing_from_playlist_raises(self):
        self.add_playlist(["A"])
        with self.assertRaises(KeyError):
            self.player.remove_from_playlist("B", "X")
        with self.assertRaises(KeyError):
            self.player.remove_from_playlist("Z", "X")

    # remover uma musica que nao e a atual nao muda a ordem de reproducao
    def test_remove_other_song_from_playlist(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.player.remove_from_playlist("B", "X")
        self.assertEqual(self.titles(self.player.playlist()), ["A", "C"])
        self.assertEqual(self.next_titles(1), ["C"])

    # remover a musica atual: a proxima da playlist toca sem ser pulada
    def test_remove_current_from_playlist(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.player.remove_from_playlist("A", "X")
        self.assertEqual(self.titles(self.player.playlist()), ["B", "C"])
        self.assertEqual(self.next_titles(1), ["B"])

    # com duplicata, remove a primeira ocorrencia quando ela nao e a atual
    def test_remove_duplicate_from_playlist(self):
        self.add_playlist(["A", "B", "A"])
        self.player.play()
        self.player.next_song()  # atual: B
        self.player.remove_from_playlist("A", "X")
        self.assertEqual(self.titles(self.player.playlist()), ["B", "A"])

    # esvaziar a playlist e adicionar de novo comeca da primeira musica nova
    def test_empty_playlist_then_add_again(self):
        self.add_playlist(["A"])
        self.player.play()
        self.player.remove_from_playlist("A", "X")
        self.add_playlist(["B", "C"])
        self.assertEqual(self.next_titles(2), ["B", "C"])

    # ---------- reproducao ----------

    # play comeca pela primeira musica da playlist
    def test_play_starts_at_first_song(self):
        self.add_playlist(["A", "B", "C"])
        self.assertEqual(self.title(self.player.play()), "A")
        self.assertEqual(self.title(self.player.now_playing()), "A")

    # play com algo tocando nao muda a musica
    def test_play_while_playing_keeps_song(self):
        self.add_playlist(["A", "B"])
        self.player.play()
        self.assertEqual(self.title(self.player.play()), "A")
        self.assertEqual(self.player.history(), [])

    # next_song sem nada tocando funciona como play (nao pula a primeira)
    def test_next_without_play_starts_at_first(self):
        self.add_playlist(["A", "B"])
        self.assertEqual(self.next_titles(2), ["A", "B"])

    # next_song segue a ordem da playlist
    def test_next_follows_playlist(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.assertEqual(self.next_titles(2), ["B", "C"])

    # repeat desligado: depois da ultima musica o player para
    def test_end_without_repeat_stops(self):
        self.add_playlist(["A", "B"])
        self.player.play()
        self.assertEqual(self.next_titles(2), ["B", None])
        self.assertIsNone(self.player.now_playing())

    # depois de parar no fim, play recomeca da primeira musica
    def test_play_after_stop_restarts_playlist(self):
        self.add_playlist(["A", "B"])
        self.player.play()
        self.next_titles(2)
        self.assertEqual(self.title(self.player.play()), "A")
        self.assertEqual(self.next_titles(1), ["B"])

    # repeat ligado: depois da ultima musica volta para a primeira
    def test_end_with_repeat_loops(self):
        self.add_playlist(["A", "B", "C"])
        self.player.set_repeat(True)
        self.player.play()
        self.assertEqual(self.next_titles(5), ["B", "C", "A", "B", "C"])

    # playlist com uma musica so e repeat ligado repete a mesma musica
    def test_single_song_with_repeat(self):
        self.add_playlist(["A"])
        self.player.set_repeat(True)
        self.player.play()
        self.assertEqual(self.next_titles(2), ["A", "A"])

    # o repeat pode ser ligado e desligado
    def test_set_repeat(self):
        self.player.set_repeat(True)
        self.assertTrue(self.player.is_repeat())
        self.player.set_repeat(False)
        self.assertFalse(self.player.is_repeat())

    # desligar o repeat no meio faz o player parar no fim
    def test_disable_repeat_midway(self):
        self.add_playlist(["A", "B"])
        self.player.set_repeat(True)
        self.player.play()
        self.player.set_repeat(False)
        self.assertEqual(self.next_titles(2), ["B", None])

    # ---------- fila "tocar a seguir" ----------

    # enqueue devolve a musica e ela aparece em up_next na ordem de chegada
    def test_enqueue(self):
        song = self.player.enqueue("D", "X")
        self.player.enqueue("E", "X")
        self.assertIs(song, self.library.find("D", "X"))
        self.assertEqual(self.titles(self.player.up_next()), ["D", "E"])

    # musica que nao existe na biblioteca nao entra na fila
    def test_enqueue_missing_raises(self):
        with self.assertRaises(KeyError):
            self.player.enqueue("Z", "X")
        self.assertEqual(self.player.up_next(), [])

    # a fila tem prioridade e nao muda a posicao da playlist
    def test_queue_has_priority(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.player.enqueue("D", "X")
        self.player.enqueue("E", "X")
        self.assertEqual(self.next_titles(3), ["D", "E", "B"])
        self.assertEqual(self.player.up_next(), [])

    # tocar da fila antes da playlist nao pula a primeira musica da playlist
    def test_queue_before_playlist_does_not_skip_first(self):
        self.add_playlist(["A", "B"])
        self.player.enqueue("D", "X")
        self.assertEqual(self.title(self.player.play()), "D")
        self.assertEqual(self.next_titles(2), ["A", "B"])

    # so a fila, sem playlist: toca a fila e depois para
    def test_queue_without_playlist(self):
        self.player.enqueue("D", "X")
        self.assertEqual(self.title(self.player.play()), "D")
        self.assertEqual(self.next_titles(1), [None])

    # ---------- historico e "anterior" ----------

    # next_song empilha a musica que estava tocando
    def test_history_records_played_songs(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.next_titles(2)
        # do mais recente para o mais antigo
        self.assertEqual(self.titles(self.player.history()), ["B", "A"])

    # previous_song volta pelo historico
    def test_previous_goes_back_through_history(self):
        self.add_playlist(["A", "B", "C"])
        self.player.play()
        self.next_titles(2)  # atual: C
        self.assertEqual(self.title(self.player.previous_song()), "B")
        self.assertEqual(self.title(self.player.previous_song()), "A")
        self.assertEqual(self.title(self.player.now_playing()), "A")

    # previous_song inclui musicas que vieram da fila
    def test_previous_includes_queued_songs(self):
        self.add_playlist(["A", "B"])
        self.player.play()
        self.player.enqueue("D", "X")
        self.player.next_song()  # D
        self.player.next_song()  # B
        self.assertEqual(self.title(self.player.previous_song()), "D")

    # previous_song com historico vazio levanta IndexError sem mudar a musica
    def test_previous_with_empty_history_raises(self):
        with self.assertRaises(IndexError):
            self.player.previous_song()
        self.add_playlist(["A"])
        self.player.play()
        with self.assertRaises(IndexError):
            self.player.previous_song()
        self.assertEqual(self.title(self.player.now_playing()), "A")

    # previous_song nao move a playlist: o proximo continua de onde a playlist estava
    def test_previous_does_not_move_playlist(self):
        self.add_playlist(["A", "B", "C", "D"])
        self.player.play()
        self.next_titles(2)  # atual: C
        self.player.previous_song()  # volta para B
        self.assertEqual(self.next_titles(1), ["D"])

    # previous_song pula musicas que foram removidas da biblioteca
    def test_previous_skips_removed_songs(self):
        self.player.enqueue("A", "X")
        self.player.enqueue("B", "X")
        self.player.enqueue("C", "X")
        self.player.play()  # A
        self.player.next_song()  # B
        self.player.next_song()  # C
        self.player.remove_from_library("B", "X")
        self.assertEqual(self.title(self.player.previous_song()), "A")

    # ---------- remover da biblioteca ----------

    # musica fora de uso pode ser removida da biblioteca
    def test_remove_from_library_not_in_use(self):
        removed = self.player.remove_from_library("E", "X")
        self.assertEqual(removed.title, "E")
        with self.assertRaises(KeyError):
            self.library.find("E", "X")

    # musica tocando, na playlist ou na fila nao pode ser removida
    def test_remove_from_library_in_use_raises(self):
        self.add_playlist(["A"])
        self.player.enqueue("B", "X")
        self.player.enqueue("C", "X")
        self.player.play()  # B tocando, C na fila, A na playlist
        for title in ("A", "B", "C"):
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    self.player.remove_from_library(title, "X")
        self.assertEqual(self.library.size(), 5)

    # musica que so esta no historico pode ser removida
    def test_remove_from_library_only_in_history(self):
        self.player.enqueue("A", "X")
        self.player.play()
        self.player.next_song()  # A vai para o historico, nada tocando
        self.player.remove_from_library("A", "X")
        with self.assertRaises(KeyError):
            self.library.find("A", "X")

    # remover da biblioteca musica inexistente levanta KeyError
    def test_remove_from_library_missing_raises(self):
        with self.assertRaises(KeyError):
            self.player.remove_from_library("Z", "X")


if __name__ == "__main__":
    unittest.main()
