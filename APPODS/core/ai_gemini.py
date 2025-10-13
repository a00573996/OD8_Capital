# APPODS/core/ai_gemini.py
from __future__ import annotations
import os
import json
import re
from typing import List, Optional
from pathlib import Path

# Se asume que google-genai ya está instalado
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Por favor, instala el SDK de Gemini: pip install google-genai")
    genai = None
    types = None

# --- Configuración y Carga de Categorías ---

# Implementación placeholder para Path (ajusta esto a tu estructura real)
def get_data_dir() -> Path:
    """Devuelve el directorio de datos de la aplicación."""
    # En un entorno real, esto podría ser Path.home() / ".appods"
    return Path(os.environ.get("APP_DATA_DIR", "."))

CATS_JSON = get_data_dir() / "categorias.json"

def _load_categorias() -> List[str]:
    """Carga categorías desde JSON o usa un fallback por defecto."""
    if CATS_JSON.exists():
        try:
            with open(CATS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            cats = data.get("categorias")
            if isinstance(cats, list) and cats:
                return cats
        except Exception:
            pass
    
    # Fallback por defecto
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

# --- Construcción del Prompt y Normalización ---

def _build_prompt(texto: str, categorias: List[str]) -> str:
    """Construye el prompt de usuario con ejemplos y la lista de categorías."""
    lista = "\n".join(f"- {c}" for c in categorias)
    ejemplos = """
Ejemplos:
- "Costco compra quincenal" -> "Alimentos y Bebidas > Supermercado"
- "Starbucks latte" -> "Alimentos y Bebidas > Cafetería / Snacks"
- "Taquería (cena)" -> "Alimentos y Bebidas > Restaurante / Comida rápida"
- "Uber al aeropuerto" -> "Transporte > Gasolina / Ride-hailing"
- "Pago CFE" -> "Vivienda y Servicios > Servicios básicos (luz, agua, internet)"
- "Consulta médica general" -> "Salud y Bienestar > Medicinas / Consultas"
- "Audífonos electrónicos" -> "Compras Personales > Ropa / Electrónica / Hogar"
- "Botella de tequila (para casa)" -> "Alimentos y Bebidas > Supermercado"
- "Centenario Plata" -> "Alimentos y Bebidas > Supermercado"
- "Despensa del mes" -> "Alimentos y Bebidas > Supermercado"
    """.strip()

    return f"""
Lista de categorías válidas:
{lista}

{ejemplos}

Clasifica el siguiente gasto: "{texto}"
"""

def _normalize_to_set(cat: str, allowed: List[str]) -> Optional[str]:
    """Normaliza la salida del modelo a una categoría válida."""
    if not cat:
        return None
    c = cat.strip().lower()
    mapping = {a.strip().lower(): a for a in allowed}
    
    # 1) Coincidencia exacta (o casi)
    if c in mapping:
        return mapping[c]
    
    # 2) Coincidencia por contenido (más flexible)
    for k, v in mapping.items():
        if c in k or k in c:
            return v
            
    return None

# --- Función Principal con Correcciones y Logging Detallado ---

def clasificar_texto_gemini(texto: str) -> str:
    """
    Clasifica un texto de gasto usando la API de Gemini con Native JSON Mode 
    e imprime el procedimiento detallado en la terminal para depuración.
    """
    if genai is None or types is None:
        return "Otros" # Fallback si el SDK no está disponible
        
    categorias = _load_categorias()
    api_key = os.getenv("GEMINI_API_KEY")
    final = "Otros" # Fallback inicial

    if not api_key:
        print("[GEMINI] ❌ ERROR: GEMINI_API_KEY no configurada. Devolviendo 'Otros'.")
        return final

    try:
        client = genai.Client(api_key=api_key)

        # 1. Definición del System Instruction (Instrucciones Imperativas)
        system_instruction = f"""
ACTÚA COMO UN CLASIFICADOR DE GASTOS ESTRICTO. Debes clasificar el siguiente gasto en EXACTAMENTE UNA categoría de la lista. ESTÁ PROHIBIDO inventar o modificar categorías. SIEMPRE elige la opción más cercana.

Reglas de decisión:
- Víveres, ingredientes, y **bebidas alcohólicas para consumo en casa (ej: tequila, vino, cerveza)** ⇒ Supermercado.
- Comida preparada para consumo inmediato ⇒ Restaurante / Comida rápida.
- Café/bebidas de cafetería/snacks ⇒ Cafetería / Snacks.
- Transporte por app o gasolina ⇒ Gasolina / Ride-hailing.
- Transporte público/peajes/estacionamiento ⇒ Público / Estacionamiento.
- Servicios del hogar (luz/agua/internet) ⇒ Servicios básicos.
- Renta/mantenimiento del inmueble ⇒ Renta / Hogar.
- Salud humana (consultas, medicinas) ⇒ Medicinas / Consultas.
- Artículos (ropa/electrónica/hogar) ⇒ Compras Personales.
- Mascotas ⇒ Mascotas > Alimento / Cuidado.
- Streaming/eventos/cine ⇒ Entretenimiento.
- Ahorro/pagos bancarios/impuestos ⇒ Finanzas/Trámites.
- En caso de duda razonable (no hay opción cercana), utiliza la categoría "Otros".
"""
        
        # 2. Definición del Esquema JSON (ENUM restringe la salida a categorías válidas)
        json_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "categoria": types.Schema(
                    type=types.Type.STRING,
                    description="La categoría exacta del gasto elegida de la lista.",
                    enum=categorias 
                )
            },
            required=["categoria"],
        )
        
        # 3. Construcción del Prompt y Logging
        prompt = _build_prompt(texto, categorias)
        
        print("\n" + "=" * 80)
        print(f"[GEMINI PROCESO] 📩 Enviando solicitud para gasto: '{texto}'")
        print("--- SYSTEM INSTRUCTION ---")
        print(system_instruction.strip())
        print("--- USER PROMPT (incluye ejemplos) ---")
        print(prompt.strip())
        print("--- CONFIGURATION ---")
        print(f"Modelo: gemini-2.5-flash | Temperature: 0.0 (Determinista)")
        print(f"JSON Schema Enum (Categorías): {len(categorias)} opciones")
        print("-" * 50)


        # 4. Llamada a la API
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=json_schema,
                temperature=0.0, # Temperatura 0 para ser menos creativo
            ),
        )
        
        # 5. Procesamiento y Logging de la Respuesta
        print(f"[GEMINI PROCESO] 📬 Respuesta RAW de la API:")
        print(resp.text)
        print("-" * 50)
        
        try:
            raw_json = json.loads(resp.text)
            cat = (raw_json.get("categoria") or "").strip()
            
            # Validación final de la lógica de negocio
            match = _normalize_to_set(cat, categorias)
            final = match if match else "Otros"

        except json.JSONDecodeError:
            print(f"[GEMINI PROCESO] ⚠️ ERROR: La respuesta no es un JSON válido o no se ajusta al esquema.")

    except Exception as e:
        print(f"[GEMINI PROCESO] ❌ ERROR CRÍTICO en la API (Conexión/Auth): {e}")
        
    print(f"[GEMINI RESULTADO] ✅ '{texto}' clasificado como: '{final}'")
    print("=" * 80 + "\n")
    return final