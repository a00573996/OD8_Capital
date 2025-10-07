# APPODS/core/ai.py
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import os
import json

# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def _norm(s: str) -> str:
    """Normaliza a minúsculas y sin acentos para comparaciones robustas."""
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

DEFAULT_CATS: List[str] = [
    "Comida y Bebidas", "Transporte", "Entretenimiento", "Salud",
    "Educación", "Hogar y Servicios", "Compras", "Otros"
]

DEFAULT_KEYMAP: Dict[str, str] = {
    "uber": "Transporte", "didi": "Transporte", "taxi": "Transporte", "gasolina": "Transporte",
    "starbucks": "Comida y Bebidas", "cafe": "Comida y Bebidas", "café": "Comida y Bebidas", "pizza": "Comida y Bebidas",
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
def _load_config() -> Tuple[List[str], Dict[str, str]]:
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
        except Exception as e:
            print(f"[AI CONFIG] Error leyendo {CATS_JSON}: {e}. Uso defaults.")

    # Defaults (con keymap normalizado)
    return DEFAULT_CATS, { _norm(k): v for k, v in DEFAULT_KEYMAP.items() }


# Expuestos (se cargan al importar)
CATEGORIAS, KEYMAP = _load_config()


def reload_config() -> Tuple[List[str], Dict[str, str]]:
    """Recarga categorias.json sin reiniciar la app (útil si editas el JSON en caliente)."""
    global CATEGORIAS, KEYMAP
    CATEGORIAS, KEYMAP = _load_config()
    print("[AI CONFIG] Recargado categorias.json")
    return CATEGORIAS, KEYMAP


# ---------------------------------------------------------------------
# Helpers de mapeo tolerante para salida de IA
# ---------------------------------------------------------------------
def _norm_map_categorias() -> Dict[str, str]:
    """Devuelve un mapa normalizado -> categoría original exacta."""
    return { _norm(c): c for c in CATEGORIAS }

def _best_match(ai_cat: str) -> Optional[str]:
    """
    Intenta casar la salida de la IA con una categoría válida, de forma tolerante.
    - match exacto normalizado
    - contains/begins con tokens
    - tokens simples (ej. 'supermercado', 'cafe', 'gasolina')
    """
    if not ai_cat:
        return None
    nm = _norm(ai_cat)
    cats_norm = _norm_map_categorias()

    # 1) Match exacto (normalizado)
    if nm in cats_norm:
        return cats_norm[nm]

    # 2) Heurística: contains / begins / ends
    for k, original in cats_norm.items():
        if nm == k:
            return original
        if nm in k or k in nm:
            return original

    # 3) Tokens
    tokens = nm.replace(">", " ").replace("/", " ").split()
    for tk in tokens:
        if tk and tk in cats_norm:
            return cats_norm[tk]

    return None

def _extract_json_text(resp) -> str:
    """Lee el JSON string de la respuesta de OpenAI (Responses API o Chat Completions)."""
    # Responses API (openai>=1.x)
    try:
        return resp.output[0].content[0].text
    except Exception:
        pass
    # Chat Completions
    try:
        return resp.choices[0].message.content
    except Exception:
        return ""


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
    Intenta IA primero. Ajusta la salida de IA a la categoría más cercana.
    Si no hay API key o hay error o no se puede casar la salida, usa local.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            # Few-shot + lista cerrada
            prompt = f"""
Clasifica el siguiente gasto en UNA categoría EXACTA de esta lista (elige literalmente una):

{chr(10).join('- ' + c for c in CATEGORIAS)}

Reglas:
- Devuelve SOLO JSON válido con una clave: {{ "categoria": "<UNA de la lista arriba>" }}
- No inventes categorías nuevas.
- Si dudas, elige la más cercana.

Ejemplos:
- "Starbucks latte" -> "Alimentos > Cafetería"
- "Uber al aeropuerto" -> "Transporte > Ride-hailing"
- "Pago CFE" -> "Vivienda/Servicios > Luz"
- "Costco compra quincenal" -> "Alimentos > Supermercado"
- "Netflix" -> "Entretenimiento > Streaming"
- "Farmacia Guadalajara ibuprofeno" -> "Compras > Farmacia/Perfumería"

Texto: "{texto}"
            """

            # Responses API
            resp = client.responses.create(
                model="gpt-4o-mini",
                input=prompt,
                response_format={"type": "json_object"},
                timeout=12,
            )

            raw = _extract_json_text(resp)
            out = json.loads(raw) if raw else {}
            ai_cat = (out.get("categoria") or "").strip()

            match = _best_match(ai_cat)
            if match:
                print(f"[IA] '{texto}' -> '{ai_cat}' => '{match}'")
                return match
            else:
                print(f"[IA] sin match válido: '{ai_cat}', caigo a local")
        except Exception as e:
            print(f"[IA] error: {e} (caigo a local)")

    # Fallback local
    cat_local = clasificar_local(texto)
    print(f"[LOCAL] '{texto}' -> '{cat_local}'")
    return cat_local


# ---------------------------------------------------------------------
# Depuración
# ---------------------------------------------------------------------
def debug_ai_config():
    """
    Imprime en consola datos útiles para depurar configuración de categorías.
    Llama a esta función desde donde prefieras si necesitas diagnosticar.
    """
    print("JSON de categorías:", CATS_JSON)
    print("Total categorías:", len(CATEGORIAS))
    has_costco = 'costco' in KEYMAP
    print("KEYMAP contiene 'costco':", has_costco)
    if has_costco:
        print("KEYMAP['costco'] ->", KEYMAP.get('costco'))
