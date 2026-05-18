# JOBFLOW — Contexto del Proyecto para Agente de Desarrollo

> Este archivo es el contexto de inicialización del proyecto **JobFlow**.
> Debe ser leído por el agente antes de escribir cualquier línea de código.
> No se deben agregar librerías, frameworks ni herramientas que no estén listadas aquí.

---

## 1. Descripción General

**JobFlow** es una aplicación de escritorio personal construida con Python + Streamlit.

Su propósito es llevar un registro estructurado de postulaciones a vacantes de empleo. El usuario proporciona un link de cualquier plataforma de trabajo (LinkedIn, Glassdoor, Indeed, etc.), y la aplicación:

1. Accede al link mediante un agente de navegación (Playwright).
2. Extrae automáticamente los campos relevantes de la vacante.
3. Muestra los datos al usuario para confirmación o edición.
4. Guarda el registro en un archivo Excel local (`jobflow.xlsx`).
5. Permite al usuario marcar si recibió respuesta de esa empresa.
6. Genera un dashboard visual con estadísticas de sus postulaciones.

La aplicación es **100% local y personal**. No tiene backend externo, base de datos remota, ni autenticación.

---

## 2. Stack Tecnológico — FIJO, NO MODIFICAR

> El agente **NO debe proponer, instalar ni usar** ninguna librería fuera de esta lista.
> Si considera que algo falta, debe preguntarle al usuario antes de proceder.

### Lenguaje
- **Python 3.11+**

### Interfaz de Usuario
- **Streamlit** — Framework principal de UI. Toda la interfaz se construye aquí.

### Web Scraping / Agente de Navegación
- **Playwright (Python)** — Para acceder a páginas con JavaScript (LinkedIn, Glassdoor, etc.).
  - Se usa en modo **headless=False** con perfil de usuario real para aprovechar sesiones activas del navegador y evitar bloqueos.
  - El agente toma un snapshot del DOM renderizado para extraer información.
  - **NO se usa requests, BeautifulSoup, Selenium, Scrapy ni ningún otro scraper.**

### Almacenamiento de Datos
- **openpyxl** — Para leer y escribir el archivo Excel `data/jobflow.xlsx`.
- **pandas** — Para manipular y filtrar los datos en memoria.
- El archivo de datos es un `.xlsx` local. **No se usa base de datos (SQLite, PostgreSQL, etc.), ni archivos CSV.**

### Visualización / Gráficas
- **Plotly** — Para gráficas interactivas en el dashboard (respondidas vs. no respondidas, etc.).

### Utilidades
- **python-dateutil** — Para manejo y parseo de fechas.

### Archivo de dependencias
```
streamlit
playwright
openpyxl
pandas
plotly
python-dateutil
```

---

## 3. Estructura de Carpetas — OBLIGATORIA

El agente debe respetar esta estructura al crear, editar o referenciar archivos.

```
jobflow/
│
├── app.py                        # Punto de entrada — Streamlit UI principal
│
├── scraper/
│   ├── __init__.py
│   ├── agent.py                  # Lógica central de Playwright (abrir link, snapshot)
│   └── parsers/
│       ├── __init__.py
│       ├── linkedin.py           # Parser específico para LinkedIn
│       ├── glassdoor.py          # Parser específico para Glassdoor
│       └── generic.py            # Parser de fallback para cualquier otra URL
│
├── storage/
│   ├── __init__.py
│   └── excel_handler.py          # Leer, escribir y actualizar jobflow.xlsx
│
├── charts/
│   ├── __init__.py
│   └── dashboard.py              # Funciones para generar gráficas con Plotly
│
├── data/
│   └── jobflow.xlsx              # Archivo de datos (se crea automáticamente si no existe)
│
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Instrucciones de instalación y uso
```

**Reglas de estructura:**
- Cada carpeta con lógica Python debe tener su `__init__.py`.
- Ningún módulo debe importar directamente desde `app.py`.
- `app.py` es el único punto que importa de `scraper/`, `storage/` y `charts/`.

---

## 4. Esquema de Datos — Columnas del Excel

El archivo `data/jobflow.xlsx` tiene **una única hoja** llamada `postulaciones`.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Entero autoincremental | Identificador único de la postulación |
| `titulo` | Texto | Nombre del puesto de trabajo |
| `empresa` | Texto | Nombre de la empresa |
| `ubicacion` | Texto | Ciudad, país o "Remoto" |
| `modalidad` | Texto | Remoto / Híbrido / Presencial |
| `turno` | Texto | Tiempo completo / Medio tiempo / Por proyecto |
| `nivel_experiencia` | Texto | Junior / Mid / Senior / No especificado |
| `salario` | Texto | Rango salarial si está disponible, vacío si no |
| `tecnologias` | Texto | Skills o tecnologías mencionadas (separadas por coma) |
| `descripcion_corta` | Texto | Primeros ~300 caracteres de la descripción |
| `url_vacante` | Texto | El link original que proporcionó el usuario |
| `plataforma` | Texto | LinkedIn / Glassdoor / Indeed / Otro |
| `fecha_publicacion` | Fecha | Fecha en que la empresa publicó la vacante |
| `fecha_postulacion` | Fecha | Fecha en que el usuario guardó el registro (automática: hoy) |
| `respondio` | Booleano | False por defecto; el usuario lo cambia manualmente |
| `notas` | Texto | Campo libre para comentarios del usuario |

