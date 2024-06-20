import os
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
import requests
import re

from entidades.listaFavoritos import ListaFavoritos
from entidades.user import User
from entidades.avaliacao import Avaliacao
from entidades.base import Base

# Caminho do arquivo do banco de dados
DATABASE_PATH = 'dataBase.db'

engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=True)

Session = sessionmaker(bind = engine)
# Verifica se o arquivo do banco de dados existe, caso contrário, cria-o
if not os.path.exists(DATABASE_PATH):
    # Criação das tabelas no banco de dados
    Base.metadata.create_all(engine)
    print("Banco de dados criado com sucesso!")