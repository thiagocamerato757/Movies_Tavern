from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

# Criação da engine e base
engine = create_engine('sqlite:///dataBase.db', echo=True)
Base = declarative_base()

# Definição da tabela users
class User(Base):
    __tablename__ = 'users'
    
    UserName = Column(String(50), primary_key=True, nullable=False)
    Passworld = Column(String(80), nullable=False)
    Class = Column(String(50), nullable=False)

# Definição da tabela avaliacoes
class Avaliacao(Base):
    __tablename__ = 'avaliacoes'
    
    id_filme = Column(Integer, nullable=False)
    UserName = Column(String(50), ForeignKey('users.UserName'), nullable=False)
    stars = Column(Integer, nullable=False)
    comentario = Column(String(1000), nullable=True)
    
    __table_args__ = (
        PrimaryKeyConstraint('id_filme', 'UserName'),
    )

# Criação das tabelas no banco de dados
Base.metadata.create_all(engine)
