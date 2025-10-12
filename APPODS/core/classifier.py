# core/classifier.py — clasifica al usuario con base en profile.json (MXN)

from __future__ import annotations
from typing import Dict, Any

def _to_float(x, default=0.0) -> float:
    try:
        if x is None: return float(default)
        if isinstance(x, str): x = x.replace(",", "").replace("$", "").strip()
        return float(x)
    except Exception:
        return float(default)

def _to_int(x, default=0) -> int:
    try:
        return int(float(x))
    except Exception:
        return int(default)

# ---------- Etiquetadores ----------
def _segmento_ingreso(imt: float) -> str:
    if imt < 10_000: return "Bajo"
    if imt < 20_000: return "Medio bajo"
    if imt < 40_000: return "Medio"
    if imt < 80_000: return "Medio alto"
    return "Alto"

def _estabilidad_ingreso(vi: float) -> str:
    vi_pct = vi * 100
    if vi_pct < 5:   return "Fijo"
    if vi_pct < 20:  return "Baja volatilidad"
    if vi_pct < 40:  return "Media"
    return "Alta"

def _carga_vivienda(cv: float) -> str:
    cv_pct = cv * 100
    if cv_pct < 20:  return "Baja"
    if cv_pct < 30:  return "Moderada"
    if cv_pct < 45:  return "Alta"
    return "Crítica"

def _carga_deuda(dsr: float) -> str:
    dsr_pct = dsr * 100
    if dsr_pct == 0: return "Sin deuda"
    if dsr_pct < 10: return "Baja"
    if dsr_pct < 20: return "Moderada"
    if dsr_pct < 35: return "Alta"
    return "Crítica"

def _carga_fijos(cf: float) -> str:
    cf_pct = cf * 100
    if cf_pct < 20:  return "Ligera"
    if cf_pct < 35:  return "Sostenible"
    if cf_pct < 50:  return "Pesada"
    return "Estrés"

def _capacidad_ahorro(ca: float) -> str:
    ca_pct = ca * 100
    if ca_pct <= 0:  return "Nula"
    if ca_pct <= 10: return "Baja"
    if ca_pct <= 20: return "Media"
    if ca_pct <= 30: return "Buena"
    return "Muy buena"

def _perfil_consumo(igd: float, comer: int, cafe: int, online: int) -> Dict[str, Any]:
    if igd < 25:  nivel = "Bajo"
    elif igd < 60: nivel = "Medio"
    else:         nivel = "Alto"
    tags = []
    if comer >= 3:  tags.append("Foodie")
    if cafe >= 3:   tags.append("Café lover")
    if online >= 3: tags.append("Onliner")
    return {"IGD": round(igd, 1), "nivel": nivel, "tags": tags}

def _ratio_aporte(monto_obj: float, meses: int, aport: float) -> float:
    if meses <= 0 or monto_obj <= 0: return 0.0
    req = monto_obj / meses
    if req <= 0: return 0.0
    return max(0.0, aport / req)

def _aporte_label(ratio: float) -> str:
    if ratio < 0.5:  return "Aporte insuficiente"
    if ratio <= 1.0: return "Alineado"
    return "Sobre-meta"

def _persona(labels: Dict[str, str], consumo: Dict[str, Any], dependientes: int) -> str:
    dep_txt = "con dependientes" if dependientes and dependientes > 0 else "sin dependientes"
    cons_txt = consumo["nivel"].lower()
    return f"Ingreso {labels['segmento_ingreso'].lower()}, vivienda {labels['carga_vivienda'].lower()}, deuda {labels['carga_deuda'].lower()}, discrecional {cons_txt}, {dep_txt}"

def _prioridades(ca: float, cv: float, dsr: float, consumo: Dict[str, Any], vi: float) -> list[str]:
    out = []
    if ca <= 0 or cv > 0.45 or dsr > 0.35:
        out.append("Flujo esencial: bajar vivienda/fijos, negociar deudas y micro-presupuesto")
    if dsr >= 0.20:
        out.append("Estrategia de deudas (avalancha/bola de nieve) y tope de discrecional")
    # Fondo de emergencia según estabilidad
    if vi > 0.40:
        out.append("Fondo de emergencia 6–12 meses por ingreso volátil")
    else:
        out.append("Fondo de emergencia 3–6 meses")
    if consumo["nivel"] == "Alto":
        out.append("Límites a ‘comer fuera/café/online’ con alertas al 80%")
    return out

