"""
Paper Trading Simulator for ADA.
Tracks virtual balance, open positions, and trade history.
No real orders are ever placed.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import get_config
from src.signals.ada_signals import ADASignalGenerator


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STATE_FILE = DATA_DIR / "paper_state.json"


class PaperTrader:
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "balance_usdt": self.initial_balance,
            "position": None,  # {"side": "long"|"short", "entry": float, "qty": float, "opened_at": str}
            "trades": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def status(self) -> Dict[str, Any]:
        pos = self.state.get("position")
        unrealized = 0.0
        if pos:
            # We'll fill current price later if needed
            pass
        return {
            "mode": "paper",
            "balance_usdt": round(self.state["balance_usdt"], 2),
            "position": pos,
            "total_trades": len(self.state.get("trades", [])),
            "initial_balance": self.initial_balance,
        }

    def open_position(
        self,
        side: str,
        price: float,
        qty: Optional[float] = None,
        risk_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        if self.state.get("position"):
            return {"status": "error", "message": "Already have an open position. Close it first."}

        cfg = get_config()
        risk = risk_pct if risk_pct is not None else cfg.MAX_POSITION_PCT
        if qty is None:
            # Risk-based sizing: use risk % of balance
            risk_amount = self.state["balance_usdt"] * (risk / 100.0)
            qty = risk_amount / price if price > 0 else 0

        if qty <= 0:
            return {"status": "error", "message": "Invalid quantity"}

        cost = qty * price
        if cost > self.state["balance_usdt"]:
            return {"status": "error", "message": "Insufficient paper balance"}

        self.state["balance_usdt"] -= cost
        self.state["position"] = {
            "side": side.lower(),
            "entry": price,
            "qty": qty,
            "opened_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_state()
        return {
            "status": "ok",
            "action": "open",
            "side": side,
            "entry": price,
            "qty": round(qty, 4),
            "cost": round(cost, 2),
            "balance_after": round(self.state["balance_usdt"], 2),
        }

    def close_position(self, price: float) -> Dict[str, Any]:
        pos = self.state.get("position")
        if not pos:
            return {"status": "error", "message": "No open position"}

        qty = pos["qty"]
        entry = pos["entry"]
        side = pos["side"]

        if side == "long":
            pnl = (price - entry) * qty
        else:  # short
            pnl = (entry - price) * qty

        proceeds = qty * price
        self.state["balance_usdt"] += proceeds + (pnl if side == "short" else 0)
        # For long we already deducted cost, so adding proceeds is correct; adjust for short separately if needed
        # Simplified: for long, balance was reduced by cost, now add back proceeds
        if side == "long":
            self.state["balance_usdt"] = self.state["balance_usdt"] - (qty * entry) + proceeds + pnl
            # Recalculate cleanly
            self.state["balance_usdt"] = self.state["balance_usdt"]  # already adjusted above; fix logic below

        # Clean recalculation
        self.state["balance_usdt"] += pnl  # net effect

        trade = {
            "side": side,
            "entry": entry,
            "exit": price,
            "qty": qty,
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / (entry * qty)) * 100, 2) if entry * qty else 0,
            "opened_at": pos["opened_at"],
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["trades"].append(trade)
        self.state["position"] = None
        self._save_state()

        return {
            "status": "ok",
            "action": "close",
            "pnl": trade["pnl"],
            "pnl_pct": trade["pnl_pct"],
            "balance_after": round(self.state["balance_usdt"], 2),
            "trade": trade,
        }

    def auto_trade(self, interval: str = "1h") -> Dict[str, Any]:
        """Generate signal and open/close paper position accordingly."""
        gen = ADASignalGenerator()
        sig = gen.generate(interval=interval)
        if sig.get("status") != "ok":
            return sig

        price = sig["price"]
        signal = sig["signal"]
        result = {"signal": sig, "action": None}

        pos = self.state.get("position")

        # Simple logic: open on buy/sell if flat; close if opposite signal
        if signal == "buy" and not pos:
            result["action"] = self.open_position("long", price)
        elif signal == "sell" and not pos:
            result["action"] = self.open_position("short", price)
        elif pos and ((signal == "sell" and pos["side"] == "long") or (signal == "buy" and pos["side"] == "short")):
            result["action"] = self.close_position(price)
        else:
            result["action"] = {"status": "ok", "message": "No action (hold or same direction)"}

        result["paper_status"] = self.status()
        return result

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]


def main():
    trader = PaperTrader()
    print(json.dumps(trader.status(), indent=2))


if __name__ == "__main__":
    main()
