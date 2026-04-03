"""
Estrategia de trading basada en cruces de SMA + filtro RSI.

Señales:
  BUY  → SMA rápida cruza por encima de SMA lenta Y RSI < zona de sobrecompra
  SELL → SMA rápida cruza por debajo de SMA lenta O RSI > zona de sobrecompra
  HOLD → en cualquier otro caso
"""

import logging
import pandas as pd

from config import SMA_FAST, SMA_SLOW, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD

logger = logging.getLogger(__name__)


def compute_sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def compute_rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def bars_to_df(bars) -> pd.DataFrame:
    """Convierte barras de ib_insync a DataFrame."""
    data = [{"date": b.date, "open": b.open, "high": b.high,
             "low": b.low, "close": b.close, "volume": b.volume}
            for b in bars]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def evaluate(bars) -> str:
    """
    Evalúa barras históricas y devuelve la señal: 'BUY', 'SELL' o 'HOLD'.
    """
    df = bars_to_df(bars)

    if len(df) < SMA_SLOW + 1:
        logger.warning("Datos insuficientes (%d barras, necesita %d)",
                       len(df), SMA_SLOW + 1)
        return "HOLD"

    df["sma_fast"] = compute_sma(df["close"], SMA_FAST)
    df["sma_slow"] = compute_sma(df["close"], SMA_SLOW)
    df["rsi"] = compute_rsi(df["close"])

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    sma_cross_up = (prev["sma_fast"] <= prev["sma_slow"] and
                    latest["sma_fast"] > latest["sma_slow"])
    sma_cross_down = (prev["sma_fast"] >= prev["sma_slow"] and
                      latest["sma_fast"] < latest["sma_slow"])
    rsi_val = latest["rsi"]

    if sma_cross_up and rsi_val < RSI_OVERBOUGHT:
        logger.info("Señal BUY — SMA cruce alcista, RSI=%.1f", rsi_val)
        return "BUY"
    elif rsi_val < RSI_OVERSOLD and not sma_cross_down:
        logger.info("Señal BUY — RSI=%.1f en sobreventa", rsi_val)
        return "BUY"
    elif sma_cross_down or rsi_val > RSI_OVERBOUGHT:
        logger.info("Señal SELL — SMA cruce bajista o RSI=%.1f sobrecomprado", rsi_val)
        return "SELL"
    else:
        logger.debug("Señal HOLD — SMA_fast=%.2f, SMA_slow=%.2f, RSI=%.1f",
                      latest["sma_fast"], latest["sma_slow"], rsi_val)
        return "HOLD"
