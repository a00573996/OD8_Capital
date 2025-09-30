
Sesión 5 · Adaptación de la ventana

Nombre: Juan Pablo
Matrícula: A0057399
Ventana asignada: win_table.py

Lista de cambios aplicados

Título de la subventana cambiado a “Win Table”.

Tamaño ajustado a 1920×1080 para trabajar con tablas amplias.

Reemplazo del Listbox por un ttk.Treeview.

Definición de cinco columnas: Categoría, Subcategoría, Monto, Fecha, Dinero Total.

Encabezados visibles y anchos de columna configurados para lectura clara.

Campo de entrada rápida y botón Agregar para insertar registros.

Botones Eliminar seleccionado, Limpiar y Cerrar.

Prevención de inserciones vacías con aviso mediante messagebox.

Distribución con grid y pesos para que la tabla se expanda correctamente.
Puede invocarse desde el menú principal sin cambios adicionales en la arquitectura.
![WhatsApp Image 2025-09-29 at 21 14 26_be7e53e0](https://github.com/user-attachments/assets/0ff817e6-542b-47f3-b3c5-ed9ca6a93522)


 Reflexión

Estos cambios hacen que la ventana sea útil para el propósito del proyecto. La tabla con cinco columnas organiza la información de manera directa y permite ver categorías, fechas y montos sin perderse. El tamaño a 1920×1080 mejora la lectura cuando hay más filas. Los botones de agregar, eliminar y limpiar facilitan probar el flujo de datos sin depender todavía de archivos externos. Con esta base es sencillo conectar la tabla a un origen real en la carpeta data, calcular totales y preparar reportes. En conjunto, la ventana queda alineada con una gestión simple y clara de información financiera, que es lo que necesitamos para avanzar.
