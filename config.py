"""
Configuración central del bot IBKR.

Todas las constantes y parámetros se leen de variables de entorno
con valores por defecto seguros para paper trading.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Conexión IBKR (TWS / IB Gateway) ───────────────────────────────────────
TWS_HOST = os.getenv("TWS_HOST", "127.0.0.1")
TWS_PORT = int(os.getenv("TWS_PORT", "7497"))        # 7497=paper, 7496=live
CLIENT_ID = int(os.getenv("TWS_CLIENT_ID", "1"))

# ─── Universo de activos ────────────────────────────────────────────────────
# Lista de tickers separados por coma
WATCHLIST = os.getenv("WATCHLIST", "AAPL,MSFT,GOOGL,AMZN,NVDA").split(",")
EXCHANGE = os.getenv("EXCHANGE", "SMART")
CURRENCY = os.getenv("CURRENCY", "USD")

# ─── Gestión de riesgo ──────────────────────────────────────────────────────
MAX_POSITION_SIZE = int(os.getenv("MAX_POSITION_SIZE", "100"))
MAX_PORTFOLIO_PCT = float(os.getenv("MAX_PORTFOLIO_PCT", "0.05"))   # 5% por posición
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.02"))          # 2%
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.04"))      # 4%
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "500.0"))       # USD

# ─── Estrategia ─────────────────────────────────────────────────────────────
SMA_FAST = int(os.getenv("SMA_FAST", "10"))
SMA_SLOW = int(os.getenv("SMA_SLOW", "30"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))

# ─── API keys (para el pipeline de briefing) ────────────────────────────────
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
