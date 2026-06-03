import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="BIST ROBOT", layout="wide")

st.title("📊 BIST ROBOT - STABLE FIX")

stocks = ["THYAO.IS","ASELS.IS","TUPRS.IS","KCHOL.IS","ASTOR.IS"]

results = []

for s in stocks:

    df = yf.download(s, period="6mo", progress=False)

    if df is None or df.empty:
        st.warning(f"{s} veri yok")
        continue

    # 🔥 MULTIINDEX FIX
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df["Close"].dropna()

    if len(close) < 10:
        continue

    fiyat = float(close.iloc[-1])

    # SKOR
    skor = 0

    if close.iloc[-1] > close.rolling(20).mean().iloc[-1]:
        skor += 50

    if close.iloc[-1] > close.iloc[-5]:
        skor += 30

    if close.iloc[-1] > close.mean():
        skor += 20

    if skor >= 80:
        sinyal = "🟢 GÜÇLÜ AL"
    elif skor >= 50:
        sinyal = "🟡 AL"
    else:
        sinyal = "🔴 SAT"

    results.append([s, round(fiyat,2), skor, sinyal])

df_out = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])

st.dataframe(df_out, use_container_width=True)