## 👥 Equipo

- **Profesor Camilo Duque** — Arquitectura y revisión final  
- **Alfredo de Alba Ulloa**  
- **Daniel Santino Alejandri Cure**  
- **David Alejandro Flores Cruz**  
- **Juan Pablo Padilla Ramírez**  
- **Rodrigo Otero Juárez**
 ---
# 💰 ZAVE — Finanzas Personales (ODS 8)

**ZAVE** es una aplicación de escritorio desarrollada en **Python** (Tkinter/CustomTkinter) diseñada para ayudar a las personas en México a comprender y mejorar su situación financiera personal.  
El proyecto está alineado con el **ODS 8: Trabajo decente y crecimiento económico**.

Ofrece un completo perfil de usuario, registro de ingresos y gastos, reporte financiero con visualización gráfica y **recomendaciones personalizadas** con opciones de exportación (MD/HTML/PDF).

---

## 🧭 Contenidos

- [Equipo](#-equipo)
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
---

## ✨ Características

- **Perfil de usuario**: gestión de datos personales, situación financiera, hábitos, metas y preferencias con validación en línea.
- **Ingresos**: registro de ingresos fijos y variables con cálculo del total mensual.
- **Registro de gastos**: captura con **clasificación automática** (Gemini → OpenAI → fallback local), edición y persistencia CSV.
- **Reporte**: tabla y **gráfica** (barras/pastel) con porcentajes y montos.
- **Recomendaciones personalizadas**: plan de acción corto, mediano y largo plazo con exportación (MD/HTML/PDF).
- **Interfaz**: navegación simple, *splash* inicial, paleta coherente y UI adaptativa.

---

## 🧱 Arquitectura y stack

| Componente | Tecnología/Librería | Propósito principal |
|-------------|---------------------|----------------------|
| **Lenguaje** | Python 3.10+ | Lógica de negocio y backend |
| **UI** | Tkinter + CustomTkinter | Interfaz de usuario |
| **Imágenes** | Pillow | Manejo de imágenes |
| **Gráficas** | Matplotlib | Visualizaciones |
| **HTTP / Enriquecimiento** | Requests | APIs externas |
| **IA** | `google-genai`, `openai` | Clasificación automática |
| **Exportación PDF** | ReportLab | Generación de PDF |
| **Configuración** | `python-dotenv` | Gestión de `.env` |

---

## 📁 Estructura del proyecto

```bash
APPODS/
├── app/
│   ├── start.py        # Punto de entrada (splash → main)
│   ├── main.py         # Menú principal
│   ├── splash.py       # Pantalla de carga
│   ├── win_home.py     # Perfil de usuario
│   ├── win_form.py     # Ingresos
│   ├── win_list.py     # Gastos (IA/CSV)
│   ├── win_table.py    # Reporte (tabla + gráfica)
│   └── win_reco.py     # Recomendaciones + exportar
├── core/
│   ├── profile.py      # Manejo de profile.json
│   ├── storage.py      # Manejo de gastos.csv
│   ├── ai.py           # Pipeline OpenAI
│   ├── ai_gemini.py    # Pipeline Gemini
│   ├── classifier.py   # Reglas y métricas
│   └── paths.py        # Helpers de rutas
├── assets/
│   └── ZAVE LOGO.png   # Logo
├── data/
│   ├── categorias.json # Categorías + keymap
│   ├── gastos.csv
│   └── profile.json
├── .env                # (Opcional) API keys
├── requirements.txt
└── README.md
```

> **Nota**: puedes renombrar la carpeta raíz sin romper dependencias.

---

## 🛠 Instalación

### 1. Crear entorno virtual

**Windows (PowerShell)**:
```powershell
cd APPODS
python -m venv .venv
.\.venv\Scriptsctivate
python -m pip install --upgrade pip
```

**macOS / Linux**:
```bash
cd APPODS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuración de API keys (.env)

Crea un archivo `.env` en la raíz del proyecto y agrega tus claves:

```env
OPENAI_API_KEY=tu_clave_openai
GEMINI_API_KEY=tu_clave_gemini
```

> Si no configuras claves, se usará el clasificador local (basado en `categorias.json`).

---

## ▶️ Ejecución desde VS Code (Run and Debug)

1. Abre el proyecto (`APPODS/`) en VS Code.  
2. Activa el entorno virtual `.venv`.  
3. Abre **Run and Debug (Ctrl+Shift+D)**.  
4. Selecciona **"Ejecutar ZAVE (splash+main)"**.  
5. Presiona **F5** o el botón ▶️.

Configuración de `launch.json`:

```json
{
  "name": "Ejecutar ZAVE (splash+main)",
  "type": "debugpy",
  "request": "launch",
  "module": "app.start",
  "console": "integratedTerminal",
  "justMyCode": true,
  "cwd": "${workspaceFolder}/APPODS",
  "python": "${command:python.interpreterPath}"
}
```

### Flujo sugerido (demo)

1. **Perfil de usuario** → completa tus datos.  
2. **Ingresos** → registra ingreso fijo y variables.  
3. **Gastos** → agrega ejemplos y prueba clasificación.  
4. **Reporte** → consulta totales y gráfica.  
5. **Recomendaciones** → revisa y exporta el plan.

---

## 🪟 Ventanas del sistema

| Módulo | Ventana | Función |
|--------|----------|---------|
| `win_home.py` | Perfil de usuario | Datos personales y metas |
| `win_form.py` | Ingresos | Registro de ingresos |
| `win_list.py` | Gastos | Clasificación IA / CSV |
| `win_table.py` | Reporte | Tabla y gráfica |
| `win_reco.py` | Recomendaciones | Plan y exportación |
| `main.py` | Inicio | Menú y navegación |
| `splash.py` | Splash | Pantalla inicial |

---

## 🤖 Clasificación automática de gastos (IA)

Pipeline de clasificación (prioridad descendente):

1. **Gemini (`google-genai`)** → Enum de categorías específicas.  
2. **OpenAI (`openai`)** → Devuelve categoría + confianza.  
3. **Fallback local** → Mapeo por palabras clave (`data/categorias.json`).

> Si ocurre un error o límite de cuota (429), el sistema usa automáticamente el clasificador local.

---

## 🧩 Recomendaciones personalizadas

El sistema analiza métricas clave:

- Ingreso total y capacidad de ahorro.  
- Cargas fijas y esenciales.  
- IGD (Índice de Gasto Discrecional).  
- Top de categorías y metas del usuario.

### Horizontes de acción

- **Corto plazo (0–30 días)** → Quick wins, control de fugas.  
- **Mediano plazo (1–6 meses)** → Fondo de emergencia.  
- **Largo plazo (6–24 meses)** → Inversión y optimización fiscal.

> Exportables a **Markdown**, **HTML** o **PDF**.

---

## 🧪 Solución de problemas

| Problema | Posible causa / solución |
|-----------|--------------------------|
| Ventana no maximiza | Usa `root.state("zoomed")` (Windows/Linux). |
| Logo no visible | Verifica `assets/ZAVE LOGO.png`. |
| Error 401/429 (Gemini/OpenAI) | Revisa `.env` y cuota. Fallback local. |
| Tk no disponible (macOS) | Instala con `brew install python-tk`. |

---


