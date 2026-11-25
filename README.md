# Player de Música

Projeto acadêmico da disciplina de **Estrutura de Dados**.

**Tema:** player de música com biblioteca, playlist, fila "tocar a seguir" e histórico, em que cada parte do sistema é construída sobre uma estrutura de dados implementada do zero, sem usar as estruturas prontas da linguagem (`dict`, `list.sort`, etc.) no núcleo.

## Integrante

- **Caio Henrique Brito Galdino** (projeto individual)

## Funcionalidades

- Adicionar e remover músicas da biblioteca (título, artista e duração).
- Buscar músicas pelo título (ignora maiúsculas/minúsculas e espaços extras).
- Listar a biblioteca em ordem alfabética ou por duração.
- Montar uma playlist, que pode repetir do início (modo repetir).
- Adicionar músicas na fila "tocar a seguir", que tem prioridade sobre a playlist, e retirar músicas dela.
- Destacar na playlist a música que está tocando.
- Voltar para a música anterior usando o histórico.
- Interface web (HTML + JavaScript) conectada ao backend Python por uma API REST.

## Como executar

Pré-requisitos: **Python 3** (testado com 3.14) e `pip`.

```bash
# 1. clonar o repositório
git clone <url-do-repositorio>
cd player-de-musica

# 2. criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. instalar as dependências
pip install -r requirements.txt

# 4. subir o servidor
flask --app backend.api.app run
```

Depois, abra **http://localhost:5000** no navegador.

Os comandos devem ser executados **na raiz do projeto**, porque o código usa imports relativos (`backend.api.app`).

### Músicas de exemplo

Ao iniciar, o servidor carrega as músicas do arquivo `backend/data/seed.json` (uma lista de objetos `{"title", "artist", "duration"}`, com a duração em segundos). O arquivo já vem com 10 músicas conhecidas, incluindo duas com o mesmo título ("Hallelujah", de Leonard Cohen e de Jeff Buckley) para demonstrar títulos repetidos na tabela hash e o desempate por artista na AVL. Os dados ficam em memória: o que for adicionado pela interface se perde quando o servidor é reiniciado.

### Testes

```bash
python -m unittest discover -s tests
```

Há testes para cada estrutura, para os serviços, para todas as rotas da API e para o teste de carga.

## Organização do projeto

```
backend/
├── structures/   # estruturas de dados (pilha, fila, lista circular, hash, AVL)
├── models/       # modelo Song (validação e formatação da música)
├── services/     # regras do sistema: LibraryService e PlayerService
├── api/          # API REST em Flask
└── data/         # músicas de exemplo (seed.json)
frontend/         # interface web: index.html, style.css, app.js
tests/            # testes automatizados (unittest)
load_test.py      # teste de carga (altura da AVL, hash e tempos)
```

O sistema é dividido em camadas: o **frontend** só conversa com a **API**; a API só traduz HTTP/JSON para chamadas aos **serviços**; os serviços aplicam as regras usando as **estruturas**.

## Estruturas de dados utilizadas

### Lista circular duplamente encadeada: playlist

`backend/structures/circular_linked_list.py`

Cada nó aponta para o próximo e para o anterior, e o último nó aponta de volta para o primeiro. A lista guarda um ponteiro para a música atual.

**Por que nessa parte:**
- **Modo repetir:** ao chegar no fim, o `next()` do último nó já leva ao primeiro, sem nenhum tratamento especial.
- **Avançar e voltar** na playlist é só seguir `next`/`prev` a partir do nó atual, em O(1).
- **Remover a música atual** é O(1): como o nó conhece o anterior e o próximo, basta religar os vizinhos.
- A playlist cresce e diminui o tempo todo; com nós encadeados não é preciso realocar nem deslocar elementos.

A mesma estrutura também é usada na biblioteca para guardar todas as músicas que têm o mesmo título (ver tabela hash).

### Fila (FIFO): "tocar a seguir"

`backend/structures/queue.py`

Lista simplesmente encadeada com ponteiros para o início e o fim.