# ---------- Núcleo ----------
def classify_user(state: Dict[str, Any]) -> Dict[str, Any]:
    u    = state.get("usuario", {})
    ing  = state.get("ingresos", {})
    sit  = state.get("situacion", {})
    meta = state.get("metas", {})

    fijo = _to_float(ing.get("fijo_mensual", 0.0))
    vars_list = ing.get("variables", []) or []
    var_sum = sum(_to_float(v.get("monto", 0.0)) for v in vars_list)
    imt = max(0.0, fijo + var_sum)

    vivienda_gasto = _to_float((sit.get("vivienda") or {}).get("gasto_mensual", 0.0))
    deuda_pago     = _to_float((sit.get("deudas") or {}).get("pago_mensual_total", 0.0))
    gasto_fijo     = _to_float(sit.get("gasto_fijo_mensual", 0.0))

    vi = (var_sum / imt) if imt > 0 else 0.0
    cv = (vivienda_gasto / imt) if imt > 0 else 0.0
    dsr = (deuda_pago / imt) if imt > 0 else 0.0
    cf  = (gasto_fijo / imt) if imt > 0 else 0.0
    ca_amount = max(0.0, imt - (vivienda_gasto + deuda_pago + gasto_fijo))
    ca = (ca_amount / imt) if imt > 0 else 0.0

    hab = sit.get("habitos", {}) or {}
    comer  = _to_int(hab.get("comer_fuera", 0))
    cafe   = _to_int(hab.get("cafe_fuera", 0))
    online = _to_int(hab.get("compras_online", 0))
    igd = ((comer + cafe + online) / 15.0) * 100.0

    # Metas
    monto_obj  = _to_float(meta.get("monto_objetivo", 0.0))
    meses      = _to_int(meta.get("horizonte_meses", 0))
    aport_mens = _to_float(meta.get("aportacion_mensual", 0.0))
    ratio_ap   = _ratio_aporte(monto_obj, meses, aport_mens)

    # Labels
    labels = {
        "segmento_ingreso": _segmento_ingreso(imt),
        "estabilidad_ingreso": _estabilidad_ingreso(vi),
        "carga_vivienda": _carga_vivienda(cv),
        "carga_deuda": _carga_deuda(dsr),
        "carga_fijos": _carga_fijos(cf),
        "capacidad_ahorro": _capacidad_ahorro(ca),
        "aporte_meta": _aporte_label(ratio_ap),
    }
    consumo = _perfil_consumo(igd, comer, cafe, online)
    dependientes = _to_int(sit.get("dependientes", 0))
    persona_str = _persona(labels, consumo, dependientes)
    prios = _prioridades(ca, cv, dsr, consumo, vi)

    return {
        "generated_from": "profile.json",
        "metrics": {
            "ingreso_total_mensual": round(imt, 2),
            "ingreso_fijo": round(fijo, 2),
            "ingreso_variables": round(var_sum, 2),
            "volatilidad_ingreso": round(vi, 4),
            "carga_vivienda": round(cv, 4),
            "carga_deuda": round(dsr, 4),
            "carga_fijos": round(cf, 4),
            "capacidad_ahorro_pct": round(ca, 4),
            "capacidad_ahorro_mxn": round(ca_amount, 2),
            "IGD": round(igd, 1),
            "meta_objetivo": round(monto_obj, 2),
            "meta_meses": meses,
            "aportacion_mensual": round(aport_mens, 2),
            "ratio_aporte": round(ratio_ap, 3),
        },
        "labels": labels,
        "perfil_consumo": consumo,
        "etapa_vida": {
            "ocupacion": (sit.get("ocupacion") or "N/D"),
            "dependientes": dependientes
        },
        "vivienda": (sit.get("vivienda") or {}).get("tipo", "N/D"),
        "movilidad": sit.get("transporte", "N/D"),
        "mascotas": "Sí" if (sit.get("mascotas") or {}).get("tiene") else "No",
        "metas": {
            "principal": meta.get("principal", "N/D"),
            "aporte_label": labels["aporte_meta"]
        },
        "persona": persona_str,
        "prioridades": prios,
    }

