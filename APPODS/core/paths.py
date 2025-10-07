# APPODS/core/paths.py
from pathlib import Path

def get_repo_root() -> Path:
    """Intenta encontrar la raíz del repo (donde existe /data y /APPODS)."""
    here = Path(__file__).resolve()
    for anc in [here] + list(here.parents):
        if (anc / "data").is_dir() and (anc / "APPODS").is_dir():
            return anc
    # Fallback razonable: subir 2 niveles (core → APPODS → raíz)
    return Path(__file__).resolve().parents[2]

def get_data_dir() -> Path:
    root = get_repo_root()
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data

