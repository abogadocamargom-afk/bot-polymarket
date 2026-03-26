import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE TELEGRAM ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Arbitraje Nicolas", layout="wide")
st.title("🏛️ Sistema de Vigilancia Polymarket")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    try:
        requests.post(url, data={"chat_id": ID_CHAT, "text": mensaje}, timeout=5)
    except:
        pass

def cargar_datos():
    try:
        # Usamos CoinGecko para evitar el bloqueo geográfico de Binance
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()['bitcoin']['usd']
        poly = requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 100}).json()
        return btc, poly
    except:
        return 0, []

precio_btc, mercados = cargar_datos()

# Dashboard
col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="Precio BTC (Real)", value=f"${precio_btc:,}")
    if st.button('🔄 Refrescar'):
        st.rerun()

with col2:
    st.subheader("Análisis de Mercados (Bitcoin)")
    lista = []
    if isinstance(mercados, list):
        for m in mercados:
            pregunta = m.get('question', '')
            if any(palabra in pregunta.upper() for palabra in ["BITCOIN", "BTC"]):
                precio_yes = float(m.get('outcome_prices', {}).get('yes', 0))
                lista.append({"Evento": pregunta, "Precio SÍ": precio_yes})
    
    if lista:
        st.table(pd.DataFrame(lista))
        if st.checkbox("Enviar estado actual a Telegram"):
            enviar_telegram(f"📊 Reporte: BTC a ${precio_btc:,}. {len(lista)} mercados analizados.")
    else:
        st.info("Buscando mercados activos...")
