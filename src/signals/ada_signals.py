"""
ADA Trading Signal Generator
Uses price data + RSI / EMA / MACD to produce buy/sell/hold signals.
Designed for Hermes Agent ADA skill.
"""

from typing import Dict, Any, Optional
import pandas as pd

from src.data.ada_price import ADAPriceFetcher


class ADASignalGenerator:
    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)

    def generate(self, interval: str = "1h", lookback: int = 100) -> Dict[str, Any]:
        """Generate a trading signal for ADA."""
        df = self.fetcher.get_with_indicators(interval=interval, limit=lookback)
        if df.empty or len(df) < 30:
            return {
                "status": "error",
                "message": "Insufficient data",
                "signal": "hold",
            }

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        price = float(latest["close"])
        rsi = float(latest["rsi_14"]) if pd.notna(latest["rsi_14"]) else None
        ema20 = float(latest["ema_20"]) if pd.notna(latest["ema_20"]) else None
        ema50 = float(latest["ema_50"]) if pd.notna(latest["ema_50"]) else None
        macd = float(latest["macd"]) if pd.notna(latest["macd"]) else None
        macd_signal = float(latest["macd_signal"]) if pd.notna(latest["macd_signal"]) else None
        macd_hist = float(latest["macd_hist"]) if pd.notna(latest["macd_hist"]) else None

        signal = "hold"
        confidence = 0.0
        reasons = []

        # RSI conditions
        if rsi is not None:
            if rsi < 30:
                signal = "buy"
                confidence += 0.35
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                signal = "sell"
                confidence += 0.35
                reasons.append(f"RSI overbought ({rsi:.1f})")

        # EMA trend
        if ema20 is not None and ema50 is not None:
            if price > ema20 > ema50:
                if signal != "sell":
                    signal = "buy"
                    confidence += 0.25
                    reasons.append("Price above EMA20 > EMA50 (uptrend)")
            elif price < ema20 < ema50:
                if signal != "buy":
                    signal = "sell"
                    confidence += 0.25
                    reasons.append("Price below EMA20 < EMA50 (downtrend)")

        # MACD crossover
        if macd is not None and macd_signal is not None:
            prev_macd = float(prev["macd"]) if pd.notna(prev["macd"]) else None
            prev_sig = float(prev["macd_signal"]) if pd.notna(prev["macd_signal"]) else None
            if prev_macd is not None and prev_sig is not None:
                if prev_macd <= prev_sig and macd > macd_signal:
                    if signal != "sell":
                        signal = "buy"
                        confidence += 0.3
                        reasons.append("MACD bullish crossover")
                elif prev_macd >= prev_sig and macd < macd_signal:
                    if signal != "buy":
                        signal = "sell"
                        confidence += 0.3
                        reasons.append("MACD bearish crossover")

        # Risk levels
        atr_approx = (df["high"] - df["low"]).tail(14).mean()
        stop_loss = None
        take_profit = None
        if signal == "buy":
            stop_loss = round(price - atr_approx * 1.5, 6)
            take_profit = round(price + atr_approx * 2.5, 6)
        elif signal == "sell":
            stop_loss = round(price + atr_approx * 1.5, 6)
            take_profit = round(price - atr_approx * 2.5, 6)

        return {
            "status": "ok",
            "symbol": "ADA",
            "interval": interval,
            "price": price,
            "signal": signal,
            "confidence": round(min(confidence, 1.0), 2),
            "rsi": round(rsi, 2) if rsi else None,
            "ema20": round(ema20, 6) if ema20 else None,
            "ema50": round(ema50, 6) if ema50 else None,
            "macd_hist": round(macd_hist, 6) if macd_hist else None,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reasons": reasons,
            "timestamp": df.index[-1].isoformat() if len(df) else None,
        }


def main():
    gen = ADASignalGenerator()
    result = gen.generate("1h")
    print(result)


if __name__ == "__main__":
    main()
