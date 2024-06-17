import os
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
import requests
import re
from entidades.base import Base

# Definição da tabela users
class User(Base):
    __tablename__ = 'users'
    
    UserName = Column(String(50), primary_key=True, nullable=False)
    Passworld = Column(String(80), nullable=False)
    Class = Column(String(50), nullable=False)