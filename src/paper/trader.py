"""
Paper Trading Simulator for ADA.
- Requires Multi-Timeframe agreement + near S/R + ATR filter before entry
- Better position sizing based on SL distance
- Daily loss limit and max open risk
- Natural Thai Telegram notifications
"""

import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import get_config
from src.signals.ada_signals import ADASignalGenerator
from src.signals.multi_tf import MultiTimeframeAnalyzer
from src.analysis.levels import SupportResistance
from src.data.ada_price import ADAPriceFetcher
from src.notify.telegram import TelegramNotifier


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STATE_FILE = DATA_DIR / "paper_state.json"


class PaperTrader:
    def __init__(self, initial_balance: float = 10000.0, notify: bool = True):
        self.initial_balance = initial_balance
        self.state = self._load_state()
        self.fetcher = ADAPriceFetcher()
        self.notifier = TelegramNotifier() if notify else None
        self.multi = MultiTimeframeAnalyzer()
        self.levels = SupportResistance()

    def _load_state(self) -> Dict[str, Any]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "balance_usdt": self.initial_balance,
            "position": None,
            "trades": [],
            "equity_curve": [{"ts": datetime.now(timezone.utc).isoformat(), "equity": self.initial_balance}],
            "daily_pnl": {},
            "daily_trades": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _today_key(self) -> str:
        return date.today().isoformat()

    def _trades_today(self) -> int:
        return self.state.get("daily_trades", {}).get(self._today_key(), 0)

    def _daily_pnl(self) -> float:
        return self.state.get("daily_pnl", {}).get(self._today_key(), 0.0)

    def _notify(self, text: str):
        if self.notifier and self.notifier.enabled:
            self.notifier.send(text)

    def _record_equity(self):
        equity = self.state["balance_usdt"]
        pos = self.state.get("position")
        if pos:
            try:
                price = self.fetcher.get_current_price()["price_usd"]
                if pos["side"] == "long":
                    equity += (price - pos["entry"]) * pos["qty"]
                else:
                    equity += (pos["entry"] - price) * pos["qty"]
            except Exception:
                pass
        self.state.setdefault("equity_curve", []).append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "equity": round(equity, 2),
        })
        self.state["equity_curve"] = self.state["equity_curve"][-500:]

    def status(self) -> Dict[str, Any]:
        pos = self.state.get("position")
        current_price = None
        unrealized = 0.0
        if pos:
            try:
                current_price = self.fetcher.get_current_price()["price_usd"]
                if pos["side"] == "long":
                    unrealized = (current_price - pos["entry"]) * pos["qty"]
                else:
                    unrealized = (pos["entry"] - current_price) * pos["qty"]
            except Exception:
                pass

        stats = self.performance_stats()
        return {
            "mode": "paper",
            "balance_usdt": round(self.state["balance_usdt"], 2),
            "position": pos,
            "current_price": current_price,
            "unrealized_pnl": round(unrealized, 2),
            "equity": round(self.state["balance_usdt"] + unrealized, 2),
            "total_trades": len(self.state.get("trades", [])),
            "trades_today": self._trades_today(),
            "daily_pnl": round(self._daily_pnl(), 2),
            "stats": stats,
        }

    def performance_stats(self) -> Dict[str, Any]:
        trades = self.state.get("trades", [])
        if not trades:
            return {"win_rate": 0, "profit_factor": 0, "max_drawdown": 0, "total_pnl": 0, "num_trades": 0}

        pnls = [t["pnl"] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf") if gross_profit > 0 else 0

        curve = [e["equity"] for e in self.state.get("equity_curve", [])]
        max_dd = 0.0
        peak = curve[0] if curve else self.initial_balance
        for eq in curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        return {
            "num_trades": len(trades),
            "win_rate": round(len(wins) / len(trades) * 100, 1),
            "profit_factor": profit_factor,
            "max_drawdown_pct": round(max_dd * 100, 2),
            "total_pnl": round(sum(pnls), 2),
            "avg_win": round(sum(wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0,
        }

    def _check_daily_loss_limit(self) -> bool:
        """Return True if daily loss limit is breached."""
        limit_pct = float(os.getenv("DAILY_LOSS_LIMIT_PCT", "3"))
        daily_pnl = self._daily_pnl()
        equity = self.state["balance_usdt"]
        if equity <= 0:
            return True
        loss_pct = abs(min(daily_pnl, 0)) / equity * 100
        return loss_pct >= limit_pct

    def check_sl_tp(self) -> Optional[Dict[str, Any]]:
        pos = self.state.get("position")
        if not pos or not pos.get("stop_loss") or not pos.get("take_profit"):
            return None

        try:
            price = self.fetcher.get_current_price()["price_usd"]
        except Exception:
            return None

        side = pos["side"]
        sl = pos["stop_loss"]
        tp = pos["take_profit"]

        hit = False
        reason = ""
        if side == "long":
            if price <= sl:
                hit, reason = True, "stop_loss"
            elif price >= tp:
                hit, reason = True, "take_profit"
        else:
            if price >= sl:
                hit, reason = True, "stop_loss"
            elif price <= tp:
                hit, reason = True, "take_profit"

        if hit:
            result = self.close_position(price, reason=reason)
            result["trigger"] = reason
            return result
        return None

    def _near_level(self, price: float, level: Optional[float], threshold_pct: float = 1.5) -> bool:
        if not level or level <= 0:
            return False
        return abs(price - level) / level * 100 <= threshold_pct

    def _passes_filters(self, signal: str, price: float, multi: Dict, levels: Dict) -> tuple[bool, str]:
        """Return (allowed, reason)."""
        # 1. Multi-TF agreement
        rec = multi.get("recommendation", "hold")
        if rec != signal:
            return False, f"Multi-TF recommendation is {rec}, not {signal}"

        agreement = multi.get("agreement", "0/0")
        try:
            agree_num = int(agreement.split("/")[0])
            if agree_num < 2:
                return False, "Not enough timeframe agreement (need >=2)"
        except Exception:
            return False, "Invalid agreement data"

        # 2. Near Support / Resistance
        nearest_sup = levels.get("nearest_support")
        nearest_res = levels.get("nearest_resistance")
        if signal == "buy":
            if not self._near_level(price, nearest_sup):
                return False, "Not near support for buy"
        elif signal == "sell":
            if not self._near_level(price, nearest_res):
                return False, "Not near resistance for sell"

        # 3. ATR / volatility filter (avoid quiet market)
        # Approximate using level distance or skip if no good data
        # For simplicity: require some distance between S/R
        if nearest_sup and nearest_res:
            range_pct = abs(nearest_res - nearest_sup) / price * 100
            if range_pct < 1.0:
                return False, "Market too quiet (S/R range < 1%)"

        return True, "All filters passed"

    def open_position(
        self,
        side: str,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        risk_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        if self.state.get("position"):
            return {"status": "error", "message": "Already have an open position."}

        if self._check_daily_loss_limit():
            return {"status": "error", "message": "Daily loss limit reached. Trading paused."}

        cfg = get_config()
        max_daily = int(os.getenv("MAX_DAILY_TRADES", "5"))
        if self._trades_today() >= max_daily:
            return {"status": "error", "message": f"Daily trade limit reached ({max_daily})"}

        # Max open risk (percentage of equity)
        max_risk_pct = float(os.getenv("MAX_OPEN_RISK_PCT", "5"))
        risk = min(risk_pct or cfg.MAX_POSITION_PCT, max_risk_pct)
        risk_amount = self.state["balance_usdt"] * (risk / 100.0)

        # Position sizing based on actual SL distance
        if stop_loss and abs(price - stop_loss) > 0:
            risk_per_unit = abs(price - stop_loss)
            qty = risk_amount / risk_per_unit
        else:
            # Fallback: use 2% of price as assumed risk
            risk_per_unit = price * 0.02
            qty = risk_amount / risk_per_unit if risk_per_unit > 0 else 0

        if qty <= 0:
            return {"status": "error", "message": "Invalid quantity"}

        cost = qty * price
        if cost > self.state["balance_usdt"] * 0.9:
            qty = (self.state["balance_usdt"] * 0.9) / price
            cost = qty * price

        self.state["balance_usdt"] -= cost
        self.state["position"] = {
            "side": side.lower(),
            "entry": price,
            "qty": round(qty, 6),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "opened_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state.setdefault("daily_trades", {})[self._today_key()] = self._trades_today() + 1
        self._record_equity()
        self._save_state()

        side_th = "ซื้อ" if side.lower() == "long" else "ขาย"
        msg = (
            f"เปิดตำแหน่งจำลอง (Paper)\n\n"
            f"ทำการ: {side_th} ADA\n"
            f"ราคาเข้า: {round(price, 6)} USDT\n"
            f"จำนวน: {round(qty, 2)} ADA\n"
            f"จุดขาดทุน: {stop_loss or '-'}\n"
            f"เป้าหมายกำไร: {take_profit or '-'}\n\n"
            f"ผ่านการกรอง Multi-TF + ใกล้แนวรับ/ต้าน\n"
            f"นี้เป็นการจำลองเทรดเท่านั้น ยังไม่ได้ใช้เงินจริง"
        )
        self._notify(msg)

        return {
            "status": "ok",
            "action": "open",
            "side": side,
            "entry": price,
            "qty": round(qty, 4),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "cost": round(cost, 2),
            "balance_after": round(self.state["balance_usdt"], 2),
        }

    def close_position(self, price: float, reason: str = "manual") -> Dict[str, Any]:
        pos = self.state.get("position")
        if not pos:
            return {"status": "error", "message": "No open position"}

        qty = pos["qty"]
        entry = pos["entry"]
        side = pos["side"]

        if side == "long":
            pnl = (price - entry) * qty
        else:
            pnl = (entry - price) * qty

        self.state["balance_usdt"] += qty * entry + pnl

        # Record daily PnL
        today = self._today_key()
        self.state.setdefault("daily_pnl", {})[today] = self._daily_pnl() + pnl

        trade = {
            "side": side,
            "entry": entry,
            "exit": price,
            "qty": qty,
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / (entry * qty)) * 100, 2) if entry * qty else 0,
            "reason": reason,
            "opened_at": pos["opened_at"],
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state["trades"].append(trade)
        self.state["position"] = None
        self._record_equity()
        self._save_state()

        reason_th = {
            "stop_loss": "ถึงจุดขาดทุน",
            "take_profit": "ถึงเป้าหมายกำไร",
            "opposite_signal": "สัญญาณตรงข้าม",
            "manual": "ปิดเอง",
        }.get(reason, reason)

        result_text = "กำไร" if pnl >= 0 else "ขาดทุน"
        side_th = "ซื้อ" if side == "long" else "ขาย"

        msg = (
            f"ปิดตำแหน่งจำลอง (Paper)\n\n"
            f"ทำการ: ปิด {side_th} ADA\n"
            f"เหตุผล: {reason_th}\n"
            f"ราคาปิด: {round(price, 6)} USDT\n"
            f"ผลลัพธ์: {result_text} {abs(trade['pnl'])} USDT ({trade['pnl_pct']}%)\n\n"
            f"นี้เป็นการจำลองเทรดเท่านั้น ยังไม่ได้ใช้เงินจริง"
        )
        self._notify(msg)

        return {
            "status": "ok",
            "action": "close",
            "reason": reason,
            "pnl": trade["pnl"],
            "pnl_pct": trade["pnl_pct"],
            "balance_after": round(self.state["balance_usdt"], 2),
            "trade": trade,
        }

    def auto_trade(self, interval: str = "1h") -> Dict[str, Any]:
        """Improved auto trade with multi-TF, S/R, and risk filters."""
        sl_tp_result = self.check_sl_tp()
        if sl_tp_result:
            return {"sl_tp_triggered": sl_tp_result, "paper_status": self.status()}

        if self._check_daily_loss_limit():
            return {
                "status": "paused",
                "message": "Daily loss limit reached. No new trades today.",
                "paper_status": self.status(),
            }

        # Multi-timeframe analysis
        multi = self.multi.analyze()
        if multi.get("status") != "ok":
            return multi

        recommendation = multi.get("recommendation", "hold")
        if recommendation not in ("buy", "sell"):
            return {
                "status": "ok",
                "message": "No multi-TF agreement for entry",
                "multi_tf": multi,
                "paper_status": self.status(),
            }

        # Levels
        levels = self.levels.find_levels(interval="1h")
        price = levels.get("current_price") or multi.get("timeframes", {}).get("1h", {}).get("price")
        if not price:
            return {"status": "error", "message": "Could not get current price"}

        # Filters
        allowed, reason = self._passes_filters(recommendation, price, multi, levels)
        if not allowed:
            return {
                "status": "ok",
                "message": f"Filters not passed: {reason}",
                "multi_tf": multi,
                "levels": levels,
                "paper_status": self.status(),
            }

        # Get SL/TP from 1h signal
        sig_1h = multi.get("timeframes", {}).get("1h", {})
        stop_loss = sig_1h.get("stop_loss")
        take_profit = sig_1h.get("take_profit")

        side = "long" if recommendation == "buy" else "short"
        action = self.open_position(side, price, stop_loss=stop_loss, take_profit=take_profit)

        return {
            "status": "ok",
            "multi_tf": multi,
            "levels": levels,
            "filter_reason": reason,
            "action": action,
            "paper_status": self.status(),
        }

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]


def main():
    trader = PaperTrader()
    print(json.dumps(trader.status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
