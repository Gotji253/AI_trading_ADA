"""
Manager_Agent — ประสานงาน Alpha → Risk → Execution
รองรับ Emergency Stop และ Max Drawdown Hard Stop
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
        self.trading_enabled = True
        self.quarantine_mode = False

    def run_cycle(self) -> Dict[str, Any]:
        if not self.trading_enabled or self.quarantine_mode:
            return {
                "cycle": "halted",
                "message": "Trading is halted (emergency / quarantine mode)",
                "quarantine": self.quarantine_mode,
                "status": self.execution.status(),
            }

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

        # Hard stop triggered by max drawdown
        if risk_out.get("hard_stop"):
            stop_result = self.emergency_stop(reason="max_drawdown")
            return {
                "cycle": "quarantine",
                "reason": risk_out.get("reason"),
                "emergency": stop_result,
                "status": self.execution.status(),
            }

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
        status = self.execution.status()
        status["trading_enabled"] = self.trading_enabled
        status["quarantine_mode"] = self.quarantine_mode
        return status

    def emergency_stop(self, reason: str = "manual") -> Dict[str, Any]:
        """ปิดตำแหน่งทั้งหมดทันที แล้วหยุดการเทรดใหม่ (เข้าโหมดกักกัน)"""
        self.trading_enabled = False
        self.quarantine_mode = True
        status = self.execution.status()
        closed = None

        if status.get("position"):
            try:
                price = status.get("current_price") or status["position"]["entry"]
                closed = self.execution.close(price, reason=f"emergency_stop:{reason}")
            except Exception as e:
                closed = {"error": str(e)}

        return {
            "status": "quarantine",
            "trading_enabled": False,
            "quarantine_mode": True,
            "reason": reason,
            "closed_position": closed,
            "message": f"Emergency stop activated ({reason}). All positions closed. System in quarantine mode.",
        }

    def resume(self) -> Dict[str, Any]:
        """เปิดการเทรดใหม่หลัง quarantine (ต้องทำด้วยมือ)"""
        self.trading_enabled = True
        self.quarantine_mode = False
        return {
            "status": "resumed",
            "trading_enabled": True,
            "quarantine_mode": False,
            "message": "Trading re-enabled. Quarantine cleared.",
        }
