import telebot
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import cv2
import numpy as np
import time

# Configuración del bot de Telegram
TOKEN = '6566621512:AAGrRQvBAHnTVgYTvA3l_LoFQUeAvCB-Vas'
CHAT_ID = '7384537356'
bot = telebot.TeleBot(TOKEN)

# URL principal del Consulado
URL_BASE = "https://www.exteriores.gob.es/Consulados/lahabana/es/ServiciosConsulares/Paginas/index.aspx?scco=Cuba&scd=166&scca=Certificados&scs=Certificado+de+nacimiento"

# Función para enviar mensajes
def enviar_mensaje(texto):
    try:
        bot.send_message(CHAT_ID, texto)
    except Exception as e:
        print(f"[ERROR enviando mensaje]: {e}")

# Función que busca el enlace correcto
def obtener_enlace_cita():
    try:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
        resp = requests.get(URL_BASE, headers=headers, timeout=10)
        if resp.status_code != 200:
            enviar_mensaje("Error al acceder a la página principal del consulado.")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        enlaces = soup.find_all('a')
        for enlace in enlaces:
            texto = enlace.text.strip().lower()
            if 'solicitar certificado de nacimiento' in texto and 'dni' not in texto:
    href = enlace['href']
    if not href.startswith("http"):
        href = "https://www.exteriores.gob.es" + href
    return href
        enviar_mensaje("No se encontró el enlace al trámite de certificado de nacimiento.")
    except Exception as e:
        enviar_mensaje(f"Error al buscar el enlace: {e}")
    return None

# Función para analizar si hay citas disponibles
def hay_cita_disponible(imagen_bytes):
    try:
        image = Image.open(io.BytesIO(imagen_bytes)).convert('RGB')
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2HSV)
        verde_bajo = np.array([50, 50, 50])
        verde_alto = np.array([80, 255, 255])
        mascara = cv2.inRange(hsv, verde_bajo, verde_alto)
        porcentaje_verde = (cv2.countNonZero(mascara) / (mascara.size)) * 100
        return porcentaje_verde > 1
    except Exception as e:
        enviar_mensaje(f"Error analizando la imagen: {e}")
        return False

# Función principal de revisión
def revisar():
    while True:
        try:
            enlace_cita = obtener_enlace_cita()
            if not enlace_cita:
                time.sleep(60)
                continue
            resp = requests.get(enlace_cita, timeout=15)
            if resp.status_code != 200:
                enviar_mensaje("No se pudo cargar la página del sistema de citas.")
                time.sleep(60)
                continue
            imagen = resp.content
            if hay_cita_disponible(imagen):
                enviar_mensaje("¡Hay citas disponibles para certificado de nacimiento!")
            else:
                print("[Sin disponibilidad] No hay citas en este momento.")
        except Exception as e:
            enviar_mensaje(f"Error general: {e}")
        time.sleep(60)

if __name__ == "__main__":
    enviar_mensaje("Bot iniciado correctamente.")
    revisar()