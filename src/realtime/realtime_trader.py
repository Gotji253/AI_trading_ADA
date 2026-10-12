"""
Real-time Paper Trading Runner
Runs the improved Ensemble Donchian strategy continuously with live data.
"""

import time
import os
from datetime import datetime, timezone
from typing import Dict, Any

from src.paper.ensemble_trader import EnsemblePaperTrader
from src.data.multi_asset_fetcher import MultiAssetFetcher
from src.strategies.ensemble_donchian import EnsembleDonchianStrategy


class RealtimePaperTrader:
    """Real-time paper trading system."""

    def __init__(self):
        self.paper = EnsemblePaperTrader()
        self.fetcher = MultiAssetFetcher()
        self.strategy = EnsembleDonchianStrategy(
            use_btc_trend_filter=True,
            min_hold_days=7,
        )
        self.running = False
        self.check_interval = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))  # 5 min default

    def run_once(self) -> Dict[str, Any]:
        """Run a single cycle with live data."""
        print(f"[{datetime.now(timezone.utc).isoformat()}] Running cycle...")

        # Get BTC data for trend filter
        btc_df = self.fetcher.get_ohlcv("BTCUSDT", "1d", 250)

        # Override strategy analysis to include BTC filter
        # (Simplified for now; full integration would update paper trader)
        result = self.paper.run_cycle()

        print(f"  Status: {result.get('status')}")
        print(f"  Actions: {len(result.get('actions', []))}")
        if result.get("actions"):
            for act in result["actions"]:
                print(f"    -> {act}")

        return result

    def start(self, max_cycles: int = None):
        """Start the real-time loop."""
        self.running = True
        cycles = 0
        print("=== Real-time Paper Trading Started ===")
        print(f"Interval: {self.check_interval}s")
        print(f"Assets: {self.paper.assets}")
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                self.run_once()
                cycles += 1
                if max_cycles and cycles >= max_cycles:
                    break
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            self.running = False
            print("=== Real-time Paper Trading Stopped ===")

    def stop(self):
        self.running = False


def main():
    trader = RealtimePaperTrader()
    # For testing: run a few cycles
    # trader.start(max_cycles=3)
    trader.run_once()


if __name__ == "__main__":
    main()