**Por que nessa parte:** as músicas escolhidas para tocar a seguir devem sair **na ordem em que foram adicionadas**: a primeira a entrar é a primeira a tocar. A fila tem prioridade sobre a playlist: enquanto houver músicas nela, o player toca da fila sem mexer na posição da playlist. Inserir no fim e retirar do início são O(1). Além das operações clássicas, a fila tem um `remove(valor)` para o usuário desistir de uma música antes de ela tocar; ele percorre a fila a partir do início (O(n) no pior caso) e não altera a ordem das demais.

### Pilha (LIFO): histórico

`backend/structures/stack.py`

Lista simplesmente encadeada com ponteiro para o topo.

**Por que nessa parte:** o botão "anterior" deve voltar para a **última** música que tocou, depois para a penúltima, e assim por diante. Esse é exatamente o comportamento de uma pilha: cada música que termina é empilhada, e o "anterior" desempilha. Empilhar e desempilhar são O(1).

### Tabela hash: busca por título

`backend/structures/hash_table.py`

Vetor de tamanho fixo de "baldes", em que cada balde é uma lista encadeada (**encadeamento separado** para tratar colisões). A função de hash é própria (polinomial, base 31, sobre os caracteres da chave). Quando o fator de carga passa de **0,75**, a tabela dobra de tamanho e redistribui as chaves (**rehash**), o que mantém as listas dos baldes curtas.

**Por que nessa parte:** buscar uma música pelo título é a operação mais comum do usuário, e a hash faz isso em **O(1) em média**, sem percorrer a biblioteca inteira.

**Títulos repetidos:** a chave é o título normalizado (minúsculas, sem espaços extras), e o valor é uma **lista circular com todas as músicas daquele título**. Assim, "Imagine - John Lennon" e "Imagine - A Perfect Circle" convivem; só é proibido repetir o par título + artista.

### Árvore AVL: listagem ordenada

`backend/structures/avl_tree.py`

Árvore binária de busca balanceada: após cada inserção ou remoção, as rotações (simples e duplas) garantem que a diferença de altura entre as subárvores de qualquer nó seja no máximo 1. A altura é contada em arestas (folha = 0, árvore vazia = -1).

**Por que nessa parte:** a biblioteca precisa ser exibida **em ordem** (por título ou por duração). Um percurso em ordem (in-order) na árvore devolve os elementos já ordenados em O(n), sem precisar de um algoritmo de ordenação a cada listagem. O balanceamento garante altura O(log n), então inserir e remover continuam rápidos mesmo que as músicas sejam adicionadas já em ordem (caso em que uma árvore binária comum degeneraria em uma lista).

São usadas **duas árvores**, uma para cada critério de ordenação:
- **por título:** chave `título\0artista` (o artista desempata títulos iguais);
- **por duração:** chave `duração\0título\0artista`, com a duração preenchida com zeros à esquerda para que a comparação de texto respeite a ordem numérica.

### Resumo

| Parte do sistema | Estrutura | Operação principal |
|---|---|---|
| Playlist | Lista circular duplamente encadeada | avançar/voltar e repetir do início |
| Tocar a seguir | Fila | primeira adicionada, primeira a tocar |
| Histórico | Pilha | última que tocou, primeira a voltar |
| Busca por título | Tabela hash | encontrar pelo título em O(1) médio |
| Ordenação | Árvore AVL (×2) | listar por título ou por duração |

Uma mesma música (o mesmo objeto `Song`) é compartilhada por todas as estruturas; elas guardam referências, não cópias.

## Complexidade das operações

*n* = número de elementos da estrutura.

### Lista circular duplamente encadeada

| Operação | Melhor caso | Pior caso |
|---|---|---|
| `append` (inserir no fim) | O(1) | O(1) |
| `remove(valor)` | O(1): valor no início | O(n): valor no fim ou ausente |
| `remove_current` | O(1) | O(1) |
| `next` / `prev` / `current` | O(1) | O(1) |
| `is_at_end` | O(1) | O(1) |
| `current_index` | O(1): atual no início | O(n): atual no fim |
| `to_list` | O(n) | O(n) |

