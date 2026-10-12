"""
Alpha_Agent High-Quality Setup Validator
ทดสอบความแม่นยำของ Setup คุณภาพสูง (Long / Short) บนข้อมูลย้อนหลัง
"""

from typing import Dict, Any, List
import pandas as pd
import json

from src.agents.regime_agent import RegimeAgent
from src.analysis.market_analyzer import MarketAnalyzer


class AlphaSetupValidator:
    def __init__(self):
        self.regime_agent = RegimeAgent()
        self.analyzer = MarketAnalyzer()

    def validate_from_df(self, df: pd.DataFrame, forward_bars: int = 12, step: int = 6) -> Dict[str, Any]:
        """ทดสอบ Setup คุณภาพสูงบน DataFrame"""
        if len(df) < 60:
            return {"status": "error", "message": "Not enough data"}

        results = []

        for i in range(50, len(df) - forward_bars, step):
            slice_df = df.iloc[: i + 1].copy()

            # Mock data sources
            original_regime = self.regime_agent.fetcher.get_with_indicators
            original_levels = self.analyzer.levels.find_levels

            def mock_get(interval="1h", limit=150):
                if interval == "1h":
                    return slice_df.tail(min(limit, len(slice_df)))
                try:
                    res = slice_df.resample("4h").agg({
                        "open": "first", "high": "max", "low": "min",
                        "close": "last", "volume": "sum"
                    }).dropna()
                    return res.tail(40)
                except Exception:
                    return pd.DataFrame()

            def mock_levels(interval="1h"):
                # Simple support/resistance from recent data
                recent = slice_df.tail(50)
                return {
                    "current_price": float(recent["close"].iloc[-1]),
                    "nearest_support": float(recent["low"].min()),
                    "nearest_resistance": float(recent["high"].max()),
                }

            self.regime_agent.fetcher.get_with_indicators = mock_get
            self.analyzer.levels.find_levels = mock_levels
            self.analyzer.regime = self.regime_agent

            try:
                analysis = self.analyzer.analyze()
            finally:
                self.regime_agent.fetcher.get_with_indicators = original_regime
                self.analyzer.levels.find_levels = original_levels

            rec = analysis.get("recommendation", "hold")
            quality = analysis.get("setup_quality", "none")
            setup_type = analysis.get("setup_type")

            if quality != "high" or rec not in ("buy", "sell"):
                continue

            # Evaluate future move
            future = df.iloc[i + 1 : i + 1 + forward_bars]
            if future.empty:
                continue

            start_price = float(df["close"].iloc[i])
            end_price = float(future["close"].iloc[-1])
            ret_pct = (end_price / start_price - 1) * 100

            correct = (rec == "buy" and ret_pct > 0.3) or (rec == "sell" and ret_pct < -0.3)

            results.append({
                "setup_type": setup_type,
                "signal": rec,
                "return_pct": round(ret_pct, 2),
                "correct": correct,
            })

        return self._summarize(results)

    def _summarize(self, results: List[Dict]) -> Dict[str, Any]:
        if not results:
            return {"status": "ok", "total_high_quality_setups": 0, "message": "No high-quality setups found"}

        df = pd.DataFrame(results)
        accuracy = round(df["correct"].mean() * 100, 1)

        by_type = {}
        for t in df["setup_type"].unique():
            sub = df[df["setup_type"] == t]
            by_type[t] = {
                "count": int(len(sub)),
                "accuracy": round(sub["correct"].mean() * 100, 1),
                "avg_return": round(sub["return_pct"].mean(), 2),
            }

        return {
            "status": "ok",
            "total_high_quality_setups": len(df),
            "overall_accuracy": accuracy,
            "by_setup_type": by_type,
        }


def main():
    print("Alpha Setup Validator - use with CSV or live data")
    print("Example: from src.backtest.alpha_setup_validator import AlphaSetupValidator")


if __name__ == "__main__":
    main()
