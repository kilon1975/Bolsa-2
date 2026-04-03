"""
Control de riesgo: validación pre-orden y stop-loss / take-profit.
"""

import logging
from ib_insync import IB, Stock

from config import (
    MAX_POSITION_SIZE, MAX_PORTFOLIO_PCT,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, MAX_DAILY_LOSS,
)

logger = logging.getLogger(__name__)


class RiskManager:
    """Valida órdenes contra las reglas de riesgo antes de ejecutarlas."""

    def __init__(self, ib: IB):
        self.ib = ib
        self.daily_pnl = 0.0

    def check_order(self, contract: Stock, quantity: int, price: float) -> bool:
        """Devuelve True si la orden cumple todas las reglas de riesgo."""
        if quantity > MAX_POSITION_SIZE:
            logger.warning("Rechazada: cantidad %d > máximo %d",
                           quantity, MAX_POSITION_SIZE)
            return False

        if self.daily_pnl <= -MAX_DAILY_LOSS:
            logger.warning("Rechazada: pérdida diaria %.2f >= límite %.2f",
                           abs(self.daily_pnl), MAX_DAILY_LOSS)
            return False

        nlv = self._get_nlv()
        if nlv > 0:
            order_value = quantity * price
            if order_value / nlv > MAX_PORTFOLIO_PCT:
                logger.warning("Rechazada: valor orden %.2f = %.1f%% del portafolio (máx %.1f%%)",
                               order_value, (order_value / nlv) * 100,
                               MAX_PORTFOLIO_PCT * 100)
                return False

        return True

    def calc_stop_loss(self, entry_price: float) -> float:
        return round(entry_price * (1 - STOP_LOSS_PCT), 2)

    def calc_take_profit(self, entry_price: float) -> float:
        return round(entry_price * (1 + TAKE_PROFIT_PCT), 2)

    def update_daily_pnl(self, pnl: float):
        self.daily_pnl = pnl
        if pnl <= -MAX_DAILY_LOSS:
            logger.critical("ALERTA: pérdida diaria %.2f alcanzó el límite", abs(pnl))

    def _get_nlv(self) -> float:
        try:
            summary = self.ib.reqAccountSummary(account="", tag="NetLiquidation")
            self.ib.sleep(0.5)
            nlv = float(summary[0].value) if summary else 0.0
            self.ib.cancelAccountSummary()
            return nlv
        except Exception:
            logger.error("No se pudo obtener NLV")
            return 0.0
