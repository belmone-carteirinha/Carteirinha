# app/config.py

import os

class Config:
    SECRET_KEY = 'sua_chave_secreta'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///carteirinhas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
