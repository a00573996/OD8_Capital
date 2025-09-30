# David Alejandro Flores Cruz - A00573996

## win_form

### Lista de cambios aplicados a la ventana

---

#### Título y tamaño
- Se cambió el título a **“Registro de usuario e ingresos”**.
- Se amplió el tamaño de la ventana a **1920×1080**.

---

#### Datos del usuario
- Se añadieron campos para **Nombre**, **Edad** y **Correo electrónico**.
- Se implementó validación de:
  - Edad → **entero positivo**
  - Correo electrónico → **formato válido**

---

#### Sección de ingresos
- Campo de **Ingreso fijo mensual** con validación numérica.
- Frecuencia del ingreso con opciones:
  - Mensual
  - Quincenal
  - Semanal
  - Diario

##### Nueva subsección: Ingresos variables
- Campos: **“Concepto”** y **“Monto”**.
- Botón **“Agregar”** para añadir registros.
- **Lista (Listbox)** con *scrollbar* para mostrar ingresos variables añadidos.
- Botones:
  - **Eliminar seleccionado**
  - **Limpiar lista**

---

#### Cálculo automático
- Se añadió un **label dinámico** que muestra el **Total estimado de ingresos** (fijo + variables).

---

#### Validación y guardado
- Validaciones de entradas:
  - Nombre requerido
  - Edad numérica
  - Monto ≥ 0
  - Correo válido
- Al guardar:
  - Los datos se exportan en formato **JSON** (estructura organizada con usuario, ingresos y total).
- Manejo de errores con mensajes de advertencia o confirmación.

---

#### Interfaz estructurada
- Separadores visuales para diferenciar secciones.
- Etiquetas con fuentes más grandes y **negritas en encabezados**.
- Botones **“Guardar”** y **“Cerrar”** organizados al final de la ventana.

---

### Captura de pantalla
*(Aquí puede insertarse la captura con formato Markdown si está disponible, por ejemplo:)*

```markdown
![Captura de pantalla](ruta/de/la/imagen.png)

