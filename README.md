
# ZAVE — Finanzas Personales (ODS 8) 💰

**ZAVE** es una aplicación de escritorio desarrollada en **Python** (Tkinter/CustomTkinter) diseñada para ayudar a las personas en México a comprender y mejorar su situación financiera personal. El proyecto está firmemente alineado con el **Objetivo de Desarrollo Sostenible (ODS) 8: Trabajo decente y crecimiento económico**.

Ofrece un completo perfil de usuario, registro detallado de ingresos y gastos, un reporte financiero con visualización gráfica y **recomendaciones personalizadas** con opciones de exportación (MD/HTML/PDF).

---

## 🧭 Contenidos

* [Características](#-características)
* [Arquitectura y stack](#-arquitectura-y-stack)
* [Estructura del proyecto](#-estructura-del-proyecto)
* [Instalación](#-instalación)
* [Configuración de API keys (.env)](#-configuración-de-api-keys-env)
* [Ejecución](#-ejecución)
* [Ventanas del sistema](#-ventanas-del-sistema)
* [Clasificación automática de gastos (IA)](#-clasificación-automática-de-gastos-ia)
* [Recomendaciones personalizadas](#-recomendaciones-personalizadas)
* [Solución de problemas](#-solución-de-problemas)
* [Escalabilidad y modelo de negocio](#-escalabilidad-y-modelo-de-negocio)
* [Equipo](#-equipo)
* [Licencia](#-licencia)

---

## ✨ Características

* **Perfil de usuario**: Permite la gestión de datos personales, situación financiera, hábitos, metas y preferencias con validación en línea (**inline validation**).
* **Ingresos**: Registro de ingresos fijos y variables con cálculo del total estimado mensual.
* **Registro de gastos**: Captura de gastos con **clasificación automática** (Gemini → OpenAI → fallback local), edición y persistencia en formato CSV.
* **Reporte**: Generación de una tabla de gastos, totales acumulados y una **gráfica** (barras/pastel) mostrando porcentajes y montos.
* **Recomendaciones personalizadas**: Genera un plan de acción a corto, mediano y largo plazo. Permite **Exportar** el plan a Markdown, HTML o PDF.
* **Interfaz**: Navegación simple entre ventanas, un *splash* inicial con barra de progreso, una paleta de colores consistente y una interfaz de usuario (**UI**) adaptativa a la resolución de pantalla.

---

## 🧱 Arquitectura y stack

El proyecto está construido sobre un stack moderno y modular:

| Componente | Tecnología/Librería | Propósito principal |
| :--- | :--- | :--- |
| **Lenguaje** | Python 3.10+ | Lógica de negocio y *backend*. |
| **UI** | Tkinter + CustomTkinter | Interfaz de usuario de escritorio. |
| **Imágenes** | Pillow | Manejo de imágenes (ej. logo). |
| **Gráficas** | Matplotlib | Generación de visualizaciones de datos. |
| **HTTP / Enriquecimiento** | Requests | Consumo de APIs y enriquecimiento de contexto (Wikipedia/Nominatim). |
| **IA** | `google-genai` (Gemini) y `openai` | Clasificación automática de gastos. |
| **Exportación PDF** | ReportLab | Generación de documentos PDF. |
| **Configuración** | `python-dotenv` | Gestión de variables de entorno (.env). |

---

## 📁 Estructura del proyecto

```

APPODS/
├── app/
│   ├── start.py        \# Punto de entrada (muestra splash y luego main)
│   ├── main.py         \# Menú principal
│   ├── splash.py       \# Pantalla de carga con progreso
│   ├── win\_home.py     \# Ventana: Perfil de usuario
│   ├── win\_form.py     \# Ventana: Ingresos
│   ├── win\_list.py     \# Ventana: Registro de gastos (IA/CSV/edición)
│   ├── win\_table.py    \# Ventana: Reporte (tabla+gráfica)
│   └── win\_reco.py     \# Ventana: Recomendaciones + Exportar
├── core/
│   ├── profile.py      \# Load/save profile.json y utilidades
│   ├── storage.py      \# Manejo de gastos.csv (append/load/save)
│   ├── ai.py           \# Pipeline OpenAI
│   ├── ai\_gemini.py    \# Pipeline Gemini
│   ├── classifier.py   \# Reglas para clasificar usuario y métricas
│   └── paths.py        \# Helpers de rutas (assets/data)
├── assets/
│   └── ZAVE LOGO.png   \# Logo (usado por splash y main)
├── data/
│   ├── categorias.json \# Categorías soportadas + keymap local
│   ├── gastos.csv      \# Generado y actualizado por la app
│   └── profile.json    \# Generado y actualizado por la app
├── .env                \# (Opcional) API keys
├── requirements.txt
└── README.md

````

> **Nota**: Puedes renombrar la carpeta raíz del proyecto (`APPODS`) sin cambiar código. Si lo haces, recuerda volver a seleccionar el intérprete de `.venv` en VS Code y ejecutar la aplicación desde la nueva carpeta del proyecto.

---

## 🛠 Instalación

Sigue estos pasos para configurar y activar el entorno virtual e instalar las dependencias:

1.  **Crear entorno virtual**

    **Windows (PowerShell)**
    ```powershell
    cd APPODS
    python -m venv .venv
    .\.venv\Scripts\activate
    python -m pip install --upgrade pip
    ```

    **macOS / Linux**
    ```bash
    cd APPODS
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    ```

2.  **Instalar dependencias**

    Con el entorno virtual activado, ejecuta:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔐 Configuración de API keys (.env)

Para usar la clasificación automática de gastos con Gemini u OpenAI, crea un archivo llamado **`.env`** en la raíz del proyecto (`APPODS/`) y añade tus claves:

````

OPENAI\_API\_KEY=tu\_clave\_openai
GEMINI\_API\_KEY=tu\_clave\_gemini

````

> Si no configuras ninguna clave, el sistema usará un clasificador local de *fallback* basado en palabras clave.

---

## ▶️ Ejecución

Asegúrate de tener el entorno virtual activado (`source .venv/bin/activate` o similar).

### Opción 1: Ejecución directa (Recomendada)

Ejecuta el punto de entrada de la aplicación desde la carpeta raíz (`APPODS/`):

```bash
python -m app.start
````

### Opción 2: Ejecutar y depurar en VS Code

Si usas Visual Studio Code, puedes ejecutar el flujo de inicio con la configuración de depuración:

1.  Abre la pestaña **"Run and Debug"** (Ejecutar y Depurar).
2.  Selecciona la configuración: **`Ejecutar ZAVE (splash+main)`**.
3.  Presiona el botón de **Inicio** (triángulo verde).

### Flujo sugerido para demo:

1.  **Perfil de Usuario** $\to$ completa nombre/edad/ciudad/hábitos.
2.  **Ingresos** $\to$ registra ingreso fijo y variables.
3.  **Registro de Gastos** $\to$ agrega ejemplos, prueba la clasificación automática.
4.  **Reporte** $\to$ consulta tabla, totales y gráfica.
5.  **Recomendaciones** $\to$ revisa plan de acción y **Exportar** (MD/HTML/PDF).

-----

## 🪟 Ventanas del sistema

| Módulo | Ventana | Función clave |
| :--- | :--- | :--- |
| `win_home.py` | Perfil de usuario | Recolección de datos personales, situación, hábitos, metas y preferencias. |
| `win_form.py` | Ingresos | Registro de ingreso fijo y variables, cálculo del total estimado. |
| `win_list.py` | Registro de gastos | Alta de gastos con IA (Gemini→OpenAI→local), edición y borrado persistente (CSV). |
| `win_table.py` | Reporte | Visualización de tabla con acumulados, totales por categoría y gráfica. |
| `win_reco.py` | Recomendaciones | Generación del plan corto/mediano/largo según métricas y top gastos. Exportación. |
| `main.py` | Inicio | Menú principal, logo, saludo personalizado y navegación. |
| `splash.py` | Splash | Pantalla de carga inicial con barra de progreso. |

-----

## 🤖 Clasificación automática de gastos (IA)

El sistema intenta clasificar el gasto en un *pipeline* de tres niveles para maximizar precisión y resiliencia:

### Orden de intentos:

1.  **Gemini (`google-genai`)**: Usa un **enum** de categorías soportadas y aplica un **subset** por dominio detectado. Esto mejora la precisión al limitar las opciones y reducir las alucinaciones.
2.  **OpenAI (`openai`)**: Devuelve categoría + confianza. Si la confianza es baja, el sistema enriquece el contexto (ej. buscando el comercio en Wikipedia/Nominatim) y reintenta.
3.  **Local (*Fallback*)**: Se aplica un mapeo por palabras clave definidas en `data/categorias.json` → `keymap`.

> **Tip**: Ajusta `data/categorias.json` para personalizar las categorías y el `keymap` local. Si recibes errores de cuota (`429`) en las APIs (OpenAI o Gemini), el sistema automáticamente usará el clasificador local.

-----

## 🧩 Recomendaciones personalizadas

Las recomendaciones se basan en un análisis profundo de la situación financiera del usuario, calculando métricas clave:

  * **Ingreso total mensual** y **capacidad de ahorro** (en MXN y %).
  * **Cargas** fijas: vivienda, deudas y gastos fijos esenciales.
  * **IGD** (Índice de Gasto Discrecional).
  * **Top de categorías de gasto** (extraídas de `gastos.csv`).
  * **Metas del usuario** (objetivo, horizonte, aportación).

Se estructuran en tres horizontes de acción:

  * **Corto (0–30 días)**: Enfocado en *quick wins* y contención de fugas de dinero.
  * **Mediano (1–6 meses)**: Creación de fondo de emergencia; ajustes estructurales de vivienda/fijos.
  * **Largo (6–24 meses)**: Automatización de inversión; consolidación de deudas; optimización fiscal.

Las recomendaciones son exportables a **Markdown, HTML o PDF** (usando ReportLab).

-----

## 🧪 Solución de problemas

| Problema | Posible causa y solución |
| :--- | :--- |
| La ventana principal no maximiza. | En Windows/Linux se usa `root.state("zoomed")`. En macOS se intenta aplicar `geometry` a pantalla completa si *zoomed* no está disponible. |
| Logo no visible. | Verifica que el archivo `assets/ZAVE LOGO.png` exista y que tengas permisos de lectura. |
| Gemini/OpenAI error 401/429. | Error de autenticación o cuota. Revisa el archivo `.env`, las variables de entorno y tu plan de uso. El sistema caerá al clasificador local como *fallback*. |
| Tk no disponible (macOS). | Instala Tk junto a tu distribución de Python (por ejemplo, `brew install python-tk`, según tu gestor de paquetes). |

-----

## 👥 Equipo

  * **Profesor Camilo Duque** — Código base, arquitectura y revisión final.
  * [Nombre 1] — Recomendaciones (lógica/UX/exportación).
  * [Nombre 2] — Perfil de usuario (validaciones/estado).
  * [Nombre 3] — Ingresos (fijos/variables).
  * [Nombre 4] — Registro de gastos (IA/CSV/edición).
  * [Nombre 5] — Reporte (tabla, totales, gráfica).
  * [Nombre 6] — Integración (splash, navegación, empaquetado).

-----

## 📜 Licencia

[Aquí puedes especificar la licencia, por ejemplo: **MIT** o **Apache 2.0**.]

```

He aplicado el formato Markdown a todo el texto y corregido la instrucción de ejecución para VS Code (`Ejecutar ZAVE (splash+main)`).

¿Necesitas ayuda para elegir una **Licencia** o te gustaría que te generara el contenido para la sección de Escalabilidad y Modelo de Negocio?
```
