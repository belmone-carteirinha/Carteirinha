import streamlit as st from datetime import datetime from sqlalchemy import Column, Integer, String, Date, create_engine from sqlalchemy.ext.declarative import declarative_base from sqlalchemy.orm import sessionmaker from io import BytesIO import qrcode import os from fpdf import FPDF from PIL import Image, ImageDraw, ImageFont import base64

Configurações do banco de dados

Base = declarative_base() engine = create_engine("sqlite:///banco.db") Session = sessionmaker(bind=engine)

def get_session(): return Session()

Modelo de dados

class Carteirinha(Base): tablename = "carteirinhas" id = Column(Integer, primary_key=True) nome = Column(String) matricula = Column(String) curso = Column(String) cpf = Column(String) data_nascimento = Column(Date) dias_aula = Column(String) validade = Column(String) foto = Column(String) assinatura_secretario = Column(String) logo_prefeitura = Column(String) logo_secretaria = Column(String) imagem_gerada = Column(String) nome_secretario = Column(String)

def init_db(): Base.metadata.create_all(engine)

Funções auxiliares

def salvar_arquivo(uploaded_file, pasta="static"): if not os.path.exists(pasta): os.makedirs(pasta) caminho = os.path.join(pasta, uploaded_file.name) with open(caminho, "wb") as f: f.write(uploaded_file.getbuffer()) return caminho

def gerar_qr_code(link): qr = qrcode.make(link) buffer = BytesIO() qr.save(buffer, format="PNG") buffer.seek(0) return buffer

def exportar_pdf(carteirinha): pdf = FPDF() pdf.add_page() pdf.set_font("Arial", size=12) pdf.cell(200, 10, txt="Carteirinha de " + carteirinha.nome, ln=True) pdf.cell(200, 10, txt="Matrícula: " + carteirinha.matricula, ln=True) pdf.cell(200, 10, txt="Curso: " + carteirinha.curso, ln=True) pdf.cell(200, 10, txt="Data de Nascimento: " + str(carteirinha.data_nascimento), ln=True) pdf.cell(200, 10, txt="Validade: " + str(carteirinha.validade), ln=True) pdf_buffer = BytesIO() pdf.output(pdf_buffer) pdf_buffer.seek(0) return pdf_buffer

def gerar_imagem_carteirinha(carteirinha): largura, altura = 1000, 600 imagem = Image.new("RGB", (largura, altura), "white") draw = ImageDraw.Draw(imagem) fonte = ImageFont.load_default()

draw.text((30, 30), f"Nome: {carteirinha.nome}", font=fonte, fill="black")
draw.text((30, 70), f"Matrícula: {carteirinha.matricula}", font=fonte, fill="black")
draw.text((30, 110), f"Curso: {carteirinha.curso}", font=fonte, fill="black")
draw.text((30, 150), f"CPF: {carteirinha.cpf}", font=fonte, fill="black")
draw.text((30, 190), f"Nascimento: {carteirinha.data_nascimento}", font=fonte, fill="black")
draw.text((30, 230), f"Dias de Aula: {carteirinha.dias_aula}", font=fonte, fill="black")
draw.text((30, 270), f"Validade: {carteirinha.validade}", font=fonte, fill="black")

if carteirinha.foto and os.path.exists(carteirinha.foto):
    foto = Image.open(carteirinha.foto).resize((100, 120))
    imagem.paste(foto, (800, 30))
if carteirinha.logo_prefeitura and os.path.exists(carteirinha.logo_prefeitura):
    logo = Image.open(carteirinha.logo_prefeitura).resize((100, 100))
    imagem.paste(logo, (30, 350))
if carteirinha.logo_secretaria and os.path.exists(carteirinha.logo_secretaria):
    logo2 = Image.open(carteirinha.logo_secretaria).resize((100, 100))
    imagem.paste(logo2, (150, 350))
