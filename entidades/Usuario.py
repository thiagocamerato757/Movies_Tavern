from entidades import User_Class
from werkzeug.security import generate_password_hash, check_password_hash
class Usuario():
    name :str
    password :str
    avaliacoes:dict
    favoritos:dict
    Class: User_Class

    def __init__(self,Name,Password) -> None:
        self.name = Name
        self.password = generate_password_hash(Password)
    
    def check_password(self, password) -> None:
        return check_password_hash(self.password_hash, password)