# app/main.py — ZAVE-MENU INICIO
from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from PIL import Image

from app.win_reco import open_win_reco      # ⭐ Recomendaciones
from app.win_home import open_win_home      # 👤 Perfil de usuario
from app.win_form import open_win_form      # 💵 Ingresos
from app.win_list import open_win_list      # 🧾 Registro de gastos
from app.win_table import open_win_table    # 📊 Reporte de gastos
from core.profile import load_profile       # para leer el nombre del usuario

APP_TITLE   = "ZAVE MENU"
APP_VERSION = "v0.1"

# Paleta / constantes
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"
DANGER             = "#DC3545"
DANGER_DARK        = "#B02A37"

# Rutas de assets
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH  = ASSETS_DIR / "ZAVE LOGO.png"

def _init_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

def _load_logo_image(root, size_px=64):
    """Carga el logo ZAVE y guarda la referencia en root para evitar GC."""
    try:
        img = Image.open(LOGO_PATH)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size_px, size_px))
        root._zave_logo_img = ctk_img  # mantener referencia viva
        return ctk_img
    except Exception:
        return None

def _nav_button(parent, text, command, *, radius, font_btn, btn_h, btn_w):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="white",
        hover_color="#EEF2FF",
        text_color=PRIMARY_BLUE,
        border_color=PRIMARY_BLUE,
        border_width=2,
        corner_radius=radius,
        font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
        height=btn_h,
        width=btn_w
    )

def _force_maximize(win: ctk.CTk):
    """Maximiza de forma robusta (Windows/Linux/macOS) incluso si el primer intento no hace efecto."""
    win.update_idletasks()

    def _zoom():
        try:
            win.state("zoomed")          # Windows / la mayoría de entornos
            return
        except Exception:
            pass
        try:
            win.wm_attributes("-zoomed", True)  # algunos X11
            return
        except Exception:
            pass
        # Fallback: ocupar toda la pantalla
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{sw}x{sh}+0+0")

    _zoom()
    win.after(50, _zoom)
    win.after(250, _zoom)

def go_to(open_window_fn, current_root: ctk.CTk):
    """Cierra Main y abre SOLO la ventana destino."""
    try:
        current_root.destroy()
    except Exception:
        pass

    new_root = ctk.CTk()
    new_root.withdraw()
    try:
        new_root.state("zoomed")
    except Exception:
        new_root.geometry("1280x800")

    open_window_fn(new_root)

    def _bind_close_for_children():
        for w in new_root.winfo_children():
            if isinstance(w, (ctk.CTkToplevel, tk.Toplevel)):
                w.protocol("WM_DELETE_WINDOW", new_root.destroy)
    new_root.after(50, _bind_close_for_children)

    new_root.mainloop()

def main():
    _init_theme()

    root = ctk.CTk()
    root.title(APP_TITLE)
    _force_maximize(root)  # <<— maximiza al abrir

    # Leer nombre del usuario para el saludo
    try:
        state = load_profile()
        nombre = (state.get("usuario", {}).get("nombre", "") or "").strip()
    except Exception:
        nombre = ""
    saludo = f"¡Hola {nombre}!" if nombre else "¡Hola!"

    # Escalado
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    scale  = min(sw/1920, sh/1080)

    radius        = max(8, int(10 * scale))
    font_title    = max(20, int(34 * scale))
    font_chip     = max(10, int(13 * scale))
    font_btn      = max(10, int(16 * scale))
    font_footer   = max(9,  int(12 * scale))
    font_saludo   = max(12, int(20 * scale))
    btn_h         = max(36, int(46 * scale))
    btn_w         = max(280, int(380 * scale))
    pad_outer     = max(20, int(40 * scale))
    pad_card_x    = max(60, int(120 * scale))
    pad_card_y    = max(20, int(40 * scale))
    pad_sep_x     = max(100, int(160 * scale))
    pad_top_title = max(18, int(36 * scale))
    pad_between   = max(6,  int(8 * scale))
    pad_after_sep = max(12, int(18 * scale))
    pad_footer    = max(6,  int(8 * scale))

    # Lienzo
    outer = ctk.CTkFrame(root, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_outer, pady=pad_outer)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(expand=True, padx=pad_card_x, pady=pad_card_y)

    # Encabezado con LOGO persistente
    logo_img = _load_logo_image(root, size_px=max(48, int(64 * scale)))
    if logo_img:
        ctk.CTkLabel(
            card, image=logo_img, text="  ZAVE",
            compound="left",
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI Semibold", font_title)
        ).pack(pady=(pad_top_title, pad_between))
    else:
        ctk.CTkLabel(
            card, text="💰\u2003ZAVE",
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI Semibold", font_title)
        ).pack(pady=(pad_top_title, pad_between))

    # Saludo personalizado en negrita
    ctk.CTkLabel(
        card,
        text=saludo,
        text_color=TEXT,
        font=ctk.CTkFont("Segoe UI Semibold", font_saludo, "bold")
    ).pack(pady=(0, pad_between))

    # Chip de versión
    ctk.CTkLabel(
        card,
        text=f"Versión {APP_VERSION}",
        text_color=TEXT_MUTED,
        fg_color=BG,
        corner_radius=max(6, int(8 * scale)),
        padx=max(8, int(10 * scale)),
        pady=max(3, int(4 * scale)),
        font=ctk.CTkFont("Segoe UI", font_chip)
    ).pack()

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .pack(fill="x", padx=pad_sep_x, pady=(pad_between * 2, pad_after_sep))

    # Botones
    _nav_button(card, "⭐\u2003Recomendaciones",
                lambda: go_to(open_win_reco, root),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "👤\u2003Perfil de Usuario",
                lambda: go_to(open_win_home, root),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "💵\u2003Ingresos",
                lambda: go_to(open_win_form, root),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "🧾\u2003Registro de Gastos",
                lambda: go_to(open_win_list, root),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "📊\u2003Reporte de Gastos",
                lambda: go_to(open_win_table, root),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .pack(fill="x", padx=pad_sep_x, pady=(pad_after_sep * 1.2, pad_between * 1.5))

    ctk.CTkButton(
        card,
        text="🚪\u2003Salir",
        command=root.destroy,
        fg_color=DANGER,
        hover_color=DANGER_DARK,
        text_color="white",
        corner_radius=radius,
        font=ctk.CTkFont("Segoe UI Semibold", font_btn),
        height=btn_h,
        width=btn_w
    ).pack(pady=(pad_between, pad_top_title))

    root.mainloop()

if __name__ == "__main__":
    main()
