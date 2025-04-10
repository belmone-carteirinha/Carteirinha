from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Criação do aplicativo Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Configure seu banco de dados
app.config['SECRET_KEY'] = 'your_secret_key'

# Instâncias do banco de dados, Flask-Login e Flask-Migrate
db = SQLAlchemy(app)
login_manager = LoginManager(app)  # Criação do LoginManager
login_manager.login_view = 'login'  # Redireciona para a página de login se não estiver autenticado
migrate = Migrate(app, db)

# Importar os modelos aqui
from app.models import Usuario, Carteirinha

# Retorna o app
def create_app():
    from app.routes import register_routes
    register_routes(app)
    return app
