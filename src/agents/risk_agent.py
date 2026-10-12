"""
Risk_Agent — Improved
- Risk per trade: 1-2% of equity
- Daily loss limit: 3-5%
- Max drawdown hard stop: 10-15%
- Max open risk cap
- Volatility-based size adjustment
- Consecutive loss cooldown
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.paper.trader import PaperTrader
from src.config import get_config


class RiskAgent:
    def __init__(self):
        self.trader = PaperTrader(notify=False)
        self.cfg = get_config()

        self.risk_per_trade_pct = float(os.getenv("RISK_PER_TRADE_PCT", "1.5"))
        self.daily_loss_limit_pct = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "4"))
        self.max_drawdown_pct = float(os.getenv("MAX_DRAWDOWN_HARD_STOP_PCT", "12"))
        self.max_open_risk_pct = float(os.getenv("MAX_OPEN_RISK_PCT", "3.0"))
        self.consecutive_loss_limit = int(os.getenv("CONSECUTIVE_LOSS_LIMIT", "3"))
        self.cooldown_minutes = int(os.getenv("LOSS_COOLDOWN_MINUTES", "30"))

        self._last_loss_time: Optional[datetime] = None
        self._consecutive_losses = 0

    def evaluate(
        self,
        signal: str,
        price: float,
        proposed_sl: Optional[float] = None,
        atr_pct: Optional[float] = None,
        regime: Optional[str] = None,
    ) -> Dict[str, Any]:
        """ตรวจสอบความเสี่ยงและคำนวณขนาดไม้"""
        status = self.trader.status()
        equity = status.get("equity") or status.get("balance_usdt", 0)
        daily_pnl = status.get("daily_pnl", 0)
        stats = status.get("stats", {})
        max_dd = stats.get("max_drawdown_pct", 0)

        # 1. Daily loss limit
        if equity > 0 and abs(min(daily_pnl, 0)) / equity * 100 >= self.daily_loss_limit_pct:
            return self._reject(f"Daily loss limit reached ({self.daily_loss_limit_pct}%)")

        # 2. Max Drawdown Hard Stop
        if max_dd >= self.max_drawdown_pct:
            return self._reject(
                f"Max drawdown hard stop ({self.max_drawdown_pct}%)",
                hard_stop=True,
            )

        # 3. Already have position
        if status.get("position"):
            return self._reject("Already have an open position")

        # 4. Consecutive loss cooldown
        if self._in_cooldown():
            return self._reject(f"Cooldown active after {self._consecutive_losses} consecutive losses")

        # 5. Calculate base risk amount
        risk_amount = equity * (self.risk_per_trade_pct / 100.0)

        # 6. Volatility adjustment
        vol_multiplier = 1.0
        if atr_pct is not None:
            if atr_pct > 2.5:
                vol_multiplier = 0.5  # High volatility → reduce size
            elif atr_pct > 1.5:
                vol_multiplier = 0.75

        if regime == "high_volatility":
            vol_multiplier = min(vol_multiplier, 0.6)

        risk_amount *= vol_multiplier

        # 7. Max open risk cap
        max_allowed_risk = equity * (self.max_open_risk_pct / 100.0)
        risk_amount = min(risk_amount, max_allowed_risk)

        # 8. Position sizing
        if proposed_sl and abs(price - proposed_sl) > 0:
            risk_per_unit = abs(price - proposed_sl)
        else:
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
            "risk_pct": round(risk_amount / equity * 100, 2) if equity else 0,
            "vol_multiplier": vol_multiplier,
            "current_equity": equity,
            "daily_pnl": daily_pnl,
            "max_drawdown_pct": max_dd,
            "consecutive_losses": self._consecutive_losses,
            "hard_stop": False,
        }

    def record_trade_result(self, pnl: float):
        """เรียกหลังปิดตำแหน่งเพื่ออัปเดต consecutive loss"""
        if pnl < 0:
            self._consecutive_losses += 1
            self._last_loss_time = datetime.now(timezone.utc)
        else:
            self._consecutive_losses = 0
            self._last_loss_time = None

    def _in_cooldown(self) -> bool:
        if self._consecutive_losses < self.consecutive_loss_limit:
            return False
        if not self._last_loss_time:
            return False
        elapsed = (datetime.now(timezone.utc) - self._last_loss_time).total_seconds() / 60
        return elapsed < self.cooldown_minutes

    def _reject(self, reason: str, hard_stop: bool = False) -> Dict[str, Any]:
        return {
            "agent": "risk",
            "approved": False,
            "reason": reason,
            "max_qty": 0,
            "hard_stop": hard_stop,
            "consecutive_losses": self._consecutive_losses,
        }
