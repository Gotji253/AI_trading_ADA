"""
Self-Improvement Engine — orchestrates the full feedback cycle.
"""

from typing import Dict, Any

from src.memory.optimizer import AdaptiveOptimizer
from src.memory.validator import ParameterValidator
from src.memory.trade_memory import TradeMemory


class SelfImprovementEngine:
    def __init__(self):
        self.optimizer = AdaptiveOptimizer()
        self.validator = ParameterValidator()
        self.memory = TradeMemory()

    def run_cycle(self) -> Dict[str, Any]:
        """
        Full cycle:
        1. Update memory
        2. Generate suggestions (Adaptive Optimization)
        3. Validate with short backtest (Walk-Forward gate)
        4. Return approval status
        """
        # 1. Refresh memory
        mem = self.memory.update_from_paper()

        # 2. Optimize
        opt = self.optimizer.suggest()

        # 3. Validate proposed params
        proposed = opt.get("parsed_suggestion", {})
        validation = self.validator.validate(proposed)

        return {
            "status": "ok",
            "memory_updated": True,
            "optimization": opt,
            "validation": validation,
            "ready_to_apply": validation.get("approved", False),
            "message": "Review validation result before applying any parameter changes.",
        }


def main():
    engine = SelfImprovementEngine()
    result = engine.run_cycle()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
