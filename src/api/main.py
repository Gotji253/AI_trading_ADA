"""
FastAPI server for Multi-Agent ADA trading system.

Run:
  uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.agents.manager import ManagerAgent
from src.memory.learning_prompt import build_learning_prompt
from src.memory.self_improve import SelfImprovementEngine
from src.analysis.ai_analyzer import ADAAIAnalyzer
from src.paper.trader import PaperTrader

app = FastAPI(title="AI_trading_ADA Multi-Agent", version="1.4.0")
manager = ManagerAgent()
engine = SelfImprovementEngine()


@app.get("/")
def root():
    return {
        "message": "AI_trading_ADA Multi-Agent API",
        "status": "running",
        "trading_enabled": manager.trading_enabled,
        "quarantine": manager.quarantine_mode,
    }


@app.get("/status")
def status():
    return manager.get_status()


@app.post("/cycle")
def run_cycle():
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
    status = manager.get_status()
    stats = status.get("stats", {})
    return {
        "equity": status.get("equity"),
        "balance": status.get("balance_usdt"),
        "daily_pnl": status.get("daily_pnl"),
        "total_trades": status.get("total_trades"),
        "open_position": status.get("position") is not None,
        "trading_enabled": status.get("trading_enabled", True),
        "quarantine_mode": status.get("quarantine_mode", False),
        "stats": stats,
    }


@app.get("/history")
def trade_history(limit: int = Query(20, ge=1, le=100)):
    trader = PaperTrader(notify=False)
    return {"trades": trader.history(limit=limit)}


@app.post("/daily-summary")
def daily_summary():
    trader = PaperTrader(notify=True)
    result = trader.daily_summary(send_telegram=True)
    return result


@app.post("/learn/analyze")
def learn_analyze():
    """วังจร Self-Improvement เต็ม (วิเคราะห์ + แนะนำ + Validate)"""
    result = engine.run_cycle()
    return JSONResponse(content=result)


@app.post("/emergency/stop")
def emergency_stop():
    result = manager.emergency_stop(reason="manual")
    return JSONResponse(content=result)


@app.post("/emergency/resume")
def emergency_resume():
    result = manager.resume()
    return JSONResponse(content=result)