if carteirinha.assinatura_secretario and os.path.exists(carteirinha.assinatura_secretario):
    assinatura = Image.open(carteirinha.assinatura_secretario).resize((200, 50))
    imagem.paste(assinatura, (700, 500))

caminho = f"static/carteirinhas/carteirinha_{carteirinha.id}.png"
os.makedirs("static/carteirinhas", exist_ok=True)
imagem.save(caminho)
return caminho

Inicia banco

init_db()

Interface Streamlit

st.set_page_config("Carteirinhas Estudantis", layout="wide") st.title("Sistema de Carteirinhas")

Menu lateral

menu = st.sidebar.radio("Menu", ["Início", "Nova Carteirinha", "Gerenciar Carteirinhas"])

Página Inicial

if menu == "Início": st.subheader("Bem-vindo!") st.write("Use o menu à esquerda para navegar.")

Criar carteirinha

elif menu == "Nova Carteirinha": st.subheader("Criar Nova Carteirinha") with st.form("form_carteirinha"): nome = st.text_input("Nome do Aluno") matricula = st.text_input("Matrícula") curso = st.text_input("Curso") cpf = st.text_input("CPF") data_nascimento = st.date_input("Data de Nascimento") dias_aula = st.text_input("Dias de Aula") validade = st.text_input("Validade")

foto = st.file_uploader("Foto do Aluno", type=["png", "jpg", "jpeg"])
    assinatura = st.file_uploader("Assinatura do Secretário", type=["png"])
    logo_prefeitura = st.file_uploader("Logo da Prefeitura", type=["png"])
    logo_secretaria = st.file_uploader("Logo da Secretaria", type=["png"])
    nome_secretario = st.text_input("Nome do Secretário")

    enviado = st.form_submit_button("Salvar")

if enviado:
    session = get_session()
    nova = Carteirinha(
        nome=nome,
        matricula=matricula,
        curso=curso,
        cpf=cpf,
        data_nascimento=data_nascimento,
        dias_aula=dias_aula,
        validade=validade,
        foto=salvar_arquivo(foto) if foto else "",
        assinatura_secretario=salvar_arquivo(assinatura) if assinatura else "",
        logo_prefeitura=salvar_arquivo(logo_prefeitura) if logo_prefeitura else "",
        logo_secretaria=salvar_arquivo(logo_secretaria) if logo_secretaria else "",
        nome_secretario=nome_secretario,
        imagem_gerada="",
    )
    session.add(nova)
    session.commit()
    st.success("Carteirinha criada com sucesso!")

Listar/gerenciar carteirinhas

elif menu == "Gerenciar Carteirinhas": st.subheader("Carteirinhas Cadastradas") session = get_session() carteirinhas = session.query(Carteirinha).all()

for c in carteirinhas:
    with st.expander(f"{c.nome} - {c.matricula}"):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Curso:** {c.curso}")
            st.write(f"**Nascimento:** {c.data_nascimento}")
            st.write(f"**Validade:** {c.validade}")
            st.write(f"**Dias de Aula:** {c.dias_aula}")
            st.write(f"**Secretário:** {c.nome_secretario}")
        with col2:
            if c.foto and os.path.exists(c.foto):
                st.image(c.foto, width=100)

        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.download_button("Baixar PDF", exportar_pdf(c), file_name=f"carteirinha_{c.id}.pdf")
        with col4:
            link_carteirinha = f"http://localhost:8501/?id={c.id}"
            qr = gerar_qr_code(link_carteirinha)
            st.download_button("QR Code", qr, file_name="qr.png")
        with col5:
            whatsapp_link = f"https://api.whatsapp.com/send?text=Confira%20sua%20carteirinha:%20{link_carteirinha}"
            st.markdown(f"[Enviar por WhatsApp]({whatsapp_link})")

        if st.button(f"Gerar imagem da carteirinha", key=f"img_{c.id}"):
            caminho_img = gerar_imagem_carteirinha(c)
            if os.path.exists(caminho_img):
                st.image(caminho_img, caption="Imagem da Carteirinha", use_column_width=True)
