# app/win_reco.py — Recomendaciones personalizadas (MX), con scroll, botón Inicio y Exportar
from __future__ import annotations
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.profile import load_profile, save_profile
from core.classifier import classify_user
from core.storage import load_gastos

# NUEVO: navegación unificada a Inicio
from app.utils.nav import go_home

# Paleta
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"
OK_GREEN           = "#16A34A"
WARN_AMBER         = "#F59E0B"
DANGER_RED         = "#DC2626"

def _pct_text(x: float) -> str:
    try: return f"{x*100:.1f}%"
    except: return "0%"

def _fmt_money(x) -> str:
    try: return f"${float(x):,.2f}"
    except: return "$0.00"

def _split_categoria(cat: str) -> tuple[str, str]:
    if not cat: return "Otros", ""
    s = str(cat)
    if ">" in s:
        p, sub = s.split(">", 1)
        return p.strip(), sub.strip()
    if "/" in s:
        p, sub = s.split("/", 1)
        return p.strip(), sub.strip()
    return s.strip(), ""

def _totales_por_categoria():
    """Suma por categoría principal desde CSV para recomendaciones específicas."""
    cats = {}
    total = 0.0
    for r in load_gastos():
        raw = r.get("monto", 0) or 0
        try:
            s = str(raw).replace("$","").replace(",","").strip()
            v = float(s) if s else 0.0
        except:
            v = 0.0
        p,_ = _split_categoria(r.get("categoria","Otros") or "Otros")
        cats[p] = cats.get(p, 0.0) + v
        total += v
    ordered = sorted(cats.items(), key=lambda kv: kv[1], reverse=True)
    with_pct = [(k, v, (v/total if total>0 else 0.0)) for k,v in ordered]
    return with_pct, total

def _chip(parent, text, bg="#EEF2FF", fg=TEXT, pad=6):
    lbl = ctk.CTkLabel(parent, text=text, text_color=fg, fg_color=bg,
                       corner_radius=8, padx=pad, pady=2,
                       font=ctk.CTkFont("Segoe UI", 11))
    lbl.pack(side="left", padx=4, pady=2)
    return lbl

