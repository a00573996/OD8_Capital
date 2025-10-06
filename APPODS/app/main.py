import tkinter as tk
from tkinter import ttk
from app.win_home import open_win_home
from app.win_form import open_win_form
from app.win_list import open_win_list
from app.win_table import open_win_table
from app.win_canvas import open_win_canvas

APP_TITLE = "ZAVE — Finanzas Personales (ODS 8)"
APP_VERSION = "v0.1"

# ---------------------------------------------------------------------
# 🎨 Estilo visual moderno (paleta + tipografía + jerarquía)
# ---------------------------------------------------------------------
def _init_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Paleta moderna
    BG = "#F3F4F6"          # gris claro cálido
    CARD_BG = "#FFFFFF"     # blanco puro
    TEXT = "#111827"        # gris azulado profundo
    MUTED = "#6B7280"       # texto secundario
    PRIMARY = "#2563EB"     # azul moderno
    PRIMARY_HOVER = "#1D4ED8"
    SUCCESS = "#16A34A"     # verde moderno
    DANGER = "#EF4444"      # rojo coral
    SEPARATOR = "#E5E7EB"

    # Base
    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)

    # Jerarquía visual
    style.configure("Header.TLabel", background=CARD_BG, foreground=TEXT, font=("Segoe UI Semibold", 26))
    style.configure("Subheader.TLabel", background=CARD_BG, foreground=MUTED, font=("Segoe UI", 12))
    style.configure("Footer.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))

    # Botones del menú
    style.configure(
        "Menu.TButton",
        padding=(14, 12),
        font=("Segoe UI Semibold", 12),
        background=PRIMARY,
        foreground="#FFFFFF",
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Menu.TButton",
        background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)],
        relief=[("pressed", "sunken")]
    )

    # Botón de salida
    style.configure(
        "Danger.TButton",
        padding=(14, 12),
        font=("Segoe UI Semibold", 12),
        background=DANGER,
        foreground="#FFFFFF",
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#DC2626"), ("pressed", "#B91C1C")],
    )

    style.configure("TSeparator", background=SEPARATOR)

# ---------------------------------------------------------------------
# 🏠 Ventana principal moderna
# ---------------------------------------------------------------------
def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("1920x1080")
    root.resizable(True, True)

    _init_style()

    # Contenedor principal
    outer = ttk.Frame(root, padding=40)
    outer.pack(fill="both", expand=True)

    # “Card” central
    card = ttk.Frame(outer, style="Card.TFrame", padding=50)
    card.pack(fill="both", expand=True, ipadx=100, ipady=50)
    card.columnconfigure(0, weight=1)

    # Encabezado con jerarquía
    ttk.Label(card, text="💰 ZAVE", style="Header.TLabel", anchor="center")\
        .grid(row=0, column=0, sticky="ew", pady=(10, 4))
    ttk.Label(card, text=f"Versión {APP_VERSION}", style="Subheader.TLabel", anchor="center")\
        .grid(row=1, column=0, sticky="ew", pady=(0, 20))

    ttk.Separator(card).grid(row=2, column=0, sticky="ew", pady=(0, 20))

    # Botones con íconos sutiles (usando emojis)
    menu_buttons = [
        ("🏠  Home / Bienvenida", lambda: open_win_home(root)),
        ("💵  Ingresos", lambda: open_win_form(root)),
        ("🧾  Registro de Gastos", lambda: open_win_list(root)),
        ("📊  Reporte de Gastos", lambda: open_win_table(root)),
        ("📈  Reporte Gráfico de Gastos", lambda: open_win_canvas(root)),
    ]

    for i, (text, cmd) in enumerate(menu_buttons, start=3):
        ttk.Button(card, text=text, style="Menu.TButton", command=cmd)\
            .grid(row=i, column=0, sticky="ew", pady=10, padx=200)

    ttk.Separator(card).grid(row=9, column=0, sticky="ew", pady=(24, 16))

    # Botón de salida visualmente separado
    ttk.Button(card, text="🚪  Salir", style="Danger.TButton", command=root.destroy)\
        .grid(row=10, column=0, sticky="ew", pady=(10, 0), padx=400)

    # Pie de página
    ttk.Label(
        outer,
        text="Proyecto: ZAVE — Jóvenes organizando sus finanzas (ODS 8)",
        style="Footer.TLabel",
        anchor="center"
    ).pack(fill="x", pady=(16, 0))

    root.mainloop()

# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
