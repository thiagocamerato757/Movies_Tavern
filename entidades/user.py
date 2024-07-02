from sqlalchemy import Column,String
from entidades.base import Base

# Definição da tabela users
class User(Base):
    __tablename__ = 'users'
    
    UserName = Column(String(50), primary_key=True, nullable=False)
    Password = Column(String(80), nullable=False)
    Class = Column(String(50), nullable=False)
