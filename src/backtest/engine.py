"""
Backtest Engine for ADA Multi-Timeframe Strategy.
Simulates Alpha_Agent logic on historical data.
Supports simple walk-forward style evaluation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import pandas as pd
import numpy as np

from src.data.ada_price import ADAPriceFetcher
from src.signals.ada_signals import ADASignalGenerator


class MultiTFBacktester:
    INTERVALS = ["15m", "1h", "4h"]

    def __init__(self, source: str = "binance"):
        self.fetcher = ADAPriceFetcher(preferred_source=source)
        self.signal_gen = ADASignalGenerator(source=source)

    def fetch_aligned_data(self, base_interval: str = "15m", limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV for all timeframes and align to base."""
        data = {}
        for tf in self.INTERVALS:
            df = self.fetcher.get_ohlcv(tf, limit=min(limit, 1000))
            if not df.empty:
                df = self.fetcher._add_indicators(df) if hasattr(self.fetcher, "_add_indicators") else df
                data[tf] = df
        return data

    def _classify_regime(self, df: pd.DataFrame, window: int = 50) -> str:
        """Simple regime classification based on price trend and volatility."""
        if len(df) < window:
            return "unknown"
        recent = df["close"].tail(window)
        returns = recent.pct_change().dropna()
        trend = (recent.iloc[-1] / recent.iloc[0] - 1) * 100
        vol = returns.std() * 100

        if trend > 3 and vol < 5:
            return "bullish"
        elif trend < -3 and vol < 5:
            return "bearish"
        elif abs(trend) < 2 or vol > 4:
            return "sideways"
        return "mixed"

    def simulate(
        self,
        data: Dict[str, pd.DataFrame],
        initial_balance: float = 10000.0,
        risk_pct: float = 2.0,
        lookback: int = 80,
    ) -> Dict[str, Any]:
        """Run bar-by-bar simulation on aligned data (using 15m as base)."""
        base = data.get("15m")
        if base is None or base.empty:
            return {"status": "error", "message": "No 15m data"}

        balance = initial_balance
        position = None  # {side, entry, qty, sl, tp, open_idx}
        trades: List[Dict] = []
        equity_curve = []

        # Iterate over 15m bars (skip early bars for lookback)
        for i in range(lookback, len(base)):
            ts = base.index[i]
            price = float(base["close"].iloc[i])

            # Build synthetic multi-TF snapshot at this point
            multi_result = self._eval_multi_at(data, i, lookback)

            recommendation = multi_result.get("recommendation", "hold")
            equity_curve.append({"ts": ts.isoformat(), "equity": round(balance, 2), "price": price})

            # Check exits first
            if position:
                exit_price = price
                hit = False
                reason = ""
                if position["side"] == "long":
                    if position.get("sl") and price <= position["sl"]:
                        hit, reason = True, "sl"
                    elif position.get("tp") and price >= position["tp"]:
                        hit, reason = True, "tp"
                else:
                    if position.get("sl") and price >= position["sl"]:
                        hit, reason = True, "sl"
                    elif position.get("tp") and price <= position["tp"]:
                        hit, reason = True, "tp"

                # Also exit on opposite signal
                if not hit and ((recommendation == "sell" and position["side"] == "long") or
                                (recommendation == "buy" and position["side"] == "short")):
                    hit, reason = True, "signal"

                if hit:
                    pnl = (exit_price - position["entry"]) * position["qty"] if position["side"] == "long" else \
                          (position["entry"] - exit_price) * position["qty"]
                    balance += position["qty"] * position["entry"] + pnl
                    trades.append({
                        "side": position["side"],
                        "entry": position["entry"],
                        "exit": exit_price,
                        "pnl": round(pnl, 2),
                        "reason": reason,
                        "regime": position.get("regime"),
                        "open_ts": position.get("open_ts"),
                        "close_ts": ts.isoformat(),
                    })
                    position = None

            # Open new position if signal and no position
            if not position and recommendation in ("buy", "sell"):
                regime = self._classify_regime(base.iloc[:i+1])
                risk_amount = balance * (risk_pct / 100.0)
                # Approximate SL distance (2% default)
                sl_dist = price * 0.02
                qty = risk_amount / sl_dist if sl_dist > 0 else 0
                if qty > 0:
                    side = "long" if recommendation == "buy" else "short"
                    sl = price - sl_dist if side == "long" else price + sl_dist
                    tp = price + sl_dist * 2 if side == "long" else price - sl_dist * 2
                    cost = qty * price
                    if cost <= balance * 0.95:
                        balance -= cost
                        position = {
                            "side": side,
                            "entry": price,
                            "qty": round(qty, 6),
                            "sl": sl,
                            "tp": tp,
                            "regime": regime,
                            "open_ts": ts.isoformat(),
                        }

        # Close any open position at end
        if position and len(base) > 0:
            final_price = float(base["close"].iloc[-1])
            pnl = (final_price - position["entry"]) * position["qty"] if position["side"] == "long" else \
                  (position["entry"] - final_price) * position["qty"]
            balance += position["qty"] * position["entry"] + pnl
            trades.append({
                "side": position["side"],
                "entry": position["entry"],
                "exit": final_price,
                "pnl": round(pnl, 2),
                "reason": "end",
                "regime": position.get("regime"),
                "open_ts": position.get("open_ts"),
                "close_ts": base.index[-1].isoformat(),
            })

        return self._summarize(trades, equity_curve, initial_balance, balance)

    def _eval_multi_at(self, data: Dict[str, pd.DataFrame], idx: int, lookback: int) -> Dict[str, Any]:
        """Approximate multi-TF evaluation at a given 15m index."""
        # For simplicity in this version: use the live generator style but on sliced data
        # In production this would recompute signals on historical slices
        scores = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        signals = []

        for tf in self.INTERVALS:
            df = data.get(tf)
            if df is None or len(df) < lookback:
                continue
            # Map index roughly (this is approximate)
            # In real implementation, resample or find corresponding bar
            slice_df = df.tail(lookback) if idx >= len(df) else df.iloc[max(0, idx-lookback):idx+1]
            if len(slice_df) < 30:
                continue
            # Simple rule based on RSI / EMA for demo
            last = slice_df.iloc[-1]
            rsi = last.get("rsi_14", 50)
            ema20 = last.get("ema_20", last["close"])
            close = last["close"]

            if rsi < 35 and close > ema20:
                sig, conf = "buy", 0.6
            elif rsi > 65 and close < ema20:
                sig, conf = "sell", 0.6
            else:
                sig, conf = "hold", 0.3

            scores[sig] += conf
            signals.append(sig)

        consensus = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        strength = scores[consensus] / total
        agreement = signals.count(consensus) if signals else 0

        rec = "hold"
        if agreement >= 2 and strength >= 0.5:
            rec = consensus

        return {
            "recommendation": rec,
            "consensus": consensus,
            "agreement": agreement,
            "strength": round(strength, 2),
        }

    def _summarize(self, trades: List[Dict], equity: List[Dict], initial: float, final: float) -> Dict[str, Any]:
        if not trades:
            return {
                "status": "ok",
                "num_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "final_balance": round(final, 2),
                "return_pct": 0,
            }

        pnls = [t["pnl"] for t in trades]
        wins = [p for p in pnls if p > 0]
        by_regime: Dict[str, List[float]] = {}
        for t in trades:
            r = t.get("regime", "unknown")
            by_regime.setdefault(r, []).append(t["pnl"])

        regime_stats = {}
        for r, ps in by_regime.items():
            regime_stats[r] = {
                "trades": len(ps),
                "pnl": round(sum(ps), 2),
                "win_rate": round(len([p for p in ps if p > 0]) / len(ps) * 100, 1) if ps else 0,
            }

        return {
            "status": "ok",
            "num_trades": len(trades),
            "total_pnl": round(sum(pnls), 2),
            "win_rate": round(len(wins) / len(trades) * 100, 1),
            "avg_pnl": round(np.mean(pnls), 2),
            "final_balance": round(final, 2),
            "return_pct": round((final / initial - 1) * 100, 2),
            "by_regime": regime_stats,
            "trades": trades[-20:],  # last 20 for brevity
            "equity_sample": equity[-50:],
        }

    def walk_forward(
        self,
        total_bars: int = 800,
        train_size: int = 400,
        test_size: int = 200,
        step: int = 100,
    ) -> Dict[str, Any]:
        """Simple walk-forward: evaluate on sequential out-of-sample windows."""
        data = self.fetch_aligned_data(limit=total_bars)
        base = data.get("15m")
        if base is None or len(base) < train_size + test_size:
            return {"status": "error", "message": "Not enough data for walk-forward"}

        results = []
        start = 0
        while start + train_size + test_size <= len(base):
            # In this version we don't re-optimize; just evaluate on test window
            test_start = start + train_size
            test_end = test_start + test_size
            # Slice data approximately
            sliced = {tf: df.iloc[max(0, test_start-100):test_end] for tf, df in data.items()}
            sim = self.simulate(sliced, lookback=60)
            results.append({
                "window": f"{test_start}-{test_end}",
                "return_pct": sim.get("return_pct", 0),
                "num_trades": sim.get("num_trades", 0),
                "win_rate": sim.get("win_rate", 0),
                "by_regime": sim.get("by_regime", {}),
            })
            start += step

        avg_return = round(np.mean([r["return_pct"] for r in results]), 2) if results else 0
        return {
            "status": "ok",
            "windows": results,
            "avg_return_pct": avg_return,
            "num_windows": len(results),
        }


def main():
    bt = MultiTFBacktester()
    print("Fetching data and running simple backtest...")
    data = bt.fetch_aligned_data(limit=500)
    result = bt.simulate(data)
    print(result)


if __name__ == "__main__":
    main()
