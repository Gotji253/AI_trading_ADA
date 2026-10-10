"""
Load configuration and API keys from environment / .env file.
"""

import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    # Exchange / data
    BINANCE_API_KEY: Optional[str] = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET: Optional[str] = os.getenv("BINANCE_API_SECRET")

    # LLM
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Model selection (OpenRouter)
    # Free models examples:
    # - meta-llama/llama-3.1-8b-instruct:free
    # - google/gemma-2-9b-it:free
    # - mistralai/mistral-7b-instruct:free
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL",
        "meta-llama/llama-3.1-8b-instruct:free"
    )

    # Trading mode
    TRADING_MODE: str = os.getenv("TRADING_MODE", "paper").lower()
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
            "openrouter_set": bool(cls.OPENROUTER_API_KEY),
            "openai_set": bool(cls.OPENAI_API_KEY),
            "openrouter_model": cls.OPENROUTER_MODEL,
        }


def get_config() -> Config:
    return Config
