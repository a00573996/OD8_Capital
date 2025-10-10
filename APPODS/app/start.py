# app/start.py — Lanza splash y luego la app principal
from app.splash import run_splash_then
from app.main import main as launch_main

if __name__ == "__main__":
    # Tiempo del splash en milisegundos
    run_splash_then(launch_main, duration_ms=1800)
