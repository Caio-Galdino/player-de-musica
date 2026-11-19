from flask import Flask, jsonify, request

from ..services.library_service import LibraryService
from ..services.player_service import PlayerService


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


def create_app():
    app = Flask(__name__)

    # uma instancia de cada servico por app: o estado fica em memoria
    library = LibraryService()
    player = PlayerService(library)

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

    return app
