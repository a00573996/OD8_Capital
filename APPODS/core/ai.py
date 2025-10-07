# APPODS/core/ai.py
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import os, json, time
import requests  # pip install requests
from .paths import get_data_dir

# ------------------------------------------------------------
# Configuración y utilidades
# ------------------------------------------------------------
CATS_JSON = get_data_dir() / "categorias.json"
CACHE_FILE = get_data_dir() / "resolve_cache.json"
CONFIDENCE_THRESHOLD = 0.65
HTTP_TIMEOUT = 6  # segundos

def _norm(s: str) -> str:
    """Minúsculas + sin acentos para comparaciones robustas."""
    if not isinstance(s, str):
        return ""
    try:
        import unicodedata
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    except Exception:
        pass
    return s.strip().lower()

# Defaults por si no existe categorias.json o está mal
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

# ------------------------------------------------------------
# Carga/recarga de configuración (categorías + keymap)
# ------------------------------------------------------------
def _load_config() -> Tuple[List[str], Dict[str, str]]:
    """Devuelve (CATEGORIAS, KEYMAP_NORMALIZADO)."""
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
    """Recarga categorias.json sin reiniciar la app."""
    global CATEGORIAS, KEYMAP
    CATEGORIAS, KEYMAP = _load_config()
    print("[AI CONFIG] Recargado categorias.json")
    return CATEGORIAS, KEYMAP

# ------------------------------------------------------------
# Caché (para evitar re-búsquedas)
# ------------------------------------------------------------
def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.load(open(CACHE_FILE, "r", encoding="utf-8"))
        except Exception:
            pass
    return {}

