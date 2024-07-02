import os
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
import requests
import re
from entidades.base import Base

class ListaFavoritos(Base):
    __tablename__ = 'listaFavoritos'
    
    userName = Column(String(50), ForeignKey('users.UserName'), nullable=False)
    movie_id = Column(Integer)
    genres = Column(String)  # Adiciona uma coluna para armazenar os gêneros
    __table_args__ = (
        PrimaryKeyConstraint('userName','movie_id'),
    )