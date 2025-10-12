# win_form.py — ZAVE (Ingresos fijos + variables, validación, total en vivo, guarda en profile.json + botón Inicio)
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re

from core.profile import load_profile, save_profile

# Paleta coherente (azul)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"

# ---- Parser estricto de dinero + formateo -----------------------------------
_MONEY_CLEAN_RE = re.compile(r"[,\s]")

def parse_money_strict(txt: str) -> float | None:
    """
    Acepta: 1234, 1,234.56, $1,234.56, 1 234,56
    Rechaza letras u otros símbolos (salvo $ , . y espacios).
    Devuelve float o None si inválido.
    """
    if txt is None:
        return None
    s = str(txt).strip()
    if s == "":
        return None
    if re.search(r"[A-Za-z]", s):
        return None
    s = s.replace("$", "")
    s = _MONEY_CLEAN_RE.sub("", s)  # quita comas y espacios
    # normaliza coma decimal estilo EU
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        if re.fullmatch(r"-?\d+(,\d+)?", s):
            s = s.replace(",", ".")
        else:
            return None
    try:
        return float(s)
    except Exception:
        return None

def fmt_money(v: float | int | str) -> str:
    try:
        return f"{float(v):,.2f}"
    except Exception:
        return "0.00"


def open_win_form(parent: ctk.CTk):
    # Ventana secundaria
    win = ctk.CTkToplevel(parent)
    win.title("Ingresos")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1280x800")
    win.minsize(1280, 720)

    # ---------- Escalado adaptable ----------
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw / 1920, sh / 1080)

    # Dimensiones
    radius    = max(8, int(10 * scale))
    font_h1   = max(18, int(28 * scale))
    font_h2   = max(14, int(20 * scale))
    font_lbl  = max(10, int(12 * scale))
    font_btn  = max(10, int(14 * scale))
    entry_h   = max(28, int(34 * scale))
    btn_h     = max(36, int(44 * scale))
    pad_x     = max(40, int(60 * scale))
    pad_y     = max(24, int(36 * scale))

    # ---------- Contenedor principal ----------
    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_x, pady=pad_y)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad_x, pady=pad_y)
    for c in range(4):
        card.grid_columnconfigure(c, weight=1)

    # ---------- Encabezado ----------
    ctk.CTkLabel(
        card, text="Ingresos (fijos y variables)",
        text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_h1)
    ).grid(row=0, column=0, columnspan=4, sticky="w", padx=pad_x, pady=(pad_y, int(8 * scale)))

    ctk.CTkLabel(
        card,
        text="Registra tu ingreso fijo mensual y, si aplica, ingresos variables (opcional). Guardamos en tu perfil para usarlo en otras secciones.",
        text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl)
    ).grid(row=1, column=0, columnspan=4, sticky="w", padx=pad_x)

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=2, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=(int(10*scale), int(14*scale)))

    # ---------- Ingreso fijo ----------
    ctk.CTkLabel(card, text="Ingreso fijo mensual*", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_ingreso_fijo = ctk.CTkEntry(card, height=entry_h, width=180)
    ent_ingreso_fijo.grid(row=3, column=1, sticky="w", pady=6)

    # Validación y formateo al salir
    def _blur_ingreso_fijo(_=None):
        raw = ent_ingreso_fijo.get().strip()
        val = parse_money_strict(raw)
        if val is None or val < 0:
            messagebox.showerror("Dato inválido", "El ingreso fijo mensual debe ser un número ≥ 0.")
            ent_ingreso_fijo.focus_set()
            return
        ent_ingreso_fijo.delete(0, "end")
        ent_ingreso_fijo.insert(0, fmt_money(val))
        _recalcular_total()

    ent_ingreso_fijo.bind("<FocusOut>", _blur_ingreso_fijo)

    ctk.CTkLabel(card, text="Frecuencia del ingreso", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=3, column=2, sticky="e", padx=(0, 8), pady=6)
    cmb_frecuencia = ctk.CTkOptionMenu(
        card, values=["Mensual", "Quincenal", "Semanal", "Diario"],
        fg_color=PRIMARY_BLUE, button_color=PRIMARY_BLUE_DARK,
        button_hover_color=PRIMARY_BLUE_DARK, text_color="white",
        font=ctk.CTkFont("Segoe UI", font_lbl)
    )
    cmb_frecuencia.set("Mensual")
    cmb_frecuencia.grid(row=3, column=3, sticky="w", pady=6)

    # ---------- Ingresos variables ----------
    ctk.CTkLabel(card, text="Ingresos variables (opcional)", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h2))\
        .grid(row=4, column=0, sticky="w", padx=pad_x, pady=(int(8*scale), 6))

    ctk.CTkLabel(card, text="Concepto", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=5, column=0, sticky="e", padx=(0, 8))
    ent_var_concepto = ctk.CTkEntry(card, height=entry_h)
    ent_var_concepto.grid(row=5, column=1, sticky="ew", pady=4)

    ctk.CTkLabel(card, text="Monto", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=5, column=2, sticky="e", padx=(0, 8))
    ent_var_monto = ctk.CTkEntry(card, height=entry_h, width=160)
    ent_var_monto.grid(row=5, column=3, sticky="w", pady=4)

    # Lista + acciones
    list_container = ctk.CTkFrame(card, fg_color=BG, corner_radius=radius)
    list_container.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=pad_x, pady=(6, 0))
    card.grid_rowconfigure(6, weight=1)

    inner = tk.Frame(list_container, bg=BG)
    inner.pack(fill="both", expand=True, padx=6, pady=6)
    inner.grid_columnconfigure(0, weight=1)
    inner.grid_rowconfigure(0, weight=1)

    lb_vars = tk.Listbox(inner, height=8, activestyle="dotbox")
    lb_vars.grid(row=0, column=0, sticky="nsew")
    sb = tk.Scrollbar(inner, orient="vertical", command=lb_vars.yview)
    sb.grid(row=0, column=1, sticky="ns")
    lb_vars.config(yscrollcommand=sb.set)

    cont_vars: list[dict] = []

    def _recalcular_total():
        fijo = parse_money_strict(ent_ingreso_fijo.get()) or 0.0
        total_vars = sum(x["monto"] for x in cont_vars)
        lbl_total.configure(text=f"Total estimado mensual:  ${fmt_money(fijo + total_vars)}")

    def _agregar_var():
        concepto = (ent_var_concepto.get() or "").strip()
        if not concepto:
            messagebox.showwarning("Aviso", "Escribe un concepto para el ingreso variable.")
            return
        val = parse_money_strict((ent_var_monto.get() or "").strip())
        if val is None or val < 0:
            messagebox.showwarning("Aviso", "El monto del ingreso variable debe ser un número ≥ 0.")
            return
        cont_vars.append({"concepto": concepto, "monto": val})
        lb_vars.insert("end", f"{concepto} — ${fmt_money(val)}")
        ent_var_concepto.delete(0, "end")
        ent_var_monto.delete(0, "end")
        _recalcular_total()

    def _eliminar_sel():
        sel = lb_vars.curselection()
        if not sel:
            return
        idx = sel[0]
        lb_vars.delete(idx)
        cont_vars.pop(idx)
        _recalcular_total()

    def _limpiar_vars():
        if lb_vars.size() == 0:
            return
        if messagebox.askyesno("Confirmar", "¿Quitar todos los ingresos variables?"):
            lb_vars.delete(0, "end")
            cont_vars.clear()
            _recalcular_total()

    actions = ctk.CTkFrame(card, fg_color=CARD_BG)
    actions.grid(row=7, column=0, columnspan=4, sticky="e", padx=pad_x, pady=(6, 2))
    ctk.CTkButton(actions, text="Agregar variable",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=radius, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
                  command=_agregar_var).pack(side="left", padx=6)
    ctk.CTkButton(actions, text="Eliminar seleccionado",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
                  corner_radius=radius, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn),
                  command=_eliminar_sel).pack(side="left", padx=6)
    ctk.CTkButton(actions, text="Limpiar variables",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=radius, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn),
                  command=_limpiar_vars).pack(side="left", padx=6)

    # ---------- Total ----------
    total_row = ctk.CTkFrame(card, fg_color=CARD_BG)
    total_row.grid(row=8, column=0, columnspan=4, sticky="e", padx=pad_x, pady=(int(8*scale), 0))
    lbl_total = ctk.CTkLabel(total_row, text="Total estimado mensual:  $0.00",
                             text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_h2))
    lbl_total.pack(side="right")

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=9, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=int(12*scale))

    # ---------- Carga de estado y Guardado ----------
    state = load_profile()  # dict con keys: usuario, ingresos, situacion, metas, preferencias

    # Rellena UI con datos previos (si existen)
    ing = state.get("ingresos", {})
    fijo_ini = float(ing.get("fijo_mensual", 0.0) or 0.0)
    ent_ingreso_fijo.insert(0, fmt_money(fijo_ini))
    cmb_frecuencia.set(ing.get("frecuencia", "Mensual"))

    vars_ini = ing.get("variables", [])
    cont_vars.extend({"concepto": v.get("concepto",""), "monto": float(v.get("monto",0.0) or 0.0)} for v in vars_ini)
    for v in cont_vars:
        lb_vars.insert("end", f"{v['concepto']} — ${fmt_money(v['monto'])}")

    _recalcular_total()

    # Guardar en profile.json (sin diálogo)
    def _guardar(*, silent: bool = False) -> bool:
        # Validar fijo
        fijo_val = parse_money_strict(ent_ingreso_fijo.get())
        if fijo_val is None or fijo_val < 0:
            if not silent:
                messagebox.showerror("Error", "El ingreso fijo mensual debe ser un número ≥ 0.")
            ent_ingreso_fijo.focus_set()
            return False

        # Actualizar estado
        state.setdefault("ingresos", {})
        state["ingresos"]["fijo_mensual"] = float(fijo_val)
        state["ingresos"]["frecuencia"]   = cmb_frecuencia.get()
        # Clonar variables (por si la UI tiene floats)
        state["ingresos"]["variables"] = [{"concepto": x["concepto"], "monto": float(x["monto"])} for x in cont_vars]

        # (Opcional) total mensual estimado:
        total_vars = sum(x["monto"] for x in cont_vars)
        state.setdefault("totales", {})
        state["totales"]["ingreso_total_estimado"] = float(fijo_val) + total_vars

        try:
            save_profile(state)
            if not silent:
                messagebox.showinfo("OK", "Ingresos guardados en tu perfil.")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("Error", f"No se pudieron guardar los datos:\n{e}")
            return False

    # --- Navegación a Inicio (Main) ---
    def _go_home():
        # 1) intentar guardado silencioso
        saved = _guardar(silent=True)
        if not saved:
            # si no se pudo guardar (validación), pedir confirmación
            if not messagebox.askyesno("Volver a inicio",
                                       "Algunos datos no son válidos y no se guardarán.\n¿Volver a inicio de todas formas?"):
                return
        # 2) cerrar esta ventana y el root oculto
        try:
            win.destroy()
        except Exception:
            pass
        try:
            parent.destroy()
        except Exception:
            pass
        # 3) relanzar Main
        from app.main import main as launch_main
        launch_main()

    # Botonera
    btns = ctk.CTkFrame(card, fg_color=CARD_BG)
    btns.grid(row=10, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=(0, pad_y))
    btns.grid_columnconfigure(0, weight=1)
    btns.grid_columnconfigure(1, weight=0)
    btns.grid_columnconfigure(2, weight=0)

    # Inicio (outlined azul) — a la izquierda
    ctk.CTkButton(btns, text="⟵ Inicio",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
                  corner_radius=8, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn),
                  command=_go_home).grid(row=0, column=0, sticky="w")

    # A la derecha: Guardar y Cerrar
    ctk.CTkButton(btns, text="Guardar",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
                  command=_guardar).grid(row=0, column=1, sticky="e", padx=6)
    ctk.CTkButton(btns, text="Cerrar",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, height=btn_h, font=ctk.CTkFont("Segoe UI", font_btn),
                  command=win.destroy).grid(row=0, column=2, sticky="e")
    # Atajos prácticos
    ent_var_concepto.bind("<Return>", lambda _e: ent_var_monto.focus_set())
    ent_var_monto.bind("<Return>", lambda _e: _agregar_var())
