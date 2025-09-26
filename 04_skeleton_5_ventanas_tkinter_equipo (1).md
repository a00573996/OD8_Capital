# 📄 04_skeleton_5_ventanas_tkinter_equipo.md

## 📌 Evidencias de la sesión 3 — Esqueleto del proyecto con Tkinter

### 🖼️ Capturas de pantalla
- **Ventana principal**  
  ![ventanaPrincipal](ventanaPrincipal.png)

- **Ventana 1 — Home / Bienvenida**  
  ![win_home](win_home.png)

- **Ventana 2 — Formulario**  
  ![win_form](win_form.png)

- **Ventana 3 — Lista (CRUD básico)**  
  ![win_list](win_list.png)

- **Ventana 4 — Tabla (Treeview con CSV)**  
  ![win_table](win_table.png)

- **Ventana 5 — Canvas (Dibujo básico)**  
  ![win_canvas](win_canvas.png)

---

### 📂 Estructura de carpetas
```
APPODS/
│
├─ app/
│   ├─ __init__.py
│   ├─ main.py          # Ventana principal con menú de navegación
│   ├─ win_home.py      # Ventana 1 (Bienvenida + MessageBox)
│   ├─ win_form.py      # Ventana 2 (Formulario + validación + guardado en archivo)
│   ├─ win_list.py      # Ventana 3 (Listbox con CRUD básico)
│   ├─ win_table.py     # Ventana 4 (Tabla con ttk.Treeview leyendo data/sample.csv)
│   └─ win_canvas.py    # Ventana 5 (Canvas con dibujos básicos)
│
├─ data/
│   └─ sample.csv       # Datos de ejemplo para la tabla
│
├─ docs/
│   ├─ 04_skeleton_5_ventanas_tkinter_equipo.md  # este archivo
│   ├─ ventanaPrincipal.png
│   ├─ win_home.png
│   ├─ win_form.png
│   ├─ win_list.png
│   ├─ win_table.png
│   └─ win_canvas.png
│
├─ .vscode/
│   └─ launch.json      # Configuración de depuración en VS Code
│
├─ .venv/               # Entorno virtual (no versionar)
└─ tests/
```

---

### 🖥️ Pasos de ejecución

**Desde terminal (PowerShell o cmd):**
```powershell
cd C:\Users\david_e9ts58v\Downloads\APPODS
. .\.venv\Scripts\Activate.ps1
python -m app.main
```

**Desde VS Code (con launch.json):**
1. Abrir la vista *Run and Debug* (`Ctrl+Shift+D`).
2. Seleccionar la configuración **Ejecutar main (app.main)**.
3. Presionar ▶ o **F5**.

---

### 👥 Roles e integrantes
- **Integrante A** → Ventana 1 — *win_home.py* (Bienvenida + messagebox).  
- **Integrante B** → Ventana 2 — *win_form.py* (Formulario con validación y guardado).  
- **Integrante C** → Ventana 3 — *win_list.py* (Listbox con CRUD básico).  
- **Integrante D** → Ventana 4 — *win_table.py* (Tabla leyendo `sample.csv`).  
- **Integrante E** → Ventana 5 — *win_canvas.py* (Canvas con dibujo básico).  

---

### 🗂️ Notas de versionado
- El archivo **`/.vscode/launch.json`** debe versionarse en GitHub para que todo el equipo tenga la misma configuración de ejecución.  
- El directorio **`.venv/`** no debe subirse al repositorio (añadirlo al `.gitignore`).  
