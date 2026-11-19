from .. models.song import Song, normalize_title
from .. structures.hash_table import HashTable
from .. structures.avl_tree import AVLTree
from .. structures.circular_linked_list import CircularLinkedList

class LibraryService:
    def __init__(self):
        # titulo normalizado -> CircularLinkedList com todas as musicas daquele titulo
        self._by_title = HashTable()
        # chave "titulo\0artista" -> song(ordem alfabetica)
        self._sorted_by_title = AVLTree()
        # chave "duracao\0titulo\0artista" -> song(ordem por duracao)
        self._sorted_by_duration = AVLTree()
        self._size = 0

    def _title_order_key(self, song):
        # "\0" e o menor caractere: desempata pelo artista sem misturar titulos
        return song.key + "\0" + normalize_title(song.artist)

    def _duration_order_key(self, song):
        # zeros a esquerda para "90" nao ficar depois de "120" na comparacao de texto
        return f"{song.duration:010d}\0{self._title_order_key(song)}"

    def _find_in_collection(self, collection, artist):
        artist_key = normalize_title(artist)

        for song in collection.to_list():
            if normalize_title(song.artist) == artist_key:
                return song

        return None

    def add_song(self, title, artist, duration):
        # o construtor da Song ja valida titulo, artista e duracao
        song = Song(title, artist, duration)

        if self._by_title.contains(song.key):
            collection = self._by_title.get(song.key)

            if self._find_in_collection(collection, song.artist) is not None:
                raise ValueError("Essa musica ja existe na biblioteca")
        else:
            collection = CircularLinkedList()
            self._by_title.put(song.key, collection)

        # o MESMO objeto vai para as tres estruturas
        collection.append(song)
        self._sorted_by_title.put(self._title_order_key(song), song)
        self._sorted_by_duration.put(self._duration_order_key(song), song)
        self._size += 1

        return song

    def find(self, title, artist):
        key = normalize_title(title)

        if not self._by_title.contains(key):
            raise KeyError("Musica nao encontrada.")

        song = self._find_in_collection(self._by_title.get(key), artist)

        if song is None:
            raise KeyError("Musica nao encontrada.")

        return song

    def find_by_title(self, title):
        key = normalize_title(title)

        if not self._by_title.contains(key):
            return []

        return self._by_title.get(key).to_list()

    def remove_song(self, title, artist):
        # find ja levanta KeyError se a musica nao existir
        song = self.find(title, artist)

        collection = self._by_title.get(song.key)
        collection.remove(song)

        # era a ultima musica com esse titulo: tira a chave da hash
        if collection.is_empty():
            self._by_title.remove(song.key)

        self._sorted_by_title.remove(self._title_order_key(song))
        self._sorted_by_duration.remove(self._duration_order_key(song))
        self._size -= 1

        return song

    def list_by_title(self):
        return self._sorted_by_title.to_list()

    def list_by_duration(self):
        return self._sorted_by_duration.to_list()

    def size(self):
        return self._size

    def is_empty(self):
        return self._size == 0