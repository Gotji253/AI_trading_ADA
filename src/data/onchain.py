"""
Basic Cardano on-chain data via Koios (free public tier, no key required).
"""

from typing import Dict, Any
import requests


class CardanoOnChain:
    KOIOS_BASE = "https://api.koios.rest/api/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AI_trading_ADA/1.0"})

    def get_tip(self) -> Dict[str, Any]:
        """Current chain tip (epoch, block height, etc.)."""
        try:
            r = self.session.get(f"{self.KOIOS_BASE}/tip", timeout=15)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                tip = data[0]
                return {
                    "status": "ok",
                    "epoch": tip.get("epoch_no"),
                    "block_height": tip.get("block_height"),
                    "block_time": tip.get("block_time"),
                    "hash": tip.get("hash"),
                    "source": "koios",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "No data"}

    def get_epoch_info(self) -> Dict[str, Any]:
        """Basic epoch parameters."""
        try:
            r = self.session.get(f"{self.KOIOS_BASE}/epoch_info", timeout=15)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                return {"status": "ok", "epochs": data[:3], "source": "koios"}  # latest few
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error"}


def main():
    oc = CardanoOnChain()
    print(oc.get_tip())


if __name__ == "__main__":
    main()
