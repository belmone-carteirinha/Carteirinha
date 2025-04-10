from app import create_app, db
from app.models import Usuario
import logging
from app import create_app
from flask_migrate import Migrate
from main import app, db  # importa o app e o db corretamente

migrate = Migrate(app, db)

# Configuração do aplicativo
app = create_app()

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

