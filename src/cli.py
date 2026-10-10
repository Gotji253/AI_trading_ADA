"""
CLI entry point for Hermes Agent ADA skill.
Usage:
  python -m src.cli ada-signal --interval 1h
  python -m src.cli ada-price
"""

import argparse
import json
import sys

from src.data.ada_price import ADAPriceFetcher
from src.signals.ada_signals import ADASignalGenerator


def cmd_price(args):
    fetcher = ADAPriceFetcher(preferred_source=args.source)
    result = fetcher.get_current_price()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_signal(args):
    gen = ADASignalGenerator(source=args.source)
    result = gen.generate(interval=args.interval)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="ada-trader")
    sub = parser.add_subparsers(dest="command", required=True)

    p_price = sub.add_parser("ada-price", help="Current ADA price snapshot")
    p_price.add_argument("--source", default="binance", choices=["binance", "coingecko"])
    p_price.set_defaults(func=cmd_price)

    p_sig = sub.add_parser("ada-signal", help="Generate ADA trading signal")
    p_sig.add_argument("--interval", default="1h", help="1m,5m,15m,1h,4h,1d")
    p_sig.add_argument("--source", default="binance", choices=["binance", "coingecko"])
    p_sig.set_defaults(func=cmd_signal)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        err = {"status": "error", "message": str(e)}
        print(json.dumps(err, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
