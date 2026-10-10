"""
Load configuration and API keys from environment / .env file.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional; user can export vars manually


class Config:
    # Exchange / data
    BINANCE_API_KEY: Optional[str] = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET: Optional[str] = os.getenv("BINANCE_API_SECRET")

    # Optional free alternative
    COINGECKO_API_KEY: Optional[str] = os.getenv("COINGECKO_API_KEY")  # not required for free tier

    # LLM (for Hermes, usually set in Hermes itself)
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Trading mode
    TRADING_MODE: str = os.getenv("TRADING_MODE", "paper").lower()  # paper | live
    MAX_POSITION_PCT: float = float(os.getenv("MAX_POSITION_PCT", "5"))
    DEFAULT_STOP_LOSS_PCT: float = float(os.getenv("DEFAULT_STOP_LOSS_PCT", "3"))
    DEFAULT_TAKE_PROFIT_PCT: float = float(os.getenv("DEFAULT_TAKE_PROFIT_PCT", "6"))

    @classmethod
    def has_binance_keys(cls) -> bool:
        return bool(cls.BINANCE_API_KEY and cls.BINANCE_API_SECRET)

    @classmethod
    def summary(cls) -> dict:
        return {
            "binance_keys_set": cls.has_binance_keys(),
            "trading_mode": cls.TRADING_MODE,
            "max_position_pct": cls.MAX_POSITION_PCT,
            "openrouter_set": bool(cls.OPENROUTER_API_KEY),
        }


def get_config() -> Config:
    return Config
