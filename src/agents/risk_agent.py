"""
Risk_Agent — คุมขนาดไม้ / Drawdown / Daily loss / Position sizing
"""

import os
from typing import Dict, Any, Optional

from src.paper.trader import PaperTrader
from src.config import get_config


class RiskAgent:
    def __init__(self):
        self.trader = PaperTrader(notify=False)
        self.cfg = get_config()

    def evaluate(self, signal: str, price: float, proposed_sl: Optional[float] = None) -> Dict[str, Any]:
        """ตรวจสอบว่าอนุญาตให้เปิดตำแหน่งได้หรือไม่ และคำนวนขนาดไม้ที่เหมาะสม"""
        status = self.trader.status()

        # Daily loss limit
        if self.trader._check_daily_loss_limit():
            return {
                "agent": "risk",
                "approved": False,
                "reason": "Daily loss limit reached",
                "max_qty": 0,
            }

        # Already have position
        if status.get("position"):
            return {
                "agent": "risk",
                "approved": False,
                "reason": "Already have an open position",
                "max_qty": 0,
            }

        # Position sizing
        max_risk_pct = float(os.getenv("MAX_OPEN_RISK_PCT", "5"))
        risk_amount = status["balance_usdt"] * (max_risk_pct / 100.0)

        if proposed_sl and abs(price - proposed_sl) > 0:
            risk_per_unit = abs(price - proposed_sl)
            max_qty = risk_amount / risk_per_unit
        else:
            max_qty = risk_amount / (price * 0.02) if price > 0 else 0

        # Cap by available balance
        max_cost = status["balance_usdt"] * 0.9
        if max_qty * price > max_cost:
            max_qty = max_cost / price

        return {
            "agent": "risk",
            "approved": True,
            "reason": "Risk checks passed",
            "max_qty": round(max_qty, 4),
            "risk_amount": round(risk_amount, 2),
            "current_equity": status.get("equity"),
            "daily_pnl": status.get("daily_pnl"),
        }
