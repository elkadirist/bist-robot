
import yfinance as yf
import pandas as pd
import ta
from ta.volatility import BollingerBands
# =========================
# MAIN SCANNER
# =========================
def scan_stocks(stocks):

    results = []

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

        # burada indicatorlar

    except:
        continue

            # =====================
            # INDICATORS
            # =====================
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()
# =====================
# BOLLINGER BANDS
# =====================
bb = BollingerBands(close=close, window=20, window_dev=2)

bb_high = bb.bollinger_hband()
bb_low = bb.bollinger_lband()
bb_mid = bb.bollinger_mavg()

# =====================
# SUPPORT / RESISTANCE
# =====================
support = close.rolling(window=20).min()
resistance = close.rolling(window=20).max()
            rsi = ta.momentum.RSIIndicator(close=close).rsi()

            macd = ta.trend.MACD(close=close)
            macd_line = macd.macd()
            signal_line = macd.macd_signal()

            # =====================
            # VOLUME
            # =====================
            vol_mean = volume.mean()
            vol_std = volume.std()

            vol_z = 0
            if vol_std > 0:
                vol_z = (volume.iloc[-1] - vol_mean) / vol_std

            # =====================
            # SCORE SYSTEM
            # =====================
            score = 0
# =====================
# SUPPORT / RESISTANCE + BOLLINGER
# =====================

# Support bounce
if abs(close.iloc[-1] - support.iloc[-1]) / close.iloc[-1] < 0.02:
    score += 15

# Resistance breakout
if close.iloc[-1] > resistance.iloc[-5]:
    score += 10

# Bollinger dip (AL fırsatı)
if close.iloc[-1] < bb_low.iloc[-1]:
    score += 20

# Bollinger üst (risk)
if close.iloc[-1] > bb_high.iloc[-1]:
    score -= 10
            # trend
            if ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
                score += 40

            # momentum
            if close.iloc[-1] > close.iloc[-5]:
                score += 15

            # RSI
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

            results.append([s, round(close.iloc[-1], 2), score, signal])

        except:
            continue

    return results
if len(close) < 50:
    continue
if len(close) < 50:
    continue

if pd.isna(close.iloc[-1]):
    continue