### Fila

| Operação | Melhor caso | Pior caso |
|---|---|---|
| `enqueue` | O(1) | O(1) |
| `dequeue` | O(1) | O(1) |
| `peek` | O(1) | O(1) |
| `remove(valor)` | O(1): valor no início | O(n): valor no fim ou ausente |
| `to_list` | O(n) | O(n) |

### Pilha

| Operação | Melhor caso | Pior caso |
|---|---|---|
| `push` | O(1) | O(1) |
| `pop` | O(1) | O(1) |
| `peek` | O(1) | O(1) |
| `to_list` | O(n) | O(n) |

### Tabela hash (encadeamento separado)

| Operação | Melhor caso | Pior caso |
|---|---|---|
| `put` | O(1) | O(n) |
| `get` / `contains` | O(1) | O(n) |
| `remove` | O(1) | O(n) |
| `_rehash` | O(n) | O(n) |

- O **melhor caso** (e o caso médio, com uma boa função de hash) acontece quando as chaves se espalham pelos baldes: cada balde tem poucos elementos.
- O **pior caso** acontece quando todas as chaves colidem no mesmo balde, que vira uma lista de *n* elementos.
- O `put` que dispara o **rehash** custa O(n), mas isso só acontece quando a tabela dobra de tamanho; distribuído entre todas as inserções, o custo continua O(1) **amortizado**.
- Calcular o hash percorre os caracteres da chave, o que é proporcional ao tamanho do título (considerado constante na análise).

### Árvore AVL

| Operação | Melhor caso | Pior caso |
|---|---|---|
| `put` (inserir) | O(log n) | O(log n) |
| `get` / `contains` | O(1): chave na raiz | O(log n) |
| `remove` | O(log n) | O(log n) |
| `min` / `max` | O(log n) | O(log n) |
| `to_list` (percurso em ordem) | O(n) | O(n) |

Como a árvore é sempre balanceada, sua altura é no máximo ~1,44·log₂(n), por isso não existe o pior caso O(n) de uma árvore binária de busca comum. Cada rotação é O(1), e no máximo O(log n) nós são rebalanceados por operação.

## Teste de carga

O script `load_test.py` insere 1.000, 5.000 e 10.000 músicas na biblioteca, pelo `LibraryService`, e mede a altura das árvores AVL, a ocupação da tabela hash e os tempos de inserção e busca. Para executar, na raiz do projeto (não é preciso subir o servidor):

```bash
python load_test.py
```

Os títulos são inseridos **em ordem crescente**, o pior caso de uma árvore binária de busca (BST) comum. As durações são espalhadas entre 60 e 599 segundos. Ao final de cada inserção, o script confere a quantidade de músicas e se a listagem por título está ordenada.

### Resultados

**Árvore AVL**

| Músicas | Altura (título) | Altura (duração) | Altura mínima ⌊log₂ n⌋ | Limite da AVL 1,44·log₂ n | BST comum (título) |
|---|---|---|---|---|---|
| 1.000 | 9 | 10 | 9 | 14,4 | 999 |
| 5.000 | 12 | 13 | 12 | 17,7 | 4.999 |
| 10.000 | 13 | 14 | 13 | 19,1 | 9.999 |

A altura é contada em arestas. A coluna da BST comum é calculada (n − 1), não medida.

**Tabela hash e tempos**

| Músicas | Capacidade da hash | Fator de carga | Colisões | Maior corrente | Tempo de inserção | Tempo médio de busca |
|---|---|---|---|---|---|---|
| 1.000 | 2.048 | 0,49 | 384 | 3 | 0,012 s | 1,78 µs |
| 5.000 | 8.192 | 0,61 | 2.070 | 4 | 0,066 s | 1,84 µs |
| 10.000 | 16.384 | 0,61 | 4.009 | 4 | 0,143 s | 1,93 µs |

