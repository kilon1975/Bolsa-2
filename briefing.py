#!/usr/bin/env python3
"""
Pipeline: Perplexity API → procesamiento → Claude API → Briefing en texto.

Consulta información actualizada del mercado bursátil vía Perplexity,
luego genera un briefing ejecutivo estructurado con Claude.
"""

import sys
import json
from datetime import datetime

import requests
import anthropic

from config import PERPLEXITY_API_KEY, ANTHROPIC_API_KEY

# ─── Paso 1: Consulta a Perplexity ──────────────────────────────────────────

def query_perplexity(topic: str) -> dict:
    """Consulta la API de Perplexity para obtener información actualizada."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un analista financiero. Proporciona datos concretos, "
                    "cifras, porcentajes y fuentes. Responde en español."
                ),
            },
            {"role": "user", "content": topic},
        ],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ─── Paso 2: Procesamiento intermedio ────────────────────────────────────────

def extract_perplexity_data(raw: dict) -> dict:
    """Extrae el contenido y las citas de la respuesta de Perplexity."""
    choice = raw["choices"][0]["message"]
    content = choice.get("content", "")
    citations = raw.get("citations", [])
    return {
        "content": content,
        "citations": citations,
        "model": raw.get("model", "unknown"),
        "retrieved_at": datetime.now().isoformat(),
    }


# ─── Paso 3: Generación del briefing con Claude ─────────────────────────────

def generate_briefing(data: dict) -> str:
    """Envía los datos procesados a Claude para generar el briefing final."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""A continuación tienes información financiera recopilada de fuentes en línea.
Genera un **briefing ejecutivo** claro y estructurado en español.

## Datos recopilados
{data['content']}

## Fuentes
{json.dumps(data['citations'], indent=2, ensure_ascii=False)}

---

El briefing debe incluir:
1. **Resumen del mercado** – panorama general en 2-3 líneas.
2. **Datos clave** – cifras, índices y variaciones relevantes.
3. **Factores y riesgos** – elementos que influyen en el mercado.
4. **Perspectiva** – tendencia esperada a corto plazo.

Usa formato limpio con secciones y bullets. Sé conciso y directo."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ─── Pipeline principal ─────────────────────────────────────────────────────

def run(topic: str | None = None):
    if not PERPLEXITY_API_KEY or not ANTHROPIC_API_KEY:
        print("Error: configura PERPLEXITY_API_KEY y ANTHROPIC_API_KEY en .env")
        sys.exit(1)

    if topic is None:
        topic = (
            "Dame un resumen actualizado del mercado bursátil hoy: "
            "principales índices (S&P 500, Nasdaq, Dow Jones, IBEX 35), "
            "movimientos destacados, noticias relevantes y factores macro."
        )

    print("⏳ Consultando Perplexity…")
    raw = query_perplexity(topic)

    print("🔄 Procesando datos…")
    data = extract_perplexity_data(raw)

    print("🤖 Generando briefing con Claude…\n")
    briefing = generate_briefing(data)

    print("=" * 60)
    print(f" BRIEFING DE MERCADO — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(briefing)
    print("=" * 60)
    print(f"\nFuente Perplexity: modelo {data['model']}")
    if data["citations"]:
        print("Referencias:")
        for i, url in enumerate(data["citations"], 1):
            print(f"  [{i}] {url}")

    return briefing


if __name__ == "__main__":
    custom_topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run(custom_topic)
