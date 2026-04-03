#!/usr/bin/env python3
"""
Punto de entrada unificado del proyecto Bolsa-2.

Modos de ejecución:
  python main.py bot             → Inicia el bot de trading IBKR
  python main.py bot --once      → Un solo ciclo de trading
  python main.py bot --briefing  → Bot + briefing de mercado al inicio
  python main.py briefing        → Solo el briefing (Perplexity + Claude)
  python main.py briefing "tema" → Briefing con tema personalizado
"""

import sys


def print_usage():
    print("""
Uso: python main.py <comando> [opciones]

Comandos:
  bot       Inicia el bot de trading IBKR
  briefing  Genera un briefing de mercado (Perplexity + Claude)

Opciones del bot:
  --once              Ejecutar un solo ciclo y salir
  --briefing          Generar briefing antes de operar
  --interval SECS     Segundos entre ciclos (default: 300)

Ejemplos:
  python main.py bot
  python main.py bot --once --briefing
  python main.py briefing
  python main.py briefing "Análisis del sector tech"
""".strip())


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_usage()
        sys.exit(0)

    command = sys.argv[1]

    if command == "bot":
        # Pasar argumentos restantes al bot
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        from bot import main as bot_main
        bot_main()

    elif command == "briefing":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        from briefing import run as run_briefing
        run_briefing(topic)

    else:
        print(f"Comando desconocido: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
