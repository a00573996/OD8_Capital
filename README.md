
Profesor Camilo Duque
# ZAVE — Finanzas Personales (ODS 8)

**ZAVE** es una app de escritorio en Python (Tkinter/CustomTkinter) que ayuda a personas en México a entender y mejorar sus finanzas personales, alineada al **ODS 8: Trabajo decente y crecimiento económico**.  
Ofrece perfil del usuario, registro de ingresos y gastos, reporte con gráfica y **recomendaciones personalizadas** con exportación (MD/HTML/PDF).

---

## 🧭 Contenidos

- [Características](#-características)
- [Arquitectura y stack](#-arquitectura-y-stack)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración de API keys (.env)](#-configuración-de-api-keys-env)
- [Ejecución](#-ejecución)
- [Ventanas del sistema](#-ventanas-del-sistema)
- [Clasificación automática de gastos (IA)](#-clasificación-automática-de-gastos-ia)
- [Recomendaciones personalizadas](#-recomendaciones-personalizadas)
- [Solución de problemas](#-solución-de-problemas)
- [Escalabilidad y modelo de negocio](#-escalabilidad-y-modelo-de-negocio)
- [Equipo](#-equipo)
- [Licencia](#-licencia)

---

## ✨ Características

- **Perfil de usuario** (validación inline).
- **Ingresos** fijos y variables con total estimado mensual.
- **Registro de gastos** con **clasificación automática** (Gemini → OpenAI → fallback local), edición y persistencia en CSV.
- **Reporte** con tabla, totales acumulados y **gráfica** (barras/pastel, % y montos).
- **Recomendaciones personalizadas** (corto/mediano/largo plazo) + **Exportar** (Markdown/HTML/PDF).
- **Navegación** simple entre ventanas y splash inicial con progreso.
- Paleta consistente y UI adaptativa (escala por resolución).

---

## 🧱 Arquitectura y stack

- **Python** 3.10+
- **UI**: Tkinter + CustomTkinter  
- **Imágenes**: Pillow  
- **Gráficas**: Matplotlib  
- **HTTP / Enriquecimiento**: Requests (Wikipedia/Nominatim sin API key)  
- **IA**: `google-genai` (Gemini) y `openai` (fallback)  
- **Exportación PDF**: ReportLab  
- **Config**: python-dotenv

---

## 📁 Estructura del proyecto

APPODS/
app/
start.py # punto de entrada (muestra splash y luego main)
main.py # menú principal
splash.py # pantalla de carga con progreso
win_home.py # ventana: Perfil de usuario
win_form.py # ventana: Ingresos
win_list.py # ventana: Registro de gastos (IA/CSV/edición)
win_table.py # ventana: Reporte (tabla+gráfica)
win_reco.py # ventana: Recomendaciones + Exportar
core/
profile.py # load/save profile.json y utilidades
storage.py # manejo de gastos.csv (append/load/save)
ai.py # pipeline OpenAI (categoría+confianza+enriquecimiento)
ai_gemini.py # pipeline Gemini (con enum / subset)
classifier.py # reglas para clasificar usuario y métricas
paths.py # helpers de rutas (assets/data)
assets/
ZAVE LOGO.png # logo (usado por splash y main)
data/
categorias.json # categorías soportadas + keymap local
gastos.csv # generado y actualizado por la app
profile.json # generado y actualizado por la app
.env # (opcional) API keys
requirements.txt
README.md

> **Nota**: Puedes renombrar la carpeta raíz del proyecto sin cambiar código. Tras el cambio, vuelve a seleccionar el intérprete de `.venv` en VS Code y ejecuta desde la carpeta del proyecto.

---

## 🛠 Instalación

1) **Crear entorno virtual**

**Windows (PowerShell)**
```powershell
cd APPODS
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip

macOS / Linux

cd APPODS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

2. Instalar dependencias

pip install -r requirements.txt

🔐 Configuración de API keys (.env)

Crea un archivo .env en la raíz del proyecto:

OPENAI_API_KEY=tu_clave_openai
GEMINI_API_KEY=tu_clave_gemini

▶️ Ejecución

Con el entorno activado y dentro de APPODS/:
python -m app.start

Flujo sugerido para demo:

Perfil de Usuario → completa nombre/edad/ciudad/hábitos.

Ingresos → registra ingreso fijo y variables.

Registro de Gastos → agrega ejemplos, prueba la clasificación automática.

Reporte → consulta tabla, totales y gráfica.

Recomendaciones → revisa plan de acción y Exportar (MD/HTML/PDF).

🪟 Ventanas del sistema
Módulo	Ventana	Función clave
win_home.py	Perfil de usuario	Datos personales, situación, hábitos, metas y preferencias. Validación inline.
win_form.py	Ingresos	Ingreso fijo + variables, total estimado, guardado en profile.json.
win_list.py	Registro de gastos	Alta de gastos con IA (Gemini→OpenAI→local), edición y borrado persistente (CSV).
win_table.py	Reporte	Tabla con acumulados, totales por categoría y gráfica (barras/pastel).
win_reco.py	Recomendaciones	Plan corto/mediano/largo según métricas y top gastos. Exportación a MD/HTML/PDF.
main.py	Inicio	Logo, saludo personalizado, navegación.
splash.py	Splash	Carga inicial con barra de progreso.

🤖 Clasificación automática de gastos (IA)

Orden de intentos:

Gemini (google-genai) con lista de categorías (enum) y subset por dominio detectado (mejora precisión sin depender de marcas).

OpenAI (openai): devuelve categoría + confianza; si la confianza es baja, se enriquece contexto (Wikipedia/Nominatim) y se reintenta.

Local (fallback): mapeo por palabras clave (ajustable en data/categorias.json → keymap).

Tip: Ajusta data/categorias.json para personalizar categorías y keymap.
Si recibes errores de cuota (429) en OpenAI o Gemini, revisa tu plan o usa el clasificador local.

🧩 Recomendaciones personalizadas

Se calculan con:

Ingreso total mensual, capacidad de ahorro (MXN y %).

Cargas: vivienda, deudas y fijos.

IGD (índice de gasto discrecional).

Top de categorías de gasto (desde CSV).

Metas del usuario (objetivo, horizonte, aportación).

Se muestran en tres horizontes:

Corto (0–30 días): quick wins y contención de fugas.

Mediano (1–6 meses): fondo de emergencia; ajustes de vivienda/fijos.

Largo (6–24 meses): automatización de inversión; consolidación de deudas; optimización fiscal.

Exportables a Markdown, HTML o PDF (ReportLab).

🧪 Solución de problemas

La ventana principal no maximiza: en Windows/Linux se usa root.state("zoomed"). En macOS se aplica geometry a pantalla completa si zoomed no está disponible.

Logo no visible: verifica que assets/ZAVE LOGO.png exista y que tengas permisos de lectura.

Gemini/OpenAI error 401/429: revisa .env, variables de entorno y tu plan de uso. Si falla, el sistema cae al clasificador local.

Tk no disponible (macOS): instala Tk junto a tu distribución de Python (por ejemplo, brew install python-tk, según tu setup).

👥 Equipo

Completar con nombres reales y roles.

[Nombre 1] — Recomendaciones (lógica/UX/exportación)

[Nombre 2] — Perfil de usuario (validaciones/estado)

[Nombre 3] — Ingresos (fijos/variables)

[Nombre 4] — Registro de gastos (IA/CSV/edición)

[Nombre 5] — Reporte (tabla, totales, gráfica)

[Nombre 6] — Integración (splash, navegación, empaquetado)