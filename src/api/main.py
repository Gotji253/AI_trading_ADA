"""
FastAPI server for Multi-Asset Trading System.
Supports: BTC, ETH, SOL, BNB, XRP

Run:
  uvicorn src.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.agents.multi_asset_manager import MultiAssetManager
from src.config.assets import get_trading_assets, get_asset_info

app = FastAPI(title="Multi-Asset Trading System", version="2.0.0")
manager = MultiAssetManager()


@app.get("/")
def root():
    return {
        "message": "Multi-Asset Trading API",
        "version": "2.0.0",
        "assets": get_trading_assets(),
        "status": "running",
        "trading_enabled": manager.trading_enabled,
        "quarantine": manager.quarantine_mode,
    }


@app.get("/status")
def status():
    return manager.get_status()


@app.get("/assets")
def list_assets():
    assets = get_trading_assets()
    return {
        "assets": [
            {"symbol": a, **get_asset_info(a)}
            for a in assets
        ]
    }


@app.post("/cycle")
def run_cycle():
    result = manager.run_cycle()
    return JSONResponse(content=result)


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


@app.get("/prices")
def get_prices():
    from src.data.multi_asset_fetcher import MultiAssetFetcher
    fetcher = MultiAssetFetcher()
    return {"prices": fetcher.get_all_prices()}


@app.post("/emergency/stop")
def emergency_stop():
    result = manager.emergency_stop(reason="manual")
    return JSONResponse(content=result)


@app.post("/emergency/resume")
def emergency_resume():
    result = manager.resume()
    return JSONResponse(content=result)


@app.get("/health")
def health():
    return {"status": "healthy", "assets": len(get_trading_assets())}
