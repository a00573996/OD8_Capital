Profesor: **Camilo Duque**
# ZAVE — Finanzas Personales (ODS 8)
**ZAVE** es una app de escritorio en Python (Tkinter/CustomTkinter) que ayuda a personas en México a entender y mejorar sus finanzas personales, alineada al **ODS 8: Trabajo decente y crecimiento económico**. Ofrece perfil del usuario, registro de ingresos y gastos, reporte con gráfica y **recomendaciones personalizadas** con exportación (MD/HTML/PDF).
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
```text
APPODS/
  app/
    start.py
    main.py
    splash.py
    win_home.py
    win_form.py
    win_list.py
    win_table.py
    win_reco.py
  core/
    profile.py
    storage.py
    ai.py
    ai_gemini.py
    classifier.py
    paths.py
  assets/
    ZAVE LOGO.png
  data/
    categorias.json
    gastos.csv
    profile.json
  .env
  requirements.txt
  README.md
  .vscode/
    launch.json
