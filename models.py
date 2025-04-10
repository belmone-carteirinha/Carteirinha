from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine("sqlite:///carteirinhas.db")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha = Column(String)
    tipo = Column(String)
    carteirinhas = relationship("Carteirinha", backref="usuario_relacionado")

class Carteirinha(Base):
    __tablename__ = "carteirinhas"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    matricula = Column(String)
    curso = Column(String)
    cpf = Column(String)
    data_nascimento = Column(Date)
    dias_aula = Column(String)
    validade = Column(String)
    foto = Column(String)
    assinatura_secretario = Column(String)
    logo_prefeitura = Column(String)
    logo_secretaria = Column(String)
    imagem_gerada = Column(String)
    nome_secretario = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))