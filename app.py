import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="BIST ROBOT", layout="wide")

st.title("📊 BIST ROBOT (RENDER STABLE)")

# 🔥 AZ VE STABİL LİSTE (Render için optimize)
stocks = [
    "THYAO.IS","ASELS.IS","TUPRS.IS","KCHOL.IS","SISE.IS",
    "BIMAS.IS","SAHOL.IS","EKGYO.IS","EREGL.IS","PGSUS.IS"
]

results = []

st.write("🔄 Veri çekiliyor... (Render optimize mod)")

for s in stocks:
    try:
        # ⚡ kısa veri (Render için önemli)
        df = yf.download(s, period="2mo", interval="1d", progress=False)

        if df is None or df.empty:
            continue

        close = df["Close"].dropna()
        volume = df["Volume"].dropna()

        if len(close) < 15:
            continue

        fiyat = float(close.iloc[-1])

        # ======================
        # BASİT SKOR SİSTEMİ
        # ======================
        skor = 0

        ma10 = close.rolling(10).mean()

        # trend
        if close.iloc[-1] > ma10.iloc[-1]:
            skor += 50

        # momentum
        if close.iloc[-1] > close.iloc[-3]:
            skor += 30

        # hacim
        if volume.iloc[-1] > volume.mean() * 1.3:
            skor += 20

        # ======================
        # SİNYAL
        # ======================
        if skor >= 80:
            sinyal = "🟢 GÜÇLÜ AL"
        elif skor >= 50:
            sinyal = "🟡 AL"
        else:
            sinyal = "🔴 SAT"

        results.append([s, round(fiyat,2), skor, sinyal])

    except:
        continue

df_out = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])
df_out = df_out.sort_values("Skor", ascending=False)

st.dataframe(df_out, use_container_width=True)

st.subheader("🟢 Güçlü AL Adayları")
st.dataframe(df_out[df_out["Skor"] >= 80], use_container_width=True)
