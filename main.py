import streamlit as st
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import qrcode
import bcrypt
from io import BytesIO

# Configurações iniciais do banco
Base = declarative_base()
engine = create_engine("sqlite:///banco.db")
SessionLocal = sessionmaker(bind=engine)

# Modelos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    senha_hash = Column(String)

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
    imagem_gerada = Column(String)
    usuario_id = Column(Integer)

# Inicializar banco e criar admin
def init_db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    if not db.query(Usuario).filter_by(username="admin").first():
        senha_hash = bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode()
        db.add(Usuario(username="admin", senha_hash=senha_hash))
        db.commit()
    db.close()

# Função de autenticação
def autenticar(username, senha):
    db = SessionLocal()
    user = db.query(Usuario).filter_by(username=username).first()
    db.close()
    if user and bcrypt.checkpw(senha.encode(), user.senha_hash.encode()):
        return True
    return False

# Geração da imagem da carteirinha
def gerar_imagem_carteirinha(c):
    pasta = "static/carteirinhas"
    os.makedirs(pasta, exist_ok=True)
    img = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.load_default()
    draw.text((30, 30), f"Nome: {c.nome}", font=fonte, fill="black")
    draw.text((30, 70), f"Matrícula: {c.matricula}", font=fonte, fill="black")
    draw.text((30, 110), f"Curso: {c.curso}", font=fonte, fill="black")
    draw.text((30, 150), f"CPF: {c.cpf}", font=fonte, fill="black")
    draw.text((30, 190), f"Nascimento: {c.data_nascimento}", font=fonte, fill="black")
    draw.text((30, 230), f"Dias de Aula: {c.dias_aula}", font=fonte, fill="black")
    draw.text((30, 270), f"Validade: {c.validade}", font=fonte, fill="black")
    caminho = os.path.join(pasta, f"carteirinha_{c.id}.png")
    img.save(caminho)
    db = SessionLocal()
    c.imagem_gerada = caminho
    db.merge(c)
    db.commit()
    db.close()
    return caminho

# Exportar PDF
def exportar_pdf(c):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Carteirinha de {c.nome}", ln=True)
    pdf.cell(200, 10, txt=f"Matrícula: {c.matricula}", ln=True)
    pdf.cell(200, 10, txt=f"Curso: {c.curso}", ln=True)
    pdf.cell(200, 10, txt=f"CPF: {c.cpf}", ln=True)
    pdf.cell(200, 10, txt=f"Nascimento: {c.data_nascimento}", ln=True)
    pdf.cell(200, 10, txt=f"Validade: {c.validade}", ln=True)
    caminho = f"static/carteirinhas/carteirinha_{c.id}.pdf"
    pdf.output(caminho)
    return caminho

# Gerar QR Code
def gerar_qr_code(link):
    qr = qrcode.make(link)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return buf

# Link WhatsApp
def gerar_link_whatsapp(link):
    return f"https://api.whatsapp.com/send?text=Confira%20sua%20carteirinha:%20{link}"

# Inicialização
init_db()
st.set_page_config(page_title="Carteirinhas", layout="centered")
st.title("Sistema de Carteirinhas")

# Sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Login
if not st.session_state.logado:
    st.subheader("Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
    if autenticar(usuario_input, senha_input):
        st.session_state.logado = True
        st.session_state.usuario = usuario_input
        st.success("Login realizado com sucesso!")
        st.stop()  # Impede renderização posterior antes do rerun
    else:
        st.error("Usuário ou senha inválidos")

# Menu
menu = ["Nova Carteirinha", "Listar Carteirinhas"]
escolha = st.sidebar.selectbox("Menu", menu)
db = SessionLocal()

if escolha == "Nova Carteirinha":
    st.subheader("Cadastrar nova carteirinha")
    with st.form("form_carteirinha"):
        nome = st.text_input("Nome")
        matricula = st.text_input("Matrícula")
        curso = st.text_input("Curso")
        cpf = st.text_input("CPF")
        nascimento = st.date_input("Nascimento", value=date(2000,1,1))
        dias_aula = st.text_input("Dias de Aula")
        validade = st.text_input("Validade")
        usuario_id = 1
        if st.form_submit_button("Salvar"):
            cart = Carteirinha(
                nome=nome, matricula=matricula, curso=curso, cpf=cpf,
                data_nascimento=nascimento, dias_aula=dias_aula, validade=validade,
                nome_secretario=nome_secretario, foto=foto, assinatura_secretario=assinatura,
                logo_prefeitura=logo_prefeitura, logo_secretaria=logo_secretaria,
                usuario_id=usuario_id
            )
            db.add(cart)
            db.commit()
            gerar_imagem_carteirinha(cart)
            st.success("Carteirinha cadastrada com sucesso!")

elif escolha == "Listar Carteirinhas":
    st.subheader("Carteirinhas Cadastradas")
    carteirinhas = db.query(Carteirinha).all()
    for c in carteirinhas:
        with st.expander(f"{c.nome} - {c.matricula}"):
            if c.imagem_gerada and os.path.exists(c.imagem_gerada):
                st.image(c.imagem_gerada, width=300)
            st.markdown(f"**Curso:** {c.curso}")
            st.markdown(f"**Validade:** {c.validade}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Exportar PDF {c.id}"):
                    path = exportar_pdf(c)
                    with open(path, "rb") as f:
                        st.download_button("Baixar PDF", f, file_name=f"carteirinha_{c.id}.pdf")
            with col2:
                qr = gerar_qr_code(f"http://meusite.com/carteirinha/{c.id}")
                st.image(qr, width=100)
                link = gerar_link_whatsapp(f"http://meusite.com/carteirinha/{c.id}")
                st.markdown(f"[Enviar por WhatsApp]({link})")

db.close()
