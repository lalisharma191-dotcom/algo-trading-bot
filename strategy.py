"""RSI + EMA + MACD combined strategy.

BUY when all three agree:
  - Fast EMA is above slow EMA (uptrend)
  - MACD line crossed above its signal line recently (fresh bullish momentum)
  - RSI is below overbought (there is still room to rise)

SELL (exit) when:
  - RSI reaches overbought, or
  - Fast EMA crosses below slow EMA, or
  - MACD line crosses below its signal line
(Stop-loss / take-profit exits are handled by risk management in the bot loop.)
"""
import pandas as pd

import config
from indicators import ema, macd, rsi


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    df["rsi"] = rsi(close, config.RSI_PERIOD)
    df["ema_fast"] = ema(close, config.EMA_FAST)
    df["ema_slow"] = ema(close, config.EMA_SLOW)
    df["macd"], df["macd_signal"], df["macd_hist"] = macd(
        close, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL
    )
    return df


def get_signal(df: pd.DataFrame) -> str:
    """Return "BUY", "SELL" or "HOLD" for the most recent closed candle."""
    if len(df) < max(config.EMA_SLOW, config.MACD_SLOW, config.RSI_PERIOD) + 2:
        return "HOLD"

    df = add_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2]

    uptrend = last["ema_fast"] > last["ema_slow"]
    # MACD crossed above its signal line within the last 3 candles (fresh momentum)
    recent = df.iloc[-4:]
    macd_above = last["macd"] > last["macd_signal"]
    macd_fresh_cross = macd_above and (recent["macd"] <= recent["macd_signal"]).any()
    rsi_has_room = config.RSI_OVERSOLD < last["rsi"] < config.RSI_OVERBOUGHT

    if uptrend and macd_fresh_cross and rsi_has_room:
        return "BUY"

    rsi_overbought = last["rsi"] >= config.RSI_OVERBOUGHT
    trend_break = prev["ema_fast"] >= prev["ema_slow"] and last["ema_fast"] < last["ema_slow"]
    macd_cross_down = prev["macd"] >= prev["macd_signal"] and last["macd"] < last["macd_signal"]

    if rsi_overbought or trend_break or macd_cross_down:
        return "SELL"

    return "HOLD"
