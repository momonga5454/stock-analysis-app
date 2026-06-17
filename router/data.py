from fastapi import APIRouter
from services.price_service import fetch_and_save_prices
from services.backtest import run_backtest

router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/prices/{symbol}")
def save_prices(symbol: str):
    return fetch_and_save_prices(symbol)

@router.get("/backtest/{symbol}")
def backtest(symbol: str, hold_days: int = 1):
    return run_backtest(symbol, hold_days)