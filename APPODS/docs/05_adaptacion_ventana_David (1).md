# Registro de usuario e ingresos (Win_Form)

**Autor:** David Alejandro Flores Cruz — *A00573996*  
**Módulo:** `win_form`

> Aplicación de escritorio para capturar datos del usuario y sus ingresos (fijos y variables), con validaciones, cálculo automático y exportación a JSON.

---

## 🧭 Índice
- [Resumen](#-resumen)
- [Características](#-características)
  - [Título y tamaño](#título-y-tamaño)
  - [Datos del usuario](#datos-del-usuario)
  - [Sección de ingresos](#sección-de-ingresos)
  - [Cálculo automático](#cálculo-automático)
  - [Validación y guardado](#validación-y-guardado)
  - [Interfaz estructurada](#interfaz-estructurada)
- [Estructura de datos (JSON)](#-estructura-de-datos-json)
- [Flujo de uso](#-flujo-de-uso)
- [Captura de pantalla](#-captura-de-pantalla)
- [Por qué estos cambios apoyan la idea del proyecto](#-por-qué-estos-cambios-apoyan-la-idea-del-proyecto)
- [Requisitos](#-requisitos)
- [Ejecución](#-ejecución)
- [Roadmap](#-roadmap)
- [Licencia](#-licencia)

---

## ✨ Resumen
La ventana permite registrar datos básicos del usuario (nombre, edad, correo) y capturar ingresos fijos y variables. Incluye validaciones, cálculo del **total estimado** y exportación en **JSON** para facilitar su análisis o integración con otros sistemas. :contentReference[oaicite:0]{index=0}

---

## ⚙️ Características

### Título y tamaño
- Título de la ventana: **“Registro de usuario e ingresos”**.  
- Tamaño ajustado a **1920×1080** para mayor amplitud. :contentReference[oaicite:1]{index=1}

### Datos del usuario
- Campos: **Nombre**, **Edad**, **Correo electrónico**.  
- Validaciones:
  - **Edad:** entero positivo.
  - **Correo:** formato válido. :contentReference[oaicite:2]{index=2}

### Sección de ingresos
- **Ingreso fijo mensual** con validación numérica.  
- **Frecuencia del ingreso:** *Mensual*, *Quincenal*, *Semanal*, *Diario*.  
- **Ingresos variables**:
  - Campos **Concepto** y **Monto**.
  - Botón **Agregar** para registrar cada ingreso.
  - **Listbox** con **scrollbar** para visualizar ingresos agregados.
  - Botones **Eliminar seleccionado** y **Limpiar lista**. :contentReference[oaicite:3]{index=3}

### Cálculo automático
- **Label dinámico** que muestra el **Total estimado** (= fijo + variables). :contentReference[oaicite:4]{index=4}

### Validación y guardado
- Reglas:
  - **Nombre requerido**.
  - **Edad numérica**.
  - **Monto ≥ 0**.
  - **Correo válido**.
- **Exportación a JSON** con estructura organizada (**usuario**, **ingresos**, **total**).
- Manejo de errores con mensajes de advertencia/confirmación. :contentReference[oaicite:5]{index=5}

### Interfaz estructurada
- **Separadores visuales** para secciones.
- **Etiquetas** con fuentes más grandes y **encabezados en negritas**.
- Botones **Guardar** y **Cerrar** organizados al final de la ventana. :contentReference[oaicite:6]{index=6}

---

## 📦 Estructura de datos (JSON)
Ejemplo de exportación:

```json
{
  "usuario": {
    "nombre": "Jane Doe",
    "edad": 28,
    "correo": "jane.doe@email.com"
  },
  "ingresos": {
    "fijo": {
      "monto": 12000,
      "frecuencia": "Mensual"
    },
    "variables": [
      { "concepto": "Freelance", "monto": 2500 },
      { "concepto": "Bonificación", "monto": 800 }
    ]
  },
  "total_estimado": 15300
}
 en una herramienta sencilla y útil para fomentar una mejor organización financiera, lo cual está en línea con el ODS 8: Trabajo decente y crecimiento económico.

