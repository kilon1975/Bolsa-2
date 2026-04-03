#!/usr/bin/env python3
"""
Bot IBKR — punto de entrada principal.

Ciclo:
  1. Conecta a TWS / IB Gateway
  2. Para cada ticker del watchlist, descarga barras y evalúa la estrategia
  3. Si hay señal BUY/SELL, valida riesgo y envía la orden
  4. Opcionalmente genera un briefing de mercado con Perplexity + Claude
  5. Repite cada ciclo según el intervalo configurado
"""

import sys
import time
import logging
import argparse
from datetime import datetime

from config import LOG_LEVEL, LOG_FILE, WATCHLIST, PERPLEXITY_API_KEY, ANTHROPIC_API_KEY
from connection import IBKRConnection
from strategy import evaluate
from orders import OrderManager
from risk import RiskManager

# ─── Logging ─────────────────────────────────────────────────────────────────

def setup_logging():
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=fmt,
                        handlers=handlers)

# ─── Ciclo principal ─────────────────────────────────────────────────────────

def run_cycle(conn: IBKRConnection, order_mgr: OrderManager,
              risk_mgr: RiskManager):
    """Ejecuta un ciclo de evaluación para todos los tickers."""
    logger = logging.getLogger("bot")
    account = conn.get_account_summary()
    nlv = account.get("NetLiquidation", 0)
    logger.info("NLV: $%.2f | Cash: $%.2f | PnL no realizado: $%.2f",
                nlv, account.get("AvailableFunds", 0),
                account.get("UnrealizedPnL", 0))

    realized = account.get("RealizedPnL", 0)
    risk_mgr.update_daily_pnl(realized)

    contracts = conn.get_watchlist_contracts()
    for contract in contracts:
        symbol = contract.symbol
        try:
            bars = conn.get_bars(contract)
            if not bars:
                logger.warning("Sin datos para %s, saltando", symbol)
                continue

            signal = evaluate(bars)
            logger.info("[%s] Señal: %s", symbol, signal)

            last_price = bars[-1].close
            qty = min(int((nlv * 0.05) / last_price), 100) if last_price > 0 else 0
            if qty == 0:
                continue

            if signal == "BUY":
                if risk_mgr.check_order(contract, qty, last_price):
                    order_mgr.buy_market(contract, qty)
                    sl = risk_mgr.calc_stop_loss(last_price)
                    tp = risk_mgr.calc_take_profit(last_price)
                    logger.info("[%s] Compra x%d @ ~%.2f | SL=%.2f | TP=%.2f",
                                symbol, qty, last_price, sl, tp)
            elif signal == "SELL":
                # Solo vender si tenemos posición
                positions = conn.get_portfolio()
                held = sum(p.position for p in positions
                           if p.contract.symbol == symbol)
                if held > 0:
                    sell_qty = min(int(held), qty)
                    order_mgr.sell_market(contract, sell_qty)
                    logger.info("[%s] Venta x%d @ ~%.2f", symbol, sell_qty, last_price)

        except Exception as exc:
            logger.error("[%s] Error en ciclo: %s", symbol, exc)


def run_briefing():
    """Genera el briefing de mercado si las API keys están configuradas."""
    logger = logging.getLogger("bot")
    if not PERPLEXITY_API_KEY or not ANTHROPIC_API_KEY:
        logger.info("Briefing omitido: faltan API keys de Perplexity/Anthropic")
        return
    try:
        from briefing import run as run_briefing_pipeline
        run_briefing_pipeline()
    except Exception as exc:
        logger.error("Error generando briefing: %s", exc)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bot de trading IBKR")
    parser.add_argument("--interval", type=int, default=300,
                        help="Segundos entre ciclos (default: 300)")
    parser.add_argument("--once", action="store_true",
                        help="Ejecutar un solo ciclo y salir")
    parser.add_argument("--briefing", action="store_true",
                        help="Generar briefing de mercado al inicio")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("bot")
    logger.info("=" * 50)
    logger.info("Bot IBKR iniciado — %s", datetime.now().strftime("%Y-%m-%d %H:%M"))
    logger.info("Watchlist: %s", ", ".join(WATCHLIST))
    logger.info("=" * 50)

    if args.briefing:
        run_briefing()

    conn = IBKRConnection()
    if not conn.connect():
        logger.critical("No se pudo conectar a IBKR. Abortando.")
        sys.exit(1)

    order_mgr = OrderManager(conn.ib)
    risk_mgr = RiskManager(conn.ib)

    try:
        while True:
            run_cycle(conn, order_mgr, risk_mgr)
            if args.once:
                break
            logger.info("Esperando %d segundos…", args.interval)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Interrumpido por el usuario")
    finally:
        order_mgr.cancel_all()
        conn.disconnect()
        logger.info("Bot detenido")


if __name__ == "__main__":
    main()
