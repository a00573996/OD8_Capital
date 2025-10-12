# main.py — ZAVE (cerrar Main y lanzar solo la ventana seleccionada)
import customtkinter as ctk
import tkinter as tk

import os
from PIL import Image  # <-- NUEVO

from app.win_home import open_win_home      # Perfil de usuario
from app.win_form import open_win_form      # Ingresos
from app.win_list import open_win_list      # Registro de gastos
from app.win_table import open_win_table    # Reporte de gastos

APP_TITLE   = "ZAVE — Finanzas Personales (ODS 8)"
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

def _init_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

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

def go_to(open_window_fn, current_root: ctk.CTk):
    """
    Cierra el Main y abre SOLO la ventana destino.
    - Crea un nuevo root oculto
    - Llama a open_window_fn(new_root) que creará un Toplevel
    - Vincula el cierre del Toplevel para terminar la app
    """
    # 1) Cerrar Main
    try:
        current_root.destroy()
    except Exception:
        pass

    # 2) Nuevo root oculto
    new_root = ctk.CTk()
    new_root.withdraw()  # no queremos que se vea el root en blanco
    try:
        new_root.state("zoomed")
    except Exception:
        new_root.geometry("1280x800")

    # 3) Crear la ventana destino (Toplevel)
    open_window_fn(new_root)

    # 4) Enlazar cierre del Toplevel para terminar la app
    #    (buscamos el/los toplevel creados por la función)
    for w in new_root.winfo_children():
        # customtkinter genera CTkToplevel que hereda de Toplevel
        if isinstance(w, (ctk.CTkToplevel, tk.Toplevel)):
            w.protocol("WM_DELETE_WINDOW", new_root.destroy)

    # 5) Mostrar solo la ventana destino (el root queda oculto)
    new_root.mainloop()

def main():
    _init_theme()

    root = ctk.CTk()
    root.title(APP_TITLE)
    try:
        root.state("zoomed")
    except Exception:
        root.geometry("1280x800")

    # Escalado
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    scale  = min(sw/1920, sh/1080)

    radius        = max(8, int(10 * scale))
    font_title    = max(20, int(34 * scale))
    font_chip     = max(10, int(13 * scale))
    font_btn      = max(10, int(16 * scale))
    font_footer   = max(9,  int(12 * scale))
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

    # --- Logo ZAVE ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.normpath(os.path.join(BASE_DIR, "..", "assets", "ZAVE LOGO.png"))

    try:
        # tamaño adaptable al escalar de pantalla
        logo_size = max(96, int(120 * scale))
        logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                dark_image=Image.open(logo_path),
                                size=(logo_size, logo_size))
        ctk.CTkLabel(card, image=logo_img, text="").pack(pady=(pad_top_title, pad_between))
    except Exception as e:
        # si el logo no se encuentra, mostramos solo el texto (fallback)
        ctk.CTkLabel(
            card, text="💰\u2003ZAVE",
            text_color=TEXT,
            font=ctk.CTkFont("Segoe UI Semibold", font_title)
        ).pack(pady=(pad_top_title, pad_between))

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

    # Botones -> usan go_to(...) para cerrar Main y abrir la ventana
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

    ctk.CTkLabel(
        outer,
        text="ZAVE — (ODS 8)",
        text_color=TEXT_MUTED,
        font=ctk.CTkFont("Segoe UI", font_footer)
    ).pack(pady=(pad_footer, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
