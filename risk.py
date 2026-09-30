"""Risk management: position sizing, stop-loss/take-profit, daily loss limit."""
from dataclasses import dataclass
from datetime import date

import config


@dataclass
class Position:
    symbol: str
    qty: float
    entry_price: float
    stop_loss: float
    take_profit: float


class RiskManager:
    def __init__(self, balance: float):
        self.balance = balance
        self.day = date.today()
        self.day_start_balance = balance

    def _roll_day(self) -> None:
        if date.today() != self.day:
            self.day = date.today()
            self.day_start_balance = self.balance

    def daily_loss_hit(self) -> bool:
        """True when today's loss reached the max daily loss limit — stop trading."""
        self._roll_day()
        drawdown = (self.day_start_balance - self.balance) / self.day_start_balance
        return drawdown >= config.MAX_DAILY_LOSS_PCT

    def position_size(self, price: float) -> float:
        """Quantity so that hitting the stop-loss loses only RISK_PER_TRADE of balance."""
        risk_amount = self.balance * config.RISK_PER_TRADE
        loss_per_unit = price * config.STOP_LOSS_PCT
        if loss_per_unit <= 0:
            return 0.0
        qty = risk_amount / loss_per_unit
        # never spend more than the whole balance
        max_qty = self.balance / price
        return round(min(qty, max_qty), 6)

    def open_position(self, symbol: str, price: float) -> Position:
        qty = self.position_size(price)
        return Position(
            symbol=symbol,
            qty=qty,
            entry_price=price,
            stop_loss=price * (1 - config.STOP_LOSS_PCT),
            take_profit=price * (1 + config.TAKE_PROFIT_PCT),
        )

    def check_exit(self, position: Position, price: float) -> str | None:
        if price <= position.stop_loss:
            return "STOP_LOSS"
        if price >= position.take_profit:
            return "TAKE_PROFIT"
        return None

    def settle(self, position: Position, exit_price: float) -> float:
        """Apply closed-trade PnL to the balance and return the PnL."""
        pnl = (exit_price - position.entry_price) * position.qty
        self.balance += pnl
        return pnl
