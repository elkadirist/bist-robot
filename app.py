import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from engine import scan_stocks

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="PRO AI TRADING DASHBOARD", layout="wide")

# =========================
# STOCK LIST
# =========================
stocks = [
    "THYAO.IS","ASELS.IS","BIMAS.IS","FROTO.IS",
    "SISE.IS","EGEEN.IS","ASTOR.IS","SASA.IS",
    "PGSUS.IS","GWIND.IS","ATATR.IS","TEKTU.IS","FRIGO.IS","RNPOL.IS"
]

# =========================
# TITLE
# =========================
st.title("📊 PRO AI TRADING DASHBOARD (BIST)")
st.write("Canlı teknik analiz + AI sinyal sistemi")

# =========================
# DATA FROM ENGINE
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

# =========================
# MANUAL BOLLINGER (SAFE + NO ERROR)
# =========================
window = 20

ma = data["Close"].rolling(window=window).mean()
std = data["Close"].rolling(window=window).std()

bb_upper = ma + (2 * std)
bb_lower = ma - (2 * std)

# =========================
# CHART
# =========================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Fiyat"
))

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

fig.update_layout(
    title=f"{selected} Teknik Analiz",
    xaxis_title="Tarih",
    yaxis_title="Fiyat",
    xaxis_rangeslider_visible=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# AI DETAIL PANEL (FIXED)
# =========================
st.subheader("🤖 AI Sinyal Detayı")

# 🔥 FIX: NO .replace(".IS","") !!!
selected_data = df[df["Hisse"] == selected]

if not selected_data.empty:
    st.dataframe(selected_data, use_container_width=True)
else:
    st.info("Bu hisse için sinyal verisi yok.")
