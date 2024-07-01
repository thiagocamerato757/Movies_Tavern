from entidades import *
from werkzeug.security import generate_password_hash, check_password_hash
class Usuario:
    def __init__(self, name, password, user_class):
        self.name = name
        self.password = generate_password_hash(password)
        self.avaliacoes = {}
        self.favoritos = {}
        self.user_class = user_class if user_class else User_Class()

    def check_password(self, password):
        return check_password_hash(self.password, password)