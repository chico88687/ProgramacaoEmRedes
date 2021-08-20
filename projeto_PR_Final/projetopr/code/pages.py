class Page:
    pages = []

    def __init__(self, nome, endereco):
        self.nome = nome
        self.endereco = endereco
        self.pages.append(self)

    def get_nome(self):
        return self.nome

    def get_endereco(self):
        return self.endereco


class PageRightLogado:
    pages = []

    def __init__(self, nome, endereco):
        self.nome = nome
        self.endereco = endereco
        self.pages.append(self)

    def get_nome(self):
        return self.nome

    def get_endereco(self):
        return self.endereco


class PageRight:
    pages = []

    def __init__(self, nome, endereco):
        self.nome = nome
        self.endereco = endereco
        self.pages.append(self)

    def get_nome(self):
        return self.nome

    def get_endereco(self):
        return self.endereco


class Mensagem:
    e = ""
    s = ""


Page("contacta-nos", "contactanos")
Page("forum", "forum")
Page("noticias", "noticias")
Page("sobre nos", "sobrenos")
Page("pesquisa", "pesquisa")

PageRight("login", "login")
PageRight("regista-te", "registate")

PageRightLogado("logout", "logout")
PageRightLogado("perfil", "perfil")
