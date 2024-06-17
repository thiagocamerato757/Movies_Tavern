import os
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
import requests
import re
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