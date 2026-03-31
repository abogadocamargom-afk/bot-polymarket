import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Monitor Nicolas", layout="wide")

if 'saldo_virtual' not in st.session_state:
    st.session_state.saldo_virtual = 1000.0
if 'historial' not in st.session_state:
    st.session_state.historial = []

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    try: 
        r = requests.post(url, data={"chat_id": ID_CHAT, "text": mensaje}, timeout=5)
        return r.status_code == 200
    except: return False

def obtener_precio_btc():
    try:
        return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()['price'])
    except: return 0

# --- EJECUCIÓN ---
st.title("⚖️ Verificación de Notificaciones")
precio = obtener_precio_btc()

if st.button('🔔 ENVIAR PRUEBA A TELEGRAM'):
    exito = enviar_telegram(f"✅ ¡Conexión verificada! El precio actual es ${precio}")
    if exito: st.success("¡Mensaje enviado! Revisa tu celular.")
    else: st.error("Fallo al enviar. Revisa el Token o el ID.")

st.divider()

if precio > 0:
    st.metric("BTC Actual", f"${precio:,} USD")
    # Si detecta BTC, manda un aviso automático (solo una vez para probar)
    if 'test_inicial' not in st.session_state:
        enviar_telegram("🤖 Bot activo y vigilando mercados...")
        st.session_state.test_inicial = True
