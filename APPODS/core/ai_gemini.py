# APPODS/core/ai_gemini.py
from __future__ import annotations

import os, json
from typing import List, Tuple, Optional, Dict
from .paths import get_data_dir

# (opcional) carga .env si lo usas
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Fallback/local reusando tu ai.py
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

# --- Carga categorías (lista reducida propuesta) ---
def _load_categorias() -> List[str]:
    if CATS_JSON.exists():
        try:
            data = json.load(open(CATS_JSON, "r", encoding="utf-8"))
            cats = data.get("categorias")
            if isinstance(cats, list) and cats:
                return cats
        except Exception:
            pass
    # Fallback mínimo
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

# --- Subsets por dominio (no por marca) ---
SUBSETS: Dict[str, List[str]] = {
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
    "salud": [
        "Salud y Bienestar > Medicinas / Consultas",
        "Compras Personales > Ropa / Electrónica / Hogar",  # por si menciona "farmacia" de retail
    ],
    "compras": [
        "Compras Personales > Ropa / Electrónica / Hogar",
    ],
    "entretenimiento": [
        "Entretenimiento y Ocio > Cine / Streaming / Eventos",
    ],
    "finanzas": [
        "Finanzas y Trámites > Ahorro / Pagos / Impuestos",
    ],
    "impuestos": [
        "Finanzas y Trámites > Ahorro / Pagos / Impuestos",
    ],
}

# --- Léxicos ligeros para detectar dominio (ingredientes y términos genéricos, NO marcas) ---
LEX: Dict[str, List[str]] = {
    "alimentos": [
        # ingredientes / comida genérica
        "atun","atún","salmon","salmón","pollo","carne","pescado","huevo","huevos","leche","yogurt","yoghurt",
        "queso","jamon","jamón","pan","tortilla","arroz","pasta","frijol","frijoles","manzana","platano","plátano",
        "verdura","verduras","fruta","frutas","jitomate","tomate","cebolla","aceite","azucar","azúcar","sal","snack",
        "snacks","botana","botanas","galleta","galletas","cereal","despensa","super","supermercado","tienda",
        # consumo inmediato / cafetería
        "restaurante","restaurant","tacos","taqueria","taquería","hamburguesa","pizza","comida","cafeteria","cafetería",
        "cafe","café","latte","capuchino","capuccino","espresso","rappi","ubereats","didi food","pedido"
    ],
    "mascotas": ["croqueta","croquetas","alimento mascotas","gato","perro","veterinaria","litter","arena","peces","acuario"],
    "transporte": ["uber","didi","taxi","gasolina","gas","parquimetro","parquímetro","metro","metrobús","autobús","camion","camión","estacionamiento","peaje"],
    "vivienda": ["renta","alquiler","cfe","luz","agua","internet","telefonia","telefonía","izzi","telmex","mantenimiento","plomero"],
    "salud": ["doctor","consulta","examen","medicina","medicamento","farmacia","seguro"],
    "compras": ["ropa","calzado","tenis","electronica","electrónica","laptop","celular","hogar"],
    "entretenimiento": ["netflix","spotify","disney","cine","concierto","boletos","videojuego","videojuegos","evento"],
    "finanzas": ["comision","comisión","interes","interés","intereses","inversion","inversión","ahorro","impuesto","sat","trámite","tramite"],
}

def _detect_subset(texto: str) -> Optional[List[str]]:
    t = _norm(texto)
    for group, words in LEX.items():
        if any(w in t for w in words):
            return SUBSETS.get(group)
    return None

# --- Descripciones breves para desambiguar "hogar" ---
DESC = {
    "Alimentos y Bebidas > Supermercado": "Compra de víveres/ingredientes/comestibles para el hogar.",
    "Alimentos y Bebidas > Restaurante / Comida rápida": "Comida preparada para consumo inmediato (restaurante/fast food).",
    "Alimentos y Bebidas > Cafetería / Snacks": "Cafeterías, bebidas de café/té y snacks/bocadillos.",
    "Compras Personales > Ropa / Electrónica / Hogar": "Artículos/objetos (ropa, electrónica, artículos del hogar). No alimentos.",
    "Vivienda y Servicios > Renta / Hogar": "Pago de renta y servicios del inmueble, mantenimiento del hogar (no compras).",
    "Vivienda y Servicios > Servicios básicos (luz, agua, internet)": "Pagos de luz, agua, internet/telefonía.",
    "Salud y Bienestar > Medicinas / Consultas": "Gastos de salud humana (consultas, estudios, medicinas).",
    "Mascotas > Alimento / Cuidado": "Alimento/accesorios/servicios para mascotas.",
    "Transporte > Gasolina / Ride-hailing": "Gasolina y apps de transporte (Uber, Didi).",
    "Transporte > Público / Estacionamiento": "Transporte público, peajes y estacionamientos.",
    "Entretenimiento y Ocio > Cine / Streaming / Eventos": "Cine, conciertos, streaming, eventos.",
    "Finanzas y Trámites > Ahorro / Pagos / Impuestos": "Ahorro/inversión, comisiones bancarias, impuestos/trámites.",
    "Otros": "No encaja en las anteriores."
}

