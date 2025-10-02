### Alfredo
# Cambios realizados en la nueva versión de `win_canvas.py`

## Ciudad consultada
Se modificó la ubicación de la consulta en la API de Open-Meteo.

- **Antes:** León, Guanajuato (`latitude=21.12`, `longitude=-101.68`).  
- **Ahora:** Zacatecas, Zacatecas (`latitude=22.77`, `longitude=-102.57`).  

## Parámetro de la API
- **Antes:** Se obtenía la **temperatura horaria** (`temperature_2m`).  
- **Ahora:** Se reemplazó por la **humedad relativa horaria** (`relative_humidity_2m`).  

## Ajustes en la gráfica de línea
- Se cambió el marcador de círculo a **cuadrado** (`marker="s"`).  
- Se incrementó el grosor de línea (`linewidth=2`).  
- Se añadió transparencia a la curva (`alpha=0.7`).  
- Se definió un **color azul** para uniformidad visual.  
- Se agregó una **rejilla con líneas punteadas** (`ax.grid(True, linestyle="--", alpha=0.5)`).  

