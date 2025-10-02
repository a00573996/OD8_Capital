# app/win_canvas.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_BASE = "https://api.open-meteo.com/v1/forecast"

def fetch_data():
    """
    Ciudad de México:
      - hourly: relative_humidity_2m, wind_speed_10m
      - rango: últimas 24h (past_days=1)
    Devuelve: horas, humedad, viento
    """
    try:
        url = (
            f"{API_BASE}?latitude=19.43&longitude=-99.13"
            "&hourly=relative_humidity_2m,wind_speed_10m"
            "&past_days=1"
            "&timezone=auto"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        j = r.json()

        horas = j["hourly"]["time"]
        humedad = j["hourly"]["relative_humidity_2m"]
        viento = j["hourly"]["wind_speed_10m"]  # Por defecto: km/h

        return horas, humedad, viento
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener los datos:\n{e}")
        return [], [], []

def create_line_chart(horas, valores, titulo, ylabel):
    """
    Línea con ajustes:
      - marker='s'
      - linewidth=2.0
      - alpha=0.85
      - rejilla con '--' y alpha=.5
    """
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(horas, valores, linestyle="-", marker="s", markersize=3, linewidth=2.0, alpha=0.85)
    ax.grid(True, linestyle="--", alpha=.5)
    ax.set_title(titulo)
    ax.set_xlabel("Hora")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def create_bar_chart(horas, valores, titulo, ylabel):
    """Barras con rejilla y alpha .85."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(horas, valores, alpha=0.85)
    ax.grid(True, linestyle="--", alpha=.5)
    ax.set_title(titulo)
    ax.set_xlabel("Hora")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig

def _clear_plot_widgets(frm: tk.Widget):
    """Elimina canvases previos (si recargas varias veces)."""
    for child in frm.winfo_children():
        # No borres el botón
        if isinstance(child, ttk.Button):
            continue
        try:
            child.destroy()
        except Exception:
            pass

def mostrar_graficas(frm, horas, humedad, viento):
    """Inserta las dos gráficas en el frame (como en tu estructura original)."""
    # Gráfica 1: Humedad (línea)
    fig1 = create_line_chart(horas, humedad, "CDMX · Humedad relativa (24h)", "%")
    canvas1 = FigureCanvasTkAgg(fig1, master=frm)
    canvas1.draw()
    canvas1.get_tk_widget().pack(pady=10, fill="x")

    # Gráfica 2: Viento (barras)
    fig2 = create_bar_chart(horas, viento, "CDMX · Velocidad del viento (24h)", "km/h (10 m)")
    canvas2 = FigureCanvasTkAgg(fig2, master=frm)
    canvas2.draw()
    canvas2.get_tk_widget().pack(pady=10, fill="x")

def open_win_canvas(parent: tk.Tk):
    """
    Ventana secundaria con botón que carga y muestra las gráficas.
    Misma estructura que el ejemplo original (sin pestañas).
    """
    win = tk.Toplevel(parent)
    win.title("Canvas · CDMX 24h · Humedad y Viento")
    win.geometry("960x900")

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    def cargar():
        _clear_plot_widgets(frm)  # Limpia gráficos anteriores
        horas, humedad, viento = fetch_data()
        if horas and humedad and viento:
            mostrar_graficas(frm, horas, humedad, viento)

    ttk.Button(frm, text="Cargar y mostrar gráficas", command=cargar).pack(pady=10)

# Para pruebas independientes (opcional)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba win_canvas")
    ttk.Button(root, text="Abrir ventana Canvas", command=lambda: open_win_canvas(root)).pack(pady=20)
    root.mainloop()
