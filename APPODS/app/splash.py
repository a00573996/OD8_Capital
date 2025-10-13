# app/splash.py
# Splash con animación y barra de progreso (bloqueante), carga de logo desde APPODS/assets.

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
import time

# Pillow para cargar y escalar el logo SIEMPRE
from PIL import Image, ImageTk, ImageOps

PRIMARY_BLUE = "#2563EB"
TEXT         = "#111827"
TEXT_MUTED   = "#6B7280"
BG           = "#FFFFFF"

# --- Rutas: prioriza APPODS/assets/ZAVE LOGO.png ---
PROJECT_ASSETS_DIR = (Path(__file__).resolve().parents[1] / "assets").resolve()
APP_ASSETS_DIR     = (Path(__file__).resolve().parent / "assets").resolve()
_LOGO_CANDIDATES = [
    PROJECT_ASSETS_DIR / "ZAVE LOGO.png",  # APPODS/assets
    APP_ASSETS_DIR / "ZAVE LOGO.png",      # app/assets (fallback)
]

def _pick_logo_path():
    for p in _LOGO_CANDIDATES:
        if p.exists():
            return p
    return _LOGO_CANDIDATES[0]

LOGO_PATH = _pick_logo_path()

def _load_logo_tkimage(target_px: int = 164):
    """
    Carga el logo y lo escala para que quepa en un cuadrado target_px x target_px
    manteniendo proporción. Si tiene canal alpha, recorta el bounding box del alpha
    para eliminar márgenes transparentes.
    """
    try:
        img = Image.open(str(LOGO_PATH)).convert("RGBA")

        # Recorte por alpha (si hay transparencia, quita márgenes transparentes)
        try:
            alpha = img.split()[-1]
            bbox = alpha.getbbox()
            if bbox:
                img = img.crop(bbox)
        except Exception:
            pass

        # Escalar manteniendo proporción para que QUEPA en target_px
        img = ImageOps.contain(img, (target_px, target_px))

        return ImageTk.PhotoImage(img)
    except Exception:
        # Fallback sólido si no se puede abrir el logo
        img = Image.new("RGBA", (target_px, target_px), (37, 99, 235, 255))
        return ImageTk.PhotoImage(img)

def run_splash_then(callback, duration_ms: int = 1000):
    """
    Muestra un splash animado durante `duration_ms` ms y luego ejecuta `callback()`.
    Bloquea la ejecución con su propio mainloop y destruye todo antes de llamar al callback.
    """
    # Root CTk (oculto). El splash será un Toplevel sobre este root.
    root = ctk.CTk()
    root.withdraw()

    # --- Toplevel splash ---
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash.configure(bg=BG)
    splash.attributes("-topmost", True)

    # Tamaño + centrado
    W, H = 520, 360
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    x = (sw - W) // 2
    y = (sh - H) // 2
    splash.geometry(f"{W}x{H}+{x}+{y}")

    # ---- Contenido ----
    body = tk.Frame(splash, bg=BG)
    body.pack(fill="both", expand=True, padx=22, pady=22)

    # Logo siempre redimensionado
    tkimg = _load_logo_tkimage(164)
    lbl_logo = tk.Label(body, image=tkimg, bg=BG)
    lbl_logo.image = tkimg  # evitar GC
    lbl_logo.pack(pady=(8, 0))

    lbl_title = tk.Label(body, text="ZAVE", font=("Segoe UI Semibold", 22), fg=TEXT, bg=BG)
    lbl_sub   = tk.Label(body, text="Finanzas personales (ODS 8)", font=("Segoe UI", 11), fg=TEXT_MUTED, bg=BG)
    lbl_title.pack(pady=(10, 2))
    lbl_sub.pack(pady=(0, 14))

    # ProgressBar de CustomTkinter dentro de un frame CTk
    pb_wrap = ctk.CTkFrame(body, fg_color=BG)
    pb_wrap.pack(fill="x", padx=6, pady=(0, 8))
    pb = ctk.CTkProgressBar(pb_wrap, height=12, corner_radius=8, progress_color=PRIMARY_BLUE)
    pb.pack(fill="x", padx=8, pady=8)
    pb.set(0.0)

    lbl_loading = tk.Label(body, text="Cargando", font=("Segoe UI", 10), fg=TEXT_MUTED, bg=BG)
    lbl_loading.pack()

    # --- Animación (after loop) ---
    start_t   = time.perf_counter()
    total_s   = max(0.2, duration_ms / 1000.0)  # evita 0
    after_id  = {"id": None}
    dots_step = {"i": 0}

    def ease_out_cubic(x: float) -> float:
        return 1 - pow(1 - x, 3)

    def tick():
        t = time.perf_counter() - start_t
        prog = min(1.0, t / total_s)
        pb.set(ease_out_cubic(prog))

        # Anima "Cargando..." con puntos
        dots_step["i"] = (dots_step["i"] + 1) % 4
        lbl_loading.config(text="Cargando" + "." * dots_step["i"] + " " * (3 - dots_step["i"]))

        if prog < 1.0:
            after_id["id"] = splash.after(70, tick)
        else:
            # Cerrar splash y root ANTES de lanzar el main
            try:
                if after_id["id"]:
                    splash.after_cancel(after_id["id"])
            except Exception:
                pass
            try:
                splash.destroy()
            except Exception:
                pass
            try:
                root.destroy()
            except Exception:
                pass
            # Lanzar main
            try:
                callback()
            except Exception:
                pass

    # Mostrar y arrancar animación
    root.after(0, splash.deiconify)
    tick()
    try:
        root.mainloop()
    except Exception:
        # Si algo falla en el loop, lanzar el callback igualmente
        try:
            callback()
        except Exception:
            pass
