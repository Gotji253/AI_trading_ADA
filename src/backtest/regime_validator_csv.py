"""
Regime_Agent Accuracy Validator (CSV Input)
รองรับไฟล์ CSV ที่ดาวน์โหลดจาก Binance

รูปแบบ CSV ที่รองรับ:
- มีคอลัมน์: open, high, low, close, volume
- มีคอลัมน์เวลา (timestamp / open_time / date) หรือใช้ index
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pathlib import Path

from src.agents.regime_agent import RegimeAgent


class CSVRegimeValidator:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.agent = RegimeAgent(source="binance")
        self.df = self._load_csv()

    def _load_csv(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")

        df = pd.read_csv(self.csv_path)

        # Normalize column names
        df.columns = [c.lower().strip() for c in df.columns]

        # Detect time column
        time_col = None
        for c in ["timestamp", "open_time", "date", "time", "datetime"]:
            if c in df.columns:
                time_col = c
                break

        if time_col:
            # Try to parse time
            if df[time_col].dtype == "int64" or df[time_col].dtype == "float64":
                # Assume milliseconds
                df["timestamp"] = pd.to_datetime(df[time_col], unit="ms", utc=True)
            else:
                df["timestamp"] = pd.to_datetime(df[time_col], utc=True)
            df = df.set_index("timestamp")
        else:
            # If no time column, create a simple index
            df.index = pd.date_range("2024-01-01", periods=len(df), freq="1h", tz="UTC")

        # Ensure required columns
        required = ["open", "high", "low", "close"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        if "volume" not in df.columns:
            df["volume"] = 0.0

        # Convert to numeric
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["open", "high", "low", "close"])
        return df[["open", "high", "low", "close", "volume"]]

    def validate(self, forward_bars: int = 12, step: int = 6) -> Dict[str, Any]:
        if len(self.df) < 80:
            return {"status": "error", "message": "CSV has too few rows"}

        results = []

        for i in range(60, len(self.df) - forward_bars, step):
            slice_df = self.df.iloc[: i + 1].copy()

            original = self.agent.fetcher.get_with_indicators

            def mock_get(interval="1h", limit=150):
                if interval == "1h":
                    return slice_df.tail(min(limit, len(slice_df)))
                # Approximate 4h from 1h data
                try:
                    res = slice_df.resample("4h").agg({
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }).dropna()
                    return res.tail(50)
                except Exception:
                    return pd.DataFrame()

            self.agent.fetcher.get_with_indicators = mock_get

            try:
                regime_result = self.agent.classify()
            finally:
                self.agent.fetcher.get_with_indicators = original

            if regime_result.get("status") != "ok":
                continue

            regime = regime_result["regime"]
            confidence = regime_result.get("confidence", 0)

            future = self.df.iloc[i + 1 : i + 1 + forward_bars]
            if future.empty:
                continue

            start_price = float(self.df["close"].iloc[i])
            end_price = float(future["close"].iloc[-1])
            max_up = (future["high"].max() / start_price - 1) * 100
            max_down = (future["low"].min() / start_price - 1) * 100
            ret_pct = (end_price / start_price - 1) * 100

            correct = self._is_correct(regime, ret_pct, max_up, max_down)

            results.append({
                "regime": regime,
                "confidence": round(confidence, 2),
                "return_pct": round(ret_pct, 2),
                "correct": correct,
            })

        return self._summarize(results)

    def _is_correct(self, regime: str, ret: float, max_up: float, max_down: float) -> bool:
        if regime == "trending_bull":
            return ret > 0.4 or max_up > 1.2
        if regime == "trending_bear":
            return ret < -0.4 or max_down < -1.2
        if regime == "ranging":
            return abs(ret) < 1.5
        if regime == "high_volatility":
            return abs(max_up) > 1.8 or abs(max_down) > 1.8
        return False

    def _summarize(self, results: List[Dict]) -> Dict[str, Any]:
        if not results:
            return {"status": "error", "message": "No valid samples"}

        df = pd.DataFrame(results)
        total = len(df)
        accuracy = round(df["correct"].mean() * 100, 1)

        by_regime = {}
        for r in sorted(df["regime"].unique()):
            sub = df[df["regime"] == r]
            by_regime[r] = {
                "count": int(len(sub)),
                "accuracy": round(sub["correct"].mean() * 100, 1),
                "avg_return": round(sub["return_pct"].mean(), 2),
                "avg_confidence": round(sub["confidence"].mean(), 2),
            }

        high_conf = df[df["confidence"] >= 0.65]
        high_acc = round(high_conf["correct"].mean() * 100, 1) if len(high_conf) else 0

        return {
            "status": "ok",
            "source": "csv",
            "csv_file": str(self.csv_path),
            "total_samples": total,
            "overall_accuracy": accuracy,
            "high_confidence_accuracy": high_acc,
            "high_confidence_samples": len(high_conf),
            "by_regime": by_regime,
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Validate Regime_Agent using Binance CSV")
    parser.add_argument("csv", help="Path to OHLCV CSV file")
    parser.add_argument("--forward", type=int, default=12, help="Forward bars to evaluate")
    parser.add_argument("--step", type=int, default=6, help="Step size")
    args = parser.parse_args()

    v = CSVRegimeValidator(args.csv)
    result = v.validate(forward_bars=args.forward, step=args.step)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
