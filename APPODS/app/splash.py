# app/splash.py — Splash ZAVE (diseño original + animaciones)
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

def run_splash_then(callback,
                    total_ms=1800,
                    fade_in_ms=400,
                    fade_out_ms=400):
    """
    Mantiene el DISEÑO PREVIO:
      - Ventana 520x360, tarjeta con esquinas 16
      - Logo 96x96, título 'ZAVE', subtítulo 'Finanzas personales sencillas'
      - Barra de progreso centrada
    Solo se añaden animaciones: fade-in, progreso, fade-out.
    """
    ctk.set_appearance_mode("light")

    app = ctk.CTk()
    app.overrideredirect(True)     # sin barra
    app.configure(fg_color=BG)
    try:
        app.attributes("-topmost", True)
    except Exception:
        pass

    # --- Tamaños (idénticos al splash original) ---
    W, H = 520, 360
    _center(app, W, H)

    # --- Tarjeta (igual) ---
    card = ctk.CTkFrame(app, fg_color=CARD_BG, corner_radius=16)
    card.pack(fill="both", expand=True, padx=18, pady=18)

    # --- Logo (igual) ---
    icon_path = Path(__file__).resolve().parents[1] / "assets" / "ZAVE LOGO.png"
    if icon_path.exists():
        logo_img = ctk.CTkImage(light_image=Image.open(icon_path), size=(96, 96))
        ctk.CTkLabel(card, image=logo_img, text="").pack(pady=(28, 8))
    else:
        logo_img = None  # no rompe

    # --- Título y subtítulo (igual) ---
    ctk.CTkLabel(
        card, text="ZAVE",
        text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", 28)
    ).pack()
    ctk.CTkLabel(
        card, text="Finanzas personales sencillas",
        text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", 13)
    ).pack(pady=(2, 16))

    # --- Progreso (igual) ---
    pb = ctk.CTkProgressBar(card, height=10, corner_radius=8, progress_color=PRIMARY_BLUE)
    pb.pack(fill="x", padx=40, pady=(4, 18))
    pb.set(0.0)

    # ---- Animaciones (solo añadidas, sin cambiar el layout) ----
    hold_ms = max(0, total_ms - fade_in_ms - fade_out_ms)
    steps_in   = max(10, fade_in_ms // 25)
    steps_hold = max(15, hold_ms // 35)
    steps_out  = max(10, fade_out_ms // 25)

    # Fade-in 0 -> 1 (acompañado de progreso hasta 35%)
    def _fade_in(i=0):
        alpha = min(1.0, i / steps_in)
        try:
            app.attributes("-alpha", alpha)
        except Exception:
            pass
        pb.set(min(0.35, alpha * 0.35))
        if i < steps_in:
            app.after(max(10, fade_in_ms // max(1, steps_in)), _fade_in, i + 1)
        else:
            _hold_progress(0)

    # Avance “hold” 35% -> 95%
    def _hold_progress(i=0):
        if steps_hold <= 0:
            _fade_out(0)
            return
        t = i / steps_hold
        pb.set(0.35 + (0.60 * t))
        if i < steps_hold:
            app.after(max(15, hold_ms // max(1, steps_hold)), _hold_progress, i + 1)
        else:
            _fade_out(0)

    # Fade-out 1 -> 0 (remate de barra a 100%) y abrir main
    def _fade_out(i=0):
        alpha = max(0.0, 1.0 - (i / steps_out))
        try:
            app.attributes("-alpha", alpha)
        except Exception:
            pass
        pb.set(min(1.0, 0.95 + (0.05 * (i / max(1, steps_out)))))
        if i < steps_out:
            app.after(max(10, fade_out_ms // max(1, steps_out)), _fade_out, i + 1)
        else:
            try:
                app.destroy()
            finally:
                callback()

    # Iniciar splash en alpha 0 (para ver el fade-in)
    try:
        app.attributes("-alpha", 0.0)
    except Exception:
        pass

    _fade_in(0)
    app.mainloop()
