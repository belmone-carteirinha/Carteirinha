from flask_login import UserMixin
from app import db

class Usuario(db.Model, UserMixin):  # Adicionando UserMixin aqui
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    # Relacionamento com a tabela Carteirinha
    carteirinhas = db.relationship('Carteirinha', backref='usuario_relacionado', lazy=True)  # Mantendo apenas essa linha

    # Definição do método is_active para o Flask-Login
    @property
    def is_active(self):
        return True  # Aqui você pode implementar a lógica para verificar se o usuário está ativo




class Carteirinha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(20), nullable=False)
    curso = db.Column(db.String(100), nullable=True)
    cpf = db.Column(db.String(14), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    dias_aula = db.Column(db.String(255), nullable=True)
    validade = db.Column(db.String(50), nullable=True)
    foto = db.Column(db.String(120), nullable=False)  
    assinatura_secretario = db.Column(db.String(120), nullable=False)  # Caminho para assinatura
    logo_prefeitura = db.Column(db.String(120), nullable=False)  # Caminho para o logo prefeitura
    logo_secretaria = db.Column(db.String(120), nullable=False)  # Caminho para o logo secretaria
    imagem_gerada = db.Column(db.String(120), nullable=True)  
    nome_secretario = db.Column(db.String(100), nullable=False)  # Nome do secretário
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Carteirinha {self.nome}>'
