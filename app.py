import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="BIST STABLE ROBOT", layout="wide")

st.title("📊 BIST STABLE AL/SAT ROBOT")

stocks = [
    "THYAO.IS","ASELS.IS","TUPRS.IS","ASTOR.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS","SAHOL.IS","EKGYO.IS","EREGL.IS",
    "PGSUS.IS","KOZAL.IS","FROTO.IS","TOASO.IS","GARAN.IS"
]

results = []

st.write("Robot çalışıyor...")

for s in stocks:
    try:
        df = yf.download(s, period="3mo", interval="1d", progress=False)

        if df is None or df.empty:
            continue

        close = df["Close"].dropna()
        volume = df["Volume"].dropna()

        if len(close) < 20:
            continue

        fiyat = float(close.iloc[-1])

        # Basit trend
        ma20 = close.rolling(20).mean()

        skor = 0

        # Trend
        if close.iloc[-1] > ma20.iloc[-1]:
            skor += 50

        # Momentum
        if close.iloc[-1] > close.iloc[-5]:
            skor += 30

        # Hacim
        if volume.iloc[-1] > volume.mean() * 1.5:
            skor += 20

        # Sinyal
        if skor >= 80:
            sinyal = "🟢 GÜÇLÜ AL"
        elif skor >= 50:
            sinyal = "🟡 AL"
        else:
            sinyal = "🔴 SAT"

        results.append([s, round(fiyat,2), skor, sinyal])

    except Exception as e:
        continue

df_out = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])
df_out = df_out.sort_values("Skor", ascending=False)

st.dataframe(df_out, use_container_width=True)

st.subheader("🟢 Güçlü AL (80+)")
st.dataframe(df_out[df_out["Skor"] >= 80], use_container_width=True)
