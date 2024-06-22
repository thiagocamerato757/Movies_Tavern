import os
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request
from sqlalchemy.orm import sessionmaker
import requests
import re
from entidades.base import Base
from werkzeug.security import generate_password_hash, check_password_hash

# Definição da tabela users
class User(Base):
    __tablename__ = 'users'
    
    UserName = Column(String(50), primary_key=True, nullable=False)
    Passworld = Column(String(80), nullable=False)
    Class = Column(String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)