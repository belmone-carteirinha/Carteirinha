from app import create_app, db
from app.models import Usuario
import logging
from app import create_app
from flask_migrate import Migrate
from main import app, db  # importa o app e o db corretamente

from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import Usuario, Carteirinha
from app import db, login_manager
from utils.exportar_pdf import exportar_pdf
from utils.gerar_qr_code import gerar_qr_code
from utils.gerar_carteirinha import gerar_imagem_carteirinha  # Importar a função
import qrcode
from io import BytesIO
from flask import send_file
import urllib.parse
from fpdf import FPDF  # Usando fpdf para gerar PDF
from app.utils import enviar_whatsapp  # Supondo que a função esteja no arquivo utils.py
from flask import render_template, url_for, redirect, flash
from .utils import enviar_whatsapp  # Importando a função do utils.py
from .models import Carteirinha  # Certifique-se de que os modelos estão configurados corretamente
import webbrowser
from flask import url_for
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, redirect, url_for, request
from flask import url_for, redirect
from urllib.parse import quote
from flask_login import login_required
from app.models import Carteirinha    # Supondo que você tenha o modelo 'Carteirinha'
from werkzeug.utils import secure_filenam

# Função para registrar as rotas
def register_routes(app):
    # Função que verifica se o arquivo tem a extensão permitida
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Carregar o usuário para o login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Rota principal que redireciona para o login
    @app.route("/")
    def index():
        return redirect(url_for('login'))
    

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form['email']
            senha = request.form['senha']
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario and usuario.senha == senha:
                login_user(usuario)
                return redirect(url_for('dashboard'))
            flash("Credenciais inválidas")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        # Recuperando as carteirinhas e usuários do banco de dados
        carteirinhas = Carteirinha.query.all()
        usuarios = Usuario.query.all()
     
        # Passando os dados para o template
        return render_template("dashboard.html", carteirinhas=carteirinhas, usuarios=usuarios)

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
    # Rota para criar nova carteirinha
    @app.route("/nova", methods=['GET', 'POST'])
    @login_required
    def nova_carteirinha():
        if request.method == 'POST':
            nome = request.form['nome']
            matricula = request.form['matricula']

            # Recuperando os arquivos do formulário
            foto = request.files['foto']
            logo_prefeitura = request.files['logo_prefeitura']
            logo_secretaria = request.files['logo_secretaria']
            assinatura = request.files['assinatura_secretario_arquivo']
            nome_secretario = request.form.get('assinatura_secretario')

            # Verificando se a foto foi enviada
            if 'foto' not in request.files or foto.filename == '':
                flash('Nenhum arquivo de foto enviado!')
                return redirect(request.url)

            foto_dir = os.path.join('static', 'fotos')
            if not os.path.exists(foto_dir):
                os.makedirs(foto_dir)

            if foto and allowed_file(foto.filename):
                foto_path = os.path.join(foto_dir, secure_filename(foto.filename))
                foto.save(foto_path)
            else:
                flash('Formato de arquivo inválido. Apenas JPG, PNG e GIF são permitidos.')
                return render_template("nova_carteirinha.html")

            # Salvando a assinatura
            assinatura_dir = os.path.join('static', 'assinaturas')
            if not os.path.exists(assinatura_dir):
                os.makedirs(assinatura_dir)
            if assinatura:
                assinatura_path = os.path.join(assinatura_dir, secure_filename(assinatura.filename))
                assinatura.save(assinatura_path)

            # Salvando logos
            logo_dir = os.path.join('static', 'logos')
            if not os.path.exists(logo_dir):
                os.makedirs(logo_dir)
            if logo_prefeitura:
                logo_prefeitura_path = os.path.join(logo_dir, secure_filename(logo_prefeitura.filename))
                logo_prefeitura.save(logo_prefeitura_path)
            if logo_secretaria:
                logo_secretaria_path = os.path.join(logo_dir, secure_filename(logo_secretaria.filename))
                logo_secretaria.save(logo_secretaria_path)

            validade = request.form.get('validade', 'Sem validade')

            nova_carteirinha = Carteirinha(
                nome=nome,
                matricula=matricula,
                foto=foto_path,
                assinatura_secretario=assinatura_path,
                nome_secretario=nome_secretario,
                logo_prefeitura=logo_prefeitura_path,
                logo_secretaria=logo_secretaria_path,
                validade=validade,
                usuario_id=current_user.id
            )
            db.session.add(nova_carteirinha)
            db.session.commit()

            gerar_imagem_carteirinha(nova_carteirinha)

            flash("Carteirinha criada com sucesso!")
            return redirect(url_for('dashboard'))

        return render_template("nova_carteirinha.html")

    # Rota para editar a carteirinha
    @app.route("/editar/<int:id>", methods=['GET', 'POST'])
    @login_required
    def editar_carteirinha(id):   

        # Buscando a carteirinha do banco de dados
        c = Carteirinha.query.get_or_404(id)
    
        # Se o método da requisição for POST, significa que o formulário foi enviado
        if request.method == 'POST':
            # Atualizando os dados da carteirinha com os dados do formulário
            c.nome = request.form['nome']
            c.matricula = request.form['matricula']
            c.curso = request.form['curso']
            c.cpf = request.form['cpf']  # Atualizando o CPF
            c.data_nascimento = request.form['data_nascimento']  # Atualizando a Data de Nascimento
            c.dias_aula = request.form['dias_aula']  # Atualizando os Dias de Aula
            c.validade = request.form['validade']

            # Como o nome do secretário de educação é fixo, não é necessário salvar no banco
            c.nome_secretario = SECRETARIO_EDUCACAO  # Definindo o nome do secretário como fixo

            # Atualizando a foto, se uma nova foto for carregada
            if 'foto' in request.files and request.files['foto'].filename:
                foto = request.files['foto']
                foto_filename = secure_filename(foto.filename)
                foto_path = os.path.join('static/fotos', foto_filename)
                foto.save(foto_path)
                carteirinha.foto = foto_filename  # Atualizando o campo da foto

            # Atualizando a assinatura do secretário, se um novo arquivo for carregado
            if 'assinatura_arquivo' in request.files and request.files['assinatura_arquivo'].filename:
                assinatura_arquivo = request.files['assinatura_arquivo']
                assinatura_filename = secure_filename(assinatura_arquivo.filename)
                assinatura_path = os.path.join('static/assinaturas', assinatura_filename)
                assinatura_arquivo.save(assinatura_path)
                carteirinha.assinatura_secretario = assinatura_filename  # Atualizando a assinatura do secretário

                
            # Commitando as mudanças no banco de dados
            db.session.commit()
            flash('Carteirinha atualizada com sucesso!')
            # Gerar imagem da carteirinha após editar
            gerar_imagem_carteirinha(c)


            # Redirecionando para o painel de controle ou para outra página de sua escolha  
            return redirect(url_for('visualizar', id=c.id))
        
        # Caso a requisição seja GET, exibe o formulário de edição com os dados atuais
        return render_template("editar_carteirinha.html", carteirinha=c)
   
    @app.route("/visualizar/<int:id>")
    @login_required
    def visualizar(id):
        # Buscar a carteirinha pelo ID
        carteirinha = Carteirinha.query.get_or_404(id)

        # Formatar a data de nascimento
        nascimento = carteirinha.data_nascimento.strftime("%d/%m/%Y") if carteirinha.data_nascimento else "Data não informada"
    
        # Definir validade (se não tiver, mostra 'Sem validade')
        validade = carteirinha.validade if carteirinha.validade else "Sem validade"
    
        # Caminho da foto da carteirinha
        foto_path = carteirinha.foto if carteirinha.foto else None
    
        # Caminho da assinatura do secretário
        assinatura_path = carteirinha.assinatura_secretario if carteirinha.assinatura_secretario else None
    
        # Caminho da imagem gerada
        imagem_gerada = carteirinha.imagem_gerada if carteirinha.imagem_gerada else None
    
        # Nome do secretário (pode estar padronizado ou vir da carteirinha)
        nome_secretario = carteirinha.nome_secretario if carteirinha.nome_secretario else "Nome do Secretário não informado"
    
        # Renderizar o template e passar todos os dados necessários
        return render_template('visualizar_carteirinha.html', 
                                carteirinha=carteirinha,
                                nascimento=nascimento,
                                validade=validade,
                                foto_path=foto_path,
                                assinatura_path=assinatura_path,
                                imagem_gerada=imagem_gerada,
                                nome_secretario=nome_secretario)
  

    # Rota para exportar carteirinha como PDF
    @app.route("/exportar_pdf/<int:id>")
    @login_required
    def exportar_pdf_view(id):
        c = Carteirinha.query.get_or_404(id)
        caminho_pdf = exportar_pdf(c)
      
        # Verifique se a imagem existe antes de tentar enviar
        if os.path.exists(c.imagem_gerada):
           return send_file(c.imagem_gerada, as_attachment=True)
        else:
            flash("Imagem não encontrada!", "danger")
            return redirect(url_for('dashboard'))


    # Rota para exportar carteirinha como imagem
    @app.route("/exportar_imagem/<int:id>")
    @login_required
    def exportar_imagem(id):
        c = Carteirinha.query.get_or_404(id)
     
     
        return send_file(c.imagem_gerada, as_attachment=True)

    # Rota para enviar a carteirinha via WhatsApp
    @app.route("/enviar_whatsapp/<int:id>")
    @login_required
    def enviar_whatsapp_view(id):
        carteirinha = Carteirinha.query.get_or_404(id)
        link_carteirinha = url_for('visualizar', id=carteirinha.id, _external=True)
        mensagem = f"Olá, confira sua carteirinha: {link_carteirinha}"
        mensagem_codificada = mensagem.replace(" ", "%20")
        whatsapp_url = f"https://api.whatsapp.com/send?text={mensagem_codificada}"
        return redirect(whatsapp_url)

    # Outras rotas podem ser adicionadas aqui

    # Rotas para CRUD de usuário
    @app.route("/novo_usuario", methods=['GET', 'POST'])
    @login_required
    def novo_usuario():
        if current_user.tipo != 'admin':
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            tipo = request.form['tipo']

            novo_usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
            db.session.add(novo_usuario)
            db.session.commit()

            flash('Usuário criado com sucesso!')
            return redirect(url_for('dashboard'))

        return render_template("novo_usuario.html")

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
    
        # Gerar o QR Code com o link da carteirinha
        qr_data = url_for('visualizar', id=carteirinha.id, _external=True)
        qr_code = qrcode.make(qr_data)
    
        # Salvar o QR Code em um buffer
        img_io = BytesIO()
        qr_code.save(img_io, 'PNG')
        img_io.seek(0)
    
        # Retornar o QR Code como uma imagem
        return send_file(img_io, mimetype='image/png')
    
    @app.route("/gerar_pdf/<int:id>")
    def gerar_pdf(id):
        carteirinha = Carteirinha.query.get_or_404(id)
    
        # Criar o PDF (isso é um exemplo)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
    
        # Adicionando informações da carteirinha ao PDF
        pdf.cell(200, 10, txt="Carteirinha de " + carteirinha.nome, ln=True)
        pdf.cell(200, 10, txt="Matrícula: " + carteirinha.matricula, ln=True)
        pdf.cell(200, 10, txt="Curso: " + carteirinha.curso, ln=True)
        pdf.cell(200, 10, txt="Data de Nascimento: " + str(carteirinha.data_nascimento), ln=True)
        pdf.cell(200, 10, txt="Validade: " + str(carteirinha.validade), ln=True)
    
        # Salvar o PDF em memória
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        return send_file(pdf_output, as_attachment=True, download_name="carteirinha_" + str(id) + ".pdf", mimetype="application/pdf")
    

    @app.route("/painel")
    @login_required
    def painel():
        carteirinhas = Carteirinha.query.all()  # Busca todas as carteirinhas cadastradas
        usuarios = Usuario.query.all()  # Busca todos os usuários cadastrados
        return render_template("painel.html", carteirinhas=carteirinhas, usuarios=usuarios)



    @app.route("/criar_carteirinha", methods=['POST'])
    def criar_carteirinha():
        # Código para criar a carteirinha no banco de dados
        carteirinha = Carteirinha(nome='Nome do Aluno', matricula='1234')  # Exemplo
        db.session.add(carteirinha)
        db.session.commit()

        # Chama a função para gerar a imagem da carteirinha
        gerar_imagem_carteirinha(carteirinha)
     
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
        usuario = Usuario.query.get_or_404(id)  # Aqui define a variável!
        if request.method == 'POST':
           usuario.nome = request.form['nome']
           usuario.email = request.form['email']
           db.session.commit()
           flash('Usuário atualizado com sucesso!')
           return redirect(url_for('dashboard'))
    
        return render_template('editar_usuario.html', usuario=usuario)  # Usa a variável aqui
    
    @app.route('/excluir_usuario/<int:id>', methods=['POST'])
    @login_required
    def excluir_usuario(id):
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário excluído com sucesso!')
        return redirect(url_for('dashboard'))


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

