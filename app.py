import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta

from engine import scan_stocks

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="PRO AI TRADING DASHBOARD", layout="wide")

# =========================
# STOCK LIST
# =========================
stocks = [
    "THYAO.IS","ASELS.IS","BIMAS.IS","FROTO.IS",
    "SISE.IS","KOZAL.IS","ASTOR.IS","SASA.IS",
    "EKGYO.IS","GARAN.IS","YKBNK.IS"
]

# =========================
# TITLE
# =========================
st.title("📊 PRO AI TRADING DASHBOARD (BIST)")
st.write("Canlı teknik analiz + AI sinyal sistemi")

# =========================
# SCAN ENGINE
# =========================
results = scan_stocks(stocks)

df = pd.DataFrame(
    results,
    columns=["Hisse", "Fiyat", "Skor", "AI%", "Sinyal"]
)

# =========================
# FILTER
# =========================
min_ai = st.slider("Minimum AI %", 0, 100, 50)

filtered = df[df["AI%"] >= min_ai]

st.subheader("📋 Sinyal Tablosu")
st.dataframe(filtered.sort_values("AI%", ascending=False), use_container_width=True)

# =========================
# STOCK SELECT
# =========================
st.subheader("📈 Grafik Analizi")

selected = st.selectbox("Hisse seç", stocks)

data = yf.download(selected, period="6mo", interval="1d")
data = data.dropna()

# =========================
# INDICATORS
# =========================
ema20 = data["Close"].ewm(span=20).mean()
ema50 = data["Close"].ewm(span=50).mean()

bb = ta.volatility.BollingerBands(close=data["Close"], window=20, window_dev=2)

# =========================
# FIX: SAFE 1D CONVERSION
# =========================
bb_upper = pd.Series(bb.bollinger_hband().values.reshape(-1), index=data.index)
bb_lower = pd.Series(bb.bollinger_lband().values.reshape(-1), index=data.index)

# =========================
# CHART
# =========================
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Fiyat"
))

# EMA
fig.add_trace(go.Scatter(
    x=data.index,
    y=ema20,
    name="EMA20"
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=ema50,
    name="EMA50"
))

# Bollinger
fig.add_trace(go.Scatter(
    x=data.index,
    y=bb_upper,
    name="BB Upper"
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=bb_lower,
    name="BB Lower"
))

# =========================
# LAYOUT
# =========================
fig.update_layout(
    title=f"{selected} Teknik Analiz",
    xaxis_title="Tarih",
    yaxis_title="Fiyat",
    xaxis_rangeslider_visible=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# AI PANEL
# =========================
st.subheader("🤖 AI Sinyal Detayı")

selected_data = df[df["Hisse"] == selected.replace(".IS","")]

if not selected_data.empty:
    st.dataframe(selected_data, use_container_width=True)
else:
    st.info("Veri bulunamadı")
