"""
CLI entry point for Hermes Agent ADA skill.
"""

import argparse
import json
import sys

from src.config import get_config
from src.data.ada_price import ADAPriceFetcher
from src.signals.ada_signals import ADASignalGenerator
from src.paper.trader import PaperTrader
from src.analysis.ai_analyzer import ADAAIAnalyzer


def cmd_status(_args):
    cfg = get_config()
    result = {
        "status": "ok",
        "config": cfg.summary(),
        "message": "Ready. Default mode is paper trading.",
    }
    if not cfg.has_binance_keys():
        result["warning"] = "BINANCE_API_KEY / SECRET not set. Using public endpoints."
    if not (cfg.OPENROUTER_API_KEY or cfg.OPENAI_API_KEY):
        result["warning_llm"] = "No LLM API key set. AI analysis will not work."
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_price(args):
    fetcher = ADAPriceFetcher(preferred_source=args.source)
    result = fetcher.get_current_price()
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_signal(args):
    gen = ADASignalGenerator(source=args.source)
    result = gen.generate(interval=args.interval)
    result["trading_mode"] = get_config().TRADING_MODE
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_ai_analyze(args):
    analyzer = ADAAIAnalyzer(model=args.model)
    result = analyzer.analyze(interval=args.interval)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_paper_status(_args):
    trader = PaperTrader()
    print(json.dumps(trader.status(), ensure_ascii=False, indent=2))


def cmd_paper_auto(args):
    trader = PaperTrader()
    result = trader.auto_trade(interval=args.interval)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_paper_history(args):
    trader = PaperTrader()
    print(json.dumps(trader.history(limit=args.limit), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="ada-trader")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Check config and API key status").set_defaults(func=cmd_status)

    p_price = sub.add_parser("ada-price", help="Current ADA price snapshot")
    p_price.add_argument("--source", default="binance", choices=["binance", "coingecko"])
    p_price.set_defaults(func=cmd_price)

    p_sig = sub.add_parser("ada-signal", help="Generate ADA trading signal")
    p_sig.add_argument("--interval", default="1h")
    p_sig.add_argument("--source", default="binance", choices=["binance", "coingecko"])
    p_sig.set_defaults(func=cmd_signal)

    p_ai = sub.add_parser("ai-analyze", help="Full AI analysis of ADA (requires LLM key)")
    p_ai.add_argument("--interval", default="1h")
    p_ai.add_argument(
        "--model",
        default=None,
        help="Override OpenRouter model (default: free model from .env or config)",
    )
    p_ai.set_defaults(func=cmd_ai_analyze)

    sub.add_parser("paper-status", help="Show paper trading account status").set_defaults(func=cmd_paper_status)

    p_auto = sub.add_parser("paper-auto", help="Generate signal and auto paper-trade")
    p_auto.add_argument("--interval", default="1h")
    p_auto.set_defaults(func=cmd_paper_auto)

    p_hist = sub.add_parser("paper-history", help="Show recent paper trades")
    p_hist.add_argument("--limit", type=int, default=20)
    p_hist.set_defaults(func=cmd_paper_history)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        err = {"status": "error", "message": str(e)}
        print(json.dumps(err, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