def _save_cache(cache: dict):
    try:
        json.dump(cache, open(CACHE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception:
        pass

def _cache_key(texto: str) -> str:
    return _norm(texto)[:128]

# ------------------------------------------------------------
# Enriquecimiento (sin API key): Wikipedia / Nominatim
# ------------------------------------------------------------
def _wiki_summary(query: str) -> Optional[str]:
    """Breve extracto de Wikipedia si existe esa entrada."""
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {"action":"opensearch","search":query,"limit":1,"namespace":0,"format":"json"}
        r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if not data or len(data) < 4 or not data[1]:
            return None
        title = data[1][0]
        url2 = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(title)
        r2 = requests.get(url2, timeout=HTTP_TIMEOUT)
        if r2.ok:
            j = r2.json()
            extract = j.get("extract")
            if extract and isinstance(extract, str) and len(extract) > 20:
                return extract
    except Exception:
        pass
    return None

def _nominatim_summary(query: str) -> Optional[str]:
    """Descripción breve de OpenStreetMap/Nominatim (sin API key)."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1, "addressdetails": 0}
        r = requests.get(url, params=params, headers={"User-Agent":"ZAVE/1.0"}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        arr = r.json()
        if isinstance(arr, list) and arr:
            name = arr[0].get("display_name")
            if name and len(name) > 20:
                return f"Posible lugar/negocio: {name}"
    except Exception:
        pass
    return None

def _quick_enrich(texto: str) -> Optional[str]:
    """Devuelve una descripción corta desde caché/Wikipedia/Nominatim."""
    cache = _load_cache()
    ck = _cache_key(texto)
    hit = cache.get(ck, {})
    if "enriched" in hit:
        return hit.get("enriched") or None

    desc = _wiki_summary(texto)
    if not desc:
        # Intentar con el primer token (a veces es la marca)
        tokens = _norm(texto).split()
        if tokens:
            desc = _wiki_summary(tokens[0])
    if not desc:
        desc = _nominatim_summary(texto)

    hit["enriched"] = desc
    cache[ck] = hit
    _save_cache(cache)
    return desc

# ------------------------------------------------------------
# Mapeo tolerante de salida IA -> categoría oficial
# ------------------------------------------------------------
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
    # Tokens
    for tk in nm.replace(">", " ").replace("/", " ").split():
        if tk and tk in cats_norm:
            return cats_norm[tk]
    return None

# ------------------------------------------------------------
# Clasificación local (fallback)
# ------------------------------------------------------------
def clasificar_local(texto: str) -> str:
    """Clasifica por keymap local: busca claves normalizadas dentro del texto normalizado."""
    t = _norm(texto)
    for k_norm, cat in KEYMAP.items():
        if k_norm and k_norm in t:
            return cat
    return "Otros"

# ------------------------------------------------------------
# IA: paso 1 (categoría + confianza)
# ------------------------------------------------------------
def _ia_guess_category_and_conf(texto: str) -> tuple[Optional[str], Optional[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        cats_list = "\n".join(f"- {c}" for c in CATEGORIAS)

        prompt = f"""
Clasifica el gasto en UNA categoría EXACTA de esta lista y da un nivel de confianza 0–1.

Lista:
{cats_list}

Reglas:
- Devuelve solo JSON con dos claves: {{"categoria":"<una de la lista>", "confianza": 0.x}}
- No inventes categorías nuevas.
- Si dudas, elige la más cercana.

Texto: "{texto}"
"""
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Devuelve JSON válido."},
                      {"role":"user","content":prompt}],
            temperature=0,
            response_format={"type":"json_object"},
            timeout=12,
        )
        raw = chat.choices[0].message.content or ""
        out = json.loads(raw) if raw else {}
        ai_cat = (out.get("categoria") or "").strip()
        conf = out.get("confianza")
        try:
            conf = float(conf) if conf is not None else None
        except Exception:
            conf = None

        match = _best_match(ai_cat)
        if match:
            return match, conf
        return None, conf
    except TypeError:
        # SDK viejo sin response_format: intentamos sin JSON mode
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            cats_list = "\n".join(f"- {c}" for c in CATEGORIAS)
            user = f"""
Devuelve solo JSON: {{"categoria":"<una de la lista>", "confianza": 0.x}}
Lista:
{cats_list}

Texto: "{texto}"
"""
            chat = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"Devuelve JSON válido."},
                          {"role":"user","content":user}],
                temperature=0,
                timeout=12,
            )
            raw = chat.choices[0].message.content or ""
            out = json.loads(raw) if raw else {}
            ai_cat = (out.get("categoria") or "").strip()
            conf = out.get("confianza")
            try:
                conf = float(conf) if conf is not None else None
            except Exception:
                conf = None

            match = _best_match(ai_cat)
            if match:
                return match, conf
        except Exception as e:
            print(f"[IA-STEP1/legacy] error: {e}")
    except Exception as e:
        print(f"[IA-STEP1] error: {e}")
    return None, None

# ------------------------------------------------------------
# IA: paso 2 (reclasificar con contexto enriquecido)
# ------------------------------------------------------------
def _ia_refine_with_context(texto: str, contexto: str) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        cats_list = "\n".join(f"- {c}" for c in CATEGORIAS)
        user = f"""
Usa el siguiente contexto para entender el texto y clasificarlo en UNA categoría EXACTA de la lista.

Contexto:
\"\"\"{contexto}\"\"\"

Lista:
{cats_list}

Reglas:
- Devuelve solo JSON: {{"categoria":"<una de la lista>"}}
- No inventes categorías.

Texto: "{texto}"
"""
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Devuelve JSON válido."},
                {"role":"user","content": user},
            ],
            temperature=0,
            response_format={"type":"json_object"},
            timeout=12,
        )
        raw = chat.choices[0].message.content or ""
        out = json.loads(raw) if raw else {}
        ai_cat = (out.get("categoria") or "").strip()
        match = _best_match(ai_cat)
        return match
    except TypeError:
        # SDK viejo: sin JSON mode
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            cats_list = "\n".join(f"- {c}" for c in CATEGORIAS)
            user2 = f"""
Devuelve solo JSON: {{"categoria":"<una de la lista>"}}
Lista:
{cats_list}

Contexto:
\"\"\"{contexto}\"\"\"

Texto: "{texto}"
"""
            chat = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"Devuelve JSON válido."},
                          {"role":"user","content": user2}],
                temperature=0,
                timeout=12,
            )
            raw = chat.choices[0].message.content or ""
            out = json.loads(raw) if raw else {}
            ai_cat = (out.get("categoria") or "").strip()
            match = _best_match(ai_cat)
            return match
        except Exception as e:
            print(f"[IA-STEP2/legacy] error: {e}")
    except Exception as e:
        print(f"[IA-STEP2] error: {e}")
    return None

# ------------------------------------------------------------
# API pública: clasificar_texto
# ------------------------------------------------------------
def clasificar_texto(texto: str) -> str:
    """
    Flujo:
    1) IA pide categoría y confianza.
    2) Si confianza >= umbral -> esa categoría.
       Si no:
         2a) enriquecer (Wikipedia/Nominatim) + IA refine.
         2b) si falla: fallback local (keymap).
    3) Cachea resultado final para acelerar próximas veces.
    """
    # 0) caché final
    cache = _load_cache()
    ck = _cache_key(texto)
    if ck in cache and "final" in cache[ck]:
        return cache[ck]["final"]

    # 1) IA paso 1
    cat1, conf = _ia_guess_category_and_conf(texto)
    if cat1 and (conf is None or conf >= CONFIDENCE_THRESHOLD):
        final = cat1
    else:
        # 2) enriquecer y refinar
        contexto = _quick_enrich(texto)
        if contexto:
            cat2 = _ia_refine_with_context(texto, contexto)
            final = cat2 if cat2 else clasificar_local(texto)
        else:
            final = clasificar_local(texto)

    # 3) guarda en caché
    cache.setdefault(ck, {})
    cache[ck]["final"] = final
    _save_cache(cache)
    print(f"[FINAL] '{texto}' => '{final}' (conf={conf})")
    return final

# ------------------------------------------------------------
# Depuración
# ------------------------------------------------------------
def debug_ai_config():
    print("JSON de categorías:", CATS_JSON)
    print("Total categorías:", len(CATEGORIAS))
    print("'costco' en KEYMAP:", 'costco' in KEYMAP)
    if 'costco' in KEYMAP:
        print("KEYMAP['costco'] ->", KEYMAP['costco'])
