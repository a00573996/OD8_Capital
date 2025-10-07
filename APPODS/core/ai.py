# APPODS/core/ai.py
import os, json

CATEGORIAS = [
    "Comida y Bebidas","Transporte","Entretenimiento","Salud",
    "Educación","Hogar y Servicios","Compras","Otros"
]

# Fallback local simple por palabras clave
KEYMAP = {
    "uber":"Transporte","didi":"Transporte","taxi":"Transporte","gasolina":"Transporte",
    "starbucks":"Comida y Bebidas","café":"Comida y Bebidas","pizza":"Comida y Bebidas",
    "restaurant":"Comida y Bebidas","restaurante":"Comida y Bebidas","hamburguesa":"Comida y Bebidas",
    "netflix":"Entretenimiento","cine":"Entretenimiento","spotify":"Entretenimiento",
    "cfe":"Hogar y Servicios","luz":"Hogar y Servicios","agua":"Hogar y Servicios","internet":"Hogar y Servicios",
    "farmacia":"Salud","doctor":"Salud","medicina":"Salud",
    "colegiatura":"Educación","curso":"Educación","libro":"Educación",
    "ropa":"Compras","amazon":"Compras","mercado":"Compras"
}

def clasificar_local(texto: str) -> str:
    t = (texto or "").lower()
    for k, cat in KEYMAP.items():
        if k in t:
            return cat
    return "Otros"

def clasificar_texto(texto: str) -> str:
    """
    Devuelve UNA categoría de CATEGORIAS.
    Usa OpenAI si hay API key. Si falla o no hay key, usa fallback local.
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

