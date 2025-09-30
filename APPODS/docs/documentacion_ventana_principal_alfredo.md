# Documentación --- Ventana Principal ZAVE

## Descripción General

Esta es la ventana principal de la aplicación **ZAVE --- Finanzas
Personales (ODS 8)**.\
Su propósito es servir como menú de navegación para acceder a las
diferentes secciones de la aplicación, relacionadas con la
administración de ingresos y gastos de los usuarios.

La ventana mantiene la funcionalidad original, pero fue adaptada con un
**diseño más estético y profesional**, empleando una paleta de colores
en verde (más corporativo que el azul previo) y un layout tipo *card*
con jerarquía visual.

## Características principales

-   **Título de la aplicación**: `ZAVE — Finanzas Personales (ODS 8)`
-   **Versión mostrada**: `v0.1`
-   **Tamaño mínimo de ventana**: 480x420 píxeles
-   **Centrado automático** de la ventana en pantalla
-   **Estilos personalizados** mediante `ttk.Style`:
    -   Verde corporativo para los botones principales
    -   Rojo para el botón de salida
    -   Fondo gris claro con tarjetas blancas (*card layout*)
    -   Tipografía clara con jerarquía (encabezados, subtítulos, pie de
        página)
-   **Footer**: mensaje recordando el objetivo del proyecto alineado con
    el **ODS 8**

## Opciones del Menú

1.  **Home / Bienvenida**\
    Abre la ventana inicial con un mensaje de bienvenida.

2.  **Ingresos**\
    Abre la ventana para registrar ingresos fijos y variables.

3.  **Registro de Gastos**\
    Abre la ventana para ingresar y administrar gastos.

4.  **Reporte de Gastos**\
    Abre la ventana con reportes tabulares de gastos registrados.

5.  **Reporte Gráfico de Gastos**\
    Abre la ventana con gráficos que representan visualmente los gastos.

------------------------------------------------------------------------

### Botón especial: **Salir**

-   Ubicado al final del menú, en rojo (estilo de peligro).
-   Cierra la aplicación al presionarlo.
-   Se ajustó para que siempre **quepa dentro de la pantalla**, alineado
    con el resto de botones.

------------------------------------------------------------------------

## Justificación de los cambios de diseño

-   Se cambió el color principal de azul a verde, transmitiendo un
    estilo más profesional y relacionado con el tema financiero.\
-   Se mejoró la organización visual mediante un contenedor tipo *card*,
    separadores y jerarquía tipográfica.\
-   Se mantiene la **funcionalidad intacta** de los botones y callbacks,
    lo que garantiza compatibilidad con el resto del proyecto.

## Relación con el proyecto

Estos cambios contribuyen a la misión del proyecto **ZAVE**: ayudar a
los jóvenes y personas interesadas en organizar mejor sus finanzas,
alineándose al **ODS 8: Trabajo decente y crecimiento económico**.
