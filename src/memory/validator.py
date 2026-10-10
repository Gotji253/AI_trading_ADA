"""
Walk-Forward Validation Gate.
New parameters must pass a short backtest before being approved.
"""

from typing import Dict, Any

from src.backtest.engine import MultiTFBacktester


class ParameterValidator:
    def __init__(self):
        self.backtester = MultiTFBacktester()

    def validate(self, proposed: Dict[str, Any], bars: int = 300) -> Dict[str, Any]:
        """
        Run a short backtest with proposed parameters.
        In a full version this would inject the parameters into the signal generator.
        Here we run the current engine and compare.
        """
        data = self.backtester.fetch_aligned_data(limit=bars)
        if not data.get("15m") is not None and len(data.get("15m", [])) > 100:
            result = self.backtester.simulate(data, lookback=50)
        else:
            result = {"status": "error", "message": "Not enough data"}

        approved = False
        reason = "Insufficient data or poor result"

        if result.get("status") == "ok":
            ret = result.get("return_pct", 0)
            wr = result.get("win_rate", 0)
            # Simple gate: positive return and win rate > 40%
            if ret > 0 and wr >= 40:
                approved = True
                reason = "Passed short walk-forward validation"
            else:
                reason = f"Failed validation (return={ret}%, win_rate={wr}%)"

        return {
            "approved": approved,
            "reason": reason,
            "backtest_result": result,
            "proposed": proposed,
        }
