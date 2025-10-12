# app/win_home.py — ZAVE (Perfil con validación inline + botón "Inicio")
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re

from core.profile import load_profile, save_profile, is_valid_email, to_float, to_int

# Paleta (azul)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"
ERROR_RED          = "#DC2626"
BORDER_DEFAULT     = "#D1D5DB"

# --------- Parser de dinero estricto ---------
_MONEY_CLEAN_RE = re.compile(r"[,\s]")
def parse_money_strict(txt: str) -> float | None:
    if txt is None:
        return None
    s = str(txt).strip()
    if s == "":
        return None
    if re.search(r"[A-Za-z]", s):
        return None
    s = s.replace("$", "")
    s = _MONEY_CLEAN_RE.sub("", s)
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        if re.fullmatch(r"-?\d+(,\d+)?", s):
            s = s.replace(",", ".")
        else:
            return None
    try:
        return float(s)
    except Exception:
        return None


class ErrorInline:
    def __init__(self):
        self._labels = {}  # entry -> (parent_frame, label_widget)

    def show(self, entry: ctk.CTkEntry, message: str):
        try:
            entry.configure(border_color=ERROR_RED, border_width=2)
        except Exception:
            pass
        parent = entry.master
        info = entry.grid_info()
        row = int(info.get("row", 0))
        if entry in self._labels:
            _, lbl = self._labels[entry]
            lbl.configure(text=message)
            return
        lbl = ctk.CTkLabel(parent, text=message, text_color=ERROR_RED, justify="left",
                           font=ctk.CTkFont("Segoe UI", 10))
        lbl.grid(row=row, column=2, sticky="w", padx=(8, 0))
        self._labels[entry] = (parent, lbl)

    def clear(self, entry: ctk.CTkEntry):
        try:
            entry.configure(border_color=BORDER_DEFAULT, border_width=1)
        except Exception:
            pass
        pair = self._labels.pop(entry, None)
        if pair:
            _, lbl = pair
            try: lbl.destroy()
            except Exception: pass

    def any_error(self) -> bool:
        return bool(self._labels)

    def clear_all(self):
        for entry, (_, lbl) in list(self._labels.items()):
            try:
                entry.configure(border_color=BORDER_DEFAULT, border_width=1)
            except Exception:
                pass
            try:
                lbl.destroy()
            except Exception:
                pass
        self._labels.clear()


