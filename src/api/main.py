"""
FastAPI server for Multi-Agent ADA trading system.

Run:
  uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.agents.manager import ManagerAgent
from src.memory.learning_prompt import build_learning_prompt
from src.analysis.ai_analyzer import ADAAIAnalyzer
from src.paper.trader import PaperTrader

app = FastAPI(title="AI_trading_ADA Multi-Agent", version="1.2.0")
manager = ManagerAgent()


@app.get("/")
def root():
    return {"message": "AI_trading_ADA Multi-Agent API", "status": "running", "trading_enabled": manager.trading_enabled}


@app.get("/status")
def status():
    return manager.get_status()


@app.post("/cycle")
def run_cycle():
    """รันหนึ่งรอบ: Alpha → Risk → Execution"""
    result = manager.run_cycle()
    return JSONResponse(content=result)


@app.get("/alpha")
def alpha_signal():
    return manager.alpha.generate_signal()


@app.get("/risk")
def risk_check(signal: str = Query("buy"), price: float = Query(0.0)):
    return manager.risk.evaluate(signal, price)


@app.get("/performance/summary")
def performance_summary():
    """สรุปสถิติผลงาน paper trading"""
    status = manager.get_status()
    stats = status.get("stats", {})
    return {
        "equity": status.get("equity"),
        "balance": status.get("balance_usdt"),
        "daily_pnl": status.get("daily_pnl"),
        "total_trades": status.get("total_trades"),
        "open_position": status.get("position") is not None,
        "trading_enabled": status.get("trading_enabled", True),
        "stats": stats,
    }


@app.get("/history")
def trade_history(limit: int = Query(20, ge=1, le=100)):
    """ประวัติการเทรดล่าสุด"""
    trader = PaperTrader(notify=False)
    return {"trades": trader.history(limit=limit)}


@app.post("/daily-summary")
def daily_summary():
    """ส่งสรุปประจำวันไป Telegram (ถ้าตั้งค่าไว้)"""
    trader = PaperTrader(notify=True)
    result = trader.daily_summary(send_telegram=True)
    return result


@app.post("/learn/analyze")
def learn_analyze():
    """สร้าง prompt สำหรับการเรียนรู้ + ให้ AI วิเคราะห์ (ถ้ามี LLM key)"""
    prompt = build_learning_prompt()
    analyzer = ADAAIAnalyzer()
    try:
        analysis = analyzer._call_llm(prompt) if hasattr(analyzer, "_call_llm") else prompt
    except Exception as e:
        analysis = f"LLM call failed: {e}\n\nPrompt:\n{prompt}"

    return {
        "status": "ok",
        "learning_prompt": prompt,
        "ai_suggestion": analysis,
    }


@app.post("/emergency/stop")
def emergency_stop():
    """ปิดตำแหน่งทั้งหมดทันที + หยุดการเทรดใหม่ชั่วคราว"""
    result = manager.emergency_stop()
    return JSONResponse(content=result)


@app.post("/emergency/resume")
def emergency_resume():
    """เปิดการเทรดใหม่หลัง emergency stop"""
    manager.trading_enabled = True
    return {
        "status": "resumed",
        "trading_enabled": True,
        "message": "Trading has been re-enabled. New cycles can run again.",
    }
