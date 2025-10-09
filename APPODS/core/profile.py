# core/profile.py — manejo de perfil de usuario (JSON)
from __future__ import annotations
import json, re
from datetime import datetime
from typing import Any, Dict
from .paths import get_data_dir

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _default_profile() -> Dict[str, Any]:
    return {
        "usuario": {
            "nombre": "",
            "edad": 18,
            "genero": "No especificar",
            "ubicacion": {"pais": "MX", "ciudad": ""},
            "email": ""
        },
        "ingresos": {
            "frecuencia": "Mensual",
            "fijo_mensual": 0.0
        },
        "situacion": {
            "ocupacion": "Estudiante",
            "dependientes": 0,
            "vivienda": {"tipo": "Renta", "gasto_mensual": 0.0},
            "transporte": "Público",
            "mascotas": {"tiene": False, "tipo": ""},
            "gasto_fijo_mensual": 0.0,
            "deudas": {
                "tiene": False,
                "tipos": [],
                "pago_mensual_total": 0.0
            },
            "habitos": {
                "comer_fuera": 0,
                "cafe_fuera": 0,
                "compras_online": 0
            }
        },
        "metas": {
            "principal": "Ahorro de emergencia",
            "monto_objetivo": 0.0,
            "horizonte_meses": 6,
            "aportacion_mensual": 0.0,
            "fondo_emergencia_meses": 3
        },
        "preferencias": {
            "recordatorios": {"activo": False, "frecuencia": "Semanal"},
            "alertas_sobrepresupuesto": {"activo": False, "umbral_porcentaje": 15},
            "consentimiento_datos_locales": True
        },
        "ultima_actualizacion": ""
    }

def _profile_path():
    return get_data_dir() / "user_profile.json"

def load_profile() -> Dict[str, Any]:
    path = _profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        prof = _default_profile()
        save_profile(prof)
        return prof
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = _default_profile()
    # patch: asegurar claves mínimas
    default = _default_profile()
    def deep_merge(base, dflt):
        if isinstance(base, dict) and isinstance(dflt, dict):
            for k, v in dflt.items():
                if k not in base:
                    base[k] = v
                else:
                    base[k] = deep_merge(base[k], v)
        return base
    return deep_merge(data, default)

def save_profile(profile: Dict[str, Any]) -> None:
    profile = dict(profile or {})
    profile["ultima_actualizacion"] = datetime.now().isoformat(timespec="seconds")
    p = _profile_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def is_valid_email(email: str) -> bool:
    if not email:
        return True  # opcional
    return EMAIL_RE.match(email) is not None

def to_float(s: Any) -> float:
    if s is None:
        return 0.0
    if isinstance(s, (int, float)):
        return float(s)
    txt = str(s).strip()
    if not txt:
        return 0.0
    for ch in ["$", "MXN", "USD", "€", " "]:
        txt = txt.replace(ch, "")
    # 1.234,56 → 1234.56
    if "," in txt and "." not in txt:
        txt = txt.replace(".", "")
        txt = txt.replace(",", ".")
    else:
        txt = txt.replace(",", "")
    try:
        return float(txt)
    except Exception:
        return 0.0

def to_int(s: Any, default: int = 0) -> int:
    try:
        return int(float(str(s).strip()))
    except Exception:
        return default

