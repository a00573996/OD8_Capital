Sesión 5 — Adaptación de la ventana asignada

Nombre: Juan Pablo
Matrícula: A0057399
Ventana trabajada: win_table.py
Ruta del archivo: /src/app/win_table.py

Lista de cambios aplicados a la ventana
1) Título y dimensiones

Título actualizado a “Win Table”.

Resolución configurada a 1920×1080 para aprovechar el espacio y mejorar la legibilidad.

2) Estructura de datos en tabla

Sustitución del Listbox por un ttk.Treeview con cinco columnas:

Categoría

Subcategoría

Monto

Fecha

Dinero Total

Encabezados visibles y anchos configurados por columna.

Disposición con grid y expansión (sticky="nsew") para que la tabla ocupe el área disponible.

3) Gestión de registros

Campo de entrada rápida para agregar un nuevo registro (se inserta como Categoría; el resto de columnas se completarán en iteraciones posteriores).

Botones operativos:

Agregar: inserta una fila en la tabla.

Eliminar seleccionado: borra la fila marcada.

Limpiar: vacía la tabla completa.

Cerrar: cierra la subventana.

4) Comportamiento y validaciones básicas

Prevención de inserciones vacías con mensaje de advertencia.

Manejo de selección para evitar errores al eliminar.

Configuración de pesos en filas/columnas del Frame para un reflujo correcto de la interfaz.

5) Integración con el proyecto

Mantiene la estructura modular del proyecto de cinco ventanas.

Puede invocarse desde el menú principal sin cambios adicionales en la arquitectura.
![WhatsApp Image 2025-09-29 at 21 14 26_be7e53e0](https://github.com/user-attachments/assets/0ff817e6-542b-47f3-b3c5-ed9ca6a93522)


 Reflexión

El cambio a Treeview permite visualizar información estructurada y preparar la ventana para operaciones futuras como cálculo de totales, filtrado o exportación. La definición de columnas (Categoría, Subcategoría, Monto, Fecha, Dinero Total) alinea la interfaz con la gestión de datos del proyecto. El ajuste de resolución mejora la legibilidad y facilita pruebas con conjuntos de datos más largos. La ventana queda lista para integrarse con fuentes de datos en /data/ o formularios que alimenten la tabla.
