import webbrowser

def enviar_whatsapp(mensagem):
    """
    Função para enviar uma mensagem via WhatsApp.
    O link gerado será aberto no navegador, simulando o envio.
    
    :param mensagem: A mensagem que será enviada via WhatsApp.
    """
    # URL base do WhatsApp para envio de mensagem
    whatsapp_url = "https://wa.me/?text="

    # Codificando a mensagem para a URL
    mensagem_codificada = mensagem.replace(" ", "%20")
    
    # Construindo a URL completa
    link = f"{whatsapp_url}{mensagem_codificada}"

    # Abrindo o link no navegador, simulando o envio
    webbrowser.open(link)
    
    # Aqui você pode integrar uma API real de WhatsApp, como Twilio ou WhatsApp Business API.
    print(f"Mensagem enviada via WhatsApp: {mensagem}")
