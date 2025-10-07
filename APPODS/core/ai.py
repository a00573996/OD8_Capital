# APPODS/core/ai.py
from pathlib import Path
import os
import json

# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def _norm(s: str) -> str:
    """Normaliza a minúsculas y sin acentos para comparar de forma robusta."""
    if not isinstance(s, str):
        return ""
    try:
        import unicodedata
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    except Exception:
        pass
    return s.strip().lower()


# ---------------------------------------------------------------------
# Rutas y defaults
# ---------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # .../ODB_CAPITAL
CATS_JSON = REPO_ROOT / "data" / "categorias.json"

DEFAULT_CATS = [
    "Comida y Bebidas", "Transporte", "Entretenimiento", "Salud",
    "Educación", "Hogar y Servicios", "Compras", "Otros"
]

DEFAULT_KEYMAP = {
    "uber": "Transporte", "didi": "Transporte", "taxi": "Transporte", "gasolina": "Transporte",
    "starbucks": "Comida y Bebidas", "café": "Comida y Bebidas", "pizza": "Comida y Bebidas",
    "restaurant": "Comida y Bebidas", "restaurante": "Comida y Bebidas", "hamburguesa": "Comida y Bebidas",
    "netflix": "Entretenimiento", "cine": "Entretenimiento", "spotify": "Entretenimiento",
    "cfe": "Hogar y Servicios", "luz": "Hogar y Servicios", "agua": "Hogar y Servicios", "internet": "Hogar y Servicios",
    "farmacia": "Compras", "doctor": "Salud", "medicina": "Salud",
    "colegiatura": "Educación", "curso": "Educación", "libro": "Educación",
    "ropa": "Compras", "amazon": "Compras", "mercado": "Compras"
}


# ---------------------------------------------------------------------
# Carga de configuración (JSON opcional)
# ---------------------------------------------------------------------
def _load_config():
    """
    Devuelve (CATEGORIAS, KEYMAP_NORMALIZADO).
    Si existe /data/categorias.json lo usa; si no, usa defaults.
    KEYMAP se devuelve con claves normalizadas (minúsculas/sin acentos).
    """
    if CATS_JSON.exists():
        try:
            with open(CATS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            cats = data.get("categorias")
            keym = data.get("keymap")

            if isinstance(cats, list) and all(isinstance(x, str) for x in cats) and len(cats) > 0:
                categorias = cats
            else:
                categorias = DEFAULT_CATS

            if isinstance(keym, dict) and len(keym) > 0:
                keymap = { _norm(k): v for k, v in keym.items() if isinstance(k, str) and isinstance(v, str) }
            else:
                keymap = { _norm(k): v for k, v in DEFAULT_KEYMAP.items() }
            return categorias, keymap
        except Exception:
            # Si el JSON está mal formado, usar defaults
            pass

    # Defaults (con keymap normalizado)
    return DEFAULT_CATS, { _norm(k): v for k, v in DEFAULT_KEYMAP.items() }


# Expuestos (se cargan al importar)
CATEGORIAS, KEYMAP = _load_config()


def reload_config():
    """Recarga categorias.json sin reiniciar la app (útil si editas el JSON en caliente)."""
    global CATEGORIAS, KEYMAP
    CATEGORIAS, KEYMAP = _load_config()
    return CATEGORIAS, KEYMAP


# ---------------------------------------------------------------------
# Clasificación
# ---------------------------------------------------------------------
def clasificar_local(texto: str) -> str:
    """
    Clasificador local por palabras clave (rápido y sin internet).
    Busca cada clave normalizada dentro del texto normalizado.
    """
    t = _norm(texto)
    for k_norm, cat in KEYMAP.items():
        if k_norm and k_norm in t:
            return cat
    return "Otros"


def clasificar_texto(texto: str) -> str:
    """
    Devuelve UNA categoría (de CATEGORIAS).
    - Si hay OPENAI_API_KEY: intenta OpenAI (gpt-4o-mini)
    - Si falla o no hay API key: usa clasificar_local()
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

        # Extraer JSON de la respuesta
        out_text = resp.output[0].content[0].text  # tipo string JSON
        out = json.loads(out_text)

        cat = (out.get("categoria") or "Otros").strip()
        # Validar contra la lista actual (por si el modelo inventa algo fuera)
        return cat if cat in CATEGORIAS else "Otros"

    except Exception:
        # Cualquier error (sin red, timeout, cuota, etc.) -> fallback local
        return clasificar_local(texto)


# ---------------------------------------------------------------------
# (Opcional) Depuración
# ---------------------------------------------------------------------
def debug_ai_config():
    """
    Imprime en consola datos útiles para depurar configuración de categorías.
    Llama a esta función desde donde prefieras si necesitas diagnosticar.
    """
    print("JSON de categorías:", CATS_JSON)
    print("Total categorías:", len(CATEGORIAS))
    print("Ejemplo: contiene 'costco' en KEYMAP:", 'costco' in KEYMAP)
    if 'costco' in KEYMAP:
        print("   KEYMAP['costco'] ->", KEYMAP['costco'])

