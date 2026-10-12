"""
Hourly Real-time Paper Trading Runner
Runs the strategy every hour and logs results for data collection.
"""

import time
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from src.realtime.realtime_trader import RealtimePaperTrader


LOG_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "hourly_logs"


class HourlyRunner:
    """Run paper trading every hour and save logs."""

    def __init__(self):
        self.trader = RealtimePaperTrader()
        self.interval_seconds = 3600  # 1 hour
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _save_log(self, result: Dict[str, Any]):
        """Save cycle result to timestamped log file."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = LOG_DIR / f"cycle_{ts}.json"
        log_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Log saved: {log_file.name}")

    def run_forever(self):
        """Run continuously every hour."""
        print("=== Hourly Paper Trading Runner Started ===")
        print(f"Interval: {self.interval_seconds // 60} minutes")
        print(f"Logs: {LOG_DIR}")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                print(f"\n[{datetime.now(timezone.utc).isoformat()}] Starting hourly cycle")
                result = self.trader.run_once()
                self._save_log(result)

                # Sleep until next hour
                print(f"  Sleeping {self.interval_seconds // 60} minutes...")
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            print("\nStopped by user.")

    def run_once_now(self):
        """Run a single cycle immediately (for testing)."""
        result = self.trader.run_once()
        self._save_log(result)
        return result


def main():
    runner = HourlyRunner()
    # Uncomment to run once for testing:
    # runner.run_once_now()
    runner.run_forever()


if __name__ == "__main__":
    main()
