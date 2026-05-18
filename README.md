# 💼 JobFlow — Gestor Local de Postulaciones de Empleo

**JobFlow** es una aplicación de escritorio personal construida con **Python y Streamlit** diseñada para simplificar y automatizar el registro y seguimiento de tus postulaciones de empleo.

Pegando simplemente el enlace (URL) de cualquier vacante en LinkedIn, Glassdoor, Indeed u otras plataformas, **JobFlow** abrirá de forma transparente un navegador automatizado mediante **Playwright** para extraer toda la información relevante de la vacante, permitiéndote validarla y guardarla directamente en un archivo Excel local (`data/jobflow.xlsx`). También incluye un completo Dashboard interactivo con gráficos de Plotly.

---

## ✨ Características Principales

1. **🕵️ Extracción Inteligente y Automatizada:**
   - Navegación local no-headless con **Playwright** para heredar cookies de tu navegador activo y evitar bloqueos y captchas.
   - Extracción resiliente basada en **JSON-LD (JobPosting)** y selectores dinámicos robustos.
   - Detección automática de habilidades técnicas y palabras clave directamente desde la descripción.
2. **📊 Cuadro de Mando Visual (Dashboard):**
   - Tasa de respuestas interactiva mediante gráficos circulares de Plotly.
   - Volumen de postulaciones a lo largo del tiempo.
   - Distribución de canales de postulación por plataforma.
   - Top 10 de tecnologías y habilidades más solicitadas en tus vacantes registradas.
3. **📋 Tabla de Control Interactiva:**
   - Tabla interactiva basada en `st.data_editor` que permite la edición rápida en línea de respuestas de empresas (`respondio`) y tus comentarios/notas (`notas`).
4. **🔒 Privacidad 100% Local:**
   - Todos tus datos se almacenan en un archivo de Excel tradicional local (`data/jobflow.xlsx`), sin bases de datos complejas, servidores externos, APIs ni conexiones a internet adicionales.

---

## 🛠️ Requisitos e Instalación

### 1. Requisitos Previos
- **Python 3.11** o superior.
- Navegador Google Chrome/Chromium instalado.

### 2. Configurar el Entorno e Instalar Dependencias

Clona o accede a la carpeta del proyecto y ejecuta:

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias requeridas
pip install -r requeriments.txt

# 4. Instalar los binarios del navegador de Playwright
playwright install chromium
```

---

## 🚀 Cómo Ejecutar la Aplicación

Para lanzar la aplicación, asegúrate de estar dentro del entorno virtual activo (`venv`) y ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`.

---

## 🗺️ Estructura del Proyecto

```
jobflow/
│
├── app.py                        # Entrada Principal — Streamlit UI en Español
│
├── scraper/
│   ├── __init__.py               # Inicializador del paquete scraper
│   ├── agent.py                  # Lógica de Playwright y perfiles de Chrome
│   └── parsers/
│       ├── __init__.py           # Enrutamiento de parsers por dominio
│       ├── linkedin.py           # Parser especializado para LinkedIn
│       ├── glassdoor.py          # Parser especializado para Glassdoor
│       └── generic.py            # Parser genérico inteligente (JSON-LD y regex)
│
├── storage/
│   ├── __init__.py               # Inicializador del paquete storage
│   └── excel_handler.py          # CRUD de datos con pandas y openpyxl
│
├── charts/
│   ├── __init__.py               # Inicializador del paquete de visualizaciones
│   └── dashboard.py              # Gráficas dinámicas e interactivas en Plotly
│
├── data/
│   └── jobflow.xlsx              # Archivo de datos (generado automáticamente)
│
├── requeriments.txt              # Archivo de dependencias fijas del stack
└── README.md                     # Este archivo de documentación
```

---

## 💡 Consejos de Uso

- **URL de la vacante:**  Copia directamente el link del apartado de compartir la vacante para que sea una extracion mas exacta.
- **Sesión de Navegador Activa:** Para una extracción fluida en LinkedIn o Glassdoor sin pantallas de inicio de sesión ni bloqueos, abre una vez la vacante en tu navegador normal. Al utilizar Playwright con perfiles persistentes en `./.chrome_profile`, la aplicación heredará el contexto y podrá interactuar de manera transparente.
- **Formato de Fecha:** El campo de fecha de postulación se guarda de manera totalmente automática con el día de registro.
- **Edición Rápida:** Puedes editar las notas de seguimiento o marcar el estado de respuesta de varias vacantes en lote desde la tabla "Mis postulaciones" y persistirlos todos de una sola vez haciendo clic en **"Guardar Cambios"**.
