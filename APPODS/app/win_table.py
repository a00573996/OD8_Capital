# win_table.py — ZAVE (Reporte desde CSV con totales y categorías separadas)
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

def _parse_float_safe(raw) -> float:
    """
    Convierte cualquier valor leído del CSV a float.
    Soporta: "1,234.56", "1234,56", "1 234,56", "$1,234.56", etc.
    """
    if raw is None:
        return 0.0
    if isinstance(raw, (int, float)):
        try:
            return float(raw)
        except Exception:
            return 0.0
    s = str(raw).strip()
    if not s:
        return 0.0
    # quitar símbolos
    s = s.replace("$", "").replace("€", "").replace("MXN", "").replace("USD", "")
    s = s.replace(" ", "")
    # normalizar coma decimal europea
    # si contiene "," y no ".", asumimos coma decimal
    if "," in s and "." not in s:
        s = s.replace(".", "")   # quitar separadores de miles si los hubiera
        s = s.replace(",", ".")  # coma -> punto
    else:
        # quitar separadores de miles comunes
        # "1,234.56" -> "1234.56"
        parts = s.split(".")
        if len(parts) > 2:
            # demasiados puntos: quita los de miles y deja el último como decimal
            s = "".join(parts[:-1]) + "." + parts[-1]
        s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return 0.0

def _split_categoria(cat: str) -> tuple[str, str]:
    """
    Separa 'Principal > Subcategoria' en (principal, subcategoria).
    Si no hay '>', intenta separar por '/' o devuelve todo en principal.
    """
    if not cat:
        return "Otros", ""
    txt = str(cat)
    if ">" in txt:
        p, s = txt.split(">", 1)
        return p.strip(), s.strip()
    # categorías nuevas sintetizadas tipo "X > Y / Z": dejamos todo tras '>' como sub
    if "/" in txt:
        # heurística: si no trae ">", interpreta izquierda como principal y derecha como sub genérica
        parts = txt.split("/", 1)
        return parts[0].strip(), parts[1].strip()
    return txt.strip(), ""

def open_win_table(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Reporte de Gastos")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1280x800")
    win.minsize(1280, 720)

    # Escala simple
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw/1920, sh/1080)
    font_h1  = max(18, int(28*scale))
    font_lbl = max(10, int(12*scale))
    pad      = max(24, int(36*scale))
    radius   = max(8, int(10*scale))

    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad, pady=pad)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad, pady=pad)
    card.grid_rowconfigure(1, weight=1)
    for c in (0, 1):
        card.grid_columnconfigure(c, weight=1)

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

    # NUEVAS columnas con categoría principal y subcategoría
    columns = ("cat_principal", "subcategoria", "descripcion", "monto", "fecha", "acumulado")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    tree.heading("cat_principal", text="Categoría")
    tree.heading("subcategoria", text="Subcategoría")
    tree.heading("descripcion", text="Descripción")
    tree.heading("monto", text="Monto")
    tree.heading("fecha", text="Fecha")
    tree.heading("acumulado", text="Acumulado")

    tree.column("cat_principal", width=260, anchor="w")
    tree.column("subcategoria",  width=240, anchor="w")
    tree.column("descripcion",   width=460, anchor="w")
    tree.column("monto",         width=140, anchor="e")
    tree.column("fecha",         width=180, anchor="center")
    tree.column("acumulado",     width=160, anchor="e")

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

    btns = ctk.CTkFrame(footer, fg_color=CARD_BG)
    btns.grid(row=0, column=1, sticky="e")

    def cargar_tabla():
        """Limpia y recarga los datos desde el CSV; calcula totales."""
        for row_id in tree.get_children():
            tree.delete(row_id)

        rows = load_gastos()  # cada r es un dict (fecha, descripcion, categoria, monto)
        # Robustez: recalcular totales con nuestro parseo propio
        total_general = 0.0
        por_principal = {}
        por_subcat = {}

        # acumulado por orden de lectura
        acumulado = 0.0

        for r in rows:
            # tolerante a nombres de campo alternativos
            raw_monto = r.get("monto", r.get("amount", r.get("valor", 0)))
            monto = _parse_float_safe(raw_monto)
            acumulado += monto
            total_general += monto

            cat_txt = r.get("categoria", "Otros") or "Otros"
            principal, sub = _split_categoria(cat_txt)
            desc  = r.get("descripcion", "") or ""
            fecha = r.get("fecha", "") or ""

            tree.insert("", "end", values=(
                principal,
                sub,
                desc,
                f"${monto:,.2f}",
                fecha,
                f"${acumulado:,.2f}"
            ))

            # totales por principal
            por_principal[principal] = por_principal.get(principal, 0.0) + monto
            # totales por subcategoría (con clave combinada para claridad)
            key_sub = f"{principal} > {sub}" if sub else principal
            por_subcat[key_sub] = por_subcat.get(key_sub, 0.0) + monto

        # Texto de totales (general + por categoría principal + por subcat)
        bloques = [f"Total general: ${total_general:,.2f}"]

        if por_principal:
            orden_principal = sorted(por_principal.items(), key=lambda kv: kv[1], reverse=True)
            texto_principal = " | ".join([f"{c}: ${v:,.2f}" for c, v in orden_principal])
            bloques.append(f"[Por categoría] {texto_principal}")

        if por_subcat:
            # muestra las 5 más grandes para no saturar
            orden_sub = sorted(por_subcat.items(), key=lambda kv: kv[1], reverse=True)[:5]
            texto_sub = " | ".join([f"{c}: ${v:,.2f}" for c, v in orden_sub])
            bloques.append(f"[Top subcategorías] {texto_sub}")

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
