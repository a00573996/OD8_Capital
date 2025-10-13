# APPODS/core/ai_gemini.py — versión universal compatible con cualquier SDK
from __future__ import annotations
import os, json
from typing import List, Optional, Dict
from .paths import get_data_dir

# (opcional) .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Fallback/local
try:
    from .ai import clasificar_local, _norm
except Exception:
    import unicodedata
    def _norm(s: str) -> str:
        if not isinstance(s, str):
            return ""
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        return s.strip().lower()
    def clasificar_local(texto: str) -> str:
        return "Otros"

CATS_JSON = get_data_dir() / "categorias.json"

# --- Carga categorías ---
def _load_categorias() -> List[str]:
    if CATS_JSON.exists():
        try:
            data = json.load(open(CATS_JSON, "r", encoding="utf-8"))
            cats = data.get("categorias")
            if isinstance(cats, list) and cats:
                return cats
        except Exception:
            pass
    return [
        "Alimentos y Bebidas > Supermercado",
        "Alimentos y Bebidas > Restaurante / Comida rápida",
        "Alimentos y Bebidas > Cafetería / Snacks",
        "Transporte > Gasolina / Ride-hailing",
        "Transporte > Público / Estacionamiento",
        "Vivienda y Servicios > Renta / Hogar",
        "Vivienda y Servicios > Servicios básicos (luz, agua, internet)",
        "Salud y Bienestar > Medicinas / Consultas",
        "Compras Personales > Ropa / Electrónica / Hogar",
        "Mascotas > Alimento / Cuidado",
        "Entretenimiento y Ocio > Cine / Streaming / Eventos",
        "Finanzas y Trámites > Ahorro / Pagos / Impuestos",
        "Otros"
    ]

# --- Léxico / subsets ---
LEX = {
    "alimentos": ["super","restaurante","cafe","café","comida","pizza","hamburguesa","taquería"],
    "mascotas": ["perro","gato","veterinaria","croquetas"],
    "transporte": ["uber","didi","gasolina","taxi","metro","camión"],
    "vivienda": ["renta","cfe","agua","internet","telmex","izzi"],
    "salud": ["doctor","farmacia","consulta","medicina","seguro"],
    "compras": ["ropa","amazon","electronica","electrónica","tenis","hogar"],
    "entretenimiento": ["cine","netflix","spotify","disney","evento"],
    "finanzas": ["impuesto","sat","ahorro","inversion","inversión","banco"],
}
SUBSETS = {
    "alimentos": [
        "Alimentos y Bebidas > Supermercado",
        "Alimentos y Bebidas > Restaurante / Comida rápida",
        "Alimentos y Bebidas > Cafetería / Snacks",
    ],
    "mascotas": ["Mascotas > Alimento / Cuidado"],
    "transporte": [
        "Transporte > Gasolina / Ride-hailing",
        "Transporte > Público / Estacionamiento",
    ],
    "vivienda": [
        "Vivienda y Servicios > Renta / Hogar",
        "Vivienda y Servicios > Servicios básicos (luz, agua, internet)",
    ],
    "salud": ["Salud y Bienestar > Medicinas / Consultas"],
    "compras": ["Compras Personales > Ropa / Electrónica / Hogar"],
    "entretenimiento": ["Entretenimiento y Ocio > Cine / Streaming / Eventos"],
    "finanzas": ["Finanzas y Trámites > Ahorro / Pagos / Impuestos"],
}

def _detect_subset(texto: str) -> Optional[List[str]]:
    t = _norm(texto)
    for k, words in LEX.items():
        if any(w in t for w in words):
            return SUBSETS.get(k)
    return None

def _prefer_local_brand_short(texto: str, cat: str) -> str:
    tokens = _norm(texto).split()
    if 1 <= len(tokens) <= 3:
        loc = clasificar_local(texto)
        if loc != "Otros" and loc != cat:
            return loc
    return cat

# --- Prompt Gemini ---
def _build_prompt(texto: str, categorias: List[str]) -> str:
    lista = "\n".join(f"- {c}" for c in categorias)
    return f"""
Clasifica el gasto en UNA categoría de la lista.
Devuelve SOLO el texto exacto de la categoría (sin comillas, sin explicación).

Lista:
{lista}

Ejemplos:
- "Uber viaje" -> "Transporte > Gasolina / Ride-hailing"
- "Starbucks latte" -> "Alimentos y Bebidas > Cafetería / Snacks"
- "Pago CFE" -> "Vivienda y Servicios > Servicios básicos (luz, agua, internet)"

Texto: "{texto}"
Respuesta:
""".strip()

# --- Llamada universal a Gemini ---
def _call_gemini(prompt: str) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        # Determina cuál interfaz está disponible
        if hasattr(client, "responses"):
            # SDK moderno
            resp = client.responses.generate(
                model="gemini-2.0-flash",
                input=prompt,
                generation_config={"temperature": 0.0},
            )
            out = getattr(resp, "text", None)
        else:
            # SDK clásico
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                generation_config={"temperature": 0.0},
            )
            out = getattr(resp, "text", None)

        if not out and hasattr(resp, "candidates"):
            try:
                out = resp.candidates[0].content.parts[0].text
            except Exception:
                out = None
        return (out or "").strip()
    except Exception as e:
        print(f"[GEMINI] error generate_content: {e}")
        return None

# --- Clasificador principal ---
def clasificar_texto_gemini(texto: str) -> str:
    full = _load_categorias()
    allowed = _detect_subset(texto) or full

    prompt = _build_prompt(texto, allowed)
    cat = _call_gemini(prompt)

    # Reintento con subset
    if not cat or cat not in allowed:
        if allowed is not full:
            cat2 = _call_gemini(_build_prompt(texto, allowed))
            if cat2 and cat2 in allowed:
                cat = cat2

    # Defaults seguros
    if not cat and allowed is not full:
        if allowed == SUBSETS["alimentos"]:
            cat = "Alimentos y Bebidas > Supermercado"
        elif allowed == SUBSETS["mascotas"]:
            cat = "Mascotas > Alimento / Cuidado"

    if not cat:
        cat = clasificar_local(texto)

    cat = _prefer_local_brand_short(texto, cat)
    print(f"[GEMINI] '{texto}' => '{cat}' (subset={'reducido' if allowed is not full else 'full'})")
    return cat if cat in full else clasificar_local(texto)
