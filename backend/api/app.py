import json
import os

from flask import Flask, jsonify, request

from ..services.library_service import LibraryService
from ..services.player_service import PlayerService

# musicas de exemplo carregadas quando o servidor sobe
SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed.json")


def _songs_to_dicts(songs):
    # converte as Song (vindas do to_list das estruturas) para o formato do JSON
    return [song.to_dict() for song in songs]


def _read_json():
    # silent=True: corpo invalido vira None em vez de erro do Flask
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        raise ValueError("O corpo da requisicao deve ser um objeto JSON.")

    return data


def _require_text(data, field):
    # serve tanto para o corpo JSON quanto para request.args (os dois tem .get)
    value = data.get(field)

    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"O campo '{field}' e obrigatorio e deve ser texto.")

    return value


def _player_state(player):
    # estado completo do player: o front redesenha a tela com uma chamada so
    now_playing = player.now_playing()

    return {
        "now_playing": now_playing.to_dict() if now_playing is not None else None,
        "repeat": player.is_repeat(),
        "playlist": _songs_to_dicts(player.playlist()),
        "playlist_position": player.playlist_position(),
        "up_next": _songs_to_dicts(player.up_next()),
        "history": _songs_to_dicts(player.history()),
    }


def _load_seed(library):
    # le as musicas de exemplo do arquivo e coloca na biblioteca
    with open(SEED_PATH, encoding="utf-8") as file:
        songs = json.load(file)

    for song in songs:
        library.add_song(song["title"], song["artist"], song["duration"])


def create_app(load_seed=True):
    # static_folder e relativo a esta pasta (backend/api);
    # os arquivos do front ficam em /static/style.css, /static/app.js
    app = Flask(__name__, static_folder="../../frontend", static_url_path="/static")

    # uma instancia de cada servico por app: o estado fica em memoria
    library = LibraryService()
    player = PlayerService(library)

    # os testes usam load_seed=False para comecar com a biblioteca vazia
    if load_seed:
        _load_seed(library)

    # ---------- tratamento de erros ----------

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(KeyError)
    def handle_key_error(e):
        # str(KeyError) poe aspas na mensagem; args[0] e a mensagem pura
        return jsonify({"error": e.args[0]}), 404

    @app.errorhandler(IndexError)
    def handle_index_error(e):
        return jsonify({"error": str(e)}), 400

    # ---------- front-end ----------

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # ---------- biblioteca ----------

    @app.route("/api/songs", methods=["GET"])
    def list_songs():
        order = request.args.get("order", "title")

        if order == "title":
            songs = library.list_by_title()
        elif order == "duration":
            songs = library.list_by_duration()
        else:
            raise ValueError("Ordenacao invalida: use 'title' ou 'duration'.")

        return jsonify(_songs_to_dicts(songs))

    @app.route("/api/songs/search", methods=["GET"])
    def search_songs():
        title = _require_text(request.args, "title")
        return jsonify(_songs_to_dicts(library.find_by_title(title)))

    @app.route("/api/songs", methods=["POST"])
    def add_song():
        data = _read_json()
        title = _require_text(data, "title")
        artist = _require_text(data, "artist")
        duration = data.get("duration")

        # bool e subclasse de int no Python (True == 1), por isso a checagem extra
        if isinstance(duration, bool) or not isinstance(duration, (int, str)):
            raise ValueError("A duracao da musica deve ser um numero inteiro.")

        song = library.add_song(title, artist, duration)
        return jsonify(song.to_dict()), 201

    @app.route("/api/songs", methods=["DELETE"])
    def remove_song():
        title = _require_text(request.args, "title")
        artist = _require_text(request.args, "artist")

        # passa pelo player para respeitar a regra de "musica em uso"
        song = player.remove_from_library(title, artist)
        return jsonify(song.to_dict())

    # ---------- playlist ----------

    @app.route("/api/playlist", methods=["GET"])
    def get_playlist():
        return jsonify(_songs_to_dicts(player.playlist()))

    @app.route("/api/playlist", methods=["POST"])
    def add_to_playlist():
        data = _read_json()
        title = _require_text(data, "title")
        artist = _require_text(data, "artist")

        song = player.add_to_playlist(title, artist)
        return jsonify(song.to_dict()), 201

    @app.route("/api/playlist", methods=["DELETE"])
    def remove_from_playlist():
        title = _require_text(request.args, "title")
        artist = _require_text(request.args, "artist")

        song = player.remove_from_playlist(title, artist)
        return jsonify(song.to_dict())

    # ---------- fila "tocar a seguir" ----------

    @app.route("/api/queue", methods=["GET"])
    def get_queue():
        return jsonify(_songs_to_dicts(player.up_next()))

    @app.route("/api/queue", methods=["POST"])
    def enqueue():
        data = _read_json()
        title = _require_text(data, "title")
        artist = _require_text(data, "artist")

        song = player.enqueue(title, artist)
        return jsonify(song.to_dict()), 201

    @app.route("/api/queue", methods=["DELETE"])
    def remove_from_queue():
        title = _require_text(request.args, "title")
        artist = _require_text(request.args, "artist")

        song = player.remove_from_queue(title, artist)
        return jsonify(song.to_dict())

    # ---------- controles do player ----------
    # todas as rotas daqui devolvem o estado completo

    @app.route("/api/player", methods=["GET"])
    def get_player():
        return jsonify(_player_state(player))

    @app.route("/api/player/play", methods=["POST"])
    def play():
        player.play()
        return jsonify(_player_state(player))

    @app.route("/api/player/next", methods=["POST"])
    def next_song():
        player.next_song()
        return jsonify(_player_state(player))

    @app.route("/api/player/previous", methods=["POST"])
    def previous_song():
        # sem historico o servico levanta IndexError -> 400
        player.previous_song()
        return jsonify(_player_state(player))

    @app.route("/api/player/repeat", methods=["PUT"])
    def set_repeat():
        data = _read_json()
        enabled = data.get("enabled")

        # so aceita true/false de verdade (nao "sim", 1, etc.)
        if not isinstance(enabled, bool):
            raise ValueError("O campo 'enabled' deve ser true ou false.")

        player.set_repeat(enabled)
        return jsonify(_player_state(player))

    return app
