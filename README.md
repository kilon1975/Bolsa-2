# Bolsa-2 — Bot IBKR + Briefing de Mercado

Bot de trading automatizado para Interactive Brokers con pipeline de briefing inteligente (Perplexity + Claude).

## Arquitectura

```
bot.py              ← Punto de entrada principal (ciclo de trading)
├── config.py       ← Configuración centralizada (.env)
├── connection.py   ← Conexión a TWS / IB Gateway (ib_insync)
├── strategy.py     ← Estrategia SMA crossover + RSI
├── orders.py       ← Gestión de órdenes (market / limit)
├── risk.py         ← Control de riesgo (posición, portafolio, stop-loss)
└── briefing.py     ← Pipeline Perplexity API → Claude API → briefing
```

## Requisitos

- Python 3.11+
- TWS o IB Gateway corriendo (puerto 7497 para paper, 7496 para live)
- Cuenta IBKR con API habilitada

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus configuraciones
```

## Uso

```bash
# Ejecutar bot en modo continuo (cada 5 minutos)
python bot.py

# Un solo ciclo
python bot.py --once

# Con briefing de mercado al inicio
python bot.py --briefing

# Intervalo personalizado (60 segundos)
python bot.py --interval 60

# Solo briefing (sin bot)
python briefing.py
python briefing.py "Análisis del sector tech"
```

## Configuración (.env)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `TWS_HOST` | `127.0.0.1` | Host de TWS/Gateway |
| `TWS_PORT` | `7497` | Puerto (7497=paper, 7496=live) |
| `TWS_CLIENT_ID` | `1` | ID de cliente |
| `WATCHLIST` | `AAPL,MSFT,GOOGL,AMZN,NVDA` | Tickers a monitorear |
| `MAX_POSITION_SIZE` | `100` | Máx. acciones por orden |
| `MAX_PORTFOLIO_PCT` | `0.05` | Máx. % del portafolio por posición |
| `STOP_LOSS_PCT` | `0.02` | Stop loss (2%) |
| `TAKE_PROFIT_PCT` | `0.04` | Take profit (4%) |
| `MAX_DAILY_LOSS` | `500` | Pérdida diaria máxima (USD) |
| `PERPLEXITY_API_KEY` | — | API key de Perplexity (opcional) |
| `ANTHROPIC_API_KEY` | — | API key de Anthropic (opcional) |

## Estrategia

- **SMA Crossover**: SMA(10) cruza SMA(30) → señal de compra/venta
- **Filtro RSI(14)**: Evita compras en sobrecompra (>70) y ventas en sobreventa (<30)
- **Risk management**: Límites por posición, portafolio y pérdida diaria
