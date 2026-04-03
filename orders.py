"""
Gestión de órdenes: envío, seguimiento y cancelación.
"""

import logging
from ib_insync import IB, Stock, MarketOrder, LimitOrder, Order

logger = logging.getLogger(__name__)


class OrderManager:
    """Envía y rastrea órdenes a través de la conexión IB."""

    def __init__(self, ib: IB):
        self.ib = ib
        self.active_orders: dict[int, Order] = {}

    def buy_market(self, contract: Stock, quantity: int) -> Order | None:
        order = MarketOrder("BUY", quantity)
        return self._place(contract, order)

    def sell_market(self, contract: Stock, quantity: int) -> Order | None:
        order = MarketOrder("SELL", quantity)
        return self._place(contract, order)

    def buy_limit(self, contract: Stock, quantity: int,
                  price: float) -> Order | None:
        order = LimitOrder("BUY", quantity, price)
        return self._place(contract, order)

    def sell_limit(self, contract: Stock, quantity: int,
                   price: float) -> Order | None:
        order = LimitOrder("SELL", quantity, price)
        return self._place(contract, order)

    def _place(self, contract: Stock, order: Order) -> Order | None:
        try:
            trade = self.ib.placeOrder(contract, order)
            self.active_orders[trade.order.orderId] = trade.order
            logger.info("Orden enviada: %s %s %s x%s (id=%s)",
                        order.action, order.orderType,
                        contract.symbol, order.totalQuantity,
                        trade.order.orderId)
            return trade.order
        except Exception as exc:
            logger.error("Error al enviar orden: %s", exc)
            return None

    def cancel_all(self):
        """Cancela todas las órdenes abiertas."""
        open_orders = self.ib.openOrders()
        for order in open_orders:
            self.ib.cancelOrder(order)
            logger.info("Orden cancelada: id=%s", order.orderId)
        self.active_orders.clear()

    def get_open_orders(self) -> list:
        return self.ib.openOrders()
