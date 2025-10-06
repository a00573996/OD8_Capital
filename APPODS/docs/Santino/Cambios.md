## Diferencias entre los dos códigos

### 1. Ubicación
Primer código: **Miami, FL** (lat=25.76, lon=-80.19).  
Segundo código: **León, Gto** (lat=21.12, lon=-101.68).  

### 2. Rango de datos
Primer código: usa **forecast_days=N** → obtiene el pronóstico de los próximos días (por defecto 2).  
  Segundo código: usa **past_days=1** → obtiene datos de las últimas 24 horas.  

### 3. Función `fetch_data`
- Primer código: recibe un argumento (`fetch_data(dias=2)`) que permite elegir cuántos días de pronóstico descargar.  
- Segundo código: no recibe argumentos, siempre consulta las últimas 24 horas.  

### 4. Gráficas
- Primer código:  
  - Línea en azul.  
  - Barras en color naranja.  
  - Títulos con “Miami”.  

- Segundo código:  
  - Colores por defecto de matplotlib.  
  - Títulos con “León”.  


### 5. Ventana Tkinter
- Primer código:  
  - Ventana más compacta: `960x800`.  
  - Título de ventana: “Clima con Open-Meteo”.  
  - Botón con texto “Cargar gráficas”.  

- Segundo código:  
  - Ventana más grande: `960x1000`.  
  - Título de ventana: “Canvas con API (Open-Meteo) y gráficas”.  
  - Botón con texto “Cargar y mostrar gráficas”.  

---

### 6. Comentarios en docstrings
- Primer código: describe que obtiene datos de **Miami, pronóstico futuro**.  
- Segundo código: describe que obtiene datos de **León, últimas 24 horas**.  
