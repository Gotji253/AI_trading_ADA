"""
Manager_Agent — ประสานงาน Alpha → Risk → Execution
"""

from typing import Dict, Any

from src.agents.alpha_agent import AlphaAgent
from src.agents.risk_agent import RiskAgent
from src.agents.execution_agent import ExecutionAgent


class ManagerAgent:
    def __init__(self):
        self.alpha = AlphaAgent()
        self.risk = RiskAgent()
        self.execution = ExecutionAgent()

    def run_cycle(self) -> Dict[str, Any]:
        """รันหนึ่งรอบการตัดสินใจแบบสมบูรณ์"""
        # 1. Check existing exits first
        exit_result = self.execution.check_exits()
        if exit_result:
            return {
                "cycle": "exit_triggered",
                "result": exit_result,
                "status": self.execution.status(),
            }

        # 2. Alpha generates signal
        alpha_out = self.alpha.generate_signal()
        signal = alpha_out.get("signal", "hold")
        price = alpha_out.get("price")

        if signal not in ("buy", "sell") or not price:
            return {
                "cycle": "no_signal",
                "alpha": alpha_out,
                "status": self.execution.status(),
            }

        # 3. Risk evaluates
        sig_1h = alpha_out.get("multi_tf", {}).get("timeframes", {}).get("1h", {})
        proposed_sl = sig_1h.get("stop_loss")
        risk_out = self.risk.evaluate(signal, price, proposed_sl)

        if not risk_out.get("approved"):
            return {
                "cycle": "rejected_by_risk",
                "alpha": alpha_out,
                "risk": risk_out,
                "status": self.execution.status(),
            }

        # 4. Execution
        side = "long" if signal == "buy" else "short"
        max_qty = risk_out.get("max_qty", 0)
        if max_qty <= 0:
            return {
                "cycle": "zero_size",
                "risk": risk_out,
                "status": self.execution.status(),
            }

        exec_result = self.execution.execute(
            side=side,
            price=price,
            qty=max_qty,
            stop_loss=proposed_sl,
            take_profit=sig_1h.get("take_profit"),
            filters_passed=["multi_tf", "risk_approved"],
        )

        return {
            "cycle": "executed",
            "alpha": alpha_out,
            "risk": risk_out,
            "execution": exec_result,
            "status": self.execution.status(),
        }

    def get_status(self) -> Dict[str, Any]:
        return self.execution.status()
