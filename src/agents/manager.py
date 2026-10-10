"""
Manager_Agent — ประสานงาน Alpha → Risk → Execution
รองรับ Regime_Agent และ Emergency / Quarantine
"""

from typing import Dict, Any

from src.agents.alpha_agent import AlphaAgent
from src.agents.risk_agent import RiskAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.regime_agent import RegimeAgent


class ManagerAgent:
    def __init__(self):
        self.alpha = AlphaAgent()
        self.risk = RiskAgent()
        self.execution = ExecutionAgent()
        self.regime = RegimeAgent()
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

        # 0. Regime classification
        regime_out = self.regime.classify()

        # 1. Check existing exits first
        exit_result = self.execution.check_exits()
        if exit_result:
            return {
                "cycle": "exit_triggered",
                "regime": regime_out,
                "result": exit_result,
                "status": self.execution.status(),
            }

        # 2. Alpha generates signal (can use regime hint in future)
        alpha_out = self.alpha.generate_signal()
        signal = alpha_out.get("signal", "hold")
        price = alpha_out.get("price")

        # Adjust signal based on regime (simple example)
        strategy_hint = regime_out.get("strategy_hint", "neutral")
        if strategy_hint == "reduce_size_or_wait" and signal in ("buy", "sell"):
            # Soften signal in high vol
            signal = "hold"

        if signal not in ("buy", "sell") or not price:
            return {
                "cycle": "no_signal",
                "regime": regime_out,
                "alpha": alpha_out,
                "status": self.execution.status(),
            }

        # 3. Risk evaluates
        sig_1h = alpha_out.get("multi_tf", {}).get("timeframes", {}).get("1h", {})
        proposed_sl = sig_1h.get("stop_loss")
        risk_out = self.risk.evaluate(signal, price, proposed_sl)

        if risk_out.get("hard_stop"):
            stop_result = self.emergency_stop(reason="max_drawdown")
            return {
                "cycle": "quarantine",
                "regime": regime_out,
                "reason": risk_out.get("reason"),
                "emergency": stop_result,
                "status": self.execution.status(),
            }

        if not risk_out.get("approved"):
            return {
                "cycle": "rejected_by_risk",
                "regime": regime_out,
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
                "regime": regime_out,
                "risk": risk_out,
                "status": self.execution.status(),
            }

        exec_result = self.execution.execute(
            side=side,
            price=price,
            qty=max_qty,
            stop_loss=proposed_sl,
            take_profit=sig_1h.get("take_profit"),
            filters_passed=["multi_tf", "risk_approved", f"regime:{regime_out.get('regime')}"],
        )

        return {
            "cycle": "executed",
            "regime": regime_out,
            "alpha": alpha_out,
            "risk": risk_out,
            "execution": exec_result,
            "status": self.execution.status(),
        }

    def get_status(self) -> Dict[str, Any]:
        status = self.execution.status()
        status["trading_enabled"] = self.trading_enabled
        status["quarantine_mode"] = self.quarantine_mode
        status["current_regime"] = self.regime.classify()
        return status

    def emergency_stop(self, reason: str = "manual") -> Dict[str, Any]:
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
        self.trading_enabled = True
        self.quarantine_mode = False
        return {
            "status": "resumed",
            "trading_enabled": True,
            "quarantine_mode": False,
            "message": "Trading re-enabled. Quarantine cleared.",
        }
