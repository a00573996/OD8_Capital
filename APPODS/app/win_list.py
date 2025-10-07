# win_list.py — ZAVE (Registro de Gastos con CSV, adaptable, estilo azul)
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from core.storage import append_gasto, load_gastos, clear_gastos  # CSV: gastos.csv

# Paleta coherente (Versión A, primario AZUL)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"

# Categorías disponibles (para selección manual y para IA)
CATEGORIAS = [
    "Comida y Bebidas",
    "Transporte",
    "Entretenimiento",
    "Salud",
    "Educación",
    "Hogar y Servicios",
    "Compras",
    "Otros"
]

def open_win_list(parent: ctk.CTk):
    # Ventana secundaria
    win = ctk.CTkToplevel(parent)
    win.title("Registro de Gastos")
    win.state("zoomed")  # aprovechar resolución
    win.minsize(1280, 720)

    # ---------- Escalado adaptable respecto a 1920x1080 ----------
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw / 1920, sh / 1080)

    radius       = max(8, int(10 * scale))
    font_h1      = max(18, int(28 * scale))
    font_lbl     = max(10, int(12 * scale))
    font_btn     = max(10, int(14 * scale))
    entry_h      = max(28, int(34 * scale))
    btn_h        = max(36, int(42 * scale))
    list_height  = max(7,  int(10 * scale))
    pad_outer    = max(36, int(40 * scale))
    pad_card     = max(24, int(36 * scale))
    pad_sep_x    = max(100, int(140 * scale))

    # ---------- Contenedor principal ----------
    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_outer, pady=pad_outer)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad_card, pady=pad_card)
    for i in range(4):
        card.grid_columnconfigure(i, weight=1)
    card.grid_rowconfigure(6, weight=1)  # la lista crece

    # ---------- Encabezado ----------
    ctk.CTkLabel(
        card, text="Registro de Gastos",
        text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_h1)
    ).grid(row=0, column=0, columnspan=4, sticky="w", padx=pad_card, pady=(pad_card, int(8 * scale)))

    ctk.CTkLabel(
        card, text="Agrega tus gastos. Se guardan en data/gastos.csv para usar en el reporte.",
        text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl)
    ).grid(row=1, column=0, columnspan=4, sticky="w", padx=pad_card)

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=2, column=0, columnspan=4, sticky="ew", padx=pad_sep_x, pady=(int(12 * scale), int(16 * scale)))

    # ---------- Entradas ----------
    # Descripción
    ctk.CTkLabel(card, text="Descripción del gasto:", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl)).grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_desc = ctk.CTkEntry(card, height=entry_h)
    ent_desc.grid(row=3, column=1, sticky="ew", pady=6)

    # Monto
    ctk.CTkLabel(card, text="Monto ($):", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl)).grid(row=3, column=2, sticky="e", padx=(0, 8), pady=6)
    ent_monto = ctk.CTkEntry(card, height=entry_h, width=140)
    ent_monto.grid(row=3, column=3, sticky="w", pady=6)

    # Categoría (editable; IA la sugerirá más adelante)
    ctk.CTkLabel(card, text="Categoría:", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl)).grid(row=4, column=0, sticky="e", padx=(0, 8), pady=6)
    cmb_categoria = ctk.CTkOptionMenu(
        card, values=CATEGORIAS, fg_color="white", button_color=PRIMARY_BLUE,
        button_hover_color=PRIMARY_BLUE_DARK, text_color=PRIMARY_BLUE,
        font=ctk.CTkFont("Segoe UI", font_lbl)
    )
    cmb_categoria.set("Otros")
    cmb_categoria.grid(row=4, column=1, sticky="w", pady=6)

    # ---------- Acciones ----------
    actions = ctk.CTkFrame(card, fg_color=CARD_BG)
    actions.grid(row=4, column=2, columnspan=2, sticky="e", pady=6)

    def agregar():
        desc = (ent_desc.get() or "").strip()
        if not desc:
            messagebox.showwarning("Aviso", "Escribe la descripción del gasto.")
            return
        cat = cmb_categoria.get()
        monto_txt = (ent_monto.get() or "").strip()
        try:
            monto_val = float(monto_txt) if monto_txt else 0.0
        except ValueError:
            messagebox.showwarning("Aviso", "Monto inválido. Usa un número (ej. 120.50).")
            return

        # UI
        lb.insert("end", f"{desc}  —  [{cat}]  —  ${monto_val:,.2f}")
        ent_desc.delete(0, "end")
        ent_monto.delete(0, "end")

        # Persistencia CSV
        append_gasto(descripcion=desc, categoria=cat, monto=monto_val)

    def eliminar():
        sel = lb.curselection()
        if not sel:
            return
        # Solo borra de la vista; si quisieras también quitar del CSV,
        # necesitaríamos reescribir el archivo (no lo hacemos por simplicidad).
        lb.delete(sel[0])

    def limpiar():
        if lb.size() == 0:
            return
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los gastos (lista + archivo CSV)?"):
            lb.delete(0, "end")
            clear_gastos()

    # Botones
    ctk.CTkButton(
        actions, text="Agregar gasto",
        fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
        command=agregar
    ).pack(side="right", padx=6)

    # Stub IA (lo conectaremos luego)
    def _clasificar_stub():
        messagebox.showinfo("Próximo paso",
                            "Aquí conectaremos la clasificación con IA para sugerir categoría automáticamente.")
    ctk.CTkButton(
        actions, text="Clasificar (IA)",
        fg_color="white", hover_color="#EEF2FF",
        border_color=PRIMARY_BLUE, border_width=2, text_color=PRIMARY_BLUE,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=_clasificar_stub
    ).pack(side="right", padx=6)

    # ---------- Lista de gastos ----------
    list_container = ctk.CTkFrame(card, fg_color=BG, corner_radius=radius)
    list_container.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=pad_card, pady=(8, 0))
    card.grid_rowconfigure(5, weight=1)

    inner = tk.Frame(list_container, bg=BG)
    inner.pack(fill="both", expand=True, padx=6, pady=6)
    inner.grid_columnconfigure(0, weight=1)
    inner.grid_rowconfigure(0, weight=1)

    lb = tk.Listbox(inner, height=list_height, activestyle="dotbox")
    lb.grid(row=0, column=0, sticky="nsew")
    sb = tk.Scrollbar(inner, orient="vertical", command=lb.yview)
    sb.grid(row=0, column=1, sticky="ns")
    lb.config(yscrollcommand=sb.set)

    # Cargar CSV existente al abrir
    for r in load_gastos():
        desc  = (r.get("descripcion") or "").strip()
        cat   = (r.get("categoria") or "Otros").strip()
        monto = r.get("monto", "0.00")
        lb.insert("end", f"{desc}  —  [{cat}]  —  ${float(monto):,.2f}")

    # Enter = agregar
    def _on_enter(event):
        agregar()
    ent_desc.bind("<Return>", _on_enter)

    # ---------- Pie ----------
    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=98, column=0, columnspan=4, sticky="ew", padx=pad_sep_x, pady=(int(14 * scale), int(12 * scale)))
    ctk.CTkButton(
        card, text="Cerrar",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=win.destroy
    ).grid(row=99, column=0, columnspan=4, sticky="e", padx=pad_card, pady=(0, pad_card))
