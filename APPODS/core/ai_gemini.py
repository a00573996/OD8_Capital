# APPODS/core/ai_gemini.py
from __future__ import annotations

import os, json
from typing import List, Tuple, Optional
from .paths import get_data_dir

# Reuso de fallback local si lo tienes
try:
    from .ai import clasificar_local
except Exception:
    def clasificar_local(texto: str) -> str:
        return "Otros"

CATS_JSON = get_data_dir() / "categorias.json"

def _load_categorias() -> List[str]:
    if CATS_JSON.exists():
        try:
            data = json.load(open(CATS_JSON, "r", encoding="utf-8"))
            cats = data.get("categorias")
            if isinstance(cats, list) and cats:
                return cats
        except Exception:
            pass
    # Fallback mínimo para no romper
    return ["Comida y Bebidas", "Transporte", "Entretenimiento", "Salud",
            "Educación", "Hogar y Servicios", "Compras", "Otros"]

def _build_prompt(texto: str, categorias: List[str]) -> Tuple[str, dict]:
    # Usamos Structured Output → enum (respuesta estrictamente 1 opción)
    # https://ai.google.dev/gemini-api/docs/structured-output
    # response_mime_type: "text/x.enum" + response_schema enum -> el modelo devuelve exactamente un string de esa lista.
    cats_list = "\n".join(f"- {c}" for c in categorias)
    user = f"""
Clasifica el siguiente gasto en UNA categoría EXACTA de la lista. 
Responde SOLO con una de las opciones (sin explicación).

Lista:
{cats_list}

Texto: "{texto}"
"""
    config = {
        "response_mime_type": "text/x.enum",
        "response_schema": {
            "type": "STRING",
            "enum": categorias,  # fuerza a elegir 1
        },
        # Opcional: desactivar "thinking" para menor latencia/costo
        # "thinking_config": {"thinking_budget": 0},
    }
    return user, config

def clasificar_texto_gemini(texto: str) -> str:
    """
    Devuelve UNA categoría usando Gemini con enum estricto.
    Si falla algo (sin API key, error de red/SDK), usa clasificar_local.
    """
    categorias = _load_categorias()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # sin key: cae a local
        return clasificar_local(texto)

    try:
        # SDK nuevo (GA): google-genai
        # Quickstart: https://ai.google.dev/gemini-api/docs/quickstart
        from google import genai

        client = genai.Client()  # toma GEMINI_API_KEY del entorno
        prompt, config = _build_prompt(texto, categorias)

        # Modelo recomendado para velocidad/costo en clasificación
        # (puedes cambiar a "gemini-2.5-pro" si quieres más precisión).
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        # Con enum, la respuesta viene en resp.text como 1 string de la lista
        cat = (resp.text or "").strip()
        # Validación defensiva: asegurar que pertenece a la lista
        if cat in categorias:
            return cat
        return clasificar_local(texto)
    except Exception as e:
        print(f"[GEMINI] error: {e} (fallback local)")
        return clasificar_local(texto)