def _build_prompt(texto: str, categorias: List[str]) -> Tuple[str, dict]:
    cat_lines = []
    for c in categorias:
        d = DESC.get(c, "")
        if d:
            cat_lines.append(f"- {c}: {d}")
        else:
            cat_lines.append(f"- {c}")

    examples = (
        '- "salmon" -> "Alimentos y Bebidas > Supermercado"\n'
        '- "pollo" -> "Alimentos y Bebidas > Supermercado"\n'
        '- "croquetas perro" -> "Mascotas > Alimento / Cuidado"\n'
        '- "Starbucks latte" -> "Alimentos y Bebidas > Cafetería / Snacks"\n'
        '- "Uber al aeropuerto" -> "Transporte > Gasolina / Ride-hailing"\n'
        '- "Pago CFE" -> "Vivienda y Servicios > Servicios básicos (luz, agua, internet)"\n'
        '- "Costco compra quincenal" -> "Alimentos y Bebidas > Supermercado"'
    )

    user = f"""
Clasifica el siguiente gasto en UNA categoría EXACTA de la lista.
Reglas:
- Si es ingrediente o comestible (no preparado) ⇒ Supermercado.
- Si es comida preparada para consumo inmediato ⇒ Restaurante / Comida rápida.
- Si es cafetería/bebida/snack ⇒ Cafetería / Snacks.
- "Hogar" en Vivienda se refiere a renta/mantenimiento/servicios del inmueble (no compras).
- "Hogar" en Compras Personales se refiere a artículos/objetos del hogar (no servicios).
- Salud es para personas (no mascotas). Mascotas es su propio rubro.
- Finanzas/Trámites son movimientos financieros, no compras de productos.

Lista (con descripciones cortas):
{chr(10).join(cat_lines)}

Ejemplos:
{examples}

Responde SOLO con una de las opciones de la lista (sin explicación).

Texto: "{texto}"
"""
    config = {
        "response_mime_type": "text/x.enum",
        "response_schema": {
            "type": "STRING",
            "enum": categorias,
        },
        # "thinking_config": {"thinking_budget": 0},  # opcional
    }
    return user, config

def _prefer_local_brand_short(texto: str, cat: str) -> str:
    """Si el texto es muy corto (1-3 tokens) y el local tiene match, preferir local."""
    tokens = _norm(texto).split()
    if 1 <= len(tokens) <= 3:
        loc = clasificar_local(texto)
        if loc != "Otros" and loc != cat:
            return loc
    return cat

def clasificar_texto_gemini(texto: str) -> str:
    """
    Flujo:
    1) Detecta dominio -> reduce enum si aplica.
    2) Llama Gemini con enum (subset o full).
    3) Si la salida no pertenece al dominio esperado, reintenta con subset estricto.
    4) Si persiste, aplica defaults seguros (p.ej., alimentos -> supermercado).
    5) Si el texto es muy corto y el local tiene match, preferir local.
    """
    full = _load_categorias()
    allowed = _detect_subset(texto) or full

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return clasificar_local(texto)

    try:
        from google import genai  # pip install -U google-genai
        client = genai.Client()   # usa GEMINI_API_KEY del entorno

        # 1er intento
        prompt, config = _build_prompt(texto, allowed)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        cat = (resp.text or "").strip()

        # si allowed es subset y la salida no está en allowed, reintenta con subset (más fuerte)
        if allowed is not full and cat not in allowed:
            prompt2, config2 = _build_prompt(texto, allowed)
            resp2 = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt2,
                config=config2,
            )
            cat2 = (resp2.text or "").strip()
            if cat2 in allowed:
                cat = cat2

        # defaults seguros por dominio
        if allowed is not full and cat not in allowed:
            # dominio detectado pero el modelo insistió fuera de subset
            # reglas simples (sin marcas):
            if allowed == SUBSETS["alimentos"]:
                cat = "Alimentos y Bebidas > Supermercado"
            elif allowed == SUBSETS["mascotas"]:
                cat = "Mascotas > Alimento / Cuidado"
            # otros dominios no suelen confundirse tanto; deja tal cual o cae a local
            else:
                cat = clasificar_local(texto)

        # preferir local para textos muy cortos con match claro (ej. "costco")
        cat = _prefer_local_brand_short(texto, cat)

        print(f"[GEMINI] '{texto}' => '{cat}' (subset={'reducido' if allowed is not full else 'full'})")
        return cat if cat in full else clasificar_local(texto)

    except Exception as e:
        print(f"[GEMINI] error: {e} (fallback local)")
        return clasificar_local(texto)

