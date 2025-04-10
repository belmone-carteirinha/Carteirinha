from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from io import BytesIO
from fpdf import FPDF
import qrcode
import logging
from datetime import date

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELOS
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    carteirinhas = db.relationship('Carteirinha', backref='usuario_relacionado', lazy=True)

    @property
    def is_active(self):
        return True


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
    assinatura_secretario = db.Column(db.String(120), nullable=False)
    logo_prefeitura = db.Column(db.String(120), nullable=False)
    logo_secretaria = db.Column(db.String(120), nullable=False)
    imagem_gerada = db.Column(db.String(120), nullable=True)
    nome_secretario = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Carteirinha {self.nome}>'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ROTAS
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas')
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/alterar_senha", methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        current_user.senha = nova_senha
        db.session.commit()
        flash('Senha alterada com sucesso!')
        return redirect(url_for('dashboard'))
    return render_template("alterar_senha.html")


@app.route("/promover/<int:id>")
@login_required
def promover_usuario(id):
    if current_user.tipo != 'admin':
        return redirect(url_for('dashboard'))
    usuario = Usuario.query.get_or_404(id)
    usuario.tipo = 'admin'
    db.session.commit()
    flash(f'Usuário {usuario.nome} promovido a administrador.')
    return redirect(url_for('dashboard'))


@app.route("/gerar_qr/<int:carteirinha_id>")
def gerar_qr(carteirinha_id):
    carteirinha = Carteirinha.query.get_or_404(carteirinha_id)
    qr_data = url_for('visualizar', id=carteirinha.id, _external=True)
    qr_code = qrcode.make(qr_data)
    img_io = BytesIO()
    qr_code.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route("/gerar_pdf/<int:id>")
def gerar_pdf(id):
    carteirinha = Carteirinha.query.get_or_404(id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Carteirinha de " + carteirinha.nome, ln=True)
    pdf.cell(200, 10, txt="Matrícula: " + carteirinha.matricula, ln=True)
    pdf.cell(200, 10, txt="Curso: " + carteirinha.curso, ln=True)
    pdf.cell(200, 10, txt="Data de Nascimento: " + str(carteirinha.data_nascimento), ln=True)
    pdf.cell(200, 10, txt="Validade: " + str(carteirinha.validade), ln=True)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f"carteirinha_{id}.pdf", mimetype="application/pdf")


@app.route("/painel")
@login_required
def painel():
    carteirinhas = Carteirinha.query.all()
    usuarios = Usuario.query.all()
    return render_template("painel.html", carteirinhas=carteirinhas, usuarios=usuarios)


@app.route("/criar_carteirinha", methods=['POST'])
def criar_carteirinha():
    carteirinha = Carteirinha(
        nome='Nome do Aluno',
        matricula='1234',
        foto='caminho/foto.jpg',
        assinatura_secretario='caminho/assinatura.png',
        logo_prefeitura='caminho/logo1.png',
        logo_secretaria='caminho/logo2.png',
        nome_secretario='Secretário X',
        validade='12/2025',
        usuario_id=1
    )
    db.session.add(carteirinha)
    db.session.commit()
    return redirect(url_for('visualizar_carteirinha', id=carteirinha.id))


@app.route("/excluir_carteirinha/<int:id>", methods=['POST'])
@login_required
def excluir_carteirinha(id):
    carteirinha = Carteirinha.query.get_or_404(id)
    db.session.delete(carteirinha)
    db.session.commit()
    flash('Carteirinha excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        db.session.commit()
        flash('Usuário atualizado com sucesso!')
        return redirect(url_for('dashboard'))
    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/excluir_usuario/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuário excluído com sucesso!')
    return redirect(url_for('dashboard'))


@app.route("/visualizar_carteirinha/<int:id>")
@login_required
def visualizar_carteirinha(id):
    carteirinha = Carteirinha.query.get_or_404(id)
    return render_template("visualizar_carteirinha.html", carteirinha=carteirinha)


# CRIAÇÃO AUTOMÁTICA DO ADMINISTRADOR
def create_admin_user():
    with app.app_context():
        if not Usuario.query.filter_by(email='admin@admin.com').first():
            admin = Usuario(
                nome='Admin',
                email='admin@admin.com',
                senha='admin',  # Ideal: gerar hash!
                tipo='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário administrador criado.")
        else:
            print("Usuário administrador já existe.")


# INICIAR APLICAÇÃO
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    create_admin_user()
    app.run(debug=True)
