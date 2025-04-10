from flask_migrate import Migrate
from main import app, db  # importa o app e o db corretamente

migrate = Migrate(app, db)
