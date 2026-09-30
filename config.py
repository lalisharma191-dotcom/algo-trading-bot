"""Bot configuration. Values can be overridden with environment variables or a .env file."""
import os

from dotenv import load_dotenv

load_dotenv()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# --- Mode ---
# "paper" = simulated trading with fake money (safe, default)
# "live"  = real orders on Binance (requires API keys; use at your own risk)
MODE = os.getenv("MODE", "paper").lower()

# --- Binance API (only needed for live mode) ---
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")

# --- Market ---
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "15m")  # candle timeframe
CANDLE_LIMIT = int(os.getenv("CANDLE_LIMIT", "200"))

# --- Strategy parameters ---
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = _get_float("RSI_OVERSOLD", 30)
RSI_OVERBOUGHT = _get_float("RSI_OVERBOUGHT", 70)
EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))

# --- Risk management ---
START_BALANCE = _get_float("START_BALANCE", 1000.0)  # paper-trading balance (USDT)
RISK_PER_TRADE = _get_float("RISK_PER_TRADE", 0.01)  # risk 1% of balance per trade
STOP_LOSS_PCT = _get_float("STOP_LOSS_PCT", 0.02)    # 2% stop loss
TAKE_PROFIT_PCT = _get_float("TAKE_PROFIT_PCT", 0.04)  # 4% take profit (2:1 reward)
MAX_DAILY_LOSS_PCT = _get_float("MAX_DAILY_LOSS_PCT", 0.05)  # stop for the day at -5%
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "1"))

# --- Loop ---
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
