import yfinance as yf
import pandas as pd
import ta

# =========================
# MAIN SCANNER (STABLE)
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

            # =========================
            # MIN DATA CHECK (FIXED)
            # =========================
            if len(close) < 50:
                continue

            # =========================
            # INDICATORS
            # =========================
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=50).mean()  # daha stabil

            rsi = ta.momentum.RSIIndicator(close=close).rsi()

            macd = ta.trend.MACD(close=close)
            macd_line = macd.macd()
            signal_line = macd.macd_signal()

            # =========================
            # VOLUME SCORE
            # =========================
            vol_mean = volume.mean()
            vol_std = volume.std()

            vol_z = 0
            if vol_std and vol_std > 0:
                vol_z = (volume.iloc[-1] - vol_mean) / vol_std

            # =========================
            # SCORE SYSTEM
            # =========================
            score = 0

            # Trend
            if ema20.iloc[-1] > ema50.iloc[-1]:
                score += 25

            # Momentum
            if close.iloc[-1] > close.iloc[-5]:
                score += 10

            # RSI zone
            if 40 < rsi.iloc[-1] < 70:
                score += 15

            # MACD
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                score += 20

            # Volume spike
            if vol_z > 1.5:
                score += 20

            # =========================
            # BOLLINGER (MANUAL SAFE)
            # =========================
            ma = close.rolling(20).mean()
            std = close.rolling(20).std()

            bb_upper = ma + (2 * std)
            bb_lower = ma - (2 * std)

            # Bollinger logic
            if close.iloc[-1] < bb_lower.iloc[-1]:
                score += 10

            if close.iloc[-1] > bb_upper.iloc[-1]:
                score -= 5

            # =========================
            # SIGNAL
            # =========================
            signal = "SAT"

            ai_percent = score  # direkt AI %

            if score >= 80:
                signal = "🟢 STRONG BUY"
            elif score >= 60:
                signal = "🟡 BUY"
            elif score >= 40:
                signal = "🟠 WATCH"
            else:
                signal = "🔴 WEAK"

            results.append([
                s,
                round(close.iloc[-1], 2),
                int(score),
                int(ai_percent),
                signal
            ])

        except Exception as e:
            # DEBUG (Render log)
            print(f"{s} error:", e)
            continue

    return results
