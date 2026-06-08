import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta

from engine import scan_stocks

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="PRO AI Trading Bot", layout="wide")

# =========================
# STOCK LIST
# =========================
stocks = [
    "THYAO.IS","ASELS.IS","BIMAS.IS","FROTO.IS",
    "SISE.IS","FRIGO.IS","ASTOR.IS","SASA.IS",
    "ATATR.IS","TEKTU.IS","GWIND.IS","PGSUS.IS","EGEEN.IS","RNPOL.IS"
]

# =========================
# HEADER
# =========================
st.title("📊 PRO AI TRADING DASHBOARD (BIST)")
st.write("Canlı teknik analiz + AI sinyal sistemi")

# =========================
# SCAN RESULTS
# =========================
results = scan_stocks(stocks)

df = pd.DataFrame(
    results,
    columns=["Hisse", "Fiyat", "Skor", "AI%", "Sinyal"]
)

# =========================
# FILTERS
# =========================
col1, col2 = st.columns(2)

with col1:
    min_ai = st.slider("Minimum AI %", 0, 100, 50)

filtered_df = df[df["AI%"] >= min_ai]

# =========================
# TABLE
# =========================
st.subheader("📋 Sinyal Tablosu")
st.dataframe(
    filtered_df.sort_values("AI%", ascending=False),
    use_container_width=True
)

# =========================
# SELECT STOCK
# =========================
st.subheader("📈 Grafik Analizi")

selected = st.selectbox("Hisse seç", stocks)

data = yf.download(selected, period="6mo", interval="1d")
data.dropna(inplace=True)

# =========================
# INDICATORS
# =========================
ema20 = data["Close"].ewm(span=20).mean()
ema50 = data["Close"].ewm(span=50).mean()

bb = ta.volatility.BollingerBands(close=data["Close"], window=20, window_dev=2)

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
    y=bb.bollinger_hband(),
    name="BB Upper"
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=bb.bollinger_lband(),
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
# INFO PANEL
# =========================
latest = df[df["Hisse"] == selected.replace(".IS","")]

if not latest.empty:
    st.subheader("🤖 AI Sinyal")
    st.write(latest)
