from app import create_app, db
from app.models import Usuario
import logging
from app import create_app
from flask_migrate import Migrate
from main import app, db  # importa o app e o db corretamente

migrate = Migrate(app, db)

# Configuração do aplicativo
app = create_app()

from flask_login import UserMixin
from app import db

class Usuario(db.Model, UserMixin):  # Adicionando UserMixin aqui
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

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

# Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para criar o usuário administrador, se não existir
def create_admin_user():
    with app.app_context():
        if not Usuario.query.filter_by(email='admin@admin.com').first():
            # Criando usuário administrador
            admin = Usuario(
                nome='Admin',
                email='admin@admin.com',
                senha='admin',  # Aqui você deve utilizar hash para senhas
                tipo='admin'
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Usuário administrador criado.")
        else:
            logger.info("Usuário administrador já existe.")

# Execução da aplicação
if __name__ == '__main__':
    create_admin_user()  # Garantir que o admin exista
    app.run(debug=True)

