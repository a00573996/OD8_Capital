import tkinter as tk
from tkinter import ttk, messagebox
import csv
from pathlib import Path

def open_win_table(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Tabla (Treeview)")
    win.geometry("480x300")

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    # Definir columnas
    cols = ("nombre", "valor1", "valor2")
    tv = ttk.Treeview(frm, columns=cols, show="headings", height=10)
    for c in cols:
        tv.heading(c, text=c.capitalize())
        tv.column(c, width=120, anchor="center")
    tv.pack(fill="both", expand=True)

    # Ruta al archivo CSV (sube 1 nivel desde /app a la raíz y entra en /data/)
    ruta = Path(__file__).resolve().parents[1] / "data" / "sample.csv"

    if not ruta.exists():
        messagebox.showwarning("Aviso", f"No se encontró {ruta}. Crea el archivo de ejemplo.")
        return

    # Leer archivo CSV y cargar datos en la tabla
    with open(ruta, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tv.insert("", "end", values=(row["nombre"], row["valor1"], row["valor2"]))

    # Botón para cerrar ventana
    ttk.Button(frm, text="Cerrar", command=win.destroy).pack(pady=8, anchor="e")
