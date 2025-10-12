# Navegación segura a Inicio (Main)
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

def go_home(win: tk.Toplevel, parent: ctk.CTk | tk.Tk, after_ids: list[str] | None = None):
    """
    Cancela timers .after() pendientes, destruye la ventana actual y el root oculto,
    y relanza app.main.main() desde cero para que el logo/imágenes se carguen bien.

    - win: CTkToplevel/Toplevel de la ventana actual.
    - parent: root (oculto) que recibió esta Toplevel.
    - after_ids: lista con ids devueltos por .after(...) a cancelar.
    """
    # 1) Cancelar timers
    if after_ids:
        for aid in list(after_ids):
            try:
                win.after_cancel(aid)
            except Exception:
                pass
        after_ids.clear()

    # 2) Cerrar UI actual
    try:
        win.destroy()
    except Exception:
        pass
    try:
        parent.destroy()
    except Exception:
        pass

    # 3) Relanzar Main
    try:
        from app.main import main as launch_main
        launch_main()
    except Exception as e:
        messagebox.showerror("Error", f"No fue posible abrir Inicio:\n{e}")
