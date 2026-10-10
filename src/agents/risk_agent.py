"""
Risk_Agent — คุมขนาดไม้ / Drawdown / Daily loss / Position sizing
กฎเข้มงวด:
- Risk per trade: 1-2% of current equity
- Daily loss limit: 3-5%
- Max drawdown hard stop: 10-15% → trigger emergency
"""

import os
from typing import Dict, Any, Optional

from src.paper.trader import PaperTrader
from src.config import get_config


class RiskAgent:
    def __init__(self):
        self.trader = PaperTrader(notify=False)
        self.cfg = get_config()
        self.risk_per_trade_pct = float(os.getenv("RISK_PER_TRADE_PCT", "1.5"))  # 1-2%
        self.daily_loss_limit_pct = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "4"))  # 3-5%
        self.max_drawdown_pct = float(os.getenv("MAX_DRAWDOWN_HARD_STOP_PCT", "12"))  # 10-15%

    def evaluate(self, signal: str, price: float, proposed_sl: Optional[float] = None) -> Dict[str, Any]:
        """ตรวจสอบว่าอนุญาตให้เปิดตำแหน่งได้หรือไม่ และคำนวนขนาดไม้"""
        status = self.trader.status()
        equity = status.get("equity") or status.get("balance_usdt", 0)

        # 1. Daily loss limit
        daily_pnl = status.get("daily_pnl", 0)
        if equity > 0 and abs(min(daily_pnl, 0)) / equity * 100 >= self.daily_loss_limit_pct:
            return {
                "agent": "risk",
                "approved": False,
                "reason": f"Daily loss limit reached ({self.daily_loss_limit_pct}%)",
                "max_qty": 0,
                "hard_stop": False,
            }

        # 2. Max Drawdown Hard Stop
        stats = status.get("stats", {})
        max_dd = stats.get("max_drawdown_pct", 0)
        if max_dd >= self.max_drawdown_pct:
            return {
                "agent": "risk",
                "approved": False,
                "reason": f"Max drawdown hard stop ({self.max_drawdown_pct}%)",
                "max_qty": 0,
                "hard_stop": True,  # signal to trigger emergency
            }

        # Already have position
        if status.get("position"):
            return {
                "agent": "risk",
                "approved": False,
                "reason": "Already have an open position",
                "max_qty": 0,
                "hard_stop": False,
            }

        # 3. Risk per trade sizing (1-2% of equity)
        risk_amount = equity * (self.risk_per_trade_pct / 100.0)

        if proposed_sl and abs(price - proposed_sl) > 0:
            risk_per_unit = abs(price - proposed_sl)
            max_qty = risk_amount / risk_per_unit
        else:
            # Fallback: assume 2% stop distance
            risk_per_unit = price * 0.02
            max_qty = risk_amount / risk_per_unit if risk_per_unit > 0 else 0

        # Cap by available balance
        max_cost = equity * 0.9
        if max_qty * price > max_cost:
            max_qty = max_cost / price

        return {
            "agent": "risk",
            "approved": True,
            "reason": "Risk checks passed",
            "max_qty": round(max_qty, 4),
            "risk_amount": round(risk_amount, 2),
            "risk_pct": self.risk_per_trade_pct,
            "current_equity": equity,
            "daily_pnl": daily_pnl,
            "max_drawdown_pct": max_dd,
            "hard_stop": False,
        }
