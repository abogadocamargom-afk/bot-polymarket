import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Simulador Nicolas", layout="wide")

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
    try:
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()['bitcoin']['usd']
        poly = requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 100}).json()
        return btc, poly
    except: return 0, []

precio_btc, mercados = cargar_datos()

# --- PANEL DE CONTROL ---
col_a, col_b, col_c = st.columns(3)
with col_a: st.metric("BTC Actual", f"${precio_btc:,} USD")
with col_b: st.metric("Saldo Virtual", f"${st.session_state.saldo_virtual:,.2f} USD")
with col_c: 
    lucro = st.session_state.saldo_virtual - 1000
    st.metric("Ganancia Total", f"${lucro:,.2f} USD", delta=f"{lucro:.2f}")

if st.button('🚀 ESCANEAR Y OPERAR'):
    st.rerun()

st.divider()

# --- SIMULACIÓN MEJORADA ---
st.subheader("🕵️ Análisis de Oportunidades")
lista_analisis = []

if isinstance(mercados, list) and len(mercados) > 0:
    for m in mercados:
        pregunta = m.get('question', '')
        # Filtro más amplio: cualquier cosa de Bitcoin que tenga precio de "SÍ"
        if any(x in pregunta.upper() for x in ["BITCOIN", "BTC"]):
            precios = m.get('outcome_prices', {})
            if precios and 'yes' in precios:
                precio_poly = float(precios['yes'])
                
                # REGLA SIMPLIFICADA PARA EL SIMULACRO:
                # Si el precio es menor a 0.50, el bot "apuesta" a que subirá.
                # (Esto es solo para probar que el sistema suma y resta dinero)
                if precio_poly < 0.50:
                    ganancia = 10.0 # Supongamos una ganancia fija por operación exitosa
                    st.session_state.saldo_virtual += ganancia
                    st.session_state.historial.append({
                        "Hora": datetime.now().strftime("%H:%M:%S"),
                        "Evento": pregunta[:50] + "...",
                        "Resultado": f"+${ganancia}"
                    })
                    enviar_telegram(f"💰 Op. Virtual: {pregunta[:30]}... | Ganancia: +${ganancia}")

                lista_analisis.append({
                    "Mercado": pregunta,
                    "Precio Poly": precio_poly,
                    "Acción": "✅ COMPRA" if precio_poly < 0.50 else "Mirar"
                })

if lista_analisis:
    st.dataframe(pd.DataFrame(lista_analisis), use_container_width=True)
    if st.session_state.historial:
        st.write("### 📜 Últimas Operaciones")
        st.table(pd.DataFrame(st.session_state.historial).tail(3))
else:
    st.warning("Polymarket no devolvió mercados en este segundo. Intenta 'Escanear' de nuevo.")
