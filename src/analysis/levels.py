"""
Automatic Support / Resistance levels from recent price action.
"""

from typing import Dict, Any, List
import pandas as pd

from src.data.ada_price import ADAPriceFetcher


class SupportResistance:
    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)

    def find_levels(self, interval: str = "1h", lookback: int = 200, window: int = 5) -> Dict[str, Any]:
        df = self.fetcher.get_ohlcv(interval, lookback)
        if df.empty or len(df) < window * 2:
            return {"status": "error", "message": "Not enough data"}

        highs = df["high"]
        lows = df["low"]
        close = df["close"].iloc[-1]

        # Simple pivot-based levels
        resistance = []
        support = []

        for i in range(window, len(df) - window):
            if highs.iloc[i] == highs.iloc[i - window:i + window + 1].max():
                resistance.append(float(highs.iloc[i]))
            if lows.iloc[i] == lows.iloc[i - window:i + window + 1].min():
                support.append(float(lows.iloc[i]))

        # Cluster nearby levels (within 1%)
        def cluster(levels: List[float], threshold: float = 0.01) -> List[float]:
            if not levels:
                return []
            levels = sorted(levels)
            clustered = []
            current = [levels[0]]
            for lvl in levels[1:]:
                if abs(lvl - current[-1]) / current[-1] < threshold:
                    current.append(lvl)
                else:
                    clustered.append(sum(current) / len(current))
                    current = [lvl]
            clustered.append(sum(current) / len(current))
            return [round(x, 6) for x in clustered]

        res_levels = cluster(resistance)
        sup_levels = cluster(support)

        # Nearest levels
        nearest_res = min([r for r in res_levels if r > close], default=None)
        nearest_sup = max([s for s in sup_levels if s < close], default=None)

        return {
            "status": "ok",
            "current_price": round(float(close), 6),
            "nearest_resistance": nearest_res,
            "nearest_support": nearest_sup,
            "resistance_levels": res_levels[-5:],
            "support_levels": sup_levels[:5],
            "interval": interval,
        }


def main():
    sr = SupportResistance()
    print(sr.find_levels())


if __name__ == "__main__":
    main()
