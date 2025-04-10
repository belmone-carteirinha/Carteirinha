import streamlit as st
from models import init_db, Usuario, Carteirinha, SessionLocal
from utils import gerar_imagem_carteirinha, exportar_pdf, gerar_qr_code, gerar_link_whatsapp
from datetime import date

# Inicializar o banco de dados
init_db()

st.set_page_config(page_title="Carteirinhas", layout="centered")
st.title("Sistema de Carteirinhas")

menu = ["Login", "Nova Carteirinha", "Listar Carteirinhas"]
escolha = st.sidebar.selectbox("Menu", menu)

db = SessionLocal()

if escolha == "Nova Carteirinha":
    st.subheader("Cadastrar nova carteirinha")
    with st.form("form_carteirinha"):
        nome = st.text_input("Nome")
        matricula = st.text_input("Matrícula")
        curso = st.text_input("Curso")
        cpf = st.text_input("CPF")
        nascimento = st.date_input("Data de Nascimento", value=date(2000,1,1))
        dias_aula = st.text_input("Dias de Aula")
        validade = st.text_input("Validade")
        nome_secretario = st.text_input("Nome do Secretário")
        foto = st.text_input("Caminho da Foto")
        assinatura = st.text_input("Caminho da Assinatura")
        logo_prefeitura = st.text_input("Logo Prefeitura")
        logo_secretaria = st.text_input("Logo Secretaria")
        usuario_id = 1

        submitted = st.form_submit_button("Salvar")
        if submitted:
            cart = Carteirinha(
                nome=nome, matricula=matricula, curso=curso, cpf=cpf,
                data_nascimento=nascimento, dias_aula=dias_aula,
                validade=validade, foto=foto, assinatura_secretario=assinatura,
                logo_prefeitura=logo_prefeitura, logo_secretaria=logo_secretaria,
                nome_secretario=nome_secretario, usuario_id=usuario_id
            )
            db.add(cart)
            db.commit()
            gerar_imagem_carteirinha(cart)
            st.success("Carteirinha cadastrada com sucesso!")

elif escolha == "Listar Carteirinhas":
    st.subheader("Carteirinhas Registradas")
    carteirinhas = db.query(Carteirinha).all()
    for c in carteirinhas:
        st.markdown(f"**{c.nome}** - Matrícula: {c.matricula}")
        if c.imagem_gerada:
            st.image(c.imagem_gerada, width=300)
        if st.button(f"Exportar PDF - {c.id}"):
            path = exportar_pdf(c)
            st.success(f"PDF gerado: {path}")
        link_qr = gerar_qr_code(f"http://meusite.com/carteirinha/{c.id}")
        st.image(link_qr, width=100)
        st.markdown(f"[Enviar via WhatsApp]({gerar_link_whatsapp('http://meusite.com/carteirinha/' + str(c.id))})")