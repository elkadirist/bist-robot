import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import numpy as np
import requests
from streamlit_autorefresh import st_autorefresh

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = "TOKEN"
CHAT_ID = "CHAT_ID"

sent_signals = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =========================
# REFRESH
# =========================
st_autorefresh(interval=60000, key="refresh")

st.title("📊 PRO TRADING BOT (BIST100 AI SIGNAL ENGINE)")

# =========================
# BIST100 LIST
# =========================
stocks = [
    "THYAO.IS","ASELS.IS","TUPRS.IS","ASTOR.IS","KCHOL.IS","SISE.IS",
    "BIMAS.IS","SAHOL.IS","EKGYO.IS","EREGL.IS","PGSUS.IS","KOZAL.IS",
    "FROTO.IS","TOASO.IS","GARAN.IS","ISCTR.IS","YKBNK.IS","AKBNK.IS"
]

results = []

# =========================
# ENGINE
# =========================
for s in stocks:
    try:
        df = yf.download(s, period="1y", interval="1d", progress=False)

        if df is None or df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"].dropna()
        volume = df["Volume"].dropna()

        if len(close) < 200:
            continue

        # =====================
        # INDICATORS
        # =====================
        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()
        ema200 = close.ewm(span=200).mean()

        rsi = ta.momentum.RSIIndicator(close=close).rsi()

        macd = ta.trend.MACD(close=close)
        macd_line = macd.macd()
        signal_line = macd.macd_signal()

        # =====================
        # VOLUME Z SCORE
        # =====================
        vol_mean = volume.mean()
        vol_std = volume.std()
        vol_z = (volume.iloc[-1] - vol_mean) / (vol_std + 1e-9)

        # =====================
        # SCORE SYSTEM
        # =====================
        score = 0

        # trend
        if ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
            score += 40

        # momentum
        if close.iloc[-1] > close.iloc[-5]:
            score += 15

        # RSI zone
        if 40 < rsi.iloc[-1] < 75:
            score += 15

        # MACD
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            score += 20

        # volume spike
        if vol_z > 2:
            score += 25

        # =====================
        # SIGNAL
        # =====================
        signal = "SAT"

        if score >= 85:
            signal = "🟢 STRONG BUY"
        elif score >= 65:
            signal = "🟡 BUY"
        elif score >= 45:
            signal = "🟠 WATCH"

        results.append([s, round(close.iloc[-1],2), int(score), signal])

        # =====================
        # TELEGRAM ALERT (NO SPAM)
        # =====================
        key = f"{s}_{signal}"

        if signal == "🟢 STRONG BUY" and key not in sent_signals:
            send_telegram(f"🔥 STRONG BUY: {s}\nScore: {score}\nPrice: {close.iloc[-1]}")
            sent_signals.add(key)

    except:
        continue

# =========================
# OUTPUT
# =========================
df_out = pd.DataFrame(results, columns=["Hisse","Fiyat","Skor","Sinyal"])
df_out = df_out.sort_values("Skor", ascending=False)

st.dataframe(df_out, use_container_width=True)

st.subheader("🟢 STRONG BUY LIST")
st.dataframe(df_out[df_out["Skor"] >= 85], use_container_width=True)
