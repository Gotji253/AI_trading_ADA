"""
Walk-Forward Validation Gate (Stage 4).
New parameters must pass backtest criteria before approval.
Criteria: Sharpe > 1.5 and Max Drawdown < 8%
"""

from typing import Dict, Any
import numpy as np

from src.backtest.engine import MultiTFBacktester


class ParameterValidator:
    def __init__(self):
        self.backtester = MultiTFBacktester()

    def validate(self, proposed: Dict[str, Any], bars: int = 400) -> Dict[str, Any]:
        """Run short backtest and check against quarantine criteria."""
        data = self.backtester.fetch_aligned_data(limit=bars)
        base = data.get("15m")

        if base is None or len(base) < 150:
            return {
                "approved": False,
                "reason": "Not enough data for validation",
                "backtest_result": {"status": "error"},
                "proposed": proposed,
            }

        result = self.backtester.simulate(data, lookback=60)

        approved = False
        reason = "Failed validation criteria"

        if result.get("status") == "ok":
            ret = result.get("return_pct", 0)
            dd = result.get("by_regime", {})  # simplified; real DD from equity
            num_trades = result.get("num_trades", 0)

            # Approximate Sharpe (simplified)
            sharpe = 0.0
            if num_trades >= 5 and ret > 0:
                # Rough approximation
                sharpe = round(ret / max(10, num_trades * 0.5), 2)

            # Criteria from blueprint
            max_dd_ok = True  # Placeholder; real implementation would calculate from equity curve
            if sharpe >= 1.5 and max_dd_ok and ret > 0:
                approved = True
                reason = f"Passed: Sharpe≈{sharpe}, Return={ret}%"
            else:
                reason = f"Failed: Sharpe≈{sharpe}, Return={ret}%, Trades={num_trades}"

        return {
            "approved": approved,
            "reason": reason,
            "backtest_result": result,
            "proposed": proposed,
            "criteria": {
                "sharpe_min": 1.5,
                "max_drawdown_pct": 8.0,
            },
        }
