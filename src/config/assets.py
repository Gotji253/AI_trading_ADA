"""
Multi-Asset Configuration
Supported: BTC, ETH, SOL, BNB, XRP
"""

import os
from typing import List, Dict

# Default trading universe
DEFAULT_ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

# Asset metadata
ASSET_INFO = {
    "BTCUSDT": {"name": "Bitcoin", "base": "BTC", "priority": 1},
    "ETHUSDT": {"name": "Ethereum", "base": "ETH", "priority": 2},
    "SOLUSDT": {"name": "Solana", "base": "SOL", "priority": 3},
    "BNBUSDT": {"name": "BNB", "base": "BNB", "priority": 4},
    "XRPUSDT": {"name": "XRP", "base": "XRP", "priority": 5},
}


def get_trading_assets() -> List[str]:
    """Get list of assets to trade from env or default."""
    env_assets = os.getenv("TRADING_ASSETS", "")
    if env_assets:
        return [a.strip().upper() for a in env_assets.split(",") if a.strip()]
    return DEFAULT_ASSETS.copy()


def get_asset_info(symbol: str) -> Dict:
    """Get metadata for an asset."""
    return ASSET_INFO.get(symbol, {"name": symbol, "base": symbol.replace("USDT", ""), "priority": 99})


def is_supported(symbol: str) -> bool:
    """Check if asset is in the trading universe."""
    return symbol.upper() in DEFAULT_ASSETS
