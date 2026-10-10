"""
Paper Trading Simulator for ADA (improved).
Natural Thai Telegram notifications.
"""

import json
import os
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import get_config
from src.signals.ada_signals import ADASignalGenerator
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
            "daily_trades": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _today_key(self) -> str:
        return date.today().isoformat()

    def _trades_today(self) -> int:
        return self.state.get("daily_trades", {}).get(self._today_key(), 0)

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

        cfg = get_config()
        max_daily = int(os.getenv("MAX_DAILY_TRADES", "5"))
        if self._trades_today() >= max_daily:
            return {"status": "error", "message": f"Daily trade limit reached ({max_daily})"}

        risk = risk_pct if risk_pct is not None else cfg.MAX_POSITION_PCT
        risk_amount = self.state["balance_usdt"] * (risk / 100.0)

        if stop_loss and abs(price - stop_loss) > 0:
            risk_per_unit = abs(price - stop_loss)
            qty = risk_amount / risk_per_unit
        else:
            qty = risk_amount / price if price > 0 else 0

        if qty <= 0:
            return {"status": "error", "message": "Invalid quantity"}

        cost = qty * price
        if cost > self.state["balance_usdt"] * 0.95:
            qty = (self.state["balance_usdt"] * 0.95) / price
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
            f"ราคาเข้า: {price} USDT\n"
            f"จำนวน: {round(qty, 2)} ADA\n"
            f"จุดขาดทุน: {stop_loss or '-'}\n"
            f"เป้าหมายกำไร: {take_profit or '-'}\n\n"
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
            f"ราคาปิด: {price} USDT\n"
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
        sl_tp_result = self.check_sl_tp()
        if sl_tp_result:
            return {"sl_tp_triggered": sl_tp_result, "paper_status": self.status()}

        gen = ADASignalGenerator()
        sig = gen.generate(interval=interval)
        if sig.get("status") != "ok":
            return sig

        price = sig["price"]
        signal = sig["signal"]
        result = {"signal": sig, "action": None}

        pos = self.state.get("position")

        if signal in ("buy", "sell") and not pos and sig.get("confidence", 0) >= 0.4:
            side = "long" if signal == "buy" else "short"
            result["action"] = self.open_position(
                side, price,
                stop_loss=sig.get("stop_loss"),
                take_profit=sig.get("take_profit"),
            )
        elif pos and ((signal == "sell" and pos["side"] == "long") or (signal == "buy" and pos["side"] == "short")):
            result["action"] = self.close_position(price, reason="opposite_signal")
        else:
            result["action"] = {"status": "ok", "message": "No action"}

        result["paper_status"] = self.status()
        return result

    def history(self, limit: int = 20) -> List[Dict]:
        return self.state.get("trades", [])[-limit:]


def main():
    trader = PaperTrader()
    print(json.dumps(trader.status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
