# app/win_home.py — ZAVE (Perfil de usuario: registro y vista, con validación y guardado JSON)
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from core.profile import load_profile, save_profile, is_valid_email, to_float, to_int

# Paleta (azul, consistente con el resto)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"

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

    # Contenedor
    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad, pady=pad)

    # Layout principal: columna izq (tabs) y derecha (resumen)
    main = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    main.pack(fill="both", expand=True, padx=pad, pady=pad)
    main.grid_columnconfigure(0, weight=3)
    main.grid_columnconfigure(1, weight=2)
    main.grid_rowconfigure(1, weight=1)

    # Header
    ctk.CTkLabel(main, text="Perfil de Usuario", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_h1))\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 8))
    ctk.CTkLabel(main, text="Personaliza tu experiencia: completa tus datos para recomendaciones y metas.",
                 text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=0, column=1, sticky="e", padx=pad)

    # Tabs
    tabs = ctk.CTkTabview(main, corner_radius=radius, segmented_button_selected_color=PRIMARY_BLUE,
                          segmented_button_selected_hover_color=PRIMARY_BLUE_DARK)
    tabs.grid(row=1, column=0, sticky="nsew", padx=pad, pady=pad)

    tab_gen   = tabs.add("Generales")
    tab_sit   = tabs.add("Situación & Estilo de vida")
    tab_deu   = tabs.add("Deudas & Fijos")
    tab_metas = tabs.add("Metas")
    tab_pref  = tabs.add("Preferencias")

    # Resumen lateral
    side = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=radius)
    side.grid(row=1, column=1, sticky="nsew", padx=pad, pady=pad)
    for r in range(6): side.grid_rowconfigure(r, weight=0)
    side.grid_rowconfigure(6, weight=1)

    ctk.CTkLabel(side, text="Resumen", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", max(16, int(20*scale))))\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 8))
    sep = ctk.CTkFrame(side, fg_color=SEPARATOR, height=2)
    sep.grid(row=1, column=0, sticky="ew", padx=pad, pady=(0, 12))

    lbl_resumen = ctk.CTkLabel(side, text="", text_color=TEXT, justify="left",
                               font=ctk.CTkFont("Segoe UI", font_lbl))
    lbl_resumen.grid(row=2, column=0, sticky="nw", padx=pad)

    # --------- Campos (bindings a dict "state") ----------
    state = load_profile()  # dict vivo

    # ========== TAB GENERALES ==========
    # Columnas
    for c in range(2): tab_gen.grid_columnconfigure(c, weight=1)

    # Nombre
    ctk.CTkLabel(tab_gen, text="Nombre*", text_color=TEXT).grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 4))
    ent_nombre = ctk.CTkEntry(tab_gen); ent_nombre.grid(row=0, column=1, sticky="ew", padx=pad, pady=(pad, 4))

    # Edad
    ctk.CTkLabel(tab_gen, text="Edad*", text_color=TEXT).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
    ent_edad = ctk.CTkEntry(tab_gen, width=120); ent_edad.grid(row=1, column=1, sticky="w", padx=pad, pady=4)

    # Género
    ctk.CTkLabel(tab_gen, text="Género", text_color=TEXT).grid(row=2, column=0, sticky="w", padx=pad, pady=4)
    cmb_genero = ctk.CTkComboBox(tab_gen, values=["F", "M", "No especificar", "Otro"], state="readonly", width=200)
    cmb_genero.grid(row=2, column=1, sticky="w", padx=pad, pady=4)

    # País/Ciudad
    ctk.CTkLabel(tab_gen, text="País", text_color=TEXT).grid(row=3, column=0, sticky="w", padx=pad, pady=4)
    ent_pais = ctk.CTkEntry(tab_gen, width=160); ent_pais.grid(row=3, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_gen, text="Ciudad", text_color=TEXT).grid(row=4, column=0, sticky="w", padx=pad, pady=4)
    ent_ciudad = ctk.CTkEntry(tab_gen); ent_ciudad.grid(row=4, column=1, sticky="ew", padx=pad, pady=4)

    # Email (opcional)
    ctk.CTkLabel(tab_gen, text="Correo (opcional)", text_color=TEXT).grid(row=5, column=0, sticky="w", padx=pad, pady=4)
    ent_email = ctk.CTkEntry(tab_gen); ent_email.grid(row=5, column=1, sticky="ew", padx=pad, pady=4)

    # Ingresos
    ctk.CTkLabel(tab_gen, text="Frecuencia ingreso", text_color=TEXT).grid(row=6, column=0, sticky="w", padx=pad, pady=4)
    cmb_freq = ctk.CTkComboBox(tab_gen, state="readonly", values=["Mensual", "Quincenal", "Semanal", "Diario"], width=200)
    cmb_freq.grid(row=6, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_gen, text="Ingreso fijo mensual", text_color=TEXT).grid(row=7, column=0, sticky="w", padx=pad, pady=4)
    ent_ingreso_fijo = ctk.CTkEntry(tab_gen, width=160); ent_ingreso_fijo.grid(row=7, column=1, sticky="w", padx=pad, pady=(4, pad))

    # ========== TAB SITUACIÓN & ESTILO ==========
    for c in range(2): tab_sit.grid_columnconfigure(c, weight=1)

    ctk.CTkLabel(tab_sit, text="Ocupación", text_color=TEXT).grid(row=0, column=0, sticky="w", padx=pad, pady=(pad, 4))
    cmb_ocup = ctk.CTkComboBox(tab_sit, state="readonly",
                               values=["Estudiante", "Empleado", "Freelance", "Emprendedor", "Desempleado"], width=220)
    cmb_ocup.grid(row=0, column=1, sticky="w", padx=pad, pady=(pad,4))

    ctk.CTkLabel(tab_sit, text="Dependientes", text_color=TEXT).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
    ent_dep = ctk.CTkEntry(tab_sit, width=120); ent_dep.grid(row=1, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Vivienda (tipo)", text_color=TEXT).grid(row=2, column=0, sticky="w", padx=pad, pady=4)
    cmb_viv = ctk.CTkComboBox(tab_sit, state="readonly",
                               values=["Renta", "Hipoteca", "Con familia", "Otro"], width=220)
    cmb_viv.grid(row=2, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Gasto mensual vivienda", text_color=TEXT).grid(row=3, column=0, sticky="w", padx=pad, pady=4)
    ent_gasto_viv = ctk.CTkEntry(tab_sit, width=160); ent_gasto_viv.grid(row=3, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Transporte principal", text_color=TEXT).grid(row=4, column=0, sticky="w", padx=pad, pady=4)
    cmb_transp = ctk.CTkComboBox(tab_sit, state="readonly",
                                 values=["Público", "Auto", "Bici", "Caminar", "Ride-hailing"], width=220)
    cmb_transp.grid(row=4, column=1, sticky="w", padx=pad, pady=4)

    # Mascotas
    ctk.CTkLabel(tab_sit, text="¿Mascotas?", text_color=TEXT).grid(row=5, column=0, sticky="w", padx=pad, pady=4)
    mascotas_var = tk.BooleanVar(value=False)
    chk_masc = ctk.CTkCheckBox(tab_sit, text="Sí", variable=mascotas_var); chk_masc.grid(row=5, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Tipo de mascota", text_color=TEXT).grid(row=6, column=0, sticky="w", padx=pad, pady=4)
    ent_tipo_masc = ctk.CTkEntry(tab_sit, width=160); ent_tipo_masc.grid(row=6, column=1, sticky="w", padx=pad, pady=4)

    # Hábitos (0–5)
    ctk.CTkLabel(tab_sit, text="Comer fuera (0–5)", text_color=TEXT).grid(row=7, column=0, sticky="w", padx=pad, pady=4)
    ent_h_comer = ctk.CTkEntry(tab_sit, width=120); ent_h_comer.grid(row=7, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Café/bebidas fuera (0–5)", text_color=TEXT).grid(row=8, column=0, sticky="w", padx=pad, pady=4)
    ent_h_cafe = ctk.CTkEntry(tab_sit, width=120); ent_h_cafe.grid(row=8, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_sit, text="Compras online (0–5)", text_color=TEXT).grid(row=9, column=0, sticky="w", padx=pad, pady=(4,pad))
    ent_h_online = ctk.CTkEntry(tab_sit, width=120); ent_h_online.grid(row=9, column=1, sticky="w", padx=pad, pady=(4,pad))

    # ========== TAB DEUDAS & FIJOS ==========
    for c in range(2): tab_deu.grid_columnconfigure(c, weight=1)

    deudas_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(tab_deu, text="¿Tienes deudas?", variable=deudas_var).grid(row=0, column=0, sticky="w", padx=pad, pady=(pad,4))

    ctk.CTkLabel(tab_deu, text="Tipos (texto)", text_color=TEXT).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
    ent_deu_tipos = ctk.CTkEntry(tab_deu); ent_deu_tipos.grid(row=1, column=1, sticky="ew", padx=pad, pady=4)

    ctk.CTkLabel(tab_deu, text="Pago mensual total", text_color=TEXT).grid(row=2, column=0, sticky="w", padx=pad, pady=4)
    ent_deu_pago = ctk.CTkEntry(tab_deu, width=160); ent_deu_pago.grid(row=2, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_deu, text="Gasto fijo mensual (estimado)", text_color=TEXT).grid(row=3, column=0, sticky="w", padx=pad, pady=(4,pad))
    ent_gasto_fijo = ctk.CTkEntry(tab_deu, width=160); ent_gasto_fijo.grid(row=3, column=1, sticky="w", padx=pad, pady=(4,pad))

    # ========== TAB METAS ==========
    for c in range(2): tab_metas.grid_columnconfigure(c, weight=1)

    ctk.CTkLabel(tab_metas, text="Meta principal", text_color=TEXT).grid(row=0, column=0, sticky="w", padx=pad, pady=(pad,4))
    cmb_meta = ctk.CTkComboBox(tab_metas, state="readonly",
                               values=["Ahorro de emergencia", "Viaje", "Pagar deudas", "Educación", "Inversión", "Otro"], width=240)
    cmb_meta.grid(row=0, column=1, sticky="w", padx=pad, pady=(pad,4))

    ctk.CTkLabel(tab_metas, text="Monto objetivo", text_color=TEXT).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_monto = ctk.CTkEntry(tab_metas, width=160); ent_meta_monto.grid(row=1, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_metas, text="Horizonte (meses)", text_color=TEXT).grid(row=2, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_meses = ctk.CTkEntry(tab_metas, width=140); ent_meta_meses.grid(row=2, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_metas, text="Aportación mensual", text_color=TEXT).grid(row=3, column=0, sticky="w", padx=pad, pady=4)
    ent_meta_aport = ctk.CTkEntry(tab_metas, width=160); ent_meta_aport.grid(row=3, column=1, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_metas, text="Fondo emergencia (meses)", text_color=TEXT).grid(row=4, column=0, sticky="w", padx=pad, pady=(4,pad))
    cmb_meta_emerg = ctk.CTkComboBox(tab_metas, state="readonly", values=["3", "6", "9", "12"], width=120)
    cmb_meta_emerg.grid(row=4, column=1, sticky="w", padx=pad, pady=(4,pad))

    # ========== TAB PREFERENCIAS ==========
    for c in range(2): tab_pref.grid_columnconfigure(c, weight=1)

    rec_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(tab_pref, text="Recordatorios activos", variable=rec_var)\
        .grid(row=0, column=0, sticky="w", padx=pad, pady=(pad,4))
    ctk.CTkLabel(tab_pref, text="Frecuencia de recordatorio", text_color=TEXT).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
    cmb_rec_freq = ctk.CTkComboBox(tab_pref, state="readonly", values=["Semanal", "Mensual"], width=160)
    cmb_rec_freq.grid(row=1, column=1, sticky="w", padx=pad, pady=4)

    alert_var = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(tab_pref, text="Alertas por sobrepresupuesto", variable=alert_var)\
        .grid(row=2, column=0, sticky="w", padx=pad, pady=4)

    ctk.CTkLabel(tab_pref, text="Umbral (%)", text_color=TEXT).grid(row=3, column=0, sticky="w", padx=pad, pady=4)
    ent_umbral = ctk.CTkEntry(tab_pref, width=120); ent_umbral.grid(row=3, column=1, sticky="w", padx=pad, pady=4)

    cons_var = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(tab_pref, text="Consiento uso de datos locales", variable=cons_var)\
        .grid(row=4, column=0, sticky="w", padx=pad, pady=(4,pad))

    # --------- Carga inicial de valores en widgets ---------
    def _load_to_widgets():
        u = state["usuario"]
        ent_nombre.insert(0, u.get("nombre", ""))
        ent_edad.insert(0, str(u.get("edad", 18)))
        cmb_genero.set(u.get("genero", "No especificar"))
        ent_pais.insert(0, u.get("ubicacion", {}).get("pais", "MX"))
        ent_ciudad.insert(0, u.get("ubicacion", {}).get("ciudad", ""))
        ent_email.insert(0, u.get("email", ""))

        ing = state["ingresos"]
        cmb_freq.set(ing.get("frecuencia", "Mensual"))
        ent_ingreso_fijo.insert(0, f'{float(ing.get("fijo_mensual", 0.0)):.2f}')

        s = state["situacion"]
        cmb_ocup.set(s.get("ocupacion", "Estudiante"))
        ent_dep.insert(0, str(s.get("dependientes", 0)))
        cmb_viv.set(s.get("vivienda", {}).get("tipo", "Renta"))
        ent_gasto_viv.insert(0, f'{float(s.get("vivienda", {}).get("gasto_mensual", 0.0)):.2f}')
        cmb_transp.set(s.get("transporte", "Público"))
        mascotas = s.get("mascotas", {})
        mascotas_var.set(bool(mascotas.get("tiene", False)))
        ent_tipo_masc.insert(0, mascotas.get("tipo", ""))

        hab = s.get("habitos", {})
        ent_h_comer.insert(0, str(hab.get("comer_fuera", 0)))
        ent_h_cafe.insert(0, str(hab.get("cafe_fuera", 0)))
        ent_h_online.insert(0, str(hab.get("compras_online", 0)))

        ent_gasto_fijo.insert(0, f'{float(s.get("gasto_fijo_mensual", 0.0)):.2f}')
        deudas = s.get("deudas", {})
        deudas_var.set(bool(deudas.get("tiene", False)))
        ent_deu_tipos.insert(0, ", ".join(deudas.get("tipos", [])))
        ent_deu_pago.insert(0, f'{float(deudas.get("pago_mensual_total", 0.0)):.2f}')

        m = state["metas"]
        cmb_meta.set(m.get("principal", "Ahorro de emergencia"))
        ent_meta_monto.insert(0, f'{float(m.get("monto_objetivo", 0.0)):.2f}')
        ent_meta_meses.insert(0, str(m.get("horizonte_meses", 6)))
        ent_meta_aport.insert(0, f'{float(m.get("aportacion_mensual", 0.0)):.2f}')
        cmb_meta_emerg.set(str(m.get("fondo_emergencia_meses", 3)))

        p = state["preferencias"]
        rec = p.get("recordatorios", {})
        rec_var.set(bool(rec.get("activo", False)))
        cmb_rec_freq.set(rec.get("frecuencia", "Semanal"))
        al = p.get("alertas_sobrepresupuesto", {})
        alert_var.set(bool(al.get("activo", False)))
        ent_umbral.insert(0, str(al.get("umbral_porcentaje", 15)))
        cons_var.set(bool(p.get("consentimiento_datos_locales", True)))

    def _update_summary():
        ingreso = to_float(ent_ingreso_fijo.get())
        gasto_viv = to_float(ent_gasto_viv.get())
        gasto_fijo = to_float(ent_gasto_fijo.get())
        pago_deuda = to_float(ent_deu_pago.get()) if deudas_var.get() else 0.0

        capacidad = max(0.0, ingreso - (gasto_viv + gasto_fijo + pago_deuda))
        meta_monto = to_float(ent_meta_monto.get())
        meta_aport = to_float(ent_meta_aport.get())
        meta_meses = max(1, to_int(ent_meta_meses.get(), 1))
        # progreso estimado
        avance_pct = 0.0
        if meta_monto > 0 and meta_aport > 0:
            meses_necesarios = meta_monto / meta_aport
            avance_pct = min(100.0, (meta_aport * min(meta_meses, meses_necesarios)) / meta_monto * 100.0)

        txt = (
            f"Ingreso fijo mensual: ${ingreso:,.2f}\n"
            f"Gasto vivienda: ${gasto_viv:,.2f}   |   "
            f"Gasto fijo: ${gasto_fijo:,.2f}   |   "
            f"Pago deudas: ${pago_deuda:,.2f}\n"
            f"Capacidad de ahorro estimada: ${capacidad:,.2f}\n\n"
            f"Meta: {cmb_meta.get()}  |  Objetivo: ${meta_monto:,.2f}\n"
            f"Horizonte: {meta_meses} meses  |  Aportación: ${meta_aport:,.2f}\n"
            f"Progreso estimado (teórico): {avance_pct:.1f}%"
        )
        lbl_resumen.configure(text=txt)

    def _validate_and_save():
        # Validaciones mínimas
        nombre = ent_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        edad = to_int(ent_edad.get(), 0)
        if edad < 15:
            messagebox.showerror("Error", "La edad debe ser un entero ≥ 15.")
            return
        email = ent_email.get().strip()
        if not is_valid_email(email):
            messagebox.showerror("Error", "Correo no válido.")
            return
        if deudas_var.get() and to_float(ent_deu_pago.get()) < 0:
            messagebox.showerror("Error", "El pago mensual de deudas debe ser ≥ 0.")
            return

        # Guardar en state
        state["usuario"]["nombre"] = nombre
        state["usuario"]["edad"] = edad
        state["usuario"]["genero"] = cmb_genero.get()
        state["usuario"]["ubicacion"]["pais"] = ent_pais.get().strip() or "MX"
        state["usuario"]["ubicacion"]["ciudad"] = ent_ciudad.get().strip()
        state["usuario"]["email"] = email

        state["ingresos"]["frecuencia"] = cmb_freq.get()
        state["ingresos"]["fijo_mensual"] = to_float(ent_ingreso_fijo.get())

        state["situacion"]["ocupacion"] = cmb_ocup.get()
        state["situacion"]["dependientes"] = to_int(ent_dep.get(), 0)
        state["situacion"]["vivienda"]["tipo"] = cmb_viv.get()
        state["situacion"]["vivienda"]["gasto_mensual"] = to_float(ent_gasto_viv.get())
        state["situacion"]["transporte"] = cmb_transp.get()
        state["situacion"]["mascotas"]["tiene"] = bool(mascotas_var.get())
        state["situacion"]["mascotas"]["tipo"] = ent_tipo_masc.get().strip()
        state["situacion"]["habitos"]["comer_fuera"] = to_int(ent_h_comer.get(), 0)
        state["situacion"]["habitos"]["cafe_fuera"] = to_int(ent_h_cafe.get(), 0)
        state["situacion"]["habitos"]["compras_online"] = to_int(ent_h_online.get(), 0)
        state["situacion"]["gasto_fijo_mensual"] = to_float(ent_gasto_fijo.get())
        state["situacion"]["deudas"]["tiene"] = bool(deudas_var.get())
        tipos_txt = ent_deu_tipos.get().strip()
        state["situacion"]["deudas"]["tipos"] = [t.strip() for t in tipos_txt.split(",") if t.strip()] if tipos_txt else []
        state["situacion"]["deudas"]["pago_mensual_total"] = to_float(ent_deu_pago.get())

        state["metas"]["principal"] = cmb_meta.get()
        state["metas"]["monto_objetivo"] = to_float(ent_meta_monto.get())
        state["metas"]["horizonte_meses"] = max(1, to_int(ent_meta_meses.get(), 1))
        state["metas"]["aportacion_mensual"] = to_float(ent_meta_aport.get())
        state["metas"]["fondo_emergencia_meses"] = to_int(cmb_meta_emerg.get(), 3)

        state["preferencias"]["recordatorios"]["activo"] = bool(rec_var.get())
        state["preferencias"]["recordatorios"]["frecuencia"] = cmb_rec_freq.get()
        state["preferencias"]["alertas_sobrepresupuesto"]["activo"] = bool(alert_var.get())
        state["preferencias"]["alertas_sobrepresupuesto"]["umbral_porcentaje"] = to_int(ent_umbral.get(), 15)
        state["preferencias"]["consentimiento_datos_locales"] = bool(cons_var.get())

        try:
            save_profile(state)
            _update_summary()
            messagebox.showinfo("OK", "Perfil guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el perfil:\n{e}")

    # Botones inferiores
    btns = ctk.CTkFrame(main, fg_color=CARD_BG)
    btns.grid(row=2, column=0, columnspan=2, sticky="e", padx=pad, pady=(0, pad))
    ctk.CTkButton(btns, text="Guardar",
                  fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK, text_color="white",
                  corner_radius=8, command=_validate_and_save)\
        .pack(side="right", padx=6)
    ctk.CTkButton(btns, text="Cerrar",
                  fg_color="white", hover_color="#F8FAFF",
                  text_color=TEXT, border_color=SEPARATOR, border_width=2,
                  corner_radius=8, command=win.destroy)\
        .pack(side="right", padx=6)

    # Inicializar UI
    _load_to_widgets()
    _update_summary()
