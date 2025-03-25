import requests
import os
from dotenv import load_dotenv

load_dotenv()

def enviar_mensaje_whatsapp():
    numero = os.getenv("WHATSAPP_NUMBER")
    apikey = os.getenv("WHATSAPP_API_KEY")
    mensaje = "🚨 ¡Esta es una prueba de notificación de cita! 🚨"

    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": numero,
        "text": mensaje,
        "apikey": apikey
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("✅ Mensaje de prueba enviado correctamente.")
    else:
        print("❌ Error al enviar el mensaje:", response.text)

if __name__ == "__main__":
    enviar_mensaje_whatsapp()
