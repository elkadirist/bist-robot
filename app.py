import streamlit as st
import pandas as pd
from engine import scan_stocks
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

st.title("📊 PRO BIST ROBOT V2")

# auto refresh
st_autorefresh(interval=120000, key="refresh")

stocks = [
    "THYAO.IS","ASELS.IS","FRIGO.IS","ASTOR.IS","ATATR.IS","SISE.IS",
    "BIMAS.IS","TEKTU.IS","EKGYO.IS","GWIND.IS","PGSUS.IS","KOZAL.IS",
    "FROTO.IS","TOASO.IS","EGEEN.IS","SASA.IS","RNPOL.IS","AKBNK.IS"
]

results = scan_stocks(stocks)

df = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])
df = df.sort_values("Skor", ascending=False)

st.dataframe(df, use_container_width=True)

st.subheader("🟢 STRONG BUY")
st.dataframe(df[df["Skor"] >= 85], use_container_width=True)