É contada como colisão toda chave além da primeira em um mesmo balde. Os tempos são a mediana de 10 execuções e variam conforme a máquina e os outros programas em uso; as alturas e os demais números da hash são sempre os mesmos.

### Comentários

- **A altura cresce de forma logarítmica:** com 10 vezes mais músicas, a árvore por título passou de altura 9 para 13. Em uma BST comum, a inserção em ordem formaria uma lista, e a altura passaria de 999 para 9.999.
- **As duas árvores ficam bem abaixo do limite teórico.** A árvore por título atinge a altura mínima: a inserção em ordem crescente provoca rotações à esquerda que a mantêm compacta. A árvore por duração, que recebe as chaves fora de ordem, fica apenas um nível acima.
- **O rehash mantém a hash eficiente:** a tabela começa com 8 baldes e dobra sempre que o fator de carga passa de 0,75. Com 10.000 títulos, chegou a 16.384 baldes.
- **As colisões não pesam na busca:** mesmo com 4.009 colisões em 10.000 títulos, elas ficam espalhadas pelos baldes, e a maior corrente tem só 4 elementos.
- **O tempo de busca quase não muda** (de 1,78 para 1,93 µs com 10 vezes mais músicas), o que condiz com o custo O(1) médio da hash.
- **O tempo de inserção cresceu cerca de 12 vezes** para 10 vezes mais músicas, o que condiz com O(n log n), que prevê cerca de 13 vezes: cada música é inserida em duas árvores AVL, a O(log n) por inserção, e na hash, a O(1) amortizado.

## API

Toda a comunicação entre a interface e o backend é feita em JSON. Em caso de erro, a resposta é `{"error": "mensagem"}` com o código HTTP correspondente (`400` para dados inválidos ou operação não permitida, `404` para música não encontrada).

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/songs?order=title\|duration` | lista a biblioteca ordenada (AVL) |
| GET | `/api/songs/search?title=...` | busca pelo título (hash) |
| POST | `/api/songs` | adiciona `{title, artist, duration}` |
| DELETE | `/api/songs?title=...&artist=...` | remove da biblioteca (proibido se estiver em uso no player) |
| GET | `/api/playlist` | lista a playlist |
| POST | `/api/playlist` | adiciona `{title, artist}` à playlist |
| DELETE | `/api/playlist?title=...&artist=...` | remove da playlist |
| GET | `/api/queue` | lista a fila "tocar a seguir" |
| POST | `/api/queue` | adiciona `{title, artist}` à fila |
| DELETE | `/api/queue?title=...&artist=...` | remove da fila |
| GET | `/api/player` | estado completo do player |
| POST | `/api/player/play` | começa a tocar |
| POST | `/api/player/next` | próxima música |
| POST | `/api/player/previous` | música anterior (histórico) |
| PUT | `/api/player/repeat` | liga/desliga o repetir `{enabled: true\|false}` |

As rotas de `/api/player` devolvem sempre o estado completo (`now_playing`, `repeat`, `playlist`, `playlist_position`, `up_next`, `history`), para a interface se redesenhar com uma única chamada. `playlist_position` é a posição na playlist da música que está tocando (ou `null` se ela veio da fila), usada para destacá-la.

## Divisão de tarefas

Projeto desenvolvido individualmente: todas as etapas foram realizadas por **Caio Henrique Brito Galdino**.

| Etapa | Responsável |
|---|---|
| Modelo `Song` e estrutura inicial do projeto | Caio Henrique Brito Galdino |
| Estruturas: pilha, fila e lista circular duplamente encadeada | Caio Henrique Brito Galdino |
| Estruturas: tabela hash e árvore AVL | Caio Henrique Brito Galdino |
| Serviços da biblioteca e do player | Caio Henrique Brito Galdino |
| API REST (Flask) | Caio Henrique Brito Galdino |
| Interface web (HTML, CSS e JavaScript) | Caio Henrique Brito Galdino |
| Testes automatizados | Caio Henrique Brito Galdino |
