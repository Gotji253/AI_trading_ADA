"""
Micro-level trade logging for Self-Improvement Engine.
Captures market snapshot at entry and exit.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

LOG_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "trade_logs.jsonl"


class TradeLogger:
    def __init__(self):
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    def log_entry(self, trade_id: str, snapshot: Dict[str, Any]) -> None:
        record = {
            "event": "entry",
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "snapshot": snapshot,
        }
        self._append(record)

    def log_exit(self, trade_id: str, result: Dict[str, Any]) -> None:
        record = {
            "event": "exit",
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result,
        }
        self._append(record)

    def _append(self, record: Dict[str, Any]):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_recent(self, limit: int = 50) -> list:
        if not LOG_FILE.exists():
            return []
        lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
        records = []
        for line in lines[-limit:]:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
        return records


def build_snapshot(
    price: float,
    multi_tf: Dict,
    levels: Dict,
    indicators: Optional[Dict] = None,
    sentiment: Optional[str] = None,
    alpha_reasons: Optional[list] = None,
    risk_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a micro snapshot for logging."""
    return {
        "price": price,
        "multi_tf": {
            "recommendation": multi_tf.get("recommendation"),
            "consensus": multi_tf.get("consensus"),
            "agreement": multi_tf.get("agreement"),
            "strength": multi_tf.get("consensus_strength"),
        },
        "levels": {
            "support": levels.get("nearest_support"),
            "resistance": levels.get("nearest_resistance"),
        },
        "indicators": indicators or {},
        "sentiment": sentiment,
        "alpha_reasons": alpha_reasons or [],
        "risk_notes": risk_notes,
    }