def _bar_row(parent, label, value_pct: float, right_txt: str):
    row = ctk.CTkFrame(parent, fg_color=CARD_BG)
    row.pack(fill="x", padx=0, pady=4)
    ctk.CTkLabel(row, text=label, text_color=TEXT, width=220,
                 font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
    pb = ctk.CTkProgressBar(row, height=14, corner_radius=8,
                            progress_color=PRIMARY_BLUE)
    pb.pack(side="left", fill="x", expand=True, padx=8)
    try:
        pb.set(max(0.0, min(1.0, float(value_pct))))
    except:
        pb.set(0.0)
    ctk.CTkLabel(row, text=right_txt, text_color=TEXT_MUTED,
                 font=ctk.CTkFont("Segoe UI", 11)).pack(side="left", padx=6)
    return row

def _build_recos(cls: dict, state: dict, topcats: list[tuple[str,float,float]]):
    rec_corto, rec_med, rec_largo = [], [], []

    m   = cls.get("metrics", {})
    lab = cls.get("labels", {})
    consumo = cls.get("perfil_consumo", {})
    metas   = cls.get("metas", {}) or {}

    imt     = float(m.get("ingreso_total_mensual", 0.0))
    cv      = float(m.get("carga_vivienda", 0.0))
    dsr     = float(m.get("carga_deuda", 0.0))
    cf      = float(m.get("carga_fijos", 0.0))
    ca_mxn  = float(m.get("capacidad_ahorro_mxn", 0.0))
    ca_pct  = float(m.get("capacidad_ahorro_pct", 0.0))
    igd     = float(m.get("IGD", 0.0))

    ess = max(0.0, imt * (cv + cf + dsr))

    # --- Corto plazo (0–30 días) ---
    if ca_pct <= 0:
        rec_corto.append("Detén la fuga de caja: congela gastos discrecionales por 30 días (comer fuera, café, compras online).")
    if cv >= 0.30:
        rec_corto.append("Revisa contrato de vivienda: renegocia renta/servicios o considera roommate para bajar la carga < 30%.")
    if dsr >= 0.20:
        rec_corto.append("Define estrategia de deudas (avalancha o bola de nieve) y evita nuevos créditos.")
    if topcats:
        rec_corto.append("Ataca primero las categorías más altas con metas de reducción concretas (10–20%):")
        for k, v, p in topcats[:5]:
            rec_corto.append(f"• {k}: hoy {_fmt_money(v)} ({_pct_text(p)} del total). Propón tope mensual = {_fmt_money(v*0.85)}.")

    # --- Mediano plazo (1–6 meses) ---
    est = (lab.get("estabilidad_ingreso","Fijo") or "").lower()
    dependientes = int(state.get("situacion",{}).get("dependientes",0) or 0)
    base_months = 6 if ("alta" in est or "media" in est) else 3
    if dependientes>0: base_months += 3
    fondo_meta = base_months * ess
    rec_med.append(f"Fondo de emergencia: {base_months} meses de esenciales ≈ {_fmt_money(fondo_meta)}. Aporta automático: {_fmt_money(max(0.0, fondo_meta/ max(1, base_months*2)))}+/mes.")

    meta_p = metas.get("principal","Ahorro de emergencia")
    ratio  = float(m.get("ratio_aporte", 0.0))
    aporte_lbl = metas.get("aporte_label","Aporte insuficiente")
    if meta_p and meta_p != "N/D":
        rec_med.append(f"Meta: {meta_p} — estado: {aporte_lbl}. Ajusta aportación para estar ≥100% del requerido (hoy {ratio*100:.0f}%).")

    if igd >= 60:
        rec_med.append("Tope discrecional: fija presupuestos envelope (comer/café/online) para no exceder 15–20% del ingreso.")
    if cv >= 0.45:
        rec_med.append("Plan de mudanza (3–6 meses): busca opciones para llevar vivienda < 30% del ingreso.")
    if cf >= 0.50:
        rec_med.append("Audita servicios y suscripciones: baja fijos a < 35% (renegocia internet/luz, cancela duplicados).")

    # --- Largo plazo (6–24 meses) ---
    if ca_pct >= 0.10:
        rec_largo.append("Automatiza inversión del 10–20% del ingreso (tras cumplir fondo de emergencia).")
    else:
        rec_largo.append("Primero consolida fondo y reduce cargas; luego invierte de forma automática.")
    if dsr >= 0.35:
        rec_largo.append("Consolida deudas costosas si es viable (sin alargar plazo total) y libera flujo para metas.")
    if lab.get("segmento_ingreso") in ("Medio alto","Alto"):
        rec_largo.append("Optimiza impuestos y formaliza objetivos (AFORE/planes personales, inversión diversificada).")

    tags = set((consumo or {}).get("tags", []))
    if "Foodie" in tags:
        rec_med.append("Batch cooking y menú semanal para recortar 15–25% en ‘comer fuera’.")
    if "Café lover" in tags:
        rec_corto.append("Sustituye 50% de cafés fuera por termo en casa; reinvierte el ahorro a tu meta.")
    if "Onliner" in tags:
        rec_corto.append("Carrito 24h + regla 30 días para compras no esenciales; desactiva ‘comprar en 1 clic’.")

    return {
        "Corto plazo (0–30 días)": rec_corto,
        "Mediano plazo (1–6 meses)": rec_med,
        "Largo plazo (6–24 meses)": rec_largo,
    }

def open_win_reco(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Recomendaciones personalizadas")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1400x900")
    win.minsize(1280, 720)

    # Lista de afters por si agregas animaciones (evita pyimageX al cerrar)
    _afters: list[str] = []

    # Escala
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale  = min(sw/1920, sh/1080)
    pad    = max(24, int(36*scale))
    radius = max(8, int(10*scale))
    font_h1= max(18, int(28*scale))
    font_h2= max(14, int(20*scale))
    font_lbl=max(10, int(12*scale))

    # -------- Scroll principal --------
    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    vsb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    vsb.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=vsb.set)

    container = ctk.CTkFrame(canvas, fg_color=BG)
    canvas.create_window((0,0), window=container, anchor="nw")
    container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # ---------- Card principal ----------
    card = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad, pady=pad)

    # Header
    header = ctk.CTkFrame(card, fg_color=CARD_BG)
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=pad, pady=(pad, 8))
    ctk.CTkLabel(header, text="Recomendaciones personalizadas", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h1)).pack(side="left")

    # Botón Inicio (lógica unificada)
    def _go_home():
        go_home(win, parent, after_ids=_afters)

    ctk.CTkButton(
        header, text="⟵ Inicio",
        fg_color="white", hover_color="#F8FAFF",
        text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
        corner_radius=8, command=_go_home
    ).pack(side="right")

    # Subheader
    ctk.CTkLabel(card, text="Plan en 3 horizontes (corto / mediano / largo) según tu perfil, ingresos y gastos.",
                 text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=1, column=0, columnspan=2, sticky="w", padx=pad, pady=(0, pad//2))

    # Columnas
    for c in (0,1):
        card.grid_columnconfigure(c, weight=1)

    # ---------- Carga clasificación ----------
    state = load_profile()
    cls = state.get("classification")
    if not cls:
        try:
            cls = classify_user(state)
            state["classification"] = cls
            save_profile(state)
        except Exception as e:
            messagebox.showwarning("Aviso", f"No se pudo clasificar automáticamente:\n{e}")
            cls = {}

    # ---------- Resumen / chips ----------
    box_summary = ctk.CTkFrame(card, fg_color=BG, corner_radius=10)
    box_summary.grid(row=2, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, pad))

    persona = cls.get("persona", "Perfil no disponible")
    ctk.CTkLabel(box_summary, text=persona, text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_h2)).pack(anchor="w", padx=12, pady=(12,6))

    chips = ctk.CTkFrame(box_summary, fg_color=BG)
    chips.pack(fill="x", padx=12, pady=(0,12))
    labels = (cls.get("labels") or {})
    _chip(chips, f"Segmento: {labels.get('segmento_ingreso','N/D')}")
    _chip(chips, f"Estabilidad: {labels.get('estabilidad_ingreso','N/D')}")
    _chip(chips, f"Ahorro: {labels.get('capacidad_ahorro','N/D')}")
    _chip(chips, f"Vivienda: {labels.get('carga_vivienda','N/D')}")
    _chip(chips, f"Deuda: {labels.get('carga_deuda','N/D')}")

    # ---------- Métricas con barras ----------
    box_metrics = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=10)
    box_metrics.grid(row=3, column=0, sticky="nsew", padx=pad, pady=(0,pad))
    card.grid_rowconfigure(3, weight=0)
    ctk.CTkLabel(box_metrics, text="Tu foto financiera (mensual)", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h2)).pack(anchor="w", padx=pad, pady=(12,8))

    m = cls.get("metrics", {}) if cls else {}
    imt = float(m.get("ingreso_total_mensual", 0.0))
    _bar_row(box_metrics, "Capacidad de ahorro",
             float(m.get("capacidad_ahorro_pct", 0.0)),
             f"{_pct_text(float(m.get('capacidad_ahorro_pct',0.0)))}  |  {_fmt_money(m.get('capacidad_ahorro_mxn',0.0))}/mes")
    _bar_row(box_metrics, "Carga vivienda",
             float(m.get("carga_vivienda", 0.0)),
             f"{_pct_text(float(m.get('carga_vivienda',0.0)))}  ({_fmt_money(imt*float(m.get('carga_vivienda',0.0)))})")
    _bar_row(box_metrics, "Carga deudas",
             float(m.get("carga_deuda", 0.0)),
             f"{_pct_text(float(m.get('carga_deuda',0.0)))}  ({_fmt_money(imt*float(m.get('carga_deuda',0.0)))})")
    _bar_row(box_metrics, "Gastos fijos",
             float(m.get("carga_fijos", 0.0)),
             f"{_pct_text(float(m.get('carga_fijos',0.0)))}  ({_fmt_money(imt*float(m.get('carga_fijos',0.0)))})")
    _bar_row(box_metrics, "Gasto discrecional (IGD)",
             min(1.0, float(m.get("IGD",0.0))/100.0),
             f"{float(m.get('IGD',0.0)):.0f} / 100")

    # ---------- Top categorías de gasto (desde CSV) ----------
    box_top = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=10)
    box_top.grid(row=3, column=1, sticky="nsew", padx=pad, pady=(0,pad))
    ctk.CTkLabel(box_top, text="Top categorías de gasto", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h2)).pack(anchor="w", padx=pad, pady=(12,6))

    topcats, total_g = _totales_por_categoria()
    if not topcats:
        ctk.CTkLabel(box_top, text="No hay datos en gastos.csv todavía.",
                     text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl)).pack(anchor="w", padx=pad, pady=(0,12))
    else:
        for k, v, p in topcats[:8]:
            row = ctk.CTkFrame(box_top, fg_color=BG, corner_radius=8)
            row.pack(fill="x", padx=pad, pady=4)
            ctk.CTkLabel(row, text=k, text_color=TEXT,
                         font=ctk.CTkFont("Segoe UI", 12)).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=f"{_fmt_money(v)}   ({_pct_text(p)})", text_color=TEXT_MUTED,
                         font=ctk.CTkFont("Segoe UI", 11)).pack(side="right", padx=10)

    # ---------- Recomendaciones (corto/mediano/largo) ----------
    recs = _build_recos(cls, state, topcats)

    box_recos = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=10)
    box_recos.grid(row=4, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0,pad))

    ctk.CTkLabel(box_recos, text="Tu plan de acción", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h2)).grid(row=0, column=0, sticky="w", padx=pad, pady=(12,8))

    def _render_section(title: str, items: list[str], r: int):
        sec = ctk.CTkFrame(box_recos, fg_color=BG, corner_radius=10)
        sec.grid(row=r, column=0, sticky="ew", padx=pad, pady=6)
        ctk.CTkLabel(sec, text=title, text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(10,6))
        if not items:
            ctk.CTkLabel(sec, text="(Sin acciones específicas por ahora)", text_color=TEXT_MUTED,
                         font=ctk.CTkFont("Segoe UI", 11)).pack(anchor="w", padx=12, pady=(0,10))
        else:
            for t in items:
                ctk.CTkLabel(sec, text=f"• {t}", text_color=TEXT,
                             font=ctk.CTkFont("Segoe UI", 12), wraplength=1100, justify="left")\
                    .pack(anchor="w", padx=14, pady=2)

    r = 1
    for title in ("Corto plazo (0–30 días)", "Mediano plazo (1–6 meses)", "Largo plazo (6–24 meses)"):
        _render_section(title, recs.get(title, []), r)
        r += 1

    # ---------- Acciones rápidas + Recalcular + Exportar ----------
    actions = ctk.CTkFrame(card, fg_color=CARD_BG)
    actions.grid(row=5, column=0, columnspan=2, sticky="e", padx=pad, pady=(0,pad))

    def _open_home():
        from app.win_home import open_win_home
        open_win_home(parent)

    def _open_form():
        from app.win_form import open_win_form
        open_win_form(parent)

    def _open_list():
        from app.win_list import open_win_list
        open_win_list(parent)

    ctk.CTkButton(actions, text="Editar Perfil",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
                  corner_radius=8, command=_open_home).pack(side="left", padx=6)
    ctk.CTkButton(actions, text="Actualizar Ingresos",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
                  corner_radius=8, command=_open_form).pack(side="left", padx=6)
    ctk.CTkButton(actions, text="Ver Gastos",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
                  corner_radius=8, command=_open_list).pack(side="left", padx=6)

    def _refresh():
        s = load_profile()
        try:
            s["classification"] = classify_user(s)
            save_profile(s)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recalcular:\n{e}")
            return
        messagebox.showinfo("Listo", "Recomendaciones recalculadas. Vuelve a abrir esta ventana para ver cambios.")

    ctk.CTkButton(actions, text="Recalcular",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, command=_refresh).pack(side="left", padx=6)

    # ------- Exportar (MD/HTML/PDF) -------
    def _build_markdown(cls: dict, state: dict, topcats, recs) -> str:
        u = state.get("usuario", {})
        m = (cls or {}).get("metrics", {}) or {}
        lbl = (cls or {}).get("labels", {}) or {}

        lines = []
        lines.append("# Recomendaciones ZAVE\n")
        lines.append(f"**Persona**: {cls.get('persona','N/D')}\n")
        lines.append(f"**Nombre**: {u.get('nombre','N/D')} | **Edad**: {u.get('edad','N/D')} | **Ciudad**: {state.get('usuario',{}).get('ubicacion',{}).get('ciudad','')}\n")
        lines.append(f"**Segmento**: {lbl.get('segmento_ingreso','N/D')}  |  **Estabilidad**: {lbl.get('estabilidad_ingreso','N/D')}  |  **Ahorro**: {lbl.get('capacidad_ahorro','N/D')}\n")
        lines.append("\n---\n")
        lines.append("## Métricas\n")
        lines.append(f"- Ingreso total mensual: {_fmt_money(m.get('ingreso_total_mensual',0))}")
        lines.append(f"- Capacidad de ahorro: {_pct_text(float(m.get('capacidad_ahorro_pct',0)))} ({_fmt_money(m.get('capacidad_ahorro_mxn',0))}/mes)")
        lines.append(f"- Carga vivienda: {_pct_text(float(m.get('carga_vivienda',0)))}")
        lines.append(f"- Carga deudas: {_pct_text(float(m.get('carga_deuda',0)))}")
        lines.append(f"- Gastos fijos: {_pct_text(float(m.get('carga_fijos',0)))}")
        lines.append(f"- IGD (discrecional): {float(m.get('IGD',0)):.0f}/100\n")
        lines.append("## Top categorías de gasto\n")
        if not topcats:
            lines.append("- (Sin datos)\n")
        else:
            for k, v, p in topcats[:10]:
                lines.append(f"- {k}: {_fmt_money(v)} ({_pct_text(p)})")
            lines.append("")
        for title in ("Corto plazo (0–30 días)", "Mediano plazo (1–6 meses)", "Largo plazo (6–24 meses)"):
            lines.append(f"## {title}")
            arr = recs.get(title, [])
            if not arr:
                lines.append("- (Sin acciones por ahora)")
            else:
                for t in arr:
                    lines.append(f"- {t}")
            lines.append("")
        return "\n".join(lines)

    def _export():
        try:
            md = _build_markdown(cls, state, topcats, recs)
            path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown", "*.md"), ("HTML", "*.html"), ("Texto", "*.txt"), ("PDF", "*.pdf")],
                title="Exportar recomendaciones"
            )
            if not path:
                return
            lname = path.lower()
            if lname.endswith(".md") or lname.endswith(".txt"):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(md)
            elif lname.endswith(".html"):
                safe = (md.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
                html = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<title>Recomendaciones ZAVE</title>"
                    "<style>body{font-family: system-ui,Segoe UI,Arial,sans-serif; line-height:1.5; padding:24px;}"
                    "pre{white-space:pre-wrap;}</style></head><body>"
                    "<pre>"+ safe + "</pre></body></html>"
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
            elif lname.endswith(".pdf"):
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas as rlcanvas
                    from reportlab.lib.units import inch
                    from textwrap import wrap
                    c = rlcanvas.Canvas(path, pagesize=letter)
                    width, height = letter
                    y = height - 1*inch
                    for line in md.splitlines():
                        for chunk in wrap(line, 95):
                            c.drawString(0.75*inch, y, chunk)
                            y -= 14
                            if y < 0.75*inch:
                                c.showPage(); y = height - 1*inch
                    c.save()
                except Exception as e:
                    messagebox.showwarning("PDF no disponible", f"No se pudo exportar a PDF: {e}\nSe guardará como Markdown.")
                    alt = path.rsplit(".",1)[0] + ".md"
                    with open(alt, "w", encoding="utf-8") as f:
                        f.write(md)
                    path = alt
            messagebox.showinfo("Exportado", f"Archivo guardado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

    ctk.CTkButton(actions, text="Exportar",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, command=_export).pack(side="left", padx=6)

    # Ajustar scrollregion
    win.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Manejo del cierre por la X (igual que botón Inicio)
    win.protocol("WM_DELETE_WINDOW", _go_home)
