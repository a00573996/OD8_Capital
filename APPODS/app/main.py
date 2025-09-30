import tkinter as tk
from tkinter import ttk
from app.win_home import open_win_home
from app.win_form import open_win_form
from app.win_list import open_win_list
from app.win_table import open_win_table
from app.win_canvas import open_win_canvas

APP_TITLE = "ZAVE — Finanzas Personales (ODS 8)"
APP_VERSION = "v0.1"

def _center_window(win, w=480, h=420):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 3)
    win.geometry(f"{w}x{h}+{x}+{y}")

def _init_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Paleta profesional
    BG = "#F6F7FB"
    CARD_BG = "#FFFFFF"
    FG = "#1F2937"
    MUTED = "#6B7280"
    PRIMARY = "#16A34A"       # Verde profesional
    PRIMARY_HOVER = "#15803D" # Verde más oscuro
    DANGER = "#DC2626"
    DANGER_HOVER = "#B91C1C"
    SEPARATOR = "#E5E7EB"

    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)
    style.configure("Header.TLabel", background=CARD_BG, foreground=FG, font=("Segoe UI", 16, "bold"))
    style.configure("Subheader.TLabel", background=CARD_BG, foreground=MUTED, font=("Segoe UI", 10))
    style.configure("Footer.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))

    style.configure(
        "Menu.TButton",
        padding=(10, 10),
        font=("Segoe UI", 10, "bold"),
        background=PRIMARY,
        foreground="#FFFFFF",
        borderwidth=0,
    )
    style.map(
        "Menu.TButton",
        background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)],
        foreground=[("disabled", "#D1D5DB")],
    )

    style.configure(
        "Danger.TButton",
        padding=(10, 10),
        font=("Segoe UI", 10, "bold"),
        background=DANGER,
        foreground="#FFFFFF",
        borderwidth=0,
    )
    style.map(
        "Danger.TButton",
        background=[("active", DANGER_HOVER), ("pressed", DANGER_HOVER)],
        foreground=[("disabled", "#D1D5DB")],
    )

    style.configure("TSeparator", background=SEPARATOR)

def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.minsize(480, 420)
    root.resizable(False, False)
    _center_window(root, 520, 460)

    _init_style()

    outer = ttk.Frame(root, padding=20)
    outer.pack(fill="both", expand=True)

    card = ttk.Frame(outer, style="Card.TFrame", padding=18)
    card.pack(fill="both", expand=True)
    card.columnconfigure(0, weight=1)

    header = ttk.Label(card, text="ZAVE", style="Header.TLabel", anchor="center")
    header.grid(row=0, column=0, sticky="ew", pady=(4, 2))

    sub = ttk.Label(
        card,
        text={APP_VERSION},
        style="Subheader.TLabel",
        anchor="center",
        wraplength=440,
        justify="center",
    )
    sub.grid(row=1, column=0, sticky="ew", pady=(0, 12))

    ttk.Separator(card).grid(row=2, column=0, sticky="ew", pady=(0, 12))

    ttk.Button(card, text="1) Home / Bienvenida", style="Menu.TButton",
               command=lambda: open_win_home(root)).grid(row=3, column=0, sticky="ew", pady=6)
    ttk.Button(card, text="2) Ingresos", style="Menu.TButton",
               command=lambda: open_win_form(root)).grid(row=4, column=0, sticky="ew", pady=6)
    ttk.Button(card, text="3) Registro de Gastos", style="Menu.TButton",
               command=lambda: open_win_list(root)).grid(row=5, column=0, sticky="ew", pady=6)
    ttk.Button(card, text="4) Reporte de Gastos", style="Menu.TButton",
               command=lambda: open_win_table(root)).grid(row=6, column=0, sticky="ew", pady=6)
    ttk.Button(card, text="5) Reporte Gráfico de Gastos", style="Menu.TButton",
               command=lambda: open_win_canvas(root)).grid(row=7, column=0, sticky="ew", pady=6)

    ttk.Separator(card).grid(row=8, column=0, sticky="ew", pady=(8, 8))

    # Botón Salir ajustado
    ttk.Button(card, text="Salir", style="Danger.TButton", command=root.destroy)\
        .grid(row=9, column=0, sticky="ew", pady=(4, 0))

    footer = ttk.Label(
        outer,
        text="Proyecto: ZAVE — Jóvenes organizando sus finanzas (ODS 8)",
        style="Footer.TLabel",
        anchor="center",
    )
    footer.pack(fill="x", pady=(10, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
