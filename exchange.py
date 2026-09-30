"""Binance exchange access: market data (public) and orders (live mode only)."""
import hashlib
import hmac
import time
from urllib.parse import urlencode

import pandas as pd
import requests

import config


def get_klines(symbol: str = None, interval: str = None, limit: int = None) -> pd.DataFrame:
    """Fetch candles from Binance public API (no key needed)."""
    url = f"{config.BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol or config.SYMBOL,
        "interval": interval or config.INTERVAL,
        "limit": limit or config.CANDLE_LIMIT,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_base", "taker_quote", "ignore",
        ],
    )
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = df[col].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df[["open_time", "open", "high", "low", "close", "volume"]]


def get_price(symbol: str = None) -> float:
    url = f"{config.BASE_URL}/api/v3/ticker/price"
    resp = requests.get(url, params={"symbol": symbol or config.SYMBOL}, timeout=15)
    resp.raise_for_status()
    return float(resp.json()["price"])


def _signed_request(method: str, path: str, params: dict) -> dict:
    if not config.API_KEY or not config.API_SECRET:
        raise RuntimeError("Live mode needs BINANCE_API_KEY and BINANCE_API_SECRET")
    params = dict(params)
    params["timestamp"] = int(time.time() * 1000)
    query = urlencode(params)
    signature = hmac.new(
        config.API_SECRET.encode(), query.encode(), hashlib.sha256
    ).hexdigest()
    url = f"{config.BASE_URL}{path}?{query}&signature={signature}"
    resp = requests.request(method, url, headers={"X-MBX-APIKEY": config.API_KEY}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def place_market_order(side: str, qty: float, symbol: str = None) -> dict:
    """Place a real market order. Only called in live mode."""
    return _signed_request(
        "POST",
        "/api/v3/order",
        {
            "symbol": symbol or config.SYMBOL,
            "side": side,
            "type": "MARKET",
            "quantity": qty,
        },
    )
