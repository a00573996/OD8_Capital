# APPODS/core/ai.py
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import os, json
from .paths import get_data_dir

# ---------------- Utilidades ----------------
def _norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    try:
        import unicodedata
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    except Exception:
        pass
    return s.strip().lower()

# ---------------- Rutas y defaults ----------------
CATS_JSON = get_data_dir() / "categorias.json"

DEFAULT_CATS: List[str] = [
    "Comida y Bebidas", "Transporte", "Entretenimiento", "Salud",
    "Educación", "Hogar y Servicios", "Compras", "Otros"
]
DEFAULT_KEYMAP: Dict[str, str] = {
    "uber":"Transporte","didi":"Transporte","taxi":"Transporte","gasolina":"Transporte",
    "starbucks":"Comida y Bebidas","cafe":"Comida y Bebidas","café":"Comida y Bebidas","pizza":"Comida y Bebidas",
    "restaurant":"Comida y Bebidas","restaurante":"Comida y Bebidas","hamburguesa":"Comida y Bebidas",
    "netflix":"Entretenimiento","cine":"Entretenimiento","spotify":"Entretenimiento",
    "cfe":"Hogar y Servicios","luz":"Hogar y Servicios","agua":"Hogar y Servicios","internet":"Hogar y Servicios",
    "farmacia":"Compras","doctor":"Salud","medicina":"Salud",
    "colegiatura":"Educación","curso":"Educación","libro":"Educación",
    "ropa":"Compras","amazon":"Compras","mercado":"Compras"
}

# ---------------- Carga config (JSON opcional) ----------------
def _load_config() -> Tuple[List[str], Dict[str, str]]:
    if CATS_JSON.exists():
        try:
            data = json.load(open(CATS_JSON, "r", encoding="utf-8"))
            cats = data.get("categorias")
            keym = data.get("keymap")
            categorias = cats if isinstance(cats, list) and cats else DEFAULT_CATS
            if isinstance(keym, dict) and keym:
                keymap = { _norm(k): v for k, v in keym.items() if isinstance(k, str) and isinstance(v, str) }
            else:
                keymap = { _norm(k): v for k, v in DEFAULT_KEYMAP.items() }
            return categorias, keymap
        except Exception as e:
            print(f"[AI CONFIG] Error leyendo {CATS_JSON}: {e}. Uso defaults.")
    return DEFAULT_CATS, { _norm(k): v for k, v in DEFAULT_KEYMAP.items() }

CATEGORIAS, KEYMAP = _load_config()

def reload_config() -> Tuple[List[str], Dict[str, str]]:
    global CATEGORIAS, KEYMAP
    CATEGORIAS, KEYMAP = _load_config()
    print("[AI CONFIG] Recargado categorias.json")
    return CATEGORIAS, KEYMAP

# ---------------- Mapeo tolerante ----------------
def _norm_map_categorias() -> Dict[str, str]:
    return { _norm(c): c for c in CATEGORIAS }

def _best_match(ai_cat: str) -> Optional[str]:
    if not ai_cat:
        return None
    nm = _norm(ai_cat)
    cats_norm = _norm_map_categorias()
    if nm in cats_norm:
        return cats_norm[nm]
    for k, original in cats_norm.items():
        if nm == k or nm in k or k in nm:
            return original
    for tk in nm.replace(">", " ").replace("/", " ").split():
        if tk and tk in cats_norm:
            return cats_norm[tk]
    return None

# ---------------- Clasificación ----------------
def clasificar_local(texto: str) -> str:
    t = _norm(texto)
    for k_norm, cat in KEYMAP.items():
        if k_norm and k_norm in t:
            return cat
    return "Otros"

def _build_chat_messages(texto: str):
    sys = ("Eres un asistente que clasifica gastos en UNA sola categoría EXACTA "
           "desde una lista específica. Devuelve siempre JSON válido.")
    cats_list = "\n".join(f"- {c}" for c in CATEGORIAS)
    examples = (
        '- "Starbucks latte" -> "Alimentos > Cafetería"\n'
        '- "Uber al aeropuerto" -> "Transporte > Ride-hailing"\n'
        '- "Pago CFE" -> "Vivienda/Servicios > Luz"\n'
        '- "Costco compra quincenal" -> "Alimentos > Supermercado"\n'
        '- "Netflix" -> "Entretenimiento > Streaming"\n'
        '- "Farmacia Guadalajara ibuprofeno" -> "Compras > Farmacia/Perfumería"'
    )
    user = f"""
Clasifica el siguiente gasto en UNA categoría EXACTA de esta lista (elige literalmente una):

{cats_list}

Reglas:
- Devuelve SOLO JSON válido con una clave: {{ "categoria": "<UNA de la lista arriba>" }}
- No inventes categorías nuevas.
- Si dudas, elige la más cercana.

Ejemplos:
{examples}

Texto: "{texto}"
"""
    return [{"role":"system","content":sys},{"role":"user","content":user}]

def clasificar_texto(texto: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            messages = _build_chat_messages(texto)

            # 1) Intento con JSON mode (SDK reciente)
            try:
                chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"},
                    timeout=12,
                )
            except TypeError:
                # 2) Fallback: sin response_format (SDK más viejo)
                chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    timeout=12,
                )

            raw = chat.choices[0].message.content or ""
            try:
                out = json.loads(raw)
            except Exception:
                out = {}

            ai_cat = (out.get("categoria") or "").strip()
            match = _best_match(ai_cat)
            if match:
                print(f"[IA] '{texto}' -> '{ai_cat}' => '{match}'")
                return match
            else:
                print(f"[IA] sin match válido: '{ai_cat}', caigo a local")
        except Exception as e:
            print(f"[IA] error: {e} (caigo a local)")

    cat_local = clasificar_local(texto)
    print(f"[LOCAL] '{texto}' -> '{cat_local}'")
    return cat_local

# ---------------- Depuración ----------------
def debug_ai_config():
    print("JSON de categorías:", CATS_JSON)
    print("Total categorías:", len(CATEGORIAS))
    print("'costco' en KEYMAP:", 'costco' in KEYMAP)
    if 'costco' in KEYMAP:
        print("KEYMAP['costco'] ->", KEYMAP['costco'])

