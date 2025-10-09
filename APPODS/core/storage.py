# core/storage.py — manejo robusto de gastos.csv
from __future__ import annotations
import csv, os
from datetime import datetime
from typing import List, Dict, Tuple
from .paths import get_data_dir

DATA_DIR = get_data_dir()
GASTOS_CSV = DATA_DIR / "gastos.csv"
FIELDNAMES = ["fecha", "descripcion", "categoria", "monto"]

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _csv_is_empty(path) -> bool:
    return (not path.exists()) or (path.stat().st_size == 0)

def append_gasto(descripcion: str, categoria: str, monto: float, fecha: str | None = None) -> None:
    """
    Agrega una fila al CSV garantizando encabezado y saltos correctos.
    """
    _ensure_data_dir()
    new_file = not GASTOS_CSV.exists()
    write_header = _csv_is_empty(GASTOS_CSV)

    # Abrir SIEMPRE con newline="" en Windows para que csv maneje saltos.
    with open(GASTOS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()  # escribe 'fecha,descripcion,categoria,monto\n'
        writer.writerow({
            "fecha": fecha or datetime.now().isoformat(timespec="seconds"),
            "descripcion": descripcion,
            "categoria": categoria,
            "monto": f"{float(monto):.2f}",
        })

def load_gastos() -> List[Dict[str, str]]:
    """
    Carga todas las filas del CSV. Ignora líneas vacías.
    Devuelve una lista de dicts con llaves: fecha, descripcion, categoria, monto.
    """
    _ensure_data_dir()
    rows: List[Dict[str, str]] = []
    if not GASTOS_CSV.exists():
        return rows
    with open(GASTOS_CSV, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not r:
                continue
            # Normaliza a las llaves esperadas; si falta alguna, pon string vacío
            row = {
                "fecha": (r.get("fecha") or "").strip(),
                "descripcion": (r.get("descripcion") or "").strip(),
                "categoria": (r.get("categoria") or "").strip(),
                "monto": (r.get("monto") or "").strip(),
            }
            # Si por error el header quedó pegado (ej: 'monto2025-...'), intenta recuperarlo:
            if not row["monto"]:
                for k in list(r.keys()):
                    if k and isinstance(k, str) and k.strip().lower().startswith("monto"):
                        row["monto"] = (r.get(k) or "").strip()
                        break
            # descartar filas totalmente vacías
            if any(row.values()):
                rows.append(row)
    return rows

def clear_gastos(write_header: bool = True) -> None:
    """
    Limpia el CSV. Si write_header=True, deja solo el encabezado.
    """
    _ensure_data_dir()
    with open(GASTOS_CSV, "w", encoding="utf-8", newline="") as f:
        if write_header:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            
def save_all_gastos(rows: list[dict]) -> None:
    """
    Reescribe 'gastos.csv' con la lista recibida (debe incluir encabezados correctos).
    Cada item: {"fecha": str, "descripcion": str, "categoria": str, "monto": str/float}
    """
    GASTOS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(GASTOS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "fecha": (r.get("fecha") or "").strip(),
                "descripcion": (r.get("descripcion") or "").strip(),
                "categoria": (r.get("categoria") or "").strip(),
                "monto": f"{float(r.get('monto', 0) or 0):.2f}",
            })

def totals(rows: List[Dict[str, str]]) -> Tuple[float, Dict[str, float]]:
    """
    Calcula total general y totales por categoría (texto completo).
    """
    def _to_float(x: str) -> float:
        s = (x or "").strip()
        if not s:
            return 0.0
        s = s.replace("$", "").replace("MXN", "").replace("USD", "").replace("€", "")
        s = s.replace(" ", "")
        # 1.234,56 -> 1234.56
        if "," in s and "." not in s:
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
        try:
            return float(s)
        except Exception:
            return 0.0

    total = 0.0
    por_cat: Dict[str, float] = {}
    for r in rows:
        cat = (r.get("categoria") or "Otros").strip() or "Otros"
        monto = _to_float(r.get("monto", "0"))
        total += monto
        por_cat[cat] = por_cat.get(cat, 0.0) + monto
    return total, por_cat
