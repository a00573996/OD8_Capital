# win_list.py — ZAVE (Registro de Gastos con IA/CSV + edición + botón Inicio + eliminación persistente)
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json

# Persistencia CSV
from core.storage import append_gasto, load_gastos, clear_gastos, save_all_gastos

# IA: primero Gemini, luego OpenAI (ai.py). Si ambas fallan, ai.py cae a local.
from core.ai_gemini import clasificar_texto_gemini
from core.ai import clasificar_texto as clasificar_texto_openai

# Utilidad para ubicar data/
from core.paths import get_data_dir

# Paleta coherente (Versión A, primario AZUL)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"


def _load_categorias_list() -> list[str]:
    """Carga la lista de categorías desde data/categorias.json (o un fallback)."""
    try:
        with open(get_data_dir() / "categorias.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            cats = data.get("categorias")
            if isinstance(cats, list) and cats:
                return cats
    except Exception:
        pass
    return [
        "Alimentos y Bebidas > Supermercado",
        "Alimentos y Bebidas > Restaurante / Comida rápida",
        "Alimentos y Bebidas > Cafetería / Snacks",
        "Transporte > Gasolina / Ride-hailing",
        "Transporte > Público / Estacionamiento",
        "Vivienda y Servicios > Renta / Hogar",
        "Vivienda y Servicios > Servicios básicos (luz, agua, internet)",
        "Salud y Bienestar > Medicinas / Consultas",
        "Compras Personales > Ropa / Electrónica / Hogar",
        "Mascotas > Alimento / Cuidado",
        "Entretenimiento y Ocio > Cine / Streaming / Eventos",
        "Finanzas y Trámites > Ahorro / Pagos / Impuestos",
        "Otros"
    ]


def open_win_list(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Registro de Gastos")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1280x800")
    win.minsize(1280, 720)

    # ---------- Escalado adaptable ----------
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
        card,
        text="Ingresa la descripción y el monto. La categoría se clasifica automáticamente (Gemini → OpenAI → local) y se guarda en data/gastos.csv. Puedes editar categoría, descripción y monto desde la lista.",
        text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl)
    ).grid(row=1, column=0, columnspan=4, sticky="w", padx=pad_card)

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=2, column=0, columnspan=4, sticky="ew", padx=pad_sep_x, pady=(int(12 * scale), int(16 * scale)))

    # ---------- Entradas ----------
    ctk.CTkLabel(card, text="Descripción del gasto:", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl)).grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_desc = ctk.CTkEntry(card, height=entry_h)
    ent_desc.grid(row=3, column=1, sticky="ew", pady=6)

    ctk.CTkLabel(card, text="Monto ($):", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl)).grid(row=3, column=2, sticky="e", padx=(0, 8), pady=6)
    ent_monto = ctk.CTkEntry(card, height=entry_h, width=140)
    ent_monto.grid(row=3, column=3, sticky="w", pady=6)

    # ---------- Acciones ----------
    actions = ctk.CTkFrame(card, fg_color=CARD_BG)
    actions.grid(row=4, column=0, columnspan=4, sticky="ew", pady=6, padx=pad_card)
    actions.grid_columnconfigure(0, weight=1)  # para empujar botones a la derecha

    # Estado interno: mapeo 1:1 lista ↔ CSV
    # lb_items[i] = {"csv_index", "desc", "cat", "monto", "fecha"}
    lb_items: list[dict] = []
    CATS = _load_categorias_list()

    def _format_row_text(desc: str, cat: str, monto_val: float) -> str:
        return f"{desc}  —  [{cat}]  —  ${monto_val:,.2f}"

    def _reload_rows_meta_from_csv():
        lb.delete(0, "end")
        lb_items.clear()
        rows = load_gastos()
        for idx, r in enumerate(rows):
            desc  = (r.get("descripcion") or "").strip()
            cat   = (r.get("categoria") or "Otros").strip()
            monto_txt = (r.get("monto") or "0").strip()
            try:
                monto_val = float(monto_txt.replace(",", "")) if monto_txt else 0.0
            except ValueError:
                monto_val = 0.0
            lb.insert("end", _format_row_text(desc, cat, monto_val))
            lb_items.append({
                "csv_index": idx,
                "desc": desc,
                "cat": cat,
                "monto": monto_val,
                "fecha": (r.get("fecha") or "").strip(),
            })

    def agregar():
        desc = (ent_desc.get() or "").strip()
        if not desc:
            messagebox.showwarning("Aviso", "Escribe la descripción del gasto.")
            return
        monto_txt = (ent_monto.get() or "").strip()
        try:
            monto_val = float(monto_txt) if monto_txt else 0.0
        except ValueError:
            messagebox.showwarning("Aviso", "Monto inválido. Usa un número (ej. 120.50).")
            return

        # IA: Gemini → OpenAI → Local
        cat = clasificar_texto_gemini(desc)
        if cat == "Otros":
            cat = clasificar_texto_openai(desc)

        # Persistir (al final del CSV)
        append_gasto(descripcion=desc, categoria=cat, monto=monto_val)

        # Recargar mapeo/visualización
        _reload_rows_meta_from_csv()

        # Limpiar campos
        ent_desc.delete(0, "end")
        ent_monto.delete(0, "end")

    def eliminar():
        sel = lb.curselection()
        if not sel:
            messagebox.showinfo("Eliminar", "Selecciona un gasto de la lista.")
            return
        i = sel[0]
        meta = lb_items[i]
        csv_idx = meta.get("csv_index", -1)

        if not messagebox.askyesno("Confirmar", "¿Eliminar el gasto seleccionado de forma permanente?"):
            return

        # Eliminar en CSV y recargar
        rows = load_gastos()
        if 0 <= csv_idx < len(rows):
            try:
                del rows[csv_idx]
                save_all_gastos(rows)    # guarda con encabezado
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar del archivo:\n{e}")
                return
        else:
            # índice inesperado; recargar por seguridad
            messagebox.showwarning("Aviso", "No se encontró el registro en el archivo. Se recargará la lista.")
        _reload_rows_meta_from_csv()

    def limpiar():
        if lb.size() == 0:
            return
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los gastos? (lista + CSV)"):
            try:
                clear_gastos()  # deja encabezado vacío
                _reload_rows_meta_from_csv()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo limpiar el archivo:\n{e}")

    # ---- Editar categoría/descripcion/monto ----
    def editar():
        sel = lb.curselection()
        if not sel:
            messagebox.showinfo("Editar", "Selecciona un gasto de la lista.")
            return
        i = sel[0]
        meta = lb_items[i]
        current_cat = meta["cat"]
        current_desc = meta["desc"]
        current_monto = meta["monto"]

        # Diálogo
        dlg = ctk.CTkToplevel(win)
        dlg.title("Editar gasto")
        dlg.transient(win)
        dlg.grab_set()
        dlg.minsize(500, 280)

        frame = ctk.CTkFrame(dlg, fg_color=CARD_BG, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Descripción
        ctk.CTkLabel(frame, text="Descripción:", text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
        ent_desc_edit = ctk.CTkEntry(frame, width=360)
        ent_desc_edit.grid(row=0, column=1, sticky="w", pady=(0, 8))
        ent_desc_edit.insert(0, current_desc)

        # Monto
        ctk.CTkLabel(frame, text="Monto ($):", text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
        ent_monto_edit = ctk.CTkEntry(frame, width=180)
        ent_monto_edit.grid(row=1, column=1, sticky="w", pady=(0, 8))
        ent_monto_edit.insert(0, f"{current_monto:.2f}")

        # Categoría
        ctk.CTkLabel(frame, text="Categoría:", text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI", 12)).grid(row=2, column=0, sticky="w")
        cmb = ctk.CTkComboBox(frame, values=CATS, state="readonly", width=360)
        try:
            pre = CATS.index(current_cat) if current_cat in CATS else 0
        except Exception:
            pre = 0
        cmb.set(CATS[pre] if CATS else current_cat)
        cmb.grid(row=2, column=1, sticky="w", pady=(0, 12))

        # Botones
        btns = ctk.CTkFrame(frame, fg_color=CARD_BG)
        btns.grid(row=3, column=0, columnspan=2, sticky="e")

        def _guardar_cambio():
            new_desc = (ent_desc_edit.get() or "").strip()
            new_monto_txt = (ent_monto_edit.get() or "").strip()
            new_cat = (cmb.get() or "").strip() or current_cat

            if not new_desc:
                messagebox.showwarning("Aviso", "La descripción no puede estar vacía.")
                return
            try:
                new_monto = float(new_monto_txt.replace(",", "")) if new_monto_txt else 0.0
            except ValueError:
                messagebox.showwarning("Aviso", "Monto inválido.")
                return

            # 1) Actualizar CSV
            rows = load_gastos()
            csv_idx = meta["csv_index"]
            if 0 <= csv_idx < len(rows):
                rows[csv_idx]["descripcion"] = new_desc
                rows[csv_idx]["categoria"] = new_cat
                rows[csv_idx]["monto"] = f"{new_monto:.2f}"
                try:
                    save_all_gastos(rows)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el cambio:\n{e}")
                    return

            # 2) Refrescar UI
            _reload_rows_meta_from_csv()
            dlg.destroy()

        ctk.CTkButton(btns, text="Guardar",
                      fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                      corner_radius=8, command=_guardar_cambio).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Cancelar",
                      fg_color="white", hover_color="#F8FAFF",
                      text_color=TEXT, border_color=SEPARATOR, border_width=2,
                      corner_radius=8, command=dlg.destroy).pack(side="right", padx=6)

    # Botones principales (a la derecha del row de acciones)
    ctk.CTkButton(
        actions, text="Agregar gasto",
        fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
        command=agregar
    ).grid(row=0, column=3, sticky="e", padx=6)

    ctk.CTkButton(
        actions, text="Eliminar seleccionado",
        fg_color="white", hover_color="#F8FAFF",
        border_color=PRIMARY_BLUE, border_width=2, text_color=PRIMARY_BLUE,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=eliminar
    ).grid(row=0, column=1, sticky="w", padx=6)

    ctk.CTkButton(
        actions, text="Limpiar",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=limpiar
    ).grid(row=0, column=0, sticky="w", padx=6)

    ctk.CTkButton(
        actions, text="Editar seleccionado",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=editar
    ).grid(row=0, column=2, sticky="w", padx=6)

    # ---------- Lista ----------
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

    # Cargar CSV al abrir
    _reload_rows_meta_from_csv()

    # Enter = agregar directo
    ent_desc.bind("<Return>", lambda e: agregar())

    # ---------- Pie ----------
    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=98, column=0, columnspan=4, sticky="ew", padx=pad_sep_x, pady=(int(14 * scale), int(12 * scale)))

    # Lógica Inicio (cierra ventana + root oculto y relanza Main)
    def _go_home():
        try:
            win.destroy()
        except Exception:
            pass
        try:
            parent.destroy()
        except Exception:
            pass
        from app.main import main as launch_main
        launch_main()

    footer = ctk.CTkFrame(card, fg_color=CARD_BG)
    footer.grid(row=99, column=0, columnspan=4, sticky="ew", padx=pad_card, pady=(0, pad_card))
    footer.grid_columnconfigure(0, weight=1)
    footer.grid_columnconfigure(1, weight=0)

    # ⟵ Inicio (izquierda)
    ctk.CTkButton(
        footer, text="⟵ Inicio",
        fg_color="white", hover_color="#F8FAFF",
        text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=_go_home
    ).grid(row=0, column=0, sticky="w")

    # Cerrar (derecha)
    ctk.CTkButton(
        footer, text="Cerrar",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        height=btn_h, corner_radius=radius, font=ctk.CTkFont("Segoe UI", font_btn),
        command=win.destroy
    ).grid(row=0, column=1, sticky="e", padx=(6, 0))
