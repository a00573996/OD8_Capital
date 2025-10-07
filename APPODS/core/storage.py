from pathlib import Path
import csv
from datetime import datetime

# Desde APPODS/core/storage.py queremos llegar a ODB_CAPITAL/data
# parents[0] = .../APPODS/core
# parents[1] = .../APPODS
# parents[2] = .../ODB_CAPITAL   ← raíz del repo (donde está /data)
DATA_PATH = Path(__file__).resolve().parents[2] / "data"
CSV_GASTOS = DATA_PATH / "gastos.csv"
CABECERA = ["fecha", "descripcion", "categoria", "monto"]

def ensure_data_file():
    """Crea /data y gastos.csv con cabecera si no existen."""
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not CSV_GASTOS.exists():
        with open(CSV_GASTOS, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(CABECERA)

def append_gasto(descripcion: str, categoria: str, monto: float = 0.0, fecha_iso: str | None = None):
    """Agrega un gasto al CSV."""
    ensure_data_file()
    if fecha_iso is None:
        fecha_iso = datetime.now().isoformat(timespec="seconds")
    with open(CSV_GASTOS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([fecha_iso, descripcion, categoria, f"{float(monto):.2f}"])

def load_gastos():
    """Lee todas las filas del CSV y devuelve lista[dict]."""
    ensure_data_file()
    rows = []
    with open(CSV_GASTOS, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def clear_gastos():
    """Limpia el archivo (deja solo cabecera)."""
    ensure_data_file()
    with open(CSV_GASTOS, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CABECERA)

def totals(rows):
    """Calcula total general y por categoría."""
    total_general = 0.0
    por_categoria = {}
    for r in rows:
        try:
            monto = float(r.get("monto", 0) or 0)
        except ValueError:
            monto = 0.0
        total_general += monto
        cat = (r.get("categoria") or "Otros").strip()
        por_categoria[cat] = por_categoria.get(cat, 0.0) + monto
    return total_general, por_categoria

