import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Dashboard Nicolas", layout="wide")
st.title("🏛️ Sistema de Vigilancia Polymarket")

def cargar_datos():
    try:
        btc = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()['bitcoin']['usd']
        poly = requests.get("https://clob.polymarket.com/markets", params={"active": True, "limit": 50}).json()
        return btc, poly
    except:
        return 0, []

precio_btc, mercados = cargar_datos()

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="Precio BTC (Real)", value=f"${precio_btc:,}")
    if st.button('🔄 Refrescar'):
        st.rerun()

with col2:
    st.subheader("Análisis de Mercados")
    lista = []
    if isinstance(mercados, list):
        for m in mercados:
            if "Bitcoin" in m.get('question', ''):
                lista.append({
                    "Evento": m.get('question'),
                    "Precio SÍ (Poly)": m.get('outcome_prices', {}).get('yes'),
                })
    st.table(pd.DataFrame(lista))
