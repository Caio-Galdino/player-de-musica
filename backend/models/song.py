def normalize_title(title):
    return " ".join(title.lower().split())

class Song:
    def __init__(self, title, artist, duration):
        # 1º nenhum campo pode ser None (precisa vir antes de qualquer strip() ou int())
        if None in (title, artist, duration):
            raise ValueError("O titulo, artista e duracao da musica nao podem ser vazios.")

        # 2º titulo e artista nao podem ser vazios (strip() agora e seguro)
        if title.strip() == "" or artist.strip() == "":
            raise ValueError("O titulo, artista e duracao da musica nao podem ser vazios.")

        # 3º converte a duracao para inteiro
        try:
            duration = int(duration)
        except ValueError:
            raise ValueError("A duracao da musica deve ser um numero inteiro.")

        # 4º so agora compara, pois duracao com certeza e int
        if duration <= 0:
            raise ValueError("A duraçao da musica deve ser maior que zero.")

        self.title = title.strip()
        self.artist = artist.strip()
        self.duration = duration
        self.key = normalize_title(title) #chave de busca

    def __str__(self): #representaçao para o usuario
        return f"{self.title} - {self.artist} ({self.format_duration()})"

    def format_duration(self):
        minutes = self.duration // 60
        seconds = self.duration % 60 #segundos que sobram apos divisao dos minutos
        return f"{minutes}:{seconds:02d}"

    def __repr__(self): #representaçao para desenvolvimento
        return (
            f"Song(title={self.title!r}, "
            f"artist={self.artist!r}, "
            f"duration={self.duration!r})"
        )

    def to_dict(self): #representaçao para json para o front-end
        return {
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "formatted_duration": self.format_duration(),
        }
