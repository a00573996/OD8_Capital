# win_form.py — ZAVE (Formulario adaptable con CustomTkinter, primario azul)
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Paleta coherente con main (Versión A, primario AZUL)
PRIMARY_BLUE       = "#2563EB"
PRIMARY_BLUE_DARK  = "#1D4ED8"
BG                 = "#F3F4F6"
CARD_BG            = "#FFFFFF"
TEXT               = "#111827"
TEXT_MUTED         = "#6B7280"
SEPARATOR          = "#E5E7EB"
DANGER             = "#DC3545"
DANGER_DARK        = "#B02A37"

def open_win_form(parent: ctk.CTk):
    # Ventana secundaria
    win = ctk.CTkToplevel(parent)
    win.title("Registro de usuario e ingresos")
    win.state("zoomed")  # abre maximizada
    win.minsize(1280, 720)

    # ---------- Escalado adaptable ----------
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    scale_w, scale_h = sw / 1920, sh / 1080
    scale = min(scale_w, scale_h)

    # Dimensiones escaladas
    radius    = max(8, int(10 * scale))
    font_h1   = max(18, int(28 * scale))
    font_h2   = max(14, int(18 * scale))
    font_lbl  = max(10, int(12 * scale))
    font_btn  = max(10, int(14 * scale))
    entry_h   = max(28, int(34 * scale))
    btn_h     = max(36, int(44 * scale))
    pad_x     = max(40, int(60 * scale))
    pad_y     = max(24, int(36 * scale))

    # ---------- Contenedores principales ----------
    outer = ctk.CTkFrame(win, fg_color=BG)
    outer.pack(fill="both", expand=True, padx=pad_x, pady=pad_y)

    card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=radius)
    card.pack(fill="both", expand=True, padx=pad_x, pady=pad_y)

    # ---------- Encabezado ----------
    ctk.CTkLabel(
        card, text="Registro de Usuario e Ingresos",
        text_color=TEXT,
        font=ctk.CTkFont("Segoe UI Semibold", font_h1)
    ).grid(row=0, column=0, columnspan=4, sticky="w", padx=pad_x, pady=(pad_y, int(8 * scale)))

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=1, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=(0, int(12 * scale)))

    # ---------- Datos del usuario ----------
    ctk.CTkLabel(card, text="Nombre:", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_nombre = ctk.CTkEntry(card, height=entry_h, width=360)
    ent_nombre.grid(row=2, column=1, sticky="w", pady=6)

    ctk.CTkLabel(card, text="Edad:", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=3, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_edad = ctk.CTkEntry(card, height=entry_h, width=120)
    ent_edad.grid(row=3, column=1, sticky="w", pady=6)

    ctk.CTkLabel(card, text="Correo electrónico (opcional):", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=4, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_email = ctk.CTkEntry(card, height=entry_h, width=420)
    ent_email.grid(row=4, column=1, columnspan=3, sticky="w", pady=6)

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=5, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=(int(12 * scale), int(12 * scale)))

    # ---------- Sección Ingresos ----------
    ctk.CTkLabel(
        card, text="Ingresos", text_color=TEXT,
        font=ctk.CTkFont("Segoe UI Semibold", font_h2)
    ).grid(row=6, column=0, sticky="w", padx=pad_x, pady=(0, int(8 * scale)))

    ctk.CTkLabel(card, text="Ingreso fijo mensual:", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=7, column=0, sticky="e", padx=(0, 8), pady=6)
    ent_ingreso_fijo = ctk.CTkEntry(card, height=entry_h, width=160)
    ent_ingreso_fijo.grid(row=7, column=1, sticky="w", pady=6)

    ctk.CTkLabel(card, text="Frecuencia del ingreso:", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=8, column=0, sticky="e", padx=(0, 8), pady=6)
    cmb_frecuencia = ctk.CTkOptionMenu(
        card, values=["Mensual", "Quincenal", "Semanal", "Diario"],
        fg_color=PRIMARY_BLUE, button_color=PRIMARY_BLUE_DARK,
        button_hover_color=PRIMARY_BLUE_DARK, text_color="white",
        font=ctk.CTkFont("Segoe UI", font_lbl)
    )
    cmb_frecuencia.set("Mensual")
    cmb_frecuencia.grid(row=8, column=1, sticky="w", pady=6)

    # ---------- Ingresos variables ----------
    ctk.CTkLabel(card, text="Ingresos variables", text_color=TEXT,
                 font=ctk.CTkFont("Segoe UI Semibold", font_lbl))\
        .grid(row=6, column=2, sticky="w", padx=pad_x, pady=(0, 6))

    ctk.CTkLabel(card, text="Concepto", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=7, column=2, sticky="w")
    ctk.CTkLabel(card, text="Monto", text_color=TEXT, font=ctk.CTkFont("Segoe UI", font_lbl))\
        .grid(row=7, column=3, sticky="w")

    var_concepto = ctk.CTkEntry(card, height=entry_h)
    var_concepto.grid(row=8, column=2, sticky="ew", padx=(0, 8), pady=(2, 8))
    var_monto = ctk.CTkEntry(card, height=entry_h, width=140)
    var_monto.grid(row=8, column=3, sticky="w", pady=(2, 8))

    cont_vars = []

    def es_numero_positivo(txt: str) -> bool:
        try:
            return float(txt) >= 0
        except ValueError:
            return False

    def actualizar_total():
        fijo_txt = ent_ingreso_fijo.get().strip()
        fijo = float(fijo_txt) if es_numero_positivo(fijo_txt) else 0.0
        total_vars = sum(item['monto'] for item in cont_vars)
        lbl_total_val.configure(text=f"${fijo + total_vars:,.2f}")

    def agregar_variable():
        concepto = var_concepto.get().strip()
        monto_txt = var_monto.get().strip()
        if not concepto:
            messagebox.showwarning("Aviso", "Escribe un concepto para el ingreso variable.")
            return
        if not es_numero_positivo(monto_txt):
            messagebox.showwarning("Aviso", "El monto debe ser un número ≥ 0.")
            return
        monto = float(monto_txt)
        cont_vars.append({"concepto": concepto, "monto": monto})
        lb_vars.insert("end", f"{concepto} — ${monto:,.2f}")
        var_concepto.delete(0, "end")
        var_monto.delete(0, "end")
        actualizar_total()

    def eliminar_seleccionado():
        sel = lb_vars.curselection()
        if not sel:
            return
        idx = sel[0]
        lb_vars.delete(idx)
        cont_vars.pop(idx)
        actualizar_total()

    def limpiar_variables():
        if lb_vars.size() == 0:
            return
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los ingresos variables?"):
            lb_vars.delete(0, "end")
            cont_vars.clear()
            actualizar_total()

    # Listbox nativo
    list_container = ctk.CTkFrame(card, fg_color=BG, corner_radius=radius)
    list_container.grid(row=9, column=2, columnspan=2, sticky="nsew", padx=pad_x, pady=(8, 0))
    inner = tk.Frame(list_container, bg=BG)
    inner.pack(fill="both", expand=True, padx=6, pady=6)
    lb_vars = tk.Listbox(inner, height=8, activestyle="dotbox")
    lb_vars.pack(side="left", fill="both", expand=True)
    sb = tk.Scrollbar(inner, orient="vertical", command=lb_vars.yview)
    sb.pack(side="right", fill="y")
    lb_vars.config(yscrollcommand=sb.set)

    # Botones de acciones
    actions = ctk.CTkFrame(card, fg_color=CARD_BG)
    actions.grid(row=10, column=2, columnspan=2, sticky="e", pady=(4, 6))
    for text, cmd, style in [
        ("Agregar", agregar_variable, ("filled", PRIMARY_BLUE, PRIMARY_BLUE_DARK)),
        ("Eliminar seleccionado", eliminar_seleccionado, ("outlined", PRIMARY_BLUE, PRIMARY_BLUE_DARK)),
        ("Limpiar", limpiar_variables, ("outlined", PRIMARY_BLUE, PRIMARY_BLUE_DARK)),
    ]:
        if style[0] == "filled":
            ctk.CTkButton(actions, text=text,
                          fg_color=style[1], hover_color=style[2],
                          text_color="white", corner_radius=radius,
                          font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
                          height=btn_h, command=cmd).pack(side="left", padx=6)
        else:
            ctk.CTkButton(actions, text=text,
                          fg_color="white", hover_color="#F8FAFF",
                          border_color=style[1], border_width=2,
                          text_color=style[1], corner_radius=radius,
                          font=ctk.CTkFont("Segoe UI", font_btn),
                          height=btn_h, command=cmd).pack(side="left", padx=6)

    # ---------- Total ----------
    total_frame = ctk.CTkFrame(card, fg_color=CARD_BG)
    total_frame.grid(row=11, column=0, columnspan=4, sticky="e", padx=pad_x, pady=(int(6 * scale), 0))
    ctk.CTkLabel(total_frame, text="Total estimado de ingresos:",
                 text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_lbl))\
        .pack(side="left", padx=(0, 6))
    lbl_total_val = ctk.CTkLabel(total_frame, text="$0.00",
                                 text_color=TEXT, font=ctk.CTkFont("Segoe UI Semibold", font_lbl))
    lbl_total_val.pack(side="left")

    ctk.CTkFrame(card, fg_color=SEPARATOR, height=2)\
        .grid(row=12, column=0, columnspan=4, sticky="ew", padx=pad_x, pady=int(12 * scale))

    # ---------- Guardar ----------
    def validar_y_guardar():
        nombre = ent_nombre.get().strip()
        edad_txt = ent_edad.get().strip()
        email = ent_email.get().strip()
        ingreso_fijo_txt = ent_ingreso_fijo.get().strip()
        frecuencia = cmb_frecuencia.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre es requerido.")
            return
        if not edad_txt.isdigit() or int(edad_txt) < 0:
            messagebox.showerror("Error", "La edad debe ser un número entero ≥ 0.")
            return
        if email and not EMAIL_RE.match(email):
            messagebox.showerror("Error", "El correo electrónico no es válido.")
            return
        if ingreso_fijo_txt and not es_numero_positivo(ingreso_fijo_txt):
            messagebox.showerror("Error", "El ingreso fijo mensual debe ser un número ≥ 0.")
            return

        ingreso_fijo = float(ingreso_fijo_txt) if ingreso_fijo_txt else 0.0
        data = {
            "usuario": {"nombre": nombre, "edad": int(edad_txt), "email": email or None},
            "ingresos": {
                "fijo_mensual": ingreso_fijo,
                "variables": cont_vars,
                "frecuencia": frecuencia
            },
            "totales": {"ingreso_total_estimado": ingreso_fijo + sum(v["monto"] for v in cont_vars)}
        }

        ruta = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Texto", "*.txt"), ("Todos", "*.*")],
            title="Guardar registro"
        )
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("OK", "Datos guardados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos:\n{e}")

    btns_final = ctk.CTkFrame(card, fg_color=CARD_BG)
    btns_final.grid(row=13, column=0, columnspan=4, sticky="e", padx=pad_x, pady=(0, pad_y))

    ctk.CTkButton(
        btns_final, text="Guardar",
        fg_color=PRIMARY_BLUE, hover_color=PRIMARY_BLUE_DARK,
        text_color="white", height=btn_h, corner_radius=radius,
        font=ctk.CTkFont("Segoe UI", font_btn, "bold"),
        command=validar_y_guardar
    ).pack(side="right", padx=6)

    ctk.CTkButton(
        btns_final, text="Cerrar",
        fg_color="white", hover_color="#F8FAFF",
        text_color=TEXT, border_color=SEPARATOR, border_width=2,
        height=btn_h, corner_radius=radius,
        font=ctk.CTkFont("Segoe UI", font_btn),
        command=win.destroy
    ).pack(side="right")
