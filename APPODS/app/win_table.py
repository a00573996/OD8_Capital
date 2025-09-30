import tkinter as tk
from tkinter import ttk, messagebox

def open_win_table(parent: tk.Tk):
    win = tk.Toplevel(parent)
    win.title("Win Table")
    win.geometry("1920x1080")

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    columns = ("categoria", "subcategoria", "monto", "fecha", "dinero_total")
    tree = ttk.Treeview(frm, columns=columns, show="headings", height=15)

    tree.heading("categoria", text="Categoría")
    tree.heading("subcategoria", text="Subcategoría")
    tree.heading("monto", text="Monto")
    tree.heading("fecha", text="Fecha")
    tree.heading("dinero_total", text="Dinero Total")

    tree.column("categoria", width=250, anchor="center")
    tree.column("subcategoria", width=250, anchor="center")
    tree.column("monto", width=200, anchor="center")
    tree.column("fecha", width=200, anchor="center")
    tree.column("dinero_total", width=250, anchor="center")

    tree.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 20))

    ent_item = ttk.Entry(frm)
    ent_item.grid(row=1, column=0, sticky="ew", padx=(0, 8))

    def agregar():
        v = ent_item.get().strip()
        if v:
            tree.insert("", "end", values=(v, "", "", "", ""))
            ent_item.delete(0, "end")
        else:
            messagebox.showwarning("Aviso", "Escribe un texto para agregar.")

    def eliminar():
        sel = tree.selection()
        if sel:
            tree.delete(sel[0])

    def limpiar():
        for row in tree.get_children():
            tree.delete(row)

    ttk.Button(frm, text="Agregar", command=agregar).grid(row=1, column=1, sticky="ew", pady=4)
    ttk.Button(frm, text="Eliminar seleccionado", command=eliminar).grid(row=2, column=1, sticky="ew", pady=4)
    ttk.Button(frm, text="Limpiar", command=limpiar).grid(row=3, column=1, sticky="ew", pady=4)
    ttk.Button(frm, text="Cerrar", command=win.destroy).grid(row=4, column=0, columnspan=2, pady=20, sticky="e")

    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=0)
    frm.rowconfigure(0, weight=1)
