import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

# 🔄 AUTO REFRESH (30 sn)
st_autorefresh(interval=30000, key="refresh")

st.set_page_config(page_title="BIST PRO ROBOT", layout="wide")

st.title("📊 BIST PRO AL/SAT ROBOT")

# 🔥 BIST100 BASİT LİSTE (örnek)
stocks = [
    "THYAO.IS","ASELS.IS","TUPRS.IS","ASTOR.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS","SAHOL.IS","EKGYO.IS","EREGL.IS",
    "PGSUS.IS","KOZAL.IS","FROTO.IS","TOASO.IS","GARAN.IS"
]

results = []

for s in stocks:
    try:
        df = yf.download(s, period="6mo", interval="1d", progress=False)

        if df is None or df.empty:
            continue

        # MultiIndex fix
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"].dropna()
        volume = df["Volume"].dropna()

        if len(close) < 50:
            continue

        # ======================
        # TEKNİK GÖSTERGELER
        # ======================
        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        rsi = ta.momentum.RSIIndicator(close=close).rsi()

        macd = ta.trend.MACD(close=close)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()

        # ======================
        # HACİM PATLAMASI
        # ======================
        vol_spike = volume.iloc[-1] > volume.mean() * 1.8

        # ======================
        # SKOR SİSTEMİ
        # ======================
        skor = 0

        # Trend
        if ema20.iloc[-1] > ema50.iloc[-1]:
            skor += 30

        # Momentum
        if close.iloc[-1] > close.iloc[-5]:
            skor += 20

        # RSI
        if 45 < rsi.iloc[-1] < 70:
            skor += 20

        # MACD
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            skor += 20

        # Hacim patlaması
        if vol_spike:
            skor += 30

        # ======================
        # SİNYAL
        # ======================
        if skor >= 80:
            sinyal = "🟢 GÜÇLÜ AL"
        elif skor >= 60:
            sinyal = "🟡 AL"
        elif skor >= 40:
            sinyal = "🟠 İZLE"
        else:
            sinyal = "🔴 SAT"

        results.append([s, round(close.iloc[-1],2), skor, sinyal])

    except:
        continue

# ======================
# TABLO
# ======================
df_out = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])
df_out = df_out.sort_values("Skor", ascending=False)

st.dataframe(df_out, use_container_width=True)

st.subheader("🔥 Güçlü AL Adayları (80+)")
st.dataframe(df_out[df_out["Skor"] >= 80], use_container_width=True)
