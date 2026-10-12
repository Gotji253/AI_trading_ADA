"""
FastAPI server for Multi-Asset Trading System.
Supports: BTC, ETH, SOL, BNB, XRP

Run:
  uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.agents.multi_asset_manager import MultiAssetManager
from src.paper.multi_asset_trader import MultiAssetPaperTrader
from src.config.assets import get_trading_assets, get_asset_info

app = FastAPI(title="Multi-Asset Trading System", version="2.1.0")
manager = MultiAssetManager()
paper = MultiAssetPaperTrader()


@app.get("/")
def root():
    return {
        "message": "Multi-Asset Trading API",
        "version": "2.1.0",
        "assets": get_trading_assets(),
        "status": "running",
        "trading_enabled": manager.trading_enabled,
        "quarantine": manager.quarantine_mode,
    }


@app.get("/status")
def status():
    return {
        "manager": manager.get_status(),
        "paper": paper.status(),
    }


@app.get("/assets")
def list_assets():
    assets = get_trading_assets()
    return {
        "assets": [
            {"symbol": a, **get_asset_info(a)}
            for a in assets
        ]
    }


@app.get("/prices")
def get_prices():
    from src.data.multi_asset_fetcher import MultiAssetFetcher
    fetcher = MultiAssetFetcher()
    return {"prices": fetcher.get_all_prices()}


@app.get("/analyze")
def analyze_all():
    return manager.analyze_all()


@app.get("/analyze/{symbol}")
def analyze_symbol(symbol: str):
    from src.data.multi_asset_fetcher import MultiAssetFetcher
    from src.analysis.enhanced_analyzer import EnhancedAnalyzer

    symbol = symbol.upper()
    if not symbol.endswith("USDT"):
        symbol = f"{symbol}USDT"

    fetcher = MultiAssetFetcher()
    df = fetcher.get_ohlcv(symbol, "1h", 100)

    if df is None or df.empty:
        return {"status": "error", "message": f"No data for {symbol}"}

    analyzer = EnhancedAnalyzer()
    result = analyzer.analyze(df)
    result["symbol"] = symbol
    return result


# Paper Trading Endpoints
@app.get("/paper/status")
def paper_status():
    return paper.status()


@app.post("/paper/cycle")
def paper_cycle():
    result = paper.run_cycle()
    return JSONResponse(content=result)


@app.post("/paper/open")
def paper_open(
    symbol: str = Query(...),
    side: str = Query(...),
    price: float = Query(...),
    stop_loss: float = Query(None),
    take_profit: float = Query(None),
):
    result = paper.open_position(symbol, side, price, stop_loss, take_profit)
    return JSONResponse(content=result)


@app.post("/paper/close")
def paper_close(symbol: str = Query(...), price: float = Query(...)):
    result = paper.close_position(symbol, price)
    return JSONResponse(content=result)


@app.get("/paper/history")
def paper_history(limit: int = Query(20, ge=1, le=100)):
    return {"trades": paper.history(limit)}


@app.post("/paper/reset")
def paper_reset():
    return paper.reset()


# Emergency
@app.post("/emergency/stop")
def emergency_stop():
    result = manager.emergency_stop(reason="manual")
    paper.state["quarantine"] = True
    paper._save_state()
    return JSONResponse(content=result)


@app.post("/emergency/resume")
def emergency_resume():
    result = manager.resume()
    paper.state["quarantine"] = False
    paper._save_state()
    return JSONResponse(content=result)


@app.get("/health")
def health():
    return {"status": "healthy", "assets": len(get_trading_assets())}
