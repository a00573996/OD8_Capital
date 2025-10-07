# win_table.py — ZAVE (Reporte desde CSV con totales)
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from core.storage import load_gastos, totals

PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"

def open_win_table(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Reporte de Gastos")
    win.state("zoomed")
    win.minsize(1280, 720)

    # Escala simple
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw/1920, sh/1080)
    font_h1  = max(18, int(28*scale))
    font_lbl = max(10, int(12*scale))
    pad      = max(24, int(36*scale))

    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad, pady=pad)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=max(8, int(10*scale)))
    card.pack(fill="both", expand=True, padx=pad, pady=pad)
    card.grid_rowconfigure(1, weight=1)
    card.grid_columnconfigure(0, weight=1)

    # Encabezado
    ctk.CTkLabel(card, text="Reporte de Gastos", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h1))\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, int(8*scale)))
    ctk.CTkLabel(card, text="Vista de gastos guardados en data/gastos.csv",
                 text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=0, column=1, sticky="e", padx=pad)

    # Tabla
    table_frame = ctk.CTkFrame(card, fg_color=CARD_BG)
    table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=pad, pady=(int(8*scale), pad))
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    columns = ("categoria", "descripcion", "monto", "fecha", "dinero_total")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    tree.heading("categoria", text="Categoría")
    tree.heading("descripcion", text="Descripción")
    tree.heading("monto", text="Monto")
    tree.heading("fecha", text="Fecha")
    tree.heading("dinero_total", text="Dinero Total (acum.)")

    tree.column("categoria", width=220, anchor="center")
    tree.column("descripcion", width=420, anchor="w")
    tree.column("monto", width=140, anchor="e")
    tree.column("fecha", width=180, anchor="center")
    tree.column("dinero_total", width=180, anchor="e")

    tree.grid(row=0, column=0, sticky="nsew")
    sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    sb.grid(row=0, column=1, sticky="ns")
    tree.config(yscrollcommand=sb.set)

    # Pie: totales
    footer = ctk.CTkFrame(card, fg_color=CARD_BG)
    footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, pad))
    footer.grid_columnconfigure(0, weight=1)

    lbl_totales = ctk.CTkLabel(footer, text="", text_color=TEXT,
                               font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_totales.grid(row=0, column=0, sticky="w")

    # Botones
    btns = ctk.CTkFrame(footer, fg_color=CARD_BG)
    btns.grid(row=0, column=1, sticky="e")

    def cargar_tabla():
        """Limpia y recarga los datos desde el CSV; calcula totales."""
        for row_id in tree.get_children():
            tree.delete(row_id)

        rows = load_gastos()
        total_general, por_cat = totals(rows)
        acumulado = 0.0

        for r in rows:
            try:
                monto = float(r.get("monto", 0) or 0)
            except ValueError:
                monto = 0.0
            acumulado += monto
            cat = r.get("categoria", "Otros")
            desc = r.get("descripcion", "")
            fecha = r.get("fecha", "")
            tree.insert("", "end", values=(cat, desc, f"${monto:,.2f}", fecha, f"${acumulado:,.2f}"))

        # Texto de totales (general + por categoría)
        bloques = [f"Total general: ${total_general:,.2f}"]
        if por_cat:
            bloques.append(" | ".join([f"{c}: ${v:,.2f}" for c, v in por_cat.items()]))
        lbl_totales.configure(text="   ".join(bloques))

    def limpiar_tabla():
        for row_id in tree.get_children():
            tree.delete(row_id)
        lbl_totales.configure(text="")

    ctk.CTkButton(btns, text="Actualizar",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, command=cargar_tabla)\
        .pack(side="left", padx=6)
    ctk.CTkButton(btns, text="Limpiar vista",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, command=limpiar_tabla)\
        .pack(side="left", padx=6)

    # Primera carga
    cargar_tabla()
