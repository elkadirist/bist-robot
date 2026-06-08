import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from engine import scan_stocks

st.set_page_config(page_title="PRO AI TRADING DASHBOARD", layout="wide")

stocks = [
    "THYAO.IS","ASELS.IS","BIMAS.IS","FROTO.IS",
    "SISE.IS","EGEEN.IS","ASTOR.IS","SASA.IS",
    "PGSUSIS","GWIND.IS","ATATR.IS","TEKTU.IS","FRIGO.IS","RNPOL.IS"
]

st.title("📊 PRO AI TRADING DASHBOARD (BIST)")
st.write("Canlı teknik analiz + AI sinyal sistemi")

# =========================
# ENGINE DATA
# =========================
results = scan_stocks(stocks)

# 🔥 SAFE DF BUILD
if results is None or len(results) == 0:
    st.error("Engine veri üretmiyor!")
    st.stop()

df = pd.DataFrame(results)

# =========================
# AUTO COLUMN FIX
# =========================
if df.shape[1] == 4:
    df.columns = ["Hisse", "Fiyat", "Skor", "Sinyal"]
    df["AI%"] = df["Skor"]
elif df.shape[1] == 5:
    df.columns = ["Hisse", "Fiyat", "Skor", "AI%", "Sinyal"]

# =========================
# FILTER
# =========================
min_ai = st.slider("Minimum AI %", 0, 100, 50)

filtered = df[df.iloc[:, -2] >= min_ai]

st.subheader("📋 Sinyal Tablosu")
st.dataframe(filtered, use_container_width=True)

# =========================
# STOCK SELECT
# =========================
selected = st.selectbox("Hisse seç", stocks)

data = yf.download(selected, period="6mo", interval="1d")
data = data.dropna()

# =========================
# INDICATORS
# =========================
ema20 = data["Close"].ewm(span=20).mean()
ema50 = data["Close"].ewm(span=50).mean()

window = 20
ma = data["Close"].rolling(window).mean()
std = data["Close"].rolling(window).std()

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
    close=data["Close"]
))

fig.add_trace(go.Scatter(x=data.index, y=ema20, name="EMA20"))
fig.add_trace(go.Scatter(x=data.index, y=ema50, name="EMA50"))
fig.add_trace(go.Scatter(x=data.index, y=bb_upper, name="BB Upper"))
fig.add_trace(go.Scatter(x=data.index, y=bb_lower, name="BB Lower"))

st.plotly_chart(fig, use_container_width=True)

# =========================
# AI DETAIL (SAFE FIX)
# =========================
st.subheader("🤖 AI Sinyal Detayı")

match = df[df.iloc[:, 0] == selected]

if not match.empty:
    st.dataframe(match, use_container_width=True)
else:
    st.warning("Bu hisse için sinyal yok (engine boş veri üretiyor olabilir)")
