import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import qrcode

def gerar_imagem_carteirinha(carteirinha, caminho_salida='static/carteirinhas'):
    if not os.path.exists(caminho_salida):
        os.makedirs(caminho_salida)
    imagem = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(imagem)
    fonte = ImageFont.load_default()
    draw.text((30, 30), f"Nome: {carteirinha.nome}", font=fonte, fill="black")
    draw.text((30, 70), f"Matrícula: {carteirinha.matricula}", font=fonte, fill="black")
    draw.text((30, 110), f"Curso: {carteirinha.curso}", font=fonte, fill="black")
    draw.text((30, 150), f"CPF: {carteirinha.cpf}", font=fonte, fill="black")
    draw.text((30, 190), f"Nascimento: {carteirinha.data_nascimento}", font=fonte, fill="black")
    draw.text((30, 230), f"Dias de Aula: {carteirinha.dias_aula}", font=fonte, fill="black")
    draw.text((30, 270), f"Validade: {carteirinha.validade}", font=fonte, fill="black")
    caminho_imagem = os.path.join(caminho_salida, f"carteirinha_{carteirinha.id}.png")
    imagem.save(caminho_imagem)
    carteirinha.imagem_gerada = caminho_imagem
    return caminho_imagem

def exportar_pdf(carteirinha):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Carteirinha de {carteirinha.nome}", ln=True)
    pdf.cell(200, 10, txt=f"Matrícula: {carteirinha.matricula}", ln=True)
    pdf.cell(200, 10, txt=f"Curso: {carteirinha.curso}", ln=True)
    pdf.cell(200, 10, txt=f"CPF: {carteirinha.cpf}", ln=True)
    pdf.cell(200, 10, txt=f"Data de Nascimento: {carteirinha.data_nascimento}", ln=True)
    pdf.cell(200, 10, txt=f"Validade: {carteirinha.validade}", ln=True)
    caminho_pdf = f"static/carteirinhas/carteirinha_{carteirinha.id}.pdf"
    pdf.output(caminho_pdf)
    return caminho_pdf

def gerar_qr_code(link, saida='static/qrcodes'):
    if not os.path.exists(saida):
        os.makedirs(saida)
    img_qr = qrcode.make(link)
    caminho = os.path.join(saida, f"qr_{hash(link)}.png")
    img_qr.save(caminho)
    return caminho

def gerar_link_whatsapp(link_carteirinha):
    mensagem = f"Olá! Aqui está sua carteirinha: {link_carteirinha}"
    return f"https://api.whatsapp.com/send?text={mensagem.replace(' ', '%20')}"