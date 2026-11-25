import math
import time

from backend.services.library_service import LibraryService

# quantidades de musicas inseridas em cada rodada
SIZES = (1000, 5000, 10000)

def build_library(total):
    library = LibraryService()

    for i in range(total):
        # zeros a esquerda: os titulos entram em ordem crescente
        # o pior caso de uma BST comum
        title = f"Musica {i:05d}"
        artist = f"Artista {i % 100}"
        # duracoes "espalhadas" entre 60 e 599 segundos
        duration = 60 + (i * 37) % 540

        library.add_song(title, artist, duration)

    return library

def check_library(library, total):
    # confirma que nada se perdeu e que a AVL devolve em ordem
    if library.size() != total:
        raise AssertionError("Quantidade de musicas incorreta.")

    previous = None

    for song in library.list_by_title():
        if previous is not None and previous.key >= song.key:
            raise AssertionError("A listagem por titulo nao esta ordenada.")
        previous = song

def measure_search(library, total):
    # tempo medio de busca por titulo na hash, em microssegundos
    start = time.perf_counter()

    for i in range(total):
        library.find_by_title(f"Musica {i:05d}")

    return (time.perf_counter() - start) / total * 1_000_000

def run(total):
    start = time.perf_counter()
    library = build_library(total)
    elapsed = time.perf_counter() - start

    check_library(library, total)

    capacity = library.hash_capacity()

    print(f"=== {total} musicas ===")
    print(f"Tempo de insercao:         {elapsed:.3f} s")
    print(f"Tempo medio de busca:      {measure_search(library, total):.2f} us")
    print(f"Altura AVL (titulo):       {library.title_tree_height()}")
    print(f"Altura AVL (duracao):      {library.duration_tree_height()}")
    print(f"Altura minima (log2 n):    {math.floor(math.log2(total))}")
    print(f"Limite AVL (1,44 log2 n):  {1.44 * math.log2(total):.1f}")
    print(f"Altura BST comum (titulo): {total - 1}")
    print(f"Capacidade da hash:        {capacity}")
    print(f"Fator de carga da hash:    {total / capacity:.2f}")
    print()

if __name__ == "__main__":
    for total in SIZES:
        run(total)
