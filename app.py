import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Simulador Pro - Nicolas", layout="wide")

if 'saldo_virtual' not in st.session_state:
    st.session_state.saldo_virtual = 1000.0
if 'historial' not in st.session_state:
    st.session_state.historial = []

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    try: requests.post(url, data={"chat_id": ID_CHAT, "text": mensaje}, timeout=5)
    except: pass

def obtener_precio_btc():
    # Intento 1: Binance (Suele ser el más estable)
    try:
        return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()['price'])
    except:
        # Intento 2: CoinGecko
        try:
            return float(requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5).json()['bitcoin']['usd'])
        except:
            # Intento 3: KuCoin
            try:
                return float(requests.get("https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT", timeout=5).json()['data']['price'])
            except:
                return 0

def obtener_mercados():
    try:
        return requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 100}, timeout=10).json()
    except:
        return []

# Ejecución
st.title("⚖️ Centro de Mando: Arbitraje Simulado")
precio_btc = obtener_precio_btc()
mercados = obtener_mercados()

# --- PANEL VISUAL ---
c1, c2, c3 = st.columns(3)
with c1: 
    st.metric("BTC Actual", f"${precio_btc:,} USD" if precio_btc > 0 else "Error de Red")
with c2: 
    st.metric("Saldo Virtual", f"${st.session_state.saldo_virtual:,.2f}")
with c3:
    st.metric("Ganancia Total", f"${st.session_state.saldo_virtual - 1000:,.2f}")

if st.button('🚀 REINTENTAR CONEXIÓN'):
    st.rerun()

st.divider()

if precio_btc > 0:
    st.success(f"Conexión establecida. Monitoreando Polymarket...")
    # Lógica de simulación
    if isinstance(mercados, list) and len(mercados) > 0:
        resumen = []
        for m in mercados:
            pregunta = m.get('question', '')
            if "Bitcoin" in pregunta or "BTC" in pregunta:
                precios = m.get('outcome_prices', {})
                if precios and 'yes' in precios:
                    p_poly = float(precios['yes'])
                    # Simulación simple de compra si está barato (< 0.40)
                    if p_poly < 0.40:
                        st.session_state.saldo_virtual += 2.0
                        st.session_state.historial.append({"Hora": datetime.now().strftime("%H:%M"), "Evento": pregunta[:40], "Ganancia": "+$2.00"})
                    resumen.append({"Mercado": pregunta, "Precio Poly": p_poly})
        
        if resumen:
            st.dataframe(pd.DataFrame(resumen), use_container_width=True)
        else:
            st.warning("No hay mercados de BTC activos en este momento.")
    else:
        st.error("No se pudo obtener datos de Polymarket. Intenta en unos segundos.")
else:
    st.warning("Aún no tenemos el precio de BTC. Reintentando automáticamente...")

if st.session_state.historial:
    st.write("### 📜 Actividad del Simulador")
    st.table(pd.DataFrame(st.session_state.historial).tail(3))
