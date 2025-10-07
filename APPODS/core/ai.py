# APPODS/core/ai.py
from pathlib import Path
import os, json

# --------- Carga de configuración desde /data/categorias.json ---------
REPO_ROOT = Path(__file__).resolve().parents[2]
CATS_JSON = REPO_ROOT / "data" / "categorias.json"

DEFAULT_CATS = [
    "Comida y Bebidas","Transporte","Entretenimiento","Salud",
    "Educación","Hogar y Servicios","Compras","Otros"
]
DEFAULT_KEYMAP = {
    "uber":"Transporte","didi":"Transporte","taxi":"Transporte","gasolina":"Transporte",
    "starbucks":"Comida y Bebidas","café":"Comida y Bebidas","pizza":"Comida y Bebidas",
    "restaurant":"Comida y Bebidas","restaurante":"Comida y Bebidas","hamburguesa":"Comida y Bebidas",
    "netflix":"Entretenimiento","cine":"Entretenimiento","spotify":"Entretenimiento",
    "cfe":"Hogar y Servicios","luz":"Hogar y Servicios","agua":"Hogar y Servicios","internet":"Hogar y Servicios",
    "farmacia":"Salud","doctor":"Salud","medicina":"Salud",
    "colegiatura":"Educación","curso":"Educación","libro":"Educación",
    "ropa":"Compras","amazon":"Compras","mercado":"Compras"
}

def _load_config():
    # Devuelve (categorias, keymap) desde JSON si existe, si no defaults
    if CATS_JSON.exists():
        try:
            with open(CATS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            cats = data.get("categorias")
            keym = data.get("keymap")
            if isinstance(cats, list) and all(isinstance(x, str) for x in cats):
                categorias = cats
            else:
                categorias = DEFAULT_CATS
            if isinstance(keym, dict):
                keymap = keym
            else:
                keymap = DEFAULT_KEYMAP
            return categorias, keymap
        except Exception:
            pass
    return DEFAULT_CATS, DEFAULT_KEYMAP

# Expuestos para usar en la app
CATEGORIAS, KEYMAP = _load_config()

def reload_config():
    """Permite recargar si editas categorias.json sin reiniciar la app."""
    global CATEGORIAS, KEYMAP
    CATEGORIAS, KEYMAP = _load_config()
    return CATEGORIAS, KEYMAP

# --------- Clasificación (fallback local + OpenAI si hay API key) ---------
def clasificar_local(texto: str) -> str:
    t = (texto or "").lower()
    for k, cat in KEYMAP.items():
        if k in t:
            return cat
    return "Otros"

def clasificar_texto(texto: str) -> str:
    """
    Devuelve UNA categoría (de CATEGORIAS).
    Usa OpenAI si hay API key; si falla/no hay, usa clasificar_local().
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return clasificar_local(texto)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
        Eres un asistente que clasifica gastos en UNA sola categoría de esta lista:
        {", ".join(CATEGORIAS)}.
        Responde exclusivamente con JSON: {{"categoria": "<una_de_las_categorias>"}}

        Texto a clasificar: "{texto}"
        """
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            response_format={"type": "json_object"},
            timeout=12,
        )
        out = json.loads(resp.output[0].content[0].text)
        cat = (out.get("categoria") or "Otros").strip()
        return cat if cat in CATEGORIAS else "Otros"
    except Exception:
        return clasificar_local(texto)


