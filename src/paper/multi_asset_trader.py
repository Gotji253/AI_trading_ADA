"""
Multi-Asset Paper Trading with Risk Management
Supports: BTC, ETH, SOL, BNB, XRP
"""

import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config.assets import get_trading_assets, get_asset_info
from src.data.multi_asset_fetcher import MultiAssetFetcher
from src.analysis.enhanced_analyzer import EnhancedAnalyzer


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STATE_FILE = DATA_DIR / "multi_asset_state.json"


class MultiAssetPaperTrader:
    """Paper trading engine for multiple assets with risk controls."""

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.assets = get_trading_assets()
        self.fetcher = MultiAssetFetcher()
        self.analyzer = EnhancedAnalyzer()
        self.state = self._load_state()

        # Risk parameters
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE_PCT", "1.5"))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "4"))
        self.max_drawdown = float(os.getenv("MAX_DRAWDOWN_HARD_STOP_PCT", "12"))
        self.max_positions = int(os.getenv("MAX_OPEN_POSITIONS", "3"))
        self.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "5"))

    def _load_state(self) -> Dict[str, Any]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "balance": self.initial_balance,
            "positions": {},  # symbol -> position dict
            "trades": [],
            "equity_curve": [],
            "daily_pnl": {},
            "daily_trades": {},
            "quarantine": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _today(self) -> str:
        return date.today().isoformat()

    def _daily_pnl(self) -> float:
        return self.state.get("daily_pnl", {}).get(self._today(), 0.0)

    def _trades_today(self) -> int:
        return self.state.get("daily_trades", {}).get(self._today(), 0)

    def _open_positions_count(self) -> int:
        return len(self.state.get("positions", {}))

    def _calculate_equity(self) -> float:
        equity = self.state["balance"]
        prices = self.fetcher.get_all_prices()
        for sym, pos in self.state.get("positions", {}).items():
            price = prices.get(sym, pos["entry"])
            if pos["side"] == "long":
                equity += (price - pos["entry"]) * pos["qty"]
            else:
                equity += (pos["entry"] - price) * pos["qty"]
        return equity

    def _check_risk_limits(self) -> Optional[str]:
        """Return error message if risk limit hit, else None."""
        # Daily loss limit
        equity = self._calculate_equity()
        daily_pnl = self._daily_pnl()
        if equity > 0 and abs(min(daily_pnl, 0)) / equity * 100 >= self.daily_loss_limit:
            return f"Daily loss limit ({self.daily_loss_limit}%) reached"

        # Max drawdown
        peak = max([e["equity"] for e in self.state.get("equity_curve", [])] + [self.initial_balance])
        if peak > 0 and (peak - equity) / peak * 100 >= self.max_drawdown:
            self.state["quarantine"] = True
            self._save_state()
            return f"Max drawdown ({self.max_drawdown}%) hit - quarantine mode"

        # Max positions
        if self._open_positions_count() >= self.max_positions:
            return f"Max positions ({self.max_positions}) reached"

        # Daily trades
        if self._trades_today() >= self.max_daily_trades:
            return f"Daily trade limit ({self.max_daily_trades}) reached"

        if self.state.get("quarantine"):
            return "System in quarantine mode"

        return None

    def status(self) -> Dict[str, Any]:
        prices = self.fetcher.get_all_prices()
        equity = self._calculate_equity()
        return {
            "mode": "paper_multi",
            "balance": round(self.state["balance"], 2),
            "equity": round(equity, 2),
            "positions": self.state.get("positions", {}),
            "open_count": self._open_positions_count(),
            "prices": prices,
            "daily_pnl": round(self._daily_pnl(), 2),
            "trades_today": self._trades_today(),
            "total_trades": len(self.state.get("trades", [])),
            "quarantine": self.state.get("quarantine", False),
            "assets": self.assets,
        }

    def open_position(self, symbol: str, side: str, price: float,
                      stop_loss: Optional[float] = None,
                      take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Open a paper position for a symbol."""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"

        risk_error = self._check_risk_limits()
        if risk_error:
            return {"status": "error", "message": risk_error}

        if symbol in self.state.get("positions", {}):
            return {"status": "error", "message": f"Already have position in {symbol}"}

        # Position sizing based on risk
        risk_amount = self.state["balance"] * (self.risk_per_trade / 100)
        if stop_loss and abs(price - stop_loss) > 0:
            qty = risk_amount / abs(price - stop_loss)
        else:
            qty = risk_amount / (price * 0.02)  # default 2% risk

        cost = qty * price
        if cost > self.state["balance"] * 0.3:  # max 30% per position
            qty = (self.state["balance"] * 0.3) / price
            cost = qty * price

        if qty <= 0 or cost > self.state["balance"]:
            return {"status": "error", "message": "Insufficient balance or invalid qty"}

        self.state["balance"] -= cost
        self.state.setdefault("positions", {})[symbol] = {
            "side": side.lower(),
            "entry": price,
            "qty": round(qty, 6),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "opened_at": datetime.now(timezone.utc).isoformat(),
        }

        today = self._today()
        self.state.setdefault("daily_trades", {})[today] = self._trades_today() + 1
        self._record_equity()
        self._save_state()

        return {
            "status": "ok",
            "action": "open",
            "symbol": symbol,
            "side": side,
            "entry": price,
            "qty": round(qty, 4),
            "cost": round(cost, 2),
            "balance_after": round(self.state["balance"], 2),
        }

    def close_position(self, symbol: str, price: float, reason: str = "manual") -> Dict[str, Any]:
        """Close a paper position."""
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"

        positions = self.state.get("positions", {})
        if symbol not in positions:
            return {"status": "error", "message": f"No position in {symbol}"}

        pos = positions[symbol]
        qty = pos["qty"]
        entry = pos["entry"]
        side = pos["side"]

        if side == "long":
            pnl = (price - entry) * qty
        else:
            pnl = (entry - price) * qty

        self.state["balance"] += qty * entry + pnl

        today = self._today()
        self.state.setdefault("daily_pnl", {})[today] = self._daily_pnl() + pnl

        trade = {
            "symbol": symbol,
            "side": side,
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
            "reason": reason,
            "balance_after": round(self.state["balance"], 2),
        }

    def _record_equity(self):
        equity = self._calculate_equity()
        self.state.setdefault("equity_curve", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "equity": round(equity, 2),
        })
        self.state["equity_curve"] = self.state["equity_curve"][-500:]

    def check_sl_tp(self) -> List[Dict[str, Any]]:
        """Check stop-loss and take-profit for all positions."""
        results = []
        prices = self.fetcher.get_all_prices()

        for symbol, pos in list(self.state.get("positions", {}).items()):
            price = prices.get(symbol)
            if not price:
                continue

            sl = pos.get("stop_loss")
            tp = pos.get("take_profit")
            side = pos["side"]

            hit = None
            if side == "long":
                if sl and price <= sl:
                    hit = "stop_loss"
                elif tp and price >= tp:
                    hit = "take_profit"
            else:
                if sl and price >= sl:
                    hit = "stop_loss"
                elif tp and price <= tp:
                    hit = "take_profit"

            if hit:
                result = self.close_position(symbol, price, reason=hit)
                result["trigger"] = hit
                results.append(result)

        return results

    def run_cycle(self) -> Dict[str, Any]:
        """Run one trading cycle: check SL/TP, analyze, open positions."""
        # Check SL/TP first
        sl_tp_results = self.check_sl_tp()

        # Check risk limits
        risk_error = self._check_risk_limits()
        if risk_error:
            return {
                "status": "paused",
                "reason": risk_error,
                "sl_tp_triggered": sl_tp_results,
                "paper_status": self.status(),
            }

        # Analyze all assets
        data = self.fetcher.get_multi_asset_data(interval="1h", limit=100)
        signals = []

        for symbol, df in data.items():
            if symbol in self.state.get("positions", {}):
                continue  # already have position
            try:
                analysis = self.analyzer.analyze(df)
                if analysis.get("quality") == "high" and analysis.get("signal") in ("buy", "sell"):
                    signals.append({
                        "symbol": symbol,
                        "signal": analysis["signal"],
                        "price": analysis.get("price"),
                        "setup": analysis.get("setup_type"),
                    })
            except Exception:
                continue

        # Open positions for signals (up to max)
        actions = []
        for sig in signals[:self.max_positions - self._open_positions_count()]:
            side = "long" if sig["signal"] == "buy" else "short"
            price = sig.get("price")
            if not price:
                continue

            # Simple SL/TP based on ATR-like percentage
            sl_pct = 2.0
            tp_pct = 4.0
            if side == "long":
                sl = price * (1 - sl_pct / 100)
                tp = price * (1 + tp_pct / 100)
            else:
                sl = price * (1 + sl_pct / 100)
                tp = price * (1 - tp_pct / 100)

            result = self.open_position(sig["symbol"], side, price, sl, tp)
            actions.append(result)

        return {
            "status": "ok",
            "sl_tp_triggered": sl_tp_results,
            "signals_found": len(signals),
            "actions": actions,
            "paper_status": self.status(),
        }

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]

    def reset(self):
        """Reset paper trading state."""
        self.state = {
            "balance": self.initial_balance,
            "positions": {},
            "trades": [],
            "equity_curve": [],
            "daily_pnl": {},
            "daily_trades": {},
            "quarantine": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save_state()
        return {"status": "reset", "balance": self.initial_balance}
