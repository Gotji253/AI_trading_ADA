"""
Paper Trading for Ensemble Donchian + ADX + Vol Filter Strategy
"""

import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.assets_config import get_trading_assets
from src.data.multi_asset_fetcher import MultiAssetFetcher
from src.strategies.ensemble_donchian import EnsembleDonchianStrategy


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STATE_FILE = DATA_DIR / "ensemble_paper_state.json"


class EnsemblePaperTrader:
    """Paper trading for Ensemble Donchian strategy."""

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.assets = get_trading_assets()
        self.fetcher = MultiAssetFetcher()
        self.strategy = EnsembleDonchianStrategy()
        self.state = self._load_state()

        # Risk parameters
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
        self.max_positions = int(os.getenv("MAX_OPEN_POSITIONS", "2"))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "3"))

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
            "daily_pnl": {},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _today(self) -> str:
        return date.today().isoformat()

    def _daily_pnl(self) -> float:
        return self.state.get("daily_pnl", {}).get(self._today(), 0.0)

    def _calculate_equity(self) -> float:
        equity = self.state["balance"]
        try:
            prices = self.fetcher.get_all_prices()
        except Exception:
            prices = {}
        for sym, pos in self.state.get("positions", {}).items():
            price = prices.get(sym, pos["entry"])
            equity += (price - pos["entry"]) * pos["qty"]
        return equity

    def status(self) -> Dict[str, Any]:
        try:
            prices = self.fetcher.get_all_prices()
        except Exception:
            prices = {}
        equity = self._calculate_equity()
        return {
            "mode": "ensemble_paper",
            "balance": round(self.state["balance"], 2),
            "equity": round(equity, 2),
            "positions": self.state.get("positions", {}),
            "open_count": len(self.state.get("positions", {})),
            "prices": prices,
            "daily_pnl": round(self._daily_pnl(), 2),
            "total_trades": len(self.state.get("trades", [])),
            "started_at": self.state.get("started_at"),
            "assets": self.assets,
        }

    def run_cycle(self) -> Dict[str, Any]:
        """Run one trading cycle."""
        # Check daily loss limit
        equity = self._calculate_equity()
        daily_pnl = self._daily_pnl()
        if equity > 0 and abs(min(daily_pnl, 0)) / equity * 100 >= self.daily_loss_limit:
            return {"status": "paused", "reason": "daily loss limit reached"}

        # Get data for all assets
        try:
            data = self.fetcher.get_multi_asset_data(interval="1d", limit=100)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        actions = []
        signals = []

        for symbol, df in data.items():
            analysis = self.strategy.analyze(df)
            signals.append({"symbol": symbol, **analysis})

            # Check exit for existing position
            if symbol in self.state.get("positions", {}):
                if analysis.get("signal") == "sell":
                    price = analysis.get("price", 0)
                    if price > 0:
                        result = self._close_position(symbol, price, "signal")
                        actions.append(result)

            # Check entry for new position
            elif analysis.get("signal") == "buy":
                if len(self.state.get("positions", {})) < self.max_positions:
                    price = analysis.get("price", 0)
                    if price > 0:
                        result = self._open_position(symbol, price, analysis)
                        actions.append(result)

        return {
            "status": "ok",
            "signals": signals,
            "actions": actions,
            "paper_status": self.status(),
        }

    def _open_position(self, symbol: str, price: float, analysis: Dict) -> Dict[str, Any]:
        risk_amount = self.state["balance"] * (self.risk_per_trade / 100)
        # Simple position sizing (2% stop assumed)
        qty = risk_amount / (price * 0.02)
        cost = qty * price

        if cost > self.state["balance"] * 0.3:
            qty = (self.state["balance"] * 0.3) / price
            cost = qty * price

        if cost > self.state["balance"]:
            return {"status": "error", "message": "insufficient balance"}

        self.state["balance"] -= cost
        self.state.setdefault("positions", {})[symbol] = {
            "entry": price,
            "qty": round(qty, 6),
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "adx": analysis.get("adx"),
            "vol_regime": analysis.get("vol_regime"),
        }
        self._record_equity()
        self._save_state()

        return {
            "status": "ok",
            "action": "open",
            "symbol": symbol,
            "entry": price,
            "qty": round(qty, 4),
            "cost": round(cost, 2),
        }

    def _close_position(self, symbol: str, price: float, reason: str) -> Dict[str, Any]:
        pos = self.state.get("positions", {}).get(symbol)
        if not pos:
            return {"status": "error", "message": "no position"}

        qty = pos["qty"]
        entry = pos["entry"]
        pnl = (price - entry) * qty

        self.state["balance"] += qty * entry + pnl

        today = self._today()
        self.state.setdefault("daily_pnl", {})[today] = self._daily_pnl() + pnl

        trade = {
            "symbol": symbol,
            "entry": entry,
            "exit": price,
            "qty": qty,
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / (entry * qty)) * 100, 2) if entry * qty else 0,
            "reason": reason,
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["trades"].append(trade)
        del self.state["positions"][symbol]

        self._record_equity()
        self._save_state()

        return {
            "status": "ok",
            "action": "close",
            "symbol": symbol,
            "pnl": trade["pnl"],
            "pnl_pct": trade["pnl_pct"],
        }

    def _record_equity(self):
        equity = self._calculate_equity()
        self.state.setdefault("equity_curve", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "equity": round(equity, 2),
        })
        self.state["equity_curve"] = self.state["equity_curve"][-500:]

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]

    def reset(self):
        self.state = {
            "balance": self.initial_balance,
            "positions": {},
            "trades": [],
            "equity_curve": [],
            "daily_pnl": {},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_state()
        return {"status": "reset", "balance": self.initial_balance}
