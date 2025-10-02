import tkinter as tk
from tkinter import ttk, messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def fetch_data():
    """
    Conecta con la API de Open-Meteo y obtiene humedad relativa horaria
    de Zacatecas (últimas 24 horas).
    Devuelve dos listas: horas y humedad relativa.
    """
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=22.77&longitude=-102.57"
            "&hourly=relativehumidity_2m&past_days=1"
            "&timezone=auto"
        )
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        horas = data["hourly"]["time"]
        humedad = data["hourly"]["relativehumidity_2m"]

        return horas, humedad
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener los datos:\n{e}")
        return [], []


def create_line_chart(horas, humedad):
    """Gráfica de línea con estilo mejorado."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(horas, humedad, linestyle="-", marker="s", markersize=4,
            linewidth=2, alpha=0.7, color="blue")
    ax.set_title("Humedad relativa en Zacatecas (línea)")
    ax.set_xlabel("Hora")
    ax.set_ylabel("% Humedad")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def create_bar_chart(horas, humedad):
    """Gráfica de barras con estilo mejorado."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(horas, humedad, color="skyblue", alpha=0.8)
    ax.set_title("Humedad relativa en Zacatecas (barras)")
    ax.set_xlabel("Hora")
    ax.set_ylabel("% Humedad")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def mostrar_graficas(frm, horas, humedad):
    """Inserta las gráficas en el frame de la ventana tkinter."""
    # Línea
    fig1 = create_line_chart(horas, humedad)
    canvas1 = FigureCanvasTkAgg(fig1, master=frm)
    canvas1.draw()
    canvas1.get_tk_widget().pack(pady=10, fill="x")

    # Barras
    fig2 = create_bar_chart(horas, humedad)
    canvas2 = FigureCanvasTkAgg(fig2, master=frm)
    canvas2.draw()
    canvas2.get_tk_widget().pack(pady=10, fill="x")


def open_win_canvas(parent: tk.Tk):
    """
    Crea la ventana secundaria con gráficas de la API.
    """
    win = tk.Toplevel(parent)
    win.title("Canvas con API (Open-Meteo) y gráficas de humedad")
    win.geometry("960x1000")

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    # Botón para cargar datos y graficar
    def cargar():
        horas, humedad = fetch_data()
        if horas and humedad:
            mostrar_graficas(frm, horas, humedad)

    ttk.Button(frm, text="Cargar y mostrar gráficas", command=cargar).pack(pady=10)


# Para pruebas independientes (opcional)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba win_canvas Zacatecas")
    ttk.Button(root, text="Abrir ventana Canvas", command=lambda: open_win_canvas(root)).pack(pady=20)
    root.mainloop()