**Reglas del esquema:**
- El campo `fecha_postulacion` se asigna automáticamente al momento de guardar. El usuario no lo edita.
- El campo `respondio` comienza en `False` siempre. El usuario lo actualiza desde la tabla de la UI.
- Todos los campos de texto pueden quedar vacíos si el scraper no los encontró.
- El `id` se genera como `max(id_existentes) + 1` al insertar un nuevo registro.

---

## 5. Flujo de Uso — Paso a Paso

```
[Usuario pega una URL en Streamlit]
        │
        ▼
[agent.py detecta la plataforma por dominio]
        │
        ▼
[Playwright abre la URL con el navegador del usuario]
        │
        ▼
[El parser correspondiente extrae los campos del DOM]
  (linkedin.py / glassdoor.py / generic.py)
        │
        ▼
[Streamlit muestra un formulario pre-llenado con los datos extraídos]
[El usuario puede editar cualquier campo antes de guardar]
        │
        ▼
[excel_handler.py guarda el registro en jobflow.xlsx]
        │
        ▼
[La tabla de registros se actualiza en pantalla]
        │
        ▼
[El usuario puede marcar "respondió" desde la tabla en cualquier momento]
        │
        ▼
[El dashboard (charts/dashboard.py) muestra estadísticas actualizadas]
```

---

## 6. Comportamiento del Agente de Scraping

- Playwright debe ejecutarse en modo **no-headless** (`headless=False`) para aprovechar la sesión real del usuario.
- El agente **no hace login automático**. Asume que el usuario ya tiene sesión abierta en su navegador.
- El agente usa el **perfil de usuario del navegador por defecto** del sistema para heredar cookies y sesiones.
- El timeout máximo de espera por página es **15 segundos**.
- Si el scraper no puede extraer un campo, lo deja vacío (no lanza error).
- El parser genérico (`generic.py`) es el fallback cuando la URL no pertenece a LinkedIn ni Glassdoor.

---

## 7. Comportamiento de la UI (Streamlit)

La aplicación tiene **tres secciones principales** en la barra lateral:

1. **➕ Nueva postulación** — Input de URL + formulario de confirmación/edición.
2. **📋 Mis postulaciones** — Tabla editable con todos los registros. Permite marcar `respondio`.
3. **📊 Dashboard** — Gráficas de estadísticas (respondidas vs. no respondidas, por plataforma, por mes).

**Reglas de UI:**
- No se usan formularios HTML nativos. Se usan los widgets de Streamlit (`st.text_input`, `st.selectbox`, `st.checkbox`, etc.).
- La tabla de postulaciones usa `st.data_editor` para permitir edición inline del campo `respondio` y `notas`.
- Los mensajes de éxito/error usan `st.success()` / `st.error()` de Streamlit.

---

## 8. Restricciones y Reglas para el Agente

| Regla | Descripción |
|---|---|
| ❌ No nuevas librerías | No agregar ninguna dependencia fuera del `requirements.txt` definido |
| ❌ No base de datos | No usar SQLite, PostgreSQL, MongoDB ni ningún ORM |
| ❌ No CSV | El almacenamiento es exclusivamente `.xlsx` con openpyxl |
| ❌ No frontend externo | No crear archivos HTML, JS o CSS separados. Todo en Streamlit |
| ❌ No login automático | El scraper no maneja credenciales ni formularios de login |
| ✅ Un archivo de datos | Siempre un único `data/jobflow.xlsx` con una única hoja |
| ✅ Modularidad | Cada responsabilidad en su módulo correspondiente según la estructura |
| ✅ Preguntar antes de cambiar | Si el agente considera necesario algo no definido aquí, pregunta primero |

---

## 9. Comandos de Instalación y Ejecución

```bash
# 1. Clonar o crear el proyecto
cd jobflow

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar navegadores de Playwright
playwright install chromium

# 5. Ejecutar la aplicación
streamlit run app.py
```

---

## 10. Contexto de Desarrollo

- **Desarrollador:** Usuario único (aplicación personal)
- **Entorno objetivo:** Windows / macOS / Linux (escritorio local)
- **Idioma de la UI:** Español
- **Idioma del código:** Inglés (nombres de variables, funciones, comentarios)
- **Idioma de este documento:** Español

---

*Versión del contexto: 1.0 — Referencia base para todo el desarrollo de JobFlow.*
