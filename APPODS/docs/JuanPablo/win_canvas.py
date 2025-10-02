import tkinter as tk
from tkinter import ttk, messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def fetch_data():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=19.43&longitude=-99.13"
            "&hourly=temperature_2m&past_days=1"
            "&timezone=auto"
        )
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        horas = data["hourly"]["time"]
        temperaturas = data["hourly"]["temperature_2m"]
        return horas, temperaturas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información:\n{e}")
        return [], []


def create_line_chart(horas, temps):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(horas, temps, linestyle="-", color="blue", marker="o", markersize=4)
    ax.set_title("Registro de temperatura (Ciudad de México)")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Temperatura °C")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def create_bar_chart(horas, temps):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(horas, temps, color="darkred")
    ax.set_title("Temperatura por hora (Barras)")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Temperatura °C")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def mostrar_graficas(frm, horas, temps):
    fig1 = create_line_chart(horas, temps)
    canvas1 = FigureCanvasTkAgg(fig1, master=frm)
    canvas1.draw()
    canvas1.get_tk_widget().place(x=80, y=100)

    fig2 = create_bar_chart(horas, temps)
    canvas2 = FigureCanvasTkAgg(fig2, master=frm)
    canvas2.draw()
    canvas2.get_tk_widget().place(x=80, y=420)


def open_win_canvas(parent: tk.Tk):
    ventana = tk.Toplevel(parent)
    ventana.title("Panel de Temperaturas - CDMX")
    ventana.geometry("960x950")

    contenedor = ttk.Frame(ventana, padding=15)
    contenedor.pack(fill="both", expand=True)

    ttk.Label(
        contenedor,
        text="Visualización climática de las últimas 24 horas",
        font=("Arial", 15)
    ).place(x=80, y=40)

    def cargar_datos():
        horas, temps = fetch_data()
        if horas and temps:
            mostrar_graficas(contenedor, horas, temps)

    ttk.Button(
        contenedor,
        text="Cargar datos meteorológicos",
        command=cargar_datos
    ).place(x=80, y=360)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ventana principal")
    ttk.Button(root, text="Abrir panel climático", command=lambda: open_win_canvas(root)).pack(pady=20)
    root.mainloop()
