from sqlalchemy import  Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from entidades.base import Base

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