def open_win_home(parent: ctk.CTk):
    win = ctk.CTkToplevel(parent)
    win.title("Perfil de Usuario")
    try:
        win.state("zoomed")
    except Exception:
        win.geometry("1280x800")
    win.minsize(1280, 720)

    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale = min(sw/1920, sh/1080)
    pad   = max(24, int(36*scale))
    radius= max(8, int(10*scale))
    font_h1 = max(18, int(28*scale))
    font_lbl= max(10, int(12*scale))
    font_btn= max(10, int(14*scale))

    err = ErrorInline()

    # ---------- Helpers ----------
    def fmt_money(v: float) -> str:
        try:
            return f"{float(v):,.2f}"
        except Exception:
            return "0.00"

    def remember_valid(entry: ctk.CTkEntry):
        entry._last_valid_text = entry.get()

    def revert_to_last_valid(entry: ctk.CTkEntry):
        last = getattr(entry, "_last_valid_text", None)
        if last is not None:
            entry.delete(0, "end")
            entry.insert(0, last)

    def set_text(entry: ctk.CTkEntry, txt: str):
        entry.delete(0, "end")
        entry.insert(0, txt)
        remember_valid(entry)

    # Validadores
    def bind_money(entry: ctk.CTkEntry, *, min_val: float = 0.0, max_val: float | None = None,
                   required: bool = False, field_name: str = "Monto"):
        def _focusout(_):
            txt = entry.get().strip()
            if txt == "":
                if required:
                    err.show(entry, f"{field_name}: requerido")
                    return
                else:
                    err.clear(entry); remember_valid(entry); return
            val = parse_money_strict(txt)
            if val is None:
                err.show(entry, f"{field_name}: valor inválido")
                revert_to_last_valid(entry); return
            if val < min_val:
                err.show(entry, f"{field_name}: mínimo {min_val:,.2f}")
                revert_to_last_valid(entry); return
            if max_val is not None and val > max_val:
                err.show(entry, f"{field_name}: máximo {max_val:,.2f}")
                revert_to_last_valid(entry); return
            err.clear(entry)
            set_text(entry, fmt_money(val))
        entry.bind("<FocusOut>", _focusout)

    def bind_int(entry: ctk.CTkEntry, *, min_val: int = 0, max_val: int | None = None,
                 required: bool = False, field_name: str = "Valor"):
        def _focusout(_):
            txt = entry.get().strip()
            if txt == "":
                if required:
                    err.show(entry, f"{field_name}: requerido")
                    return
                else:
                    err.clear(entry); remember_valid(entry); return
            if not txt.isdigit():
                err.show(entry, f"{field_name}: solo números")
                revert_to_last_valid(entry); return
            val = to_int(txt, min_val)
            if val is None:
                err.show(entry, f"{field_name}: inválido")
                revert_to_last_valid(entry); return
            if val < min_val:
                err.show(entry, f"{field_name}: mínimo {min_val}")
                revert_to_last_valid(entry); return
            if max_val is not None and val > max_val:
                err.show(entry, f"{field_name}: máximo {max_val}")
                revert_to_last_valid(entry); return
            err.clear(entry)
            set_text(entry, str(val))
        entry.bind("<FocusOut>", _focusout)

    def bind_no_digits(entry: ctk.CTkEntry, *, required=False, field_name="Texto"):
        def _keyrelease(_):
            txt = entry.get()
            filtered = "".join(ch for ch in txt if not ch.isdigit())
            if filtered != txt:
                pos = entry.index("insert")
                set_text(entry, filtered)
                try:
                    entry.icursor(max(0, pos-1))
                except Exception:
                    pass
        def _focusout(_):
            txt = entry.get().strip()
            if required and txt == "":
                err.show(entry, f"{field_name}: requerido")
                return
            if any(ch.isdigit() for ch in txt):
                err.show(entry, f"{field_name}: sin números")
                return
            err.clear(entry); remember_valid(entry)
        entry.bind("<KeyRelease>", _keyrelease)
        entry.bind("<FocusOut>", _focusout)

    # ---------- Layout principal ----------
    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad, pady=pad)

    main = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    main.pack(fill="both", expand=True, padx=pad, pady=pad)
    main.grid_columnconfigure(0, weight=3)
    main.grid_columnconfigure(1, weight=2)
    main.grid_columnconfigure(2, weight=1)
    main.grid_rowconfigure(1, weight=1)

    # Header
    ctk.CTkLabel(main, text="Perfil de Usuario", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h1))\
        .grid(row=0, column=0, columnspan=2, sticky="w", padx=pad, pady=(pad, 8))
    ctk.CTkLabel(main, text="Completa tus datos para recibir recomendaciones personalizadas.",
                 text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=0, column=1, sticky="e", padx=pad)

    # === Botón Inicio (arriba derecha) ===
    def _save_for_nav() -> bool:
        """Valida, vuelca widgets a 'state' y guarda. Sin mensajes 'OK' para no duplicar diálogos."""
        if not _validate_all_inline():
            messagebox.showerror("Revisa tus campos", "Hay datos por corregir (marcados en rojo).")
            return False
        # Volcar widgets a state (idéntico a _save)
        state["usuario"]["nombre"] = ent_nombre.get().strip()
        state["usuario"]["edad"] = to_int(ent_edad.get(), 0)
        state["usuario"]["genero"] = cmb_genero.get()
        state["usuario"]["ubicacion"]["pais"] = cmb_pais.get()
        state["usuario"]["ubicacion"]["ciudad"] = ent_ciudad.get().strip()
        state["usuario"]["email"] = ent_email.get().strip()

        # Ingresos se mantienen (se editan en ventana Ingresos)

        state["situacion"]["ocupacion"] = cmb_ocup.get()
        state["situacion"]["dependientes"] = to_int(ent_dep.get(), 0) or 0
        state["situacion"]["vivienda"]["tipo"] = cmb_viv.get()
        state["situacion"]["vivienda"]["gasto_mensual"] = parse_money_strict(ent_gasto_viv.get()) or 0.0
        state["situacion"]["transporte"] = cmb_transp.get()
        state["situacion"]["mascotas"]["tiene"] = bool(mascotas_var.get())
        state["situacion"]["mascotas"]["tipo"] = ent_tipo_masc.get().strip()
        state["situacion"]["habitos"]["comer_fuera"] = to_int(ent_h_comer.get(), 0) or 0
        state["situacion"]["habitos"]["cafe_fuera"] = to_int(ent_h_cafe.get(), 0) or 0
        state["situacion"]["habitos"]["compras_online"] = to_int(ent_h_online.get(), 0) or 0
        state["situacion"]["gasto_fijo_mensual"] = parse_money_strict(ent_gasto_fijo.get()) or 0.0

        deuda_tipo = cmb_deuda_tipo.get()
        tiene_deuda = deuda_tipo != "No tengo"
        state["situacion"]["deudas"]["tiene"] = tiene_deuda
        state["situacion"]["deudas"]["tipos"] = [] if not tiene_deuda else ([deuda_tipo] if deuda_tipo != "Varias" else ["Varias"])
        state["situacion"]["deudas"]["pago_mensual_total"] = 0.0 if not tiene_deuda else (parse_money_strict(ent_deu_pago.get()) or 0.0)

        state["metas"]["principal"] = cmb_meta.get()
        state["metas"]["monto_objetivo"] = parse_money_strict(ent_meta_monto.get()) or 0.0
        state["metas"]["horizonte_meses"] = to_int(ent_meta_meses.get(), 1) or 1
        state["metas"]["aportacion_mensual"] = parse_money_strict(ent_meta_aport.get()) or 0.0
        state["metas"]["fondo_emergencia_meses"] = to_int(cmb_meta_emerg.get(), 3) or 3

        state["preferencias"]["recordatorios"]["activo"] = bool(rec_var.get())
        state["preferencias"]["recordatorios"]["frecuencia"] = cmb_rec_freq.get()
        state["preferencias"]["alertas_sobrepresupuesto"]["activo"] = bool(alert_var.get())
        state["preferencias"]["alertas_sobrepresupuesto"]["umbral_porcentaje"] = to_int(ent_umbral.get(), 15) or 15
        state["preferencias"]["consentimiento_datos_locales"] = True

        try:
            save_profile(state)
            _update_summary()  # recalcular tarjetas
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el perfil:\n{e}")
            return False

    def _go_home():
        """Guarda, cierra esta ventana y abre el menú principal como Toplevel del root oculto."""
        if not _save_for_nav():
            return
        try:
            from app.main import open_main_menu  # evita import circular al cargar el módulo
            root = win.master if isinstance(win.master, (ctk.CTk, tk.Tk)) else None
            if root is None:
                messagebox.showerror("Error", "No se encontró la ventana principal para volver a Inicio.")
                return
            # abrir menú
            open_main_menu(root)
            # cerrar esta
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No fue posible abrir Inicio:\n{e}")

    btn_inicio = ctk.CTkButton(
        main, text="⟵ Inicio",
        fg_color="white", hover_color="#F8FAFF",
        text_color=PRIMARY_BLUE, border_color=PRIMARY_BLUE, border_width=2,
        corner_radius=8, command=_go_home
    )
    btn_inicio.grid(row=0, column=2, sticky="e", padx=pad, pady=(pad, 8))

    # Tabs
    tabs = ctk.CTkTabview(
        main, corner_radius=radius,
        segmented_button_selected_color=PRIMARY_BLUE,
        segmented_button_selected_hover_color=PRIMARY_BLUE_DARK
    )
    tabs.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=pad, pady=pad)

    tab_gen   = tabs.add("Generales")
    tab_sit   = tabs.add("Situación & Estilo de vida")
    tab_deu   = tabs.add("Deudas & Fijos")
    tab_metas = tabs.add("Metas")
    tab_pref  = tabs.add("Preferencias")

    for tab in (tab_gen, tab_sit, tab_deu, tab_metas, tab_pref):
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_columnconfigure(2, weight=1)

    # Resumen lateral
    side = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=radius)
    side.grid(row=1, column=2, sticky="nsew", padx=pad, pady=pad)
    for r in range(10): side.grid_rowconfigure(r, weight=0)
    side.grid_rowconfigure(9, weight=1)

    ctk.CTkLabel(side, text="Resumen", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", max(16, int(20*scale))))\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 10))

    card_ing = ctk.CTkFrame(side, fg_color=BG, corner_radius=10)
    card_ing.grid(row=1, column=0, sticky="ew", padx=pad, pady=(0, 8))
    card_cap = ctk.CTkFrame(side, fg_color=BG, corner_radius=10)
    card_cap.grid(row=2, column=0, sticky="ew", padx=pad, pady=8)
    card_meta = ctk.CTkFrame(side, fg_color=BG, corner_radius=10)
    card_meta.grid(row=3, column=0, sticky="ew", padx=pad, pady=8)

    lbl_ing = ctk.CTkLabel(card_ing, text="", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_ing.pack(anchor="w", padx=12, pady=10)

    ctk.CTkLabel(card_cap, text="Capacidad de ahorro (sobre ingreso)",
                 text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl)).pack(anchor="w", padx=12, pady=(10, 4))
    pb_cap = ctk.CTkProgressBar(card_cap, height=14, corner_radius=8, progress_color=PRIMARY_BLUE)
    pb_cap.pack(fill="x", padx=12)
    lbl_cap = ctk.CTkLabel(card_cap, text="", text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_cap.pack(anchor="w", padx=12, pady=(4, 10))

    ctk.CTkLabel(card_meta, text="Aportación mensual vs. requerida para tu meta",
                 text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl)).pack(anchor="w", padx=12, pady=(10, 4))
    pb_meta = ctk.CTkProgressBar(card_meta, height=14, corner_radius=8, progress_color=PRIMARY_BLUE)
    pb_meta.pack(fill="x", padx=12)
    lbl_meta = ctk.CTkLabel(card_meta, text="", text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_meta.pack(anchor="w", padx=12, pady=(4, 10))

    # Estado
    state = load_profile()

    # ---------- TAB GENERALES ----------
    row = 0
    ctk.CTkLabel(tab_gen, text="Nombre*", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(pad, 4))
    ent_nombre = ctk.CTkEntry(tab_gen)
    ent_nombre.grid(row=row, column=1, sticky="ew", padx=pad, pady=(pad, 4))
    bind_no_digits(ent_nombre, required=True, field_name="Nombre")
    row += 1

    ctk.CTkLabel(tab_gen, text="Edad* (15–110)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_edad = ctk.CTkEntry(tab_gen, width=120)
    ent_edad.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_int(ent_edad, min_val=15, max_val=110, required=True, field_name="Edad")
    row += 1

    ctk.CTkLabel(tab_gen, text="Género", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    cmb_genero = ctk.CTkComboBox(tab_gen, values=["F", "M", "No especificar", "Otro"], state="readonly", width=200)
    cmb_genero.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_gen, text="País", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    cmb_pais = ctk.CTkComboBox(tab_gen, state="readonly", values=["México"], width=160)
    cmb_pais.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_gen, text="Ciudad", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_ciudad = ctk.CTkEntry(tab_gen)
    ent_ciudad.grid(row=row, column=1, sticky="ew", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_gen, text="Correo (opcional)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_email = ctk.CTkEntry(tab_gen)
    ent_email.grid(row=row, column=1, sticky="ew", padx=pad, pady=4)
    def _email_focusout(_):
        txt = ent_email.get().strip()
        if txt and not is_valid_email(txt):
            err.show(ent_email, "Correo no válido")
        else:
            err.clear(ent_email); remember_valid(ent_email)
    ent_email.bind("<FocusOut>", _email_focusout)
    row += 1

    # ---------- TAB SITUACIÓN ----------
    row = 0
    ctk.CTkLabel(tab_sit, text="Ocupación", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(pad, 4))
    cmb_ocup = ctk.CTkComboBox(tab_sit, state="readonly",
                               values=["Estudiante", "Empleado", "Freelance", "Emprendedor", "Desempleado"], width=220)
    cmb_ocup.grid(row=row, column=1, sticky="w", padx=pad, pady=(pad,4))
    row += 1

    ctk.CTkLabel(tab_sit, text="Dependientes (0–20)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_dep = ctk.CTkEntry(tab_sit, width=120)
    ent_dep.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_int(ent_dep, min_val=0, max_val=20, required=True, field_name="Dependientes")
    row += 1

    ctk.CTkLabel(tab_sit, text="Vivienda (tipo)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    cmb_viv = ctk.CTkComboBox(tab_sit, state="readonly",
                               values=["Renta", "Hipoteca", "Con familia", "Otro"], width=220)
    cmb_viv.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_sit, text="Gasto mensual vivienda (≥ 0)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_gasto_viv = ctk.CTkEntry(tab_sit, width=160)
    ent_gasto_viv.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_money(ent_gasto_viv, min_val=0.0, max_val=1_000_000, required=False, field_name="Gasto de vivienda")
    row += 1

    ctk.CTkLabel(tab_sit, text="Transporte principal", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    cmb_transp = ctk.CTkComboBox(tab_sit, state="readonly",
                                 values=["Público", "Auto", "Bici", "Caminar", "Ride-hailing"], width=220)
    cmb_transp.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_sit, text="¿Mascotas?", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    mascotas_var = tk.BooleanVar(value=False)
    chk_masc = ctk.CTkCheckBox(tab_sit, text="Sí", variable=mascotas_var)
    chk_masc.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_sit, text="Tipo de mascota", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_tipo_masc = ctk.CTkEntry(tab_sit, width=180)
    ent_tipo_masc.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_no_digits(ent_tipo_masc, required=False, field_name="Tipo de mascota")
    row += 1

    help_hab = "Escala: 0 = nunca · 5 = muy frecuente"
    ctk.CTkLabel(tab_sit, text="Comer fuera (0–5)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=2)
    ent_h_comer = ctk.CTkEntry(tab_sit, width=120)
    ent_h_comer.grid(row=row, column=1, sticky="w", padx=pad, pady=2)
    bind_int(ent_h_comer, min_val=0, max_val=5, required=True, field_name="Comer fuera")
    ctk.CTkLabel(tab_sit, text=help_hab, text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", 9)).grid(row=row, column=2, sticky="w")
    row += 1

    ctk.CTkLabel(tab_sit, text="Café/bebidas fuera (0–5)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=2)
    ent_h_cafe = ctk.CTkEntry(tab_sit, width=120)
    ent_h_cafe.grid(row=row, column=1, sticky="w", padx=pad, pady=2)
    bind_int(ent_h_cafe, min_val=0, max_val=5, required=True, field_name="Café/bebidas")
    row += 1

    ctk.CTkLabel(tab_sit, text="Compras online (0–5)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=2)
    ent_h_online = ctk.CTkEntry(tab_sit, width=120)
    ent_h_online.grid(row=row, column=1, sticky="w", padx=pad, pady=(2, pad))
    bind_int(ent_h_online, min_val=0, max_val=5, required=True, field_name="Compras online")

    # ---------- TAB DEUDAS & FIJOS ----------
    row = 0
    ctk.CTkLabel(tab_deu, text="¿Tienes deudas?", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(pad,4))
    cmb_deuda_tipo = ctk.CTkComboBox(
        tab_deu, state="readonly",
        values=["No tengo", "Tarjeta de crédito", "Crédito personal", "Hipoteca", "Automotriz", "Estudios", "Varias"],
        width=220
    )
    cmb_deuda_tipo.grid(row=row, column=1, sticky="w", padx=pad, pady=(pad,4))
    row += 1

    ctk.CTkLabel(tab_deu, text="Pago mensual total (≥ 0)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_deu_pago = ctk.CTkEntry(tab_deu, width=160)
    ent_deu_pago.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_money(ent_deu_pago, min_val=0.0, max_val=1_000_000, required=False, field_name="Pago mensual de deudas")
    row += 1

    ctk.CTkLabel(tab_deu, text="Gasto fijo mensual (≥ 0)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(4,pad))
    ent_gasto_fijo = ctk.CTkEntry(tab_deu, width=160)
    ent_gasto_fijo.grid(row=row, column=1, sticky="w", padx=pad, pady=(4,pad))
    bind_money(ent_gasto_fijo, min_val=0.0, max_val=5_000_000, required=False, field_name="Gasto fijo mensual")

    def _on_deuda_tipo_change(choice: str | None = None):
        val = (choice or cmb_deuda_tipo.get() or "").strip()
        if val == "No tengo":
            ent_deu_pago.configure(state="disabled")
            set_text(ent_deu_pago, "0.00")
            err.clear(ent_deu_pago)
        else:
            ent_deu_pago.configure(state="normal")
    cmb_deuda_tipo.configure(command=_on_deuda_tipo_change)

    # ---------- TAB METAS ----------
    row = 0
    ctk.CTkLabel(tab_metas, text="Meta principal", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(pad,4))
    cmb_meta = ctk.CTkComboBox(tab_metas, state="readonly",
                               values=["Ahorro de emergencia", "Viaje", "Pagar deudas", "Educación", "Inversión", "Otro"], width=240)
    cmb_meta.grid(row=row, column=1, sticky="w", padx=pad, pady=(pad,4))
    row += 1

    ctk.CTkLabel(tab_metas, text="Monto objetivo (> 0)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_monto = ctk.CTkEntry(tab_metas, width=160)
    ent_meta_monto.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_money(ent_meta_monto, min_val=0.01, max_val=100_000_000, required=True, field_name="Monto objetivo")
    row += 1

    ctk.CTkLabel(tab_metas, text="Horizonte (meses ≥ 1)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_meses = ctk.CTkEntry(tab_metas, width=140)
    ent_meta_meses.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_int(ent_meta_meses, min_val=1, max_val=600, required=True, field_name="Horizonte (meses)")
    row += 1

    ctk.CTkLabel(tab_metas, text="Aportación mensual (≥ 0)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_aport = ctk.CTkEntry(tab_metas, width=160)
    ent_meta_aport.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_money(ent_meta_aport, min_val=0.0, max_val=50_000_000, required=False, field_name="Aportación mensual")
    row += 1

    ctk.CTkLabel(tab_metas, text="Fondo emergencia (meses)", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=(4,pad))
    cmb_meta_emerg = ctk.CTkComboBox(tab_metas, state="readonly", values=["3", "6", "9", "12"], width=120)
    cmb_meta_emerg.grid(row=row, column=1, sticky="w", padx=pad, pady=(4,pad))

    # ---------- TAB PREFERENCIAS ----------
    row = 0
    rec_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(tab_pref, text="Recordatorios activos", variable=rec_var)\
        .grid(row=row, column=0, sticky="w", padx=pad, pady=(pad,4))
    row += 1

    ctk.CTkLabel(tab_pref, text="Frecuencia de recordatorio", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    cmb_rec_freq = ctk.CTkComboBox(tab_pref, state="readonly", values=["Semanal", "Mensual"], width=160)
    cmb_rec_freq.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    row += 1

    alert_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(tab_pref, text="Alertas por sobrepresupuesto", variable=alert_var)\
        .grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    row += 1

    ctk.CTkLabel(tab_pref, text="Umbral (%) 1–100", text_color=TEXT).grid(row=row, column=0, sticky="w", padx=pad, pady=4)
    ent_umbral = ctk.CTkEntry(tab_pref, width=120)
    ent_umbral.grid(row=row, column=1, sticky="w", padx=pad, pady=4)
    bind_int(ent_umbral, min_val=1, max_val=100, required=True, field_name="Umbral (%)")
    row += 1

    cons_var = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(tab_pref, text="Consiento uso de datos locales", variable=cons_var)\
        .grid(row=row, column=0, sticky="w", padx=pad, pady=(4,pad))

    # --------- Carga inicial ----------
    def _load_to_widgets():
        u = state["usuario"]
        ent_nombre.insert(0, u.get("nombre", ""))
        ent_edad.insert(0, str(u.get("edad", 18)))
        cmb_genero.set(u.get("genero", "No especificar"))
        cmb_pais.set(u.get("ubicacion", {}).get("pais", "México"))
        ent_ciudad.insert(0, u.get("ubicacion", {}).get("ciudad", ""))
        ent_email.insert(0, u.get("email", ""))

        # Ingresos: solo lectura para resumen (se editan en Ingresos)
        ing = state.get("ingresos", {})
        ingreso_fijo_ro = float(ing.get("fijo_mensual", 0.0) or 0.0)
        freq_ro         = ing.get("frecuencia", "Mensual")

        s = state["situacion"]
        cmb_ocup.set(s.get("ocupacion", "Estudiante"))
        ent_dep.insert(0, str(s.get("dependientes", 0)))
        cmb_viv.set(s.get("vivienda", {}).get("tipo", "Renta"))
        ent_gasto_viv.insert(0, f"{float(s.get('vivienda', {}).get('gasto_mensual', 0.0)):,.2f}")
        cmb_transp.set(s.get("transporte", "Público"))
        mascotas = s.get("mascotas", {})
        mascotas_var.set(bool(mascotas.get("tiene", False)))
        ent_tipo_masc.insert(0, mascotas.get("tipo", ""))

        hab = s.get("habitos", {})
        ent_h_comer.insert(0, str(hab.get("comer_fuera", 0)))
        ent_h_cafe.insert(0, str(hab.get("cafe_fuera", 0)))
        ent_h_online.insert(0, str(hab.get("compras_online", 0)))

        ent_gasto_fijo.insert(0, f"{float(s.get('gasto_fijo_mensual', 0.0)):,.2f}")
        deudas = s.get("deudas", {})
        deuda_tipo_inicial = "No tengo"
        if deudas.get("tiene", False):
            tipos = deudas.get("tipos", [])
            deuda_tipo_inicial = tipos[0] if tipos else "Varias"
        cmb_deuda_tipo.set(deuda_tipo_inicial)
        ent_deu_pago.insert(0, f"{float(deudas.get('pago_mensual_total', 0.0)):,.2f}")
        _on_deuda_tipo_change(deuda_tipo_inicial)

        m = state["metas"]
        cmb_meta.set(m.get("principal", "Ahorro de emergencia"))
        ent_meta_monto.insert(0, f"{float(m.get('monto_objetivo', 0.0)):,.2f}")
        ent_meta_meses.insert(0, str(m.get("horizonte_meses", 6)))
        ent_meta_aport.insert(0, f"{float(m.get('aportacion_mensual', 0.0)):,.2f}")
        cmb_meta_emerg.set(str(m.get("fondo_emergencia_meses", 3)))

        p = state["preferencias"]
        rec = p.get("recordatorios", {})
        rec_var.set(bool(rec.get("activo", False)))
        cmb_rec_freq.set(rec.get("frecuencia", "Semanal"))
        al = p.get("alertas_sobrepresupuesto", {})
        alert_var.set(bool(al.get("activo", False)))
        ent_umbral.insert(0, str(al.get("umbral_porcentaje", 15)))
        cons_var.set(bool(p.get("consentimiento_datos_locales", True)))

        for e in (ent_nombre, ent_edad, ent_ciudad, ent_email,
                  ent_dep, ent_gasto_viv,
                  ent_h_comer, ent_h_cafe, ent_h_online,
                  ent_deu_pago, ent_gasto_fijo,
                  ent_meta_monto, ent_meta_meses, ent_meta_aport, ent_umbral, ent_tipo_masc):
            remember_valid(e)

        _update_summary(ingreso_fijo_ro, freq_ro)

    # --------- Resumen ----------
    def _update_summary(ingreso_fijo_ro: float | None = None, freq_ro: str | None = None):
        if ingreso_fijo_ro is None or freq_ro is None:
            ing = state.get("ingresos", {})
            ingreso_fijo_ro = float(ing.get("fijo_mensual", 0.0) or 0.0)
            freq_ro         = ing.get("frecuencia", "Mensual")

        gasto_viv   = parse_money_strict(ent_gasto_viv.get()) or 0.0
        gasto_fijo  = parse_money_strict(ent_gasto_fijo.get()) or 0.0
        pago_deuda  = parse_money_strict(ent_deu_pago.get()) or 0.0
        if (cmb_deuda_tipo.get() or "") == "No tengo":
            pago_deuda = 0.0

        capacidad = max(0.0, ingreso_fijo_ro - (gasto_viv + gasto_fijo + pago_deuda))
        cap_pct = (capacidad / ingreso_fijo_ro) if ingreso_fijo_ro > 0 else 0.0
        cap_pct = max(0.0, min(1.0, cap_pct))

        lbl_ing.configure(
            text=f"Ingreso (solo lectura): ${ingreso_fijo_ro:,.2f}  ·  Frecuencia: {freq_ro}"
        )
        pb_cap.set(cap_pct)
        lbl_cap.configure(text=f"Capacidad estimada: ${capacidad:,.2f}  ({cap_pct*100:.1f}% del ingreso)")

        objetivo    = parse_money_strict(ent_meta_monto.get()) or 0.0
        meses       = max(1, to_int(ent_meta_meses.get(), 1) or 1)
        aportacion  = parse_money_strict(ent_meta_aport.get()) or 0.0
        req_mensual = (objetivo / meses) if meses > 0 else 0.0
        ratio_aport = (aportacion / req_mensual) if req_mensual > 0 else 0.0
        ratio_aport = max(0.0, min(1.0, ratio_aport))
        pb_meta.set(ratio_aport)
        if req_mensual > 0:
            lbl_meta.configure(text=f"Aportación: ${aportacion:,.2f} / Requerido: ${req_mensual:,.2f}  ({ratio_aport*100:.1f}%)")
        else:
            lbl_meta.configure(text="Define objetivo y horizonte para calcular el requerido mensual.")

    # --------- Guardar (botonera inferior) ----------
    def _validate_all_inline() -> bool:
        err.clear_all()
        for e in (ent_nombre, ent_edad, ent_email,
                  ent_dep, ent_gasto_viv,
                  ent_h_comer, ent_h_cafe, ent_h_online,
                  ent_deu_pago, ent_gasto_fijo,
                  ent_meta_monto, ent_meta_meses, ent_meta_aport,
                  ent_umbral, ent_tipo_masc):
            try: e.event_generate("<FocusOut>")
            except Exception: pass
        if (cmb_deuda_tipo.get() or "") == "No tengo":
            err.clear(ent_deu_pago)
            set_text(ent_deu_pago, "0.00")
        return not err.any_error()

    def _save():
        if not _validate_all_inline():
            messagebox.showerror("Revisa tus campos", "Algunos datos necesitan corrección (marcados en rojo).")
            return
        # misma lógica de _save_for_nav(), pero con mensaje de éxito
        if _save_for_nav():
            messagebox.showinfo("OK", "Perfil guardado correctamente.")

    btns = ctk.CTkFrame(main, fg_color=CARD_BG)
    btns.grid(row=2, column=0, columnspan=3, sticky="e", padx=pad, pady=(0, pad))
    ctk.CTkButton(btns, text="Guardar",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, command=_save)\
        .pack(side="right", padx=6)
    ctk.CTkButton(btns, text="Cerrar",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, command=win.destroy)\
        .pack(side="right", padx=6)

    # ---------- Inicializar ----------
    state = load_profile()
    _load_to_widgets()
