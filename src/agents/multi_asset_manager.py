"""
Multi-Asset Manager Agent
Handles BTC, ETH, SOL, BNB, XRP
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.config.assets import get_trading_assets, get_asset_info
from src.data.multi_asset_fetcher import MultiAssetFetcher
from src.analysis.enhanced_analyzer import EnhancedAnalyzer


class MultiAssetManager:
    """Manager for multi-asset trading."""

    def __init__(self):
        self.assets = get_trading_assets()
        self.fetcher = MultiAssetFetcher()
        self.analyzer = EnhancedAnalyzer()
        self.trading_enabled = True
        self.quarantine_mode = False
        self.positions: Dict[str, Optional[Dict]] = {a: None for a in self.assets}
        self.equity = float(os.getenv("INITIAL_EQUITY", "10000"))
        self.daily_pnl = 0.0

    def get_status(self) -> Dict[str, Any]:
        """Get current status of all assets."""
        prices = self.fetcher.get_all_prices()
        open_positions = sum(1 for p in self.positions.values() if p is not None)

        return {
            "status": "ok",
            "assets": self.assets,
            "prices": prices,
            "open_positions": open_positions,
            "equity": self.equity,
            "daily_pnl": self.daily_pnl,
            "trading_enabled": self.trading_enabled,
            "quarantine_mode": self.quarantine_mode,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all assets and return signals."""
        if not self.trading_enabled or self.quarantine_mode:
            return {"status": "paused", "reason": "trading disabled or quarantine"}

        results = {}
        data = self.fetcher.get_multi_asset_data(interval="1h", limit=100)

        for symbol, df in data.items():
            try:
                analysis = self.analyzer.analyze(df)
                analysis["symbol"] = symbol
                analysis["asset_name"] = get_asset_info(symbol).get("name", symbol)
                results[symbol] = analysis
            except Exception as e:
                results[symbol] = {"status": "error", "message": str(e)}

        # Sort by signal quality
        signals = []
        for sym, res in results.items():
            if res.get("quality") == "high" and res.get("signal") in ("buy", "sell"):
                signals.append({
                    "symbol": sym,
                    "signal": res.get("signal"),
                    "setup": res.get("setup_type"),
                    "rsi": res.get("rsi"),
                    "regime": res.get("regime"),
                })

        return {
            "status": "ok",
            "analyses": results,
            "high_quality_signals": signals,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def run_cycle(self) -> Dict[str, Any]:
        """Run one trading cycle for all assets."""
        analysis = self.analyze_all()

        actions = []
        for signal in analysis.get("high_quality_signals", []):
            symbol = signal["symbol"]
            if self.positions.get(symbol) is None:
                actions.append({
                    "action": "open",
                    "symbol": symbol,
                    "direction": signal["signal"],
                    "setup": signal["setup"],
                })

        return {
            "status": "ok",
            "analysis": analysis,
            "actions": actions,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def emergency_stop(self, reason: str = "manual") -> Dict[str, Any]:
        """Stop all trading and close positions."""
        self.trading_enabled = False
        self.quarantine_mode = True
        closed = [sym for sym, pos in self.positions.items() if pos is not None]
        self.positions = {a: None for a in self.assets}

        return {
            "status": "stopped",
            "reason": reason,
            "closed_positions": closed,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def resume(self) -> Dict[str, Any]:
        """Resume trading."""
        self.trading_enabled = True
        self.quarantine_mode = False
        return {
            "status": "resumed",
            "timestamp": datetime.utcnow().isoformat(),
        }
