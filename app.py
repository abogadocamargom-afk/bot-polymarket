import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN_BOT = "8711209659:AAGgPpw1mxx9LMfiJ0MRcBATRaxInsWqIV8"
ID_CHAT = "8666845968"

st.set_page_config(page_title="Simulador Arbitraje - Nicolas", layout="wide")

# Inicializar saldo ficticio en la sesión del navegador
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

# --- PANEL DE CONTROL Y ESTADO DE CUENTA ---
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Precio BTC Actual", f"${precio_btc:,} USD")
with col_b:
    st.metric("Saldo Virtual", f"${st.session_state.saldo_virtual:,.2f} USD")
with col_c:
    lucro = st.session_state.saldo_virtual - 1000
    st.metric("Ganancia/Pérdida Total", f"${lucro:,.2f} USD", delta=f"{lucro:.2f}")

if st.button('🔄 Escanear y Operar'):
    st.rerun()

st.divider()

# --- LÓGICA DE SIMULACIÓN ---
st.subheader("🕵️ Análisis de Oportunidades en Tiempo Real")
lista_analisis = []

if isinstance(mercados, list):
    for m in mercados:
        pregunta = m.get('question', '')
        if "Bitcoin" in pregunta and "above" in pregunta.lower():
            nums = re.findall(r'\d+(?:,\d+)?', pregunta.replace(',', ''))
            if nums:
                target = float(nums[0])
                precio_poly = float(m.get('outcome_prices', {}).get('yes', 0))
                
                # REGLA DE OPORTUNIDAD: BTC Real > Target pero Poly < 0.90
                es_oportunidad = precio_btc > target and precio_poly < 0.90
                
                if es_oportunidad:
                    # SIMULACIÓN DE OPERACIÓN: "Invertimos" $100 virtuales
                    costo_operacion = 100.0
                    ganancia_potencial = (costo_operacion / precio_poly) - costo_operacion
                    
                    # Para la simulación, asumimos que se gana si la brecha es real
                    st.session_state.saldo_virtual += ganancia_potencial
                    st.session_state.historial.append({
                        "Fecha": datetime.now().strftime("%H:%M:%S"),
                        "Evento": pregunta,
                        "Ganancia": ganancia_potencial
                    })
                    enviar_telegram(f"💰 ¡OPERACIÓN FICTICIA GANADA!\nEvento: {pregunta}\nGanancia: +${ganancia_potencial:.2f}")

                lista_analisis.append({
                    "Mercado": pregunta,
                    "Target Price": target,
                    "Precio Poly": precio_poly,
                    "Estado": "🔥 COMPRA VIRTUAL" if es_oportunidad else "Equilibrado"
                })

if lista_analisis:
    df = pd.DataFrame(lista_analisis)
    st.dataframe(df, use_container_width=True)
    
    if st.session_state.historial:
        st.write("### 📜 Historial de Operaciones del Simulador")
        st.table(pd.DataFrame(st.session_state.historial).tail(5))
else:
    st.info("No hay mercados de Bitcoin disponibles para simular ahora.")
