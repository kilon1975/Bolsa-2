# CLAUDE.md

## Proyecto
Este repositorio contiene un bot de trading para Interactive Brokers hecho para dinero propio.

## Límites
- Nunca automatizar trading real sin revisión humana.
- Nunca agregar código que envíe órdenes reales por defecto.
- Priorizar paper trading, simulación y revisión manual.
- No tocar secretos, tokens, claves o credenciales.
- No imprimir secretos en logs, comentarios o artifacts.
- No modificar reglas de riesgo sin explicarlo claramente.
- No fusionar cambios a main sin revisión humana.

## Qué sí puede hacer Claude
- Mejorar código Python.
- Corregir errores.
- Mejorar README y documentación.
- Agregar tests.
- Proponer mejoras de estructura.
- Revisar pull requests.
- Ayudar con GitHub Actions seguras.

## Qué debe cuidar
- Cambios pequeños y fáciles de revisar.
- Explicar el objetivo del cambio.
- Señalar riesgos si toca sizing, stop loss, target, ejecución o conexión con broker.
- Mantener el proyecto simple para un usuario principiante.

## Arquitectura

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

## Archivos críticos (requieren revisión humana)
- `risk.py` — control de riesgo
- `orders.py` — ejecución de órdenes
- `config.py` — parámetros del bot
- `bot.py` — ciclo principal de trading
- `.env` / `.env.example` — credenciales
- `.github/workflows/` — permisos de CI/CD
