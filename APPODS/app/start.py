# app/start.py — Lanza splash y luego la app principal
from app.splash import run_splash_then
from app.main import main as launch_main

if __name__ == "__main__":
    # Duración total del splash (ms). Ej: 1800, 2200, 3000
    run_splash_then(launch_main, total_ms=1800)
