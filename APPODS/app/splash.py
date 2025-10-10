# app/splash.py — Splash de ZAVE
import customtkinter as ctk
from PIL import Image
from pathlib import Path

PRIMARY_BLUE = "#2563EB"
BG          = "#F3F4F6"
CARD_BG     = "#FFFFFF"
TEXT        = "#111827"
TEXT_MUTED  = "#6B7280"

def _center(win, w, h):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 2.6)
    win.geometry(f"{w}x{h}+{x}+{y}")

def run_splash_then(callback, duration_ms=1800):
    """Muestra splash y al terminar llama a callback() para abrir la app principal."""
    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.overrideredirect(True)  # sin barra de título
    app.configure(fg_color=BG)

    W, H = 520, 360
    _center(app, W, H)

    # Tarjeta
    card = ctk.CTkFrame(app, fg_color=CARD_BG, corner_radius=16)
    card.pack(fill="both", expand=True, padx=18, pady=18)

    # Logo
    icon_path = Path(__file__).resolve().parents[1] / "assets" / "ZAVE LOGO.png"
    if icon_path.exists():
        logo_img = ctk.CTkImage(light_image=Image.open(icon_path), size=(96, 96))
        ctk.CTkLabel(card, image=logo_img, text="").pack(pady=(28, 8))

    # Título y subtítulo
    ctk.CTkLabel(
        card, text="ZAVE",
        text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", 28)
    ).pack()
    ctk.CTkLabel(
        card, text="Finanzas personales sencillas",
        text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", 13)
    ).pack(pady=(2, 16))

    # Progreso
    pb = ctk.CTkProgressBar(card, height=10, corner_radius=8, progress_color=PRIMARY_BLUE)
    pb.pack(fill="x", padx=40, pady=(4, 18))
    pb.set(0.0)

    # Animación simple de progreso
    steps, tick = 30, duration_ms // 30
    def step(i=0):
        if i <= steps:
            pb.set(i / steps)
            app.after(tick, step, i + 1)
    step()

    # Cerrar y abrir main
    def _close_and_open():
        try:
            app.destroy()
        finally:
            callback()
    app.after(duration_ms, _close_and_open)

    # Sombra ligera (opcional visual)
    try:
        app.wm_attributes("-topmost", True)
        app.wm_attributes("-transparentcolor", "#00FF00")  # no visible, solo compatibilidad
    except Exception:
        pass

    app.mainloop()

