# app/main.py — ZAVE (Menú principal adaptable, estilo azul, con logo)
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk

from app.win_home import open_win_home        # Perfil de usuario
from app.win_form import open_win_form        # Ingresos
from app.win_list import open_win_list        # Registro de gastos
from app.win_table import open_win_table      # Reporte de gastos (tabla + gráficas)

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
    """Inicializa el tema en modo claro (sin dark)."""
    ctk.set_appearance_mode("light")
    # El tema base de CTk no afecta nuestro esquema porque definimos colores por props
    ctk.set_default_color_theme("green")

def _load_logo_images():
    """
    Carga el logo desde /assets/ZAVE LOGO.png.
    Devuelve (icon_tk, ctk_img_48) donde:
      - icon_tk: PhotoImage para icono de ventana
      - ctk_img_48: CTkImage para encabezado (48x48)
    Si no existe, devuelve (None, None).
    """
    try:
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "ZAVE LOGO.png"
        if not icon_path.exists():
            return None, None
        img = Image.open(icon_path)
        icon_tk = ImageTk.PhotoImage(img)  # para root.iconphoto
        ctk_img_48 = ctk.CTkImage(light_image=img, size=(48, 48))
        return icon_tk, ctk_img_48
    except Exception as e:
        print(f"[Advertencia] No se pudo cargar el logo: {e}")
        return None, None

def main():
    _init_theme()

    root = ctk.CTk()
    root.title(APP_TITLE)
    root.state("zoomed")  # maximiza

    # Icono de ventana y logo de encabezado
    icon_tk, ctk_logo_48 = _load_logo_images()
    if icon_tk:
        try:
            root.iconphoto(True, icon_tk)
        except Exception as e:
            print(f"[Advertencia] iconphoto: {e}")

    # --- Escalado adaptable respecto a 1920x1080 ---
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    scale_w, scale_h = sw / 1920, sh / 1080
    scale = min(scale_w, scale_h)

    # Tamaños derivados
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

    # ---------- Lienzo general ----------
    outer = ctk.CTkFrame(root, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_outer, pady=pad_outer)

    # ---------- Tarjeta central ----------
    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(expand=True, padx=pad_card_x, pady=pad_card_y)

    # ---------- Encabezado (logo + título) ----------
    header = ctk.CTkFrame(card, fg_color=CARD_BG)
    header.pack(pady=(pad_top_title, pad_between))

    if ctk_logo_48:
        ctk.CTkLabel(header, image=ctk_logo_48, text="").pack(side="left", padx=(0, 10))

    ctk.CTkLabel(
        header,
        text="ZAVE",
        text_color=TEXT,
        font=ctk.CTkFont("Segoe UI Semibold", font_title)
    ).pack(side="left")

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

    # Separador corto
    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .pack(fill="x", padx=pad_sep_x, pady=(pad_between * 2, pad_after_sep))

    # ---------- Botón outlined AZUL ----------
    def nav_button(parent, text, command):
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

    # ---------- Botones de menú ----------
    nav_button(card, "👤\u2003Perfil de usuario", lambda: open_win_home(root)).pack(pady=pad_between)
    nav_button(card, "💵\u2003Ingresos",           lambda: open_win_form(root)).pack(pady=pad_between)
    nav_button(card, "🧾\u2003Registro de Gastos", lambda: open_win_list(root)).pack(pady=pad_between)
    nav_button(card, "📊\u2003Reporte de Gastos",  lambda: open_win_table(root)).pack(pady=pad_between)

    # Separador inferior (corto)
    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .pack(fill="x", padx=pad_sep_x, pady=(pad_after_sep * 1.2, pad_between * 1.5))

    # ---------- Botón Salir (rojo) ----------
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

    # ---------- Pie de página ----------
    ctk.CTkLabel(
        outer,
        text="ZAVE — (ODS 8)",
        text_color=TEXT_MUTED,
        font=ctk.CTkFont("Segoe UI", font_footer)
    ).pack(pady=(pad_footer, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
