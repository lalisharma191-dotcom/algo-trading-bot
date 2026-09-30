"""Main trading bot loop.

Default mode is PAPER TRADING (fake money). Set MODE=live plus API keys in .env
to trade for real — only do that after testing, and only with money you can
afford to lose.
"""
import logging
import time

import config
import exchange
from risk import Position, RiskManager
from strategy import get_signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
)
log = logging.getLogger("bot")


def run() -> None:
    live = config.MODE == "live"
    log.info(
        "Starting bot | mode=%s | symbol=%s | interval=%s",
        config.MODE.upper(), config.SYMBOL, config.INTERVAL,
    )
    if not live:
        log.info("PAPER TRADING: no real orders will be placed. Balance=%.2f USDT",
                 config.START_BALANCE)

    risk = RiskManager(config.START_BALANCE)
    position: Position | None = None

    while True:
        try:
            df = exchange.get_klines()
            price = float(df["close"].iloc[-1])

            # 1) Manage an open position first (stop-loss / take-profit)
            if position is not None:
                exit_reason = risk.check_exit(position, price)
                signal = get_signal(df)
                if exit_reason or signal == "SELL":
                    reason = exit_reason or "SELL_SIGNAL"
                    if live:
                        exchange.place_market_order("SELL", position.qty)
                    pnl = risk.settle(position, price)
                    log.info("CLOSED %s @ %.2f | reason=%s | pnl=%.2f | balance=%.2f",
                             position.symbol, price, reason, pnl, risk.balance)
                    position = None

            # 2) Look for a new entry
            elif risk.daily_loss_hit():
                log.warning("Daily loss limit reached — no new trades today.")
            else:
                signal = get_signal(df)
                if signal == "BUY":
                    position = risk.open_position(config.SYMBOL, price)
                    if position.qty <= 0:
                        log.warning("Balance too small to open a position.")
                        position = None
                    else:
                        if live:
                            exchange.place_market_order("BUY", position.qty)
                        log.info(
                            "OPENED %s qty=%.6f @ %.2f | SL=%.2f | TP=%.2f | balance=%.2f",
                            position.symbol, position.qty, position.entry_price,
                            position.stop_loss, position.take_profit, risk.balance,
                        )
                else:
                    log.info("No trade | signal=%s | price=%.2f | balance=%.2f",
                             signal, price, risk.balance)

        except KeyboardInterrupt:
            log.info("Stopped by user. Final balance=%.2f", risk.balance)
            break
        except Exception:
            log.exception("Error in loop; retrying in %ss", config.POLL_SECONDS)

        time.sleep(config.POLL_SECONDS)


if __name__ == "__main__":
    run()
