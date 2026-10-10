"""
Execution_Agent — จำลองเทรด (Paper) หรือส่งคำสั่งจริง
ในอนาคตสามารถเชื่อมกับ exchange API ได้
"""

from typing import Dict, Any, Optional

from src.paper.trader import PaperTrader


class ExecutionAgent:
    def __init__(self):
        self.trader = PaperTrader(notify=True)

    def execute(
        self,
        side: str,
        price: float,
        qty: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        filters_passed: Optional[list] = None,
    ) -> Dict[str, Any]:
        """ปิดตำแหน่งจำลอง (paper)"""
        result = self.trader.open_position(
            side=side,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            filters_passed=filters_passed,
        )
        result["agent"] = "execution"
        return result

    def close(self, price: float, reason: str = "manual") -> Dict[str, Any]:
        result = self.trader.close_position(price, reason=reason)
        result["agent"] = "execution"
        return result

    def check_exits(self) -> Optional[Dict[str, Any]]:
        """ตรวจ SL/TP"""
        return self.trader.check_sl_tp()

    def status(self) -> Dict[str, Any]:
        return self.trader.status()
