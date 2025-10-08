# APPODS/core/ai_gemini.py
from __future__ import annotations

import os, json
from typing import List, Tuple, Optional
from .paths import get_data_dir

# (opcional) cargar .env si lo usas
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

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
    """
    Usamos Structured Output con ENUM para forzar que el modelo devuelva
    exactamente una de las categorías de tu lista.
    """
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
        # "thinking_config": {"thinking_budget": 0},  # opcional: latencia/costo
    }
    return user, config

def clasificar_texto_gemini(texto: str) -> str:
    """
    Devuelve UNA categoría usando Gemini (enum estricto).
    Si falla (sin API key, error de red/SDK), usa clasificar_local.
    """
    categorias = _load_categorias()

    # La API key se debe exponer como GEMINI_API_KEY en el entorno
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return clasificar_local(texto)

    try:
        # SDK nuevo (GA): google-genai
        # pip install -U google-genai
        from google import genai

        client = genai.Client()  # toma GEMINI_API_KEY del entorno
        prompt, config = _build_prompt(texto, categorias)

        # Modelo recomendado rápido/económico para clasificación
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        # Con enum, la respuesta viene en resp.text como 1 string de la lista
        cat = (resp.text or "").strip()
        if cat in categorias:
            print(f"[GEMINI] '{texto}' => '{cat}'")
            return cat
        print(f"[GEMINI] respuesta fuera de lista: '{cat}' (fallback local)")
        return clasificar_local(texto)
    except Exception as e:
        print(f"[GEMINI] error: {e} (fallback local)")
        return clasificar_local(texto)
