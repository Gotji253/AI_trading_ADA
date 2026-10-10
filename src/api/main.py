"""
FastAPI server for Multi-Agent ADA trading system.

Run:
  uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.agents.manager import ManagerAgent

app = FastAPI(title="AI_trading_ADA Multi-Agent", version="1.0.0")
manager = ManagerAgent()


@app.get("/")
def root():
    return {"message": "AI_trading_ADA Multi-Agent API", "status": "running"}


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
def risk_check(signal: str = "buy", price: float = 0.0):
    return manager.risk.evaluate(signal, price)
