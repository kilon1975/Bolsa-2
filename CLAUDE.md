# Instrucciones para Claude — Proyecto Bolsa-2 (Bot IBKR)

## REGLA PRINCIPAL

Este es un proyecto de trading con dinero real. Claude **NUNCA** debe:
- Modificar parámetros de riesgo (`config.py`) sin aprobación explícita del dueño
- Cambiar valores de `STOP_LOSS_PCT`, `TAKE_PROFIT_PCT`, `MAX_DAILY_LOSS` o `MAX_POSITION_SIZE`
- Añadir lógica que ejecute órdenes automáticamente sin validación del RiskManager
- Desactivar, reducir o eludir controles de riesgo en `risk.py`
- Tomar decisiones de inversión, recomendar compras/ventas, ni modificar la estrategia de trading sin revisión humana
- Cambiar el puerto de TWS de paper (7497) a live (7496)

## Qué SÍ puede hacer Claude

- Corregir bugs en el código
- Mejorar la calidad del código (refactoring, tipos, tests)
- Revisar pull requests buscando errores lógicos o de seguridad
- Añadir tests unitarios
- Mejorar documentación y README
- Sugerir mejoras a la estrategia (pero NO implementarlas sin aprobación)
- Responder preguntas sobre la arquitectura del proyecto

## Arquitectura del proyecto

```
main.py          → Punto de entrada unificado
bot.py           → Ciclo de trading
config.py        → Configuración centralizada (.env)
connection.py    → Conexión a IBKR (ib_insync)
strategy.py      → Estrategia SMA crossover + RSI
orders.py        → Gestión de órdenes
risk.py          → Control de riesgo (ARCHIVO CRÍTICO)
briefing.py      → Pipeline Perplexity → Claude → briefing
```

## Reglas de código

- Python 3.11+
- Logging con `logging` estándar (no print en módulos)
- Configuración siempre via `config.py` (nunca hardcodeada)
- Toda orden debe pasar por `RiskManager.check_order()` antes de ejecutarse
- Los cambios en `risk.py`, `orders.py` y `config.py` requieren revisión humana obligatoria
- Commits en español

## Archivos críticos (requieren revisión humana)

- `risk.py` — control de riesgo
- `orders.py` — ejecución de órdenes
- `config.py` — parámetros del bot
- `bot.py` — ciclo principal de trading
- `.github/workflows/claude.yml` — permisos de CI/CD
