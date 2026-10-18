"""
Paper Trading for Gold (PAXG) Breakout Strategy
"""

import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.data.multi_asset_fetcher import MultiAssetFetcher
from src.strategies.gold_breakout import GoldBreakoutStrategy


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STATE_FILE = DATA_DIR / "gold_paper_state.json"


class GoldPaperTrader:
    """Paper trading for Gold breakout strategy."""

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.symbol = "PAXGUSDT"
        self.fetcher = MultiAssetFetcher()
        self.strategy = GoldBreakoutStrategy()
        self.state = self._load_state()

        # Risk parameters
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
        self.max_positions = 1  # Only 1 position for Gold

    def _load_state(self) -> Dict[str, Any]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "balance": self.initial_balance,
            "positions": {},
            "trades": [],
            "equity_curve": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _calculate_equity(self) -> float:
        equity = self.state["balance"]
        try:
            df = self.fetcher.get_ohlcv(self.symbol, "1h", 1)
            if df is not None and not df.empty:
                price = float(df["close"].iloc[-1])
                for sym, pos in self.state.get("positions", {}).items():
                    equity += (price - pos["entry"]) * pos["qty"]
        except Exception:
            pass
        return equity

    def status(self) -> Dict[str, Any]:
        equity = self._calculate_equity()
        return {
            "mode": "gold_paper",
            "symbol": self.symbol,
            "balance": round(self.state["balance"], 2),
            "equity": round(equity, 2),
            "positions": self.state.get("positions", {}),
            "open_count": len(self.state.get("positions", {})),
            "total_trades": len(self.state.get("trades", [])),
            "started_at": self.state.get("started_at"),
        }

    def run_cycle(self) -> Dict[str, Any]:
        """Run one trading cycle."""
        # Get data
        try:
            df_1h = self.fetcher.get_ohlcv(self.symbol, "1h", 100)
            df_4h = self.fetcher.get_ohlcv(self.symbol, "4h", 100)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if df_1h is None or df_4h is None:
            return {"status": "error", "message": "failed to fetch data"}

        signal = self.strategy.get_signal(df_1h, df_4h)
        actions = []

        # Check existing position
        if self.symbol in self.state.get("positions", {}):
            pos = self.state["positions"][self.symbol]
            price = signal.get("price", 0)

            # Check SL/TP
            if price > 0:
                if price <= pos.get("sl", 0):
                    result = self._close_position(price, "stop_loss")
                    actions.append(result)
                elif price >= pos.get("tp", float("inf")):
                    result = self._close_position(price, "take_profit")
                    actions.append(result)

        # Check new entry
        elif signal.get("signal") == "buy":
            if len(self.state.get("positions", {})) < self.max_positions:
                price = signal.get("price", 0)
                if price > 0:
                    result = self._open_position(price, signal)
                    actions.append(result)

        return {
            "status": "ok",
            "signal": signal,
            "actions": actions,
            "paper_status": self.status(),
        }

    def _open_position(self, price: float, signal: Dict) -> Dict[str, Any]:
        risk_amount = self.state["balance"] * (self.risk_per_trade / 100)
        sl_distance = price * (self.strategy.sl_pct / 100)
        qty = risk_amount / sl_distance if sl_distance > 0 else 0
        cost = qty * price

        if cost > self.state["balance"] * 0.5:
            qty = (self.state["balance"] * 0.5) / price
            cost = qty * price

        if cost > self.state["balance"]:
            return {"status": "error", "message": "insufficient balance"}

        self.state["balance"] -= cost
        self.state.setdefault("positions", {})[self.symbol] = {
            "entry": price,
            "qty": round(qty, 6),
            "sl": signal.get("sl"),
            "tp": signal.get("tp"),
            "opened_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_state()

        return {
            "status": "ok",
            "action": "open",
            "symbol": self.symbol,
            "entry": price,
            "qty": round(qty, 4),
            "sl": signal.get("sl"),
            "tp": signal.get("tp"),
        }

    def _close_position(self, price: float, reason: str) -> Dict[str, Any]:
        pos = self.state.get("positions", {}).get(self.symbol)
        if not pos:
            return {"status": "error", "message": "no position"}

        qty = pos["qty"]
        entry = pos["entry"]
        pnl = (price - entry) * qty

        self.state["balance"] += qty * entry + pnl

        trade = {
            "symbol": self.symbol,
            "entry": entry,
            "exit": price,
            "qty": qty,
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / (entry * qty)) * 100, 2) if entry * qty else 0,
            "reason": reason,
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["trades"].append(trade)
        del self.state["positions"][self.symbol]
        self._save_state()

        return {
            "status": "ok",
            "action": "close",
            "symbol": self.symbol,
            "pnl": trade["pnl"],
            "pnl_pct": trade["pnl_pct"],
            "reason": reason,
        }

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]

    def reset(self):
        self.state = {
            "balance": self.initial_balance,
            "positions": {},
            "trades": [],
            "equity_curve": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_state()
        return {"status": "reset", "balance": self.initial_balance}
