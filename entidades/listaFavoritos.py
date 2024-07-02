
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from entidades.base import Base

class ListaFavoritos(Base):
    __tablename__ = 'listaFavoritos'
    userName = Column(String(50), ForeignKey('users.UserName'), nullable=False)
    movie_id = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint('userName','movie_id'),
    )