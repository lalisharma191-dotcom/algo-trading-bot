# algo-trading-bot

Python-based Binance trading bot using RSI, EMA, and MACD strategy with risk management.

> ⚠️ **Warning / चेतावनी:** Crypto trading is very risky. You can lose all your money.
> This bot starts in **paper-trading mode (fake money)** by default. Test it well before
> ever using real money, and never trade money you cannot afford to lose.
> यह bot शुरुआत में नकली पैसे (paper trading) से चलता है। असली पैसा तभी लगाएँ जब आप
> पूरी तरह test कर चुके हों, और उतना ही लगाएँ जितना डूबने पर सह सकें।

## How it works

**Strategy (RSI + EMA + MACD):**
- **BUY** when all three agree: RSI is recovering from oversold (below 30 → rising back),
  fast EMA (9) is above slow EMA (21) = uptrend, and MACD line is above its signal line.
- **SELL / exit** when RSI hits overbought (70), EMA trend breaks down, or MACD crosses down.

**Risk management:**
- Risks only **1% of balance per trade** (position sizing based on stop-loss distance)
- **2% stop-loss** and **4% take-profit** on every trade (2:1 reward-to-risk)
- Stops trading for the day after a **5% daily loss**

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env    # edit values if you want
```

## Run

**1. Backtest first** (tests the strategy on past candles, no money involved):

```bash
python backtest.py
```

**2. Paper trading** (live prices, fake money — the default):

```bash
python bot.py
```

**3. Live trading** (real money — only after you are satisfied with testing):
set `MODE=live`, `BINANCE_API_KEY` and `BINANCE_API_SECRET` in `.env`, then run `python bot.py`.

All activity is logged to the console and `bot.log`.

## Files

| File | What it does |
|---|---|
| `bot.py` | Main loop: fetch candles → signal → trade → manage stop-loss/take-profit |
| `strategy.py` | RSI + EMA + MACD buy/sell logic |
| `indicators.py` | RSI, EMA, MACD calculations (pandas only, no TA-Lib) |
| `risk.py` | Position sizing, stop-loss/take-profit, daily loss limit |
| `exchange.py` | Binance API: candles, prices, orders (live mode) |
| `backtest.py` | Test the strategy on historical data |
| `config.py` | All settings (override via `.env`) |
