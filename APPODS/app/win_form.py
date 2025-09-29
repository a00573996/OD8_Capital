import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def open_win_form(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Registro de usuario e ingresos")
    win.geometry("1920x1080")

    frm = ttk.Frame(win, padding=24)
    frm.pack(fill="both", expand=True)
    for i in range(4):
        frm.columnconfigure(i, weight=1)

    # -------------------- Encabezado --------------------
    ttk.Label(
        frm, text="Registro de Usuario e Ingresos",
        font=("Segoe UI", 18, "bold")
    ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

    # -------------------- Datos del usuario --------------------
    ttk.Label(frm, text="Nombre:").grid(row=1, column=0, sticky="e", padx=(0, 8))
    ent_nombre = ttk.Entry(frm, width=40)
    ent_nombre.grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Edad:").grid(row=2, column=0, sticky="e", padx=(0, 8))
    ent_edad = ttk.Entry(frm, width=12)
    ent_edad.grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Correo electrónico (opcional):").grid(row=3, column=0, sticky="e", padx=(0, 8))
    ent_email = ttk.Entry(frm, width=40)
    ent_email.grid(row=3, column=1, sticky="w", pady=4, columnspan=3)

    ttk.Separator(frm).grid(row=4, column=0, columnspan=4, sticky="ew", pady=12)

    # -------------------- Sección Ingresos --------------------
    ttk.Label(
        frm, text="Ingresos", font=("Segoe UI", 14, "bold")
    ).grid(row=5, column=0, sticky="w", pady=(0, 8), columnspan=2)

    # Ingreso fijo mensual
    ttk.Label(frm, text="Ingreso fijo mensual:").grid(row=6, column=0, sticky="e", padx=(0, 8))
    ent_ingreso_fijo = ttk.Entry(frm, width=20)
    ent_ingreso_fijo.grid(row=6, column=1, sticky="w", pady=4)

    # Frecuencia del ingreso
    ttk.Label(frm, text="Frecuencia del ingreso:").grid(row=7, column=0, sticky="e", padx=(0, 8))
    cmb_frecuencia = ttk.Combobox(
        frm, state="readonly",
        values=["Mensual", "Quincenal", "Semanal", "Diario"], width=18
    )
    cmb_frecuencia.current(0)
    cmb_frecuencia.grid(row=7, column=1, sticky="w", pady=4)

    # -------------------- Ingresos variables --------------------
    ttk.Label(frm, text="Ingresos variables").grid(row=5, column=2, sticky="w")
    var_concepto = ttk.Entry(frm, width=28)
    var_concepto.grid(row=7, column=2, sticky="w", pady=2)
    var_monto = ttk.Entry(frm, width=16)
    var_monto.grid(row=7, column=3, sticky="w", padx=(8, 0), pady=2)

    ttk.Label(frm, text="Concepto").grid(row=6, column=2, sticky="e", padx=(0, 0))
    ttk.Label(frm, text="Monto").grid(row=6, column=3, sticky="w", padx=(8, 0))

    cont_vars = []  # [{'concepto': str, 'monto': float}, ...]

    def es_numero_positivo(txt: str) -> bool:
        try:
            return float(txt) >= 0
        except ValueError:
            return False

    def actualizar_total():
        fijo = float(ent_ingreso_fijo.get()) if es_numero_positivo(ent_ingreso_fijo.get().strip()) else 0.0
        total_vars = sum(item['monto'] for item in cont_vars)
        lbl_total_val.config(text=f"${fijo + total_vars:,.2f}")

    def agregar_variable():
        concepto = var_concepto.get().strip()
        monto_txt = var_monto.get().strip()
        if not concepto:
            messagebox.showwarning("Aviso", "Escribe un concepto para el ingreso variable.")
            return
        if not es_numero_positivo(monto_txt):
            messagebox.showwarning("Aviso", "El monto del ingreso variable debe ser un número ≥ 0.")
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

    btn_agregar = ttk.Button(frm, text="Agregar", command=agregar_variable)
    btn_agregar.grid(row=7, column=3, sticky="e", padx=(120, 0))  # botón al extremo derecho

    # Listbox + scrollbar
    list_frame = ttk.Frame(frm)
    list_frame.grid(row=8, column=2, columnspan=2, sticky="nsew", pady=(8, 0))
    frm.rowconfigure(8, weight=1)  # la lista crece
    for c in range(2, 4):
        frm.columnconfigure(c, weight=1)

    lb_vars = tk.Listbox(list_frame, height=10)
    lb_vars.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb_vars.yview)
    sb.pack(side="right", fill="y")
    lb_vars.config(yscrollcommand=sb.set)

    # Botones bajo la lista
    btns_vars = ttk.Frame(frm)
    btns_vars.grid(row=9, column=2, columnspan=2, sticky="e", pady=6)
    ttk.Button(btns_vars, text="Eliminar seleccionado", command=eliminar_seleccionado).pack(side="left", padx=4)
    ttk.Button(btns_vars, text="Limpiar", command=limpiar_variables).pack(side="left", padx=4)

    # Total
    total_frame = ttk.Frame(frm)
    total_frame.grid(row=10, column=0, columnspan=4, sticky="e", pady=(6, 0))
    ttk.Label(total_frame, text="Total estimado de ingresos: ", font=("Segoe UI", 11, "bold")).pack(side="left")
    lbl_total_val = ttk.Label(total_frame, text="$0.00", font=("Segoe UI", 11, "bold"))
    lbl_total_val.pack(side="left")

    ttk.Separator(frm).grid(row=11, column=0, columnspan=4, sticky="ew", pady=12)

    # -------------------- Guardar --------------------
    def validar_y_guardar():
        nombre = ent_nombre.get().strip()
        edad_txt = ent_edad.get().strip()
        email = ent_email.get().strip()
        ingreso_fijo_txt = ent_ingreso_fijo.get().strip()
        frecuencia = cmb_frecuencia.get()

        # Validaciones
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
            "usuario": {
                "nombre": nombre,
                "edad": int(edad_txt),
                "email": email or None
            },
            "ingresos": {
                "fijo_mensual": ingreso_fijo,
                "variables": cont_vars,
                "frecuencia": frecuencia
            },
            "totales": {
                "ingreso_total_estimado": ingreso_fijo + sum(v["monto"] for v in cont_vars)
            }
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

    btns_final = ttk.Frame(frm)
    btns_final.grid(row=12, column=0, columnspan=4, pady=12, sticky="e")
    ttk.Button(btns_final, text="Guardar", command=validar_y_guardar).pack(side="right", padx=6)
    ttk.Button(btns_final, text="Cerrar", command=win.destroy).pack(side="right")
