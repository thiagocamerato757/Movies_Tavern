from entidades import *
class Usuario:
    def __init__(self, name, password, user_class):
        self.name = name
        self.password = password
        self.avaliacoes = {}
        self.favoritos = {}
        self.user_class = user_class if user_class else User_Class()