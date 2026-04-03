# Bolsa-2 — Bot IBKR + Briefing de Mercado

Bot de trading automatizado para Interactive Brokers con pipeline de briefing inteligente (Perplexity + Claude).

## Arquitectura

```
main.py             ← Punto de entrada unificado
├── bot.py          ← Ciclo de trading (conexión, evaluación, órdenes)
│   ├── config.py       ← Configuración centralizada (.env)
│   ├── connection.py   ← Conexión a TWS / IB Gateway (ib_insync)
│   ├── strategy.py     ← Estrategia SMA crossover + RSI
│   ├── orders.py       ← Gestión de órdenes (market / limit)
│   └── risk.py         ← Control de riesgo (posición, portafolio, stop-loss)
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
# ─── Bot de trading ──────────────────────────────────

# Modo continuo (ciclo cada 5 minutos)
python main.py bot

# Un solo ciclo
python main.py bot --once

# Con briefing de mercado al inicio
python main.py bot --briefing

# Intervalo personalizado (60 segundos)
python main.py bot --interval 60

# ─── Briefing de mercado ─────────────────────────────

# Briefing general (índices, noticias, factores macro)
python main.py briefing

# Briefing con tema personalizado
python main.py briefing "Análisis del sector tech y semiconductores"
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
| `PERPLEXITY_API_KEY` | — | API key de Perplexity (opcional, para briefing) |
| `ANTHROPIC_API_KEY` | — | API key de Anthropic (opcional, para briefing) |

## Estrategia

- **SMA Crossover**: SMA(10) cruza SMA(30) → señal de compra/venta
- **Filtro RSI(14)**: Compra adicional en sobreventa (<30), venta en sobrecompra (>70)
- **Risk management**: Límites por posición, portafolio y pérdida diaria
- **Stop-loss / Take-profit**: 2% SL, 4% TP automáticos por operación
