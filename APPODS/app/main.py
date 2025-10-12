# app/main.py — ZAVE (navegación con un solo root oculto)
import customtkinter as ctk
import tkinter as tk

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

def open_main_menu(root: ctk.CTk):
    """
    Abre el Menú Principal como CTkToplevel sobre un root oculto.
    Al pulsar una opción:
      - cierra SOLO este menú
      - abre la ventana destino como otro Toplevel (root sigue vivo)
    """
    menu = ctk.CTkToplevel(root)
    menu.title(APP_TITLE)
    try:
        menu.state("zoomed")
    except Exception:
        menu.geometry("1280x800")
    menu.minsize(1280, 720)

    # Escalado
    sw, sh = menu.winfo_screenwidth(), menu.winfo_screenheight()
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
    outer = ctk.CTkFrame(menu, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_outer, pady=pad_outer)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(expand=True, padx=pad_card_x, pady=pad_card_y)

    # Encabezado (intenta cargar logo si existe, si no, texto)
    header = ctk.CTkFrame(card, fg_color=CARD_BG)
    header.pack(pady=(pad_top_title, pad_between))
    try:
        from PIL import Image
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "ZAVE LOGO.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            cimg = ctk.CTkImage(img, size=(96,96))
            ctk.CTkLabel(header, image=cimg, text="").pack()
            ctk.CTkLabel(header, text="ZAVE", text_color=TEXT,
                         font=ctk.CTkFont("Segoe UI Semibold", font_title)).pack()
        else:
            raise FileNotFoundError
    except Exception:
        ctk.CTkLabel(header, text="💰\u2003ZAVE",
                     text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_title)).pack()

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

    # Helper para abrir y cerrar el menú
    def _open_then_close_self(open_fn):
        def _inner():
            open_fn(root)   # abre nueva ventana (otro Toplevel)
            try:
                menu.destroy()  # cierra el menú actual
            except Exception:
                pass
        return _inner

    # Botones de menú (abren ventana y cierran este menú)
    _nav_button(card, "👤\u2003Perfil de Usuario",
                _open_then_close_self(open_win_home),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "💵\u2003Ingresos",
                _open_then_close_self(open_win_form),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "🧾\u2003Registro de Gastos",
                _open_then_close_self(open_win_list),
                radius=radius, font_btn=font_btn, btn_h=btn_h, btn_w=btn_w).pack(pady=pad_between)

    _nav_button(card, "📊\u2003Reporte de Gastos",
                _open_then_close_self(open_win_table),
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

    # Cerrar el menú = cerrar toda la app
    menu.protocol("WM_DELETE_WINDOW", root.destroy)


def main():
    _init_theme()
    root = ctk.CTk()
    root.withdraw()  # mantén el root oculto
    open_main_menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
