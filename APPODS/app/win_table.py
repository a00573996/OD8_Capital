# win_table.py — ZAVE (Reporte con tabla, totales y gráfica con scroll + barras/pastel + % y montos)
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from core.storage import load_gastos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"

# ---------------------- Helpers ----------------------
def _parse_float_safe(raw) -> float:
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
    # limpiar símbolos comunes
    s = s.replace("$", "").replace("€", "").replace("MXN", "").replace("USD", "").replace(" ", "")
    # normalizar coma decimal
    if "," in s and "." not in s:
        s = s.replace(".", "")
        s = s.replace(",", ".")
    else:
        parts = s.split(".")
        if len(parts) > 2:
            s = "".join(parts[:-1]) + "." + parts[-1]
        s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return 0.0

def _split_categoria(cat: str) -> tuple[str, str]:
    if not cat:
        return "Otros", ""
    txt = str(cat)
    if ">" in txt:
        p, s = txt.split(">", 1)
        return p.strip(), s.strip()
    if "/" in txt:
        parts = txt.split("/", 1)
        return parts[0].strip(), parts[1].strip()
    return txt.strip(), ""

# ---------------------- Ventana principal ----------------------
def open_win_table(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Reporte de Gastos")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1400x900")

    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw / 1920, sh / 1080)
    font_h1  = max(18, int(28 * scale))
    font_lbl = max(10, int(12 * scale))
    pad      = max(24, int(36 * scale))
    radius   = max(8, int(10 * scale))

    # ----- Scroll principal -----
    canvas_main = tk.Canvas(win, bg=BG, highlightthickness=0)
    canvas_main.pack(side="left", fill="both", expand=True)
    scrollbar_y = ttk.Scrollbar(win, orient="vertical", command=canvas_main.yview)
    scrollbar_y.pack(side="right", fill="y")
    canvas_main.configure(yscrollcommand=scrollbar_y.set)

    frame_container = ctk.CTkFrame(canvas_main, fg_color=BG)
    canvas_main.create_window((0, 0), window=frame_container, anchor="nw")

    def _on_configure(event):
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))
    frame_container.bind("<Configure>", _on_configure)

    # ----- Contenido -----
    card = ctk.CTkFrame(frame_container, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad, pady=pad)

    ctk.CTkLabel(card, text="Reporte de Gastos", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h1))\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, int(8 * scale)))

    ctk.CTkLabel(card, text="Visualización de gastos guardados en data/gastos.csv",
                 text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=0, column=1, sticky="e", padx=pad)

    card.grid_rowconfigure(1, weight=1)   # tabla crece
    card.grid_rowconfigure(3, weight=0)   # gráfica
    for c in (0, 1):
        card.grid_columnconfigure(c, weight=1)

    # ---------------- Tabla ----------------
    table_frame = ctk.CTkFrame(card, fg_color=CARD_BG)
    table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=pad, pady=(10, pad))
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    columns = ("cat_principal", "subcategoria", "descripcion", "monto", "fecha", "acumulado")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    for col, text, width, anchor in [
        ("cat_principal", "Categoría", 260, "w"),
        ("subcategoria", "Subcategoría", 240, "w"),
        ("descripcion", "Descripción", 460, "w"),
        ("monto", "Monto", 140, "e"),
        ("fecha", "Fecha", 180, "center"),
        ("acumulado", "Acumulado", 160, "e"),
    ]:
        tree.heading(col, text=text)
        tree.column(col, width=width, anchor=anchor)

    tree.grid(row=0, column=0, sticky="nsew")
    sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    sb.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=sb.set)

    # ---------------- Totales + Botones ----------------
    footer = ctk.CTkFrame(card, fg_color=CARD_BG)
    footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, pad))
    footer.grid_columnconfigure(0, weight=1)

    lbl_totales = ctk.CTkLabel(footer, text="", text_color=TEXT,
                               font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_totales.grid(row=0, column=0, sticky="w")

    btns = ctk.CTkFrame(footer, fg_color=CARD_BG)
    btns.grid(row=0, column=1, sticky="e")

    # ------------- Gráfica integrada (barras/pastel) -------------
    chart_visible = tk.BooleanVar(value=False)
    chart_type = tk.StringVar(value="bar")  # "bar" o "pie"
    chart_frame = ctk.CTkFrame(card, fg_color=CARD_BG)
    chart_canvas_widget = None

    # Botón de alternar tipo (NO se muestra hasta que la gráfica esté visible)
    btn_switch = ctk.CTkButton(
        btns, text="Cambiar a pastel",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        corner_radius=8, command=lambda: switch_chart_type()
    )
    # Nota: no lo .pack todavía; se empaqueta cuando la gráfica se muestra

    def _destroy_chart():
        nonlocal chart_canvas_widget
        if chart_canvas_widget is not None:
            chart_canvas_widget.get_tk_widget().destroy()
            chart_canvas_widget = None
        for w in chart_frame.winfo_children():
            w.destroy()

    def _format_money(val: float) -> str:
        return f"${val:,.2f}"

    def _build_chart(por_principal: dict[str, float]):
        """
        Dibuja una barra o pastel con totales por categoría principal,
        mostrando porcentaje y monto. En barras, el texto va DENTRO de la barra,
        pegado al borde superior con contraste blanco.
        """
        nonlocal chart_canvas_widget
        _destroy_chart()

        if not por_principal:
            ctk.CTkLabel(chart_frame, text="No hay datos para graficar.",
                         text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl)).pack(padx=pad, pady=pad)
            return

        # Ordenado desc por monto
        items = sorted(por_principal.items(), key=lambda kv: kv[1], reverse=True)
        cats = [c for c, _ in items]
        vals = [v for _, v in items]
        total = sum(vals) if vals else 1.0

        if chart_type.get() == "bar":
            # Altura dinámica
            height = max(3.8, min(7.0, len(cats) * 0.48))
            fig, ax = plt.subplots(figsize=(8.5, height))
            bars = ax.bar(cats, vals, color=["#60A5FA" if i % 2 else "#3B82F6" for i in range(len(cats))])
            ax.set_title("Gasto por categoría (total, % y monto)", fontsize=12, fontweight="bold")
            ax.set_ylabel("Monto ($)")
            ax.set_xlabel("Categorías")
            ax.tick_params(axis="x", labelrotation=18)

            # Texto DENTRO de cada barra, borde superior
            max_v = max(vals) if vals else 1.0
            for rect, v in zip(bars, vals):
                pct = (v / total) * 100.0 if total else 0.0
                label = f"{pct:.1f}% — {_format_money(v)}"
                # y interno un poco por debajo de la cima
                y_text = rect.get_height() - (0.02 * max_v)
                # Evitar y negativo si barra muy pequeña
                if y_text < rect.get_height() * 0.6:
                    y_text = rect.get_height() * 0.6
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    y_text,
                    label,
                    ha="center", va="top",
                    fontsize=9, fontweight="bold",
                    color="white",
                    clip_on=True
                )

            fig.tight_layout()

        else:  # pie
            def _autopct(pct):
                v = pct / 100.0 * total
                return f"{pct:.1f}%\n{_format_money(v)}"

            fig, ax = plt.subplots(figsize=(7.5, 5.5))
            wedges, texts, autotexts = ax.pie(
                vals,
                labels=cats,
                autopct=_autopct,
                startangle=90,
                wedgeprops=dict(width=0.82),
                pctdistance=0.78
            )
            ax.axis("equal")
            ax.set_title("Distribución de gasto por categoría", fontsize=12, fontweight="bold")
            for t in autotexts: t.set_fontsize(9)
            for t in texts: t.set_fontsize(9)
            fig.tight_layout()

        chart_canvas_widget = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas_widget.draw()
        chart_canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=pad, pady=(0, pad))

    def toggle_chart():
        # Muestra/oculta la gráfica y también muestra/oculta el botón de alternar tipo
        if not chart_visible.get():
            chart_visible.set(True)
            chart_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, pad))
            rows = load_gastos()
            por_principal = {}
            for r in rows:
                monto = _parse_float_safe(r.get("monto", 0))
                principal, _ = _split_categoria(r.get("categoria", "Otros") or "Otros")
                por_principal[principal] = por_principal.get(principal, 0.0) + monto
            _build_chart(por_principal)
            btn_chart.configure(text="Ocultar gráfica")
            # ahora sí mostramos el botón de alternar tipo
            btn_switch.configure(text="Cambiar a pastel" if chart_type.get() == "bar" else "Cambiar a barras")
            btn_switch.pack(side="left", padx=6)
        else:
            chart_visible.set(False)
            _destroy_chart()
            chart_frame.grid_forget()
            btn_chart.configure(text="Mostrar gráfica")
            # ocultar el botón de alternar tipo al ocultar gráfica
            btn_switch.pack_forget()

        win.update_idletasks()
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))

    def switch_chart_type():
        chart_type.set("pie" if chart_type.get() == "bar" else "bar")
        if chart_visible.get():
            rows = load_gastos()
            por_principal = {}
            for r in rows:
                monto = _parse_float_safe(r.get("monto", 0))
                principal, _ = _split_categoria(r.get("categoria", "Otros") or "Otros")
                por_principal[principal] = por_principal.get(principal, 0.0) + monto
            _build_chart(por_principal)
        btn_switch.configure(text="Cambiar a barras" if chart_type.get() == "pie" else "Cambiar a pastel")
        win.update_idletasks()
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))

    # ------------- Tabla / Totales -------------
    def cargar_tabla():
        for row_id in tree.get_children():
            tree.delete(row_id)

        rows = load_gastos()
        total_general = 0.0
        por_principal = {}
        por_subcat = {}
        acumulado = 0.0

        for r in rows:
            monto = _parse_float_safe(r.get("monto", 0))
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

            por_principal[principal] = por_principal.get(principal, 0.0) + monto
            key_sub = f"{principal} > {sub}" if sub else principal
            por_subcat[key_sub] = por_subcat.get(key_sub, 0.0) + monto

        # Totales (texto) con % por categoría principal
        bloques = [f"Total general: ${total_general:,.2f}"]
        if por_principal and total_general > 0:
            orden_principal = sorted(por_principal.items(), key=lambda kv: kv[1], reverse=True)
            texto_principal = " | ".join([
                f"{c}: ${v:,.2f} ({(v/total_general)*100:.1f}%)"
                for c, v in orden_principal
            ])
            bloques.append(f"[Por categoría] {texto_principal}")
        lbl_totales.configure(text="   ".join(bloques))

        # Si la gráfica está visible, redibujar
        if chart_visible.get():
            _build_chart(por_principal)

        win.update_idletasks()
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))

    def limpiar_tabla():
        for row_id in tree.get_children():
            tree.delete(row_id)
        lbl_totales.configure(text="")
        if chart_visible.get():
            _destroy_chart()

    # Botones
    ctk.CTkButton(btns, text="Actualizar",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, command=cargar_tabla).pack(side="left", padx=6)

    ctk.CTkButton(btns, text="Limpiar vista",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, command=limpiar_tabla).pack(side="left", padx=6)

    btn_chart = ctk.CTkButton(btns, text="Mostrar gráfica",
                              fg_color="white", hover_color="#F8FAFF",
                              text_color=TEXT, border_color=SEPARATOR, border_width=2,
                              corner_radius=8, command=toggle_chart)
    btn_chart.pack(side="left", padx=6)

    # Primera carga
    cargar_tabla()
    win.update_idletasks()
    canvas_main.configure(scrollregion=canvas_main.bbox("all"))
