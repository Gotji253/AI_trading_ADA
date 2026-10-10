"""
CLI for running Multi-TF backtests.
"""

import argparse
import json

from src.backtest.engine import MultiTFBacktester


def main():
    parser = argparse.ArgumentParser(description="ADA Multi-TF Backtester")
    parser.add_argument("--mode", choices=["simple", "walkforward"], default="simple")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--source", default="binance")
    args = parser.parse_args()

    bt = MultiTFBacktester(source=args.source)

    if args.mode == "simple":
        data = bt.fetch_aligned_data(limit=args.limit)
        result = bt.simulate(data)
    else:
        result = bt.walk_forward(total_bars=args.limit)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
