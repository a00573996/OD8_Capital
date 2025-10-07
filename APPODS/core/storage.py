from pathlib import Path
import csv
from datetime import datetime

# Raíz del repo: .../ODB_CAPITAL
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "data"
CSV_GASTOS = DATA_PATH / "gastos.csv"
CABECERA = ["fecha", "descripcion", "categoria", "monto"]

def ensure_data_file():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not CSV_GASTOS.exists():
        with open(CSV_GASTOS, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CABECERA)

def append_gasto(descripcion: str, categoria: str, monto: float = 0.0, fecha_iso: str | None = None):
    ensure_data_file()
    if fecha_iso is None:
        fecha_iso = datetime.now().isoformat(timespec="seconds")
    with open(CSV_GASTOS, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([fecha_iso, descripcion, categoria, f"{float(monto):.2f}"])

def load_gastos():
    ensure_data_file()
    with open(CSV_GASTOS, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def clear_gastos():
    ensure_data_file()
    with open(CSV_GASTOS, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(CABECERA)

def totals(rows):
    total_general = 0.0
    por_categoria = {}
    for r in rows:
        try:
            m = float(r.get("monto", 0) or 0)
        except ValueError:
            m = 0.0
        total_general += m
        cat = (r.get("categoria") or "Otros").strip()
        por_categoria[cat] = por_categoria.get(cat, 0.0) + m
    return total_general, por_categoria

