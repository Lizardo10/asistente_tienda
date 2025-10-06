import os
from typing import Optional
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

client = None
if OpenAI and os.getenv("OPENAI_API_KEY"):
    client = OpenAI()

def ask_openai(prompt: str) -> str:
    """
    Devuelve respuesta del modelo si hay API Key, si no, responde simulado.
    """
    if client is None:
        return "🤖 (Simulado) Entiendo tu consulta: " + prompt[:120]
    try:
        # Usamos Responses API (model moderno). Cambia el nombre del modelo si deseas.
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Eres un asistente de soporte amable y breve."},
                      {"role":"user","content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"(OpenAI error) {e}"
