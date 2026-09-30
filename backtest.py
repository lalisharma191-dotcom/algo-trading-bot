"""Simple backtest: run the strategy over historical candles and report results.

Usage:
    python backtest.py                # fetches candles from Binance
    python backtest.py data.csv       # or use a CSV with open_time,open,high,low,close,volume
"""
import sys

import pandas as pd

import config
import exchange
from risk import RiskManager
from strategy import get_signal


def run_backtest(df: pd.DataFrame) -> None:
    risk = RiskManager(config.START_BALANCE)
    position = None
    trades = wins = 0
    warmup = max(config.EMA_SLOW, config.MACD_SLOW, config.RSI_PERIOD) + 5

    for i in range(warmup, len(df)):
        window = df.iloc[: i + 1]
        price = float(window["close"].iloc[-1])

        if position is not None:
            exit_reason = risk.check_exit(position, price)
            signal = get_signal(window)
            if exit_reason or signal == "SELL":
                pnl = risk.settle(position, price)
                trades += 1
                if pnl > 0:
                    wins += 1
                position = None
        else:
            if get_signal(window) == "BUY":
                position = risk.open_position(config.SYMBOL, price)
                if position.qty <= 0:
                    position = None

    if position is not None:
        risk.settle(position, float(df["close"].iloc[-1]))
        trades += 1

    print(f"Candles tested : {len(df)}")
    print(f"Closed trades  : {trades}")
    if trades:
        print(f"Win rate       : {wins / trades * 100:.1f}%")
    print(f"Start balance  : {config.START_BALANCE:.2f} USDT")
    print(f"Final balance  : {risk.balance:.2f} USDT")
    print(f"Return         : {(risk.balance / config.START_BALANCE - 1) * 100:+.2f}%")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = pd.read_csv(sys.argv[1])
        for col in ("open", "high", "low", "close"):
            data[col] = data[col].astype(float)
    else:
        data = exchange.get_klines(limit=1000)
    run_backtest(data)
