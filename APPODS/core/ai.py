# APPODS/core/ai.py
from __future__ import annotations
import os, json, re
from typing import List, Optional, Tuple
from .paths import get_data_dir

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
    return [
        "Comida y Bebidas", "Transporte", "Entretenimiento", "Salud",
        "Educación", "Hogar y Servicios", "Compras", "Otros"
    ]

def _build_prompt(texto: str, categorias: List[str], modo_json: bool) -> str:
    lista = "\n".join(f"- {c}" for c in categorias)
    reglas = """
Clasifica el gasto en EXACTAMENTE UNA categoría de la lista. No inventes categorías nuevas.
Si dudas, elige la más cercana por el tipo de gasto (víveres vs comida preparada, transporte app vs público, servicios vs renta, etc.).
    """.strip()
    if modo_json:
        salida = 'Devuelve SOLO JSON: {"categoria":"<una de la lista>"}'
    else:
        salida = "Devuelve SOLO una línea con una etiqueta exacta de la lista."
    ejemplos = """
Ejemplos:
- "Taquería la esquina" -> "Comida y Bebidas"
- "Uber aeropuerto" -> "Transporte"
- "Pago CFE" -> "Hogar y Servicios"
- "Consulta médica" -> "Salud"
- "Netflix plan" -> "Entretenimiento"
- "Audífonos" -> "Compras"
    """.strip()

    return f"""
{reglas}

Lista:
{lista}

{ejemplos}

Texto: "{texto}"

{salida}
"""

def _normalize_to_set(cat: str, allowed: List[str]) -> Optional[str]:
    if not cat:
        return None
    c = cat.strip().lower()
    mapping = {a.strip().lower(): a for a in allowed}
    if c in mapping:
        return mapping[c]
    for k, v in mapping.items():
        if c == k or c in k or k in c:
            return v
    toks = [t for t in re.split(r"[ >/]", c) if t]
    for t in toks:
        for k, v in mapping.items():
            if t and t in k:
                return v
    return None

def _parse_openai_text(raw: str) -> str:
    if not raw:
        return ""
    try:
        obj = json.loads(raw)
        cat = (obj.get("categoria") or "").strip()
        if cat:
            return cat
    except Exception:
        pass
    m = re.search(r'"categoria"\s*:\s*"([^"]+)"', raw, flags=re.I)
    if m:
        return m.group(1).strip()
    line = next((ln.strip("-• ").strip() for ln in raw.splitlines() if ln.strip()), "")
    return line

def clasificar_texto(texto: str) -> str:
    categorias = _load_categorias()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Otros"

    try:
        # pip install -U openai
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Primer intento con JSON mode (si el SDK lo soporta)
        try:
            prompt = _build_prompt(texto, categorias, modo_json=True)
            chat = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"Devuelve JSON válido con la clave 'categoria'."},
                    {"role":"user","content": prompt}
                ],
                temperature=0,
                response_format={"type":"json_object"},
                timeout=15,
            )
            raw = chat.choices[0].message.content or ""
            cat = _parse_openai_text(raw)
            match = _normalize_to_set(cat, categorias)
        except TypeError:
            # SDK sin response_format
            prompt = _build_prompt(texto, categorias, modo_json=True)
            chat = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"Devuelve JSON válido con la clave 'categoria'."},
                    {"role":"user","content": prompt}
                ],
                temperature=0,
                timeout=15,
            )
            raw = chat.choices[0].message.content or ""
            cat = _parse_openai_text(raw)
            match = _normalize_to_set(cat, categorias)

        if not match:
            # Segundo intento estrictísimo (etiqueta pura)
            prompt2 = _build_prompt(texto, categorias, modo_json=False) + \
                      "\n\nResponde ESTRICTAMENTE con una etiqueta exacta de la lista (sin explicación)."
            chat2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt2}],
                temperature=0,
                timeout=15,
            )
            raw2 = chat2.choices[0].message.content or ""
            cat2 = _parse_openai_text(raw2)
            match = _normalize_to_set(cat2, categorias)

        final = match if match else "Otros"
        print(f"[OPENAI] '{texto}' => '{final}'")
        return final
    except Exception as e:
        print(f"[OPENAI] error: {e}")
        return "Otros"
