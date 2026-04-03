"""
Conexión y gestión del ciclo de vida con IBKR vía ib_insync.
"""

import logging
from ib_insync import IB, Stock, util

from config import (
    TWS_HOST, TWS_PORT, CLIENT_ID,
    WATCHLIST, EXCHANGE, CURRENCY,
)

logger = logging.getLogger(__name__)


class IBKRConnection:
    """Wrapper sobre ib_insync.IB con reconexión y helpers."""

    def __init__(self):
        self.ib = IB()

    # ── Conexión ─────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Conecta a TWS / IB Gateway. Devuelve True si tuvo éxito."""
        try:
            self.ib.connect(TWS_HOST, TWS_PORT, clientId=CLIENT_ID)
            logger.info("Conectado a IBKR en %s:%s (client %s)",
                        TWS_HOST, TWS_PORT, CLIENT_ID)
            return True
        except Exception as exc:
            logger.error("Error al conectar a IBKR: %s", exc)
            return False

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()
            logger.info("Desconectado de IBKR")

    @property
    def is_connected(self) -> bool:
        return self.ib.isConnected()

    # ── Contratos ────────────────────────────────────────────────────────

    def make_contract(self, symbol: str) -> Stock:
        """Crea un contrato de tipo Stock para el símbolo dado."""
        return Stock(symbol, EXCHANGE, CURRENCY)

    def get_watchlist_contracts(self) -> list[Stock]:
        """Devuelve contratos para todos los tickers del watchlist."""
        return [self.make_contract(s.strip()) for s in WATCHLIST]

    # ── Datos de mercado ─────────────────────────────────────────────────

    def get_bars(self, contract: Stock, duration: str = "30 D",
                 bar_size: str = "1 day") -> list:
        """Solicita barras históricas para un contrato."""
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        logger.info("Recibidas %d barras para %s", len(bars), contract.symbol)
        return bars

    def get_portfolio(self) -> list:
        """Devuelve las posiciones actuales de la cuenta."""
        self.ib.reqPositions()
        util.sleep(1)
        return self.ib.positions()

    def get_account_summary(self) -> dict:
        """Devuelve un resumen de la cuenta (NLV, cash disponible, etc.)."""
        tags = "NetLiquidation,AvailableFunds,BuyingPower,UnrealizedPnL,RealizedPnL"
        summary = self.ib.reqAccountSummary(account="", tag=tags)
        util.sleep(1)
        result = {}
        for item in summary:
            result[item.tag] = float(item.value)
        self.ib.cancelAccountSummary()
        return result
