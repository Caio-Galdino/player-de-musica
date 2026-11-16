def normalizar_titulo(titulo):
    return " ".join(titulo.lower().split())

class Musica:
    def __init__(self, titulo, artista, duracao):
        # 1º nenhum campo pode ser None (precisa vir antes de qualquer strip() ou int())
        if None in (titulo, artista, duracao):
            raise ValueError("O titulo, artista e duracao da musica nao podem ser vazios.")

        # 2º titulo e artista nao podem ser vazios (strip() agora e seguro)
        if titulo.strip() == "" or artista.strip() == "":
            raise ValueError("O titulo, artista e duracao da musica nao podem ser vazios.")

        # 3º converte a duracao para inteiro
        try:
            duracao = int(duracao)
        except ValueError:
            raise ValueError("A duracao da musica deve ser um numero inteiro.")

        # 4º so agora compara, pois duracao com certeza e int
        if duracao <= 0:
            raise ValueError("A duraçao da musica deve ser maior que zero.")

        self.titulo = titulo.strip()
        self.artista = artista.strip()
        self.duracao = duracao
        self.chave = normalizar_titulo(titulo) #chave de busca

    def __str__(self): #representaçao para o usuario
        return f"{self.titulo} - {self.artista} ({self.formatar_duracao()})"

    def formatar_duracao(self):
        minutos = self.duracao // 60
        segundos = self.duracao % 60 #segundos que sobram apos divisao dos minutos
        return f"{minutos}:{segundos:02d}"

    def __repr__(self): #representaçao para desenvolvimento
        return (
            f"Musica(titulo={self.titulo!r}, "
            f"artista={self.artista!r}, "
            f"duracao={self.duracao!r})"
        )

    def para_dict(self): #representaçao para json para o front-end
        return {
            "titulo": self.titulo,
            "artista": self.artista,
            "duracao": self.duracao,
            "duracao_formatada": self.formatar_duracao(),
        }