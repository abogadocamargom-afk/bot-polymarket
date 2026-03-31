import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Simulador Arbitraje - Nicolas", layout="wide")

if 'saldo_virtual' not in st.session_state:
    st.session_state.saldo_virtual = 1000.0
if 'historial' not in st.session_state:
    st.session_state.historial = []

st.title("⚖️ Simulador de Arbitraje: Modo Paper Trading")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    try: requests.post(url, data={"chat_id": ID_CHAT, "text": mensaje}, timeout=5)
    except: pass

def cargar_datos():
    btc_price = 0
    # Intento 1: CoinGecko
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        btc_price = r.json()['bitcoin']['usd']
    except:
        # Intento 2: Alternativa (Binance Public API)
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
            btc_price = float(r.json()['price'])
        except:
            btc_price = 0
            
    # Mercados de Polymarket
    try:
        poly = requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 100}, timeout=10).json()
    except:
        poly = []
        
    return btc_price, poly

precio_btc, mercados = cargar_datos()

# --- PANEL DE CONTROL ---
col_a, col_b, col_c = st.columns(3)
with col_a: 
    st.metric("BTC Actual", f"${precio_btc:,} USD" if precio_btc > 0 else "Conectando...")
with col_b: 
    st.metric("Saldo Virtual", f"${st.session_state.saldo_virtual:,.2f} USD")
with col_c: 
    lucro = st.session_state.saldo_virtual - 1000
    st.metric("Ganancia Total", f"${lucro:,.2f} USD", delta=f"{lucro:.2f}")

if st.button('🚀 ESCANEAR Y OPERAR'):
    st.rerun()

st.divider()

# --- LÓGICA DE OPERACIÓN ---
if precio_btc > 0 and isinstance(mercados, list):
    lista_analisis = []
    for m in mercados:
        pregunta = m.get('question', '')
        if any(x in pregunta.upper() for x in ["BITCOIN", "BTC"]):
            precios = m.get('outcome_prices', {})
            if precios and 'yes' in precios:
                precio_poly = float(precios['yes'])
                
                # Simulamos ganancia si detectamos brecha de precio bajo
                if precio_poly < 0.50:
                    ganancia_simulada = 5.0
                    st.session_state.saldo_virtual += ganancia_simulada
                    st.session_state.historial.append({
                        "Hora": datetime.now().strftime("%H:%M:%S"),
                        "Mercado": pregunta[:50] + "...",
                        "Beneficio": f"+${ganancia_simulada}"
                    })
                    enviar_telegram(f"💰 Op. Virtual exitosa!\nEvento: {pregunta[:30]}...\nBeneficio: +$5.00")

                lista_analisis.append({
                    "Mercado": pregunta,
                    "Precio Poly": precio_poly,
                    "Acción": "✅ COMPRA" if precio_poly < 0.50 else "Mirar"
                })
    
    if lista_analisis:
        st.dataframe(pd.DataFrame(lista_analisis), use_container_width=True)
    else:
        st.info("No se encontraron mercados de Bitcoin en este escaneo.")
else:
    st.error("Error de conexión. Presiona el botón de Escanear de nuevo en 10 segundos.")

if st.session_state.historial:
    st.subheader("📜 Historial de Operaciones Ganadoras")
    st.table(pd.DataFrame(st.session_state.historial).tail(5))
