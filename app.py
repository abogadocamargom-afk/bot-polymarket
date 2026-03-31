import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURACIÓN ESTRICTA ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Nicolas: Arbitraje Real-Time", layout="wide")

# Inicialización de memoria del simulador
if 'saldo_virtual' not in st.session_state:
    st.session_state.saldo_virtual = 1000.0
if 'historial' not in st.session_state:
    st.session_state.historial = []

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": ID_CHAT, "text": mensaje}, timeout=5)
        return r.status_code == 200
    except:
        return False

def obtener_datos():
    # Intento obtener precio de BTC (Binance es el más estable)
    try:
        btc = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()['price'])
    except:
        btc = 0
    
    # Intento obtener mercados de Polymarket
    try:
        poly = requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 100}, timeout=10).json()
    except:
        poly = []
    
    return btc, poly

# --- INTERFAZ ---
st.title("🏛️ Centro de Mando: Arbitraje Nicolas")
precio_btc, mercados = obtener_datos()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("BTC Real (Binance)", f"${precio_btc:,} USD")
with col2:
    st.metric("Saldo Virtual", f"${st.session_state.saldo_virtual:,.2f}")
with col3:
    ganancia = st.session_state.saldo_virtual - 1000
    st.metric("Ganancia Acumulada", f"${ganancia:,.2f}", delta=f"{ganancia:.2f}")

if st.button('🚀 ESCANEAR Y OPERAR AHORA'):
    st.rerun()

st.divider()

# --- LÓGICA DE DETECCIÓN Y SIMULACIÓN ---
if precio_btc > 0 and isinstance(mercados, list):
    resumen_mercados = []
    
    for m in mercados:
        pregunta = m.get('question', '')
        # Buscamos eventos de Bitcoin
        if any(word in pregunta.upper() for word in ["BITCOIN", "BTC"]):
            precios = m.get('outcome_prices', {})
            if precios and 'yes' in precios:
                p_poly = float(precios['yes'])
                
                # REGLA DE OPORTUNIDAD:
                # Si el precio en Poly es < 0.85, lo consideramos "entrada" para el simulacro
                if p_poly < 0.85:
                    beneficio_ficticio = 10.0 # Ganancia por operación encontrada
                    st.session_state.saldo_virtual += beneficio_ficticio
                    
                    msg = f"💰 ¡Oportunidad Detectada!\n\nEvento: {pregunta[:60]}...\nPrecio Poly: {p_poly}\nBTC Actual: ${precio_btc:,}\n\nGanancia Ficticia: +$10.00"
                    enviar_telegram(msg)
                    
                    st.session_state.historial.append({
                        "Hora": datetime.now().strftime("%H:%M:%S"),
                        "Evento": pregunta[:50],
                        "Ganancia": "+$10.00"
                    })

                resumen_mercados.append({
                    "Mercado": pregunta,
                    "Precio Poly (SÍ)": p_poly,
                    "Estado": "🔥 OPERANDO" if p_poly < 0.85 else "Equilibrado"
                })

    if resumen_mercados:
        st.subheader("📊 Análisis de Brechas Actual")
        st.dataframe(pd.DataFrame(resumen_mercados), use_container_width=True)
    else:
        st.info("No se encontraron mercados específicos de BTC en este momento.")

if st.session_state.historial:
    st.subheader("📜 Historial de Operaciones Ganadas")
    st.table(pd.DataFrame(st.session_state.historial).tail(5))
