"""
Self-Improvement Engine — 4-Stage Quarantine Pipeline
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
        4-Stage Pipeline:
        1. Memory / Logging refresh
        2. Attribution
        3. Optimization suggestion
        4. Walk-Forward Validation
        """
        # Stage 1: Refresh memory
        mem = self.memory.update_from_paper()

        # Stage 2: Attribution
        attr_result = self.attribution.analyze()

        # Stage 3: Optimization
        opt = self.optimizer.suggest()

        # Stage 4: Validation
        proposed = opt.get("parsed_suggestion", {})
        validation = self.validator.validate(proposed)

        return {
            "status": "ok",
            "stage": "complete",
            "memory_updated": True,
            "attribution": attr_result,
            "optimization": opt,
            "validation": validation,
            "ready_to_apply": validation.get("approved", False),
            "message": (
                "Parameter changes approved. Review and apply manually."
                if validation.get("approved")
                else "Parameter changes rejected by validation. No update applied."
            ),
        }


def main():
    engine = SelfImprovementEngine()
    result = engine.run_cycle()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
