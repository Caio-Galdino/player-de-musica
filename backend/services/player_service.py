from ..structures.circular_linked_list import CircularLinkedList
from ..structures.queue import Queue
from ..structures.stack import Stack

class PlayerService:
    def __init__(self, library):
        self._library = library
        self._playlist = CircularLinkedList()
        self._up_next = Queue()
        self._history = Stack()
        self._now_playing = None
        # False: a musica atual da playlist ainda nao tocou
        self._playlist_started = False
        # True: no fil da playlist volta para a primeira; False: para de tocar
        self._repeat = False

    def _contains(self, structure, song):
        # compara por identidade: e o mesmo objeto Song da biblioteca
        for item in structure.to_list():
            if item is song:
                return True

        return False

    def _in_library(self, song):
        try:
            return self._library.find(song.title, song.artist) is song
        except KeyError:
            return False

    def _is_in_use(self, song):
        return (
            self._now_playing is song
            or self._contains(self._playlist, song)
            or self._contains(self._up_next, song)
        )

    def add_to_playlist(self, title, artist):
        song = self._library.find(title, artist)
        # repetir a mesma musica na playlist e permitido
        self._playlist.append(song)
        return song

    def remove_from_playlist(self, title, artist):
        song = self._library.find(title, artist)

        if not self._contains(self._playlist, song):
            raise KeyError("A musica nao esta na playlist")

        if self._playlist.current() is song:
            # remove exatamente o no atual; a lista anda para o proximo, que ainda nao tocou
            self._playlist.remove_current()
            self._playlist_started = False
        else:
            self._playlist.remove(song)

        if self._playlist.is_empty():
            self._playlist_started = False

        return song

    def enqueue(self, title, artist):
        song = self._library.find(title, artist)
        self._up_next.enqueue(song)
        return song

    def remove_from_library(self, title, artist):
        song = self._library.find(title, artist)

        if self._is_in_use(song):
            raise ValueError("A musica esta em uso no player e nao pode ser removida")

        return self._library.remove_song(title, artist)

    def _advance(self):
        # 1. a fila "toca a seguir" tem prioridade e nao mexe na posicao da playlist
        if not self._up_next.is_empty():
            self._now_playing = self._up_next.dequeue()
            return self._now_playing

        # 2. sem fila e sem playlist: nada para tocar
        if self._playlist.is_empty():
            self._now_playing = None
            return None

        # 3. a musica atual da playlist ainda nao tocou: toca ela sem andar
        if not self._playlist_started:
            self._playlist_started = True
            self._now_playing = self._playlist.current()
            return self._now_playing

        #4. fim da playlist com repeat desligado: para e deixa pronta no inicio
        if self._playlist.is_at_end() and not self._repeat:
            self._playlist.next()
            self._playlist_started = False
            self._now_playing = None
            return None

        #5. anda na playlist (com repeat, no fim o next ja volta para a primeira)
        self._now_playing = self._playlist.next()
        return self._now_playing

    def play(self):
        if self._now_playing is not None:
            return self._now_playing

        return self._advance()

    def next_song(self):
        if self._now_playing is not None:
            self._history.push(self._now_playing)

        return self._advance()

    def previous_song(self):
        while not self._history.is_empty():
            song = self._history.pop()

            # pula musicas que foram removidas da biblioteca depois de tocar
            if self._in_library(song):
                self._now_playing = song
                return song

        raise IndexError("Nao ha musica anterior")

    def set_repeat(self, enabled):
        self._repeat = bool(enabled)

    def is_repeat(self):
        return self._repeat

    def now_playing(self):
        return self._now_playing

    def playlist(self):
        return self._playlist.to_list()

    def up_next(self):
        return self._up_next.to_list()

    def history(self):
        # do mais recente para o mais antigo
        return self._history.to_list()