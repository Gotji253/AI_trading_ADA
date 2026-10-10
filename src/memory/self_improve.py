"""
Self-Improvement Engine — orchestrates the full feedback cycle.
รวม Attribution_Agent
"""

from typing import Dict, Any

from src.memory.optimizer import AdaptiveOptimizer
from src.memory.validator import ParameterValidator
from src.memory.trade_memory import TradeMemory
from src.agents.attribution_agent import AttributionAgent


class SelfImprovementEngine:
    def __init__(self):
        self.optimizer = AdaptiveOptimizer()
        self.validator = ParameterValidator()
        self.memory = TradeMemory()
        self.attribution = AttributionAgent()

    def run_cycle(self) -> Dict[str, Any]:
        """
        Full cycle:
        1. Update memory
        2. Attribution analysis
        3. Generate suggestions (Adaptive Optimization)
        4. Validate with short backtest
        """
        mem = self.memory.update_from_paper()

        # Attribution matrix
        attr_result = self.attribution.analyze()

        # Optimize
        opt = self.optimizer.suggest()

        # Validate
        proposed = opt.get("parsed_suggestion", {})
        validation = self.validator.validate(proposed)

        return {
            "status": "ok",
            "memory_updated": True,
            "attribution": attr_result,
            "optimization": opt,
            "validation": validation,
            "ready_to_apply": validation.get("approved", False),
            "message": "Review validation and attribution before applying changes.",
        }


def main():
    engine = SelfImprovementEngine()
    result = engine.run_cycle()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
