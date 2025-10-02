###David Flores 
# Cambios realizados en `win_canvas.py`

## 1. Ciudad consultada (latitud/longitud)
- **Antes:** León, Gto (`latitude=21.12`, `longitude=-101.68`).  
- **Ahora:** Ciudad de México (`latitude=19.43`, `longitude=-99.13`).  
- **Motivo:** Ajustar la ubicación de referencia de los datos.

## 2. Rango de datos
- **Antes:** Temperaturas horarias de las últimas 24 horas (`hourly=temperature_2m`).  
- **Ahora:** Humedad relativa y velocidad del viento de las últimas 24 horas (`hourly=relative_humidity_2m,wind_speed_10m`).  
- **Motivo:** Probar otros parámetros de la API y diversificar la información climática mostrada.

## 3. Parámetros de la API
- **Eliminado:** `temperature_2m`.  
- **Agregados:**  
  - `relative_humidity_2m` → Humedad relativa a 2 metros.  
  - `wind_speed_10m` → Velocidad del viento a 10 metros.  

## 4. Diseño de las gráficas
- **Antes:** Dos gráficas de temperatura (línea y barras).  
- **Ahora:**  
  - Gráfica de **humedad relativa** (línea).  
  - Gráfica de **velocidad del viento** (barras).

## 5. Estilo visual en gráficas
- **Antes:** Línea con `marker="o"`, grosor por defecto y sin transparencia.  
- **Ahora:**  
  - `marker="s"` (cuadrados).  
  - `linewidth=2.0` (línea más gruesa).  
  - `alpha=0.85` (ligera transparencia).  
  - Rejilla activada: `ax.grid(True, linestyle="--", alpha=0.5)`.  
- **Motivo:** Mejorar la visualización y distinguir más claramente los datos.

## 6. Estructura de ventana (Tkinter)
- **Antes:** El botón mostraba gráficas, pero al recargar se duplicaban.  
- **Ahora:** Se agregó la función `_clear_plot_widgets` para limpiar gráficos anteriores y evitar duplicaciones.  
- **Motivo:** Mantener la ventana ordenada al recargar varias veces.

## 7. Títulos y etiquetas
- Se ajustaron títulos y ejes para reflejar los nuevos parámetros:  
  - **Humedad relativa (%)**.  
  - **Velocidad del viento (km/h)**.  

---

## ✅ Resumen
La nueva versión consulta **CDMX** en lugar de León, cambia el parámetro de la API de **temperatura** a **humedad y viento**, ajusta la estética de las gráficas (marcadores, grosor, transparencia y rejilla) y mejora la interacción al evitar duplicación de gráficos al recargar.

