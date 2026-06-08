import yfinance as yf
import pandas as pd
import ta
from ta.volatility import BollingerBands


def scan_stocks(stocks):

    results = []

    for s in stocks:
        try:
            df = yf.download(
                s,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df is None or df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df["Close"].dropna()
            volume = df["Volume"].dropna()

            if len(close) < 200:
                continue

            # EMA
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()

            # RSI
            rsi = ta.momentum.RSIIndicator(close=close).rsi()

            # MACD
            macd = ta.trend.MACD(close=close)
            macd_line = macd.macd()
            signal_line = macd.macd_signal()

            # Bollinger
            bb = BollingerBands(
                close=close,
                window=20,
                window_dev=2
            )

            bb_high = bb.bollinger_hband()
            bb_low = bb.bollinger_lband()

            # Support / Resistance
            support = close.rolling(20).min()
            resistance = close.rolling(20).max()

            # Volume Z Score
            vol_mean = volume.mean()
            vol_std = volume.std()

            vol_z = 0
            if vol_std > 0:
                vol_z = (volume.iloc[-1] - vol_mean) / vol_std

            # Score
            score = 0

            # Trend
            if ema20.iloc[-1] > ema50.iloc[-1] > ema200.iloc[-1]:
                score += 40

            # Momentum
            if close.iloc[-1] > close.iloc[-5]:
                score += 15

            # RSI
            if 40 < rsi.iloc[-1] < 75:
                score += 15

            # MACD
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                score += 20

            # Volume
            if vol_z > 2:
                score += 25

            # Bollinger
            if close.iloc[-1] < bb_low.iloc[-1]:
                score += 20

            if close.iloc[-1] > bb_high.iloc[-1]:
                score -= 10

            # Support
            if abs(close.iloc[-1] - support.iloc[-1]) / close.iloc[-1] < 0.02:
                score += 15

            # Resistance Breakout
            if close.iloc[-1] > resistance.iloc[-5]:
                score += 10

            # Signal
            signal = "SAT"

            if score >= 85:
                signal = "🟢 STRONG BUY"
            elif score >= 65:
                signal = "🟡 BUY"
            elif score >= 45:
                signal = "🟠 WATCH"

            results.append([
                s,
                round(float(close.iloc[-1]), 2),
                int(score),
                signal
            ])

        except Exception:
            continue

    return results
