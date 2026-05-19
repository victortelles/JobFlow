# Cómo Contribuir a JobFlow

¡Gracias por tu interés en contribuir a **JobFlow**! 🚀

JobFlow es una herramienta personal y local para llevar el control de tus postulaciones de trabajo. Actualmente, soportamos la extracción automática de datos desde plataformas como **LinkedIn** e **Indeed**, pero existen muchísimas más bolsas de trabajo (Glassdoor, CompuTrabajo, OCC, etc.).

¡Cualquier usuario es bienvenido a contribuir agregando soporte para nuevas plataformas!

---

## 🛠️ ¿Cómo agregar un nuevo Scraper (Parser)?

Toda la lógica de extracción de datos vive en la carpeta `scraper/parsers/`. El objetivo de un parser es tomar el contenido HTML o el DOM de la página (ya cargado por Playwright) y extraer la información estructurada de la vacante.

### Pasos para crear tu propio Parser

1. **Crea un nuevo archivo para la plataforma**
   Dentro de `scraper/parsers/`, crea un archivo con el nombre de la plataforma, por ejemplo: `glassdoor.py` o `computrabajo.py`.

2. **Define la estructura esperada**
   Tu parser debe extraer la mayor cantidad de información posible y devolver un diccionario (`dict`) con las siguientes claves (basadas en el esquema de datos):
   
   ```python
   {
       "titulo": "",              # Nombre del puesto
       "empresa": "",             # Nombre de la empresa
       "ubicacion": "",           # Ciudad, país o "Remoto"
       "modalidad": "",           # Remoto / Híbrido / Presencial
       "turno": "",               # Tiempo completo / Medio tiempo, etc.
       "nivel_experiencia": "",   # Junior / Mid / Senior
       "salario": "",             # Rango salarial
       "tecnologias": "",         # Skills o tecnologías extraídas
       "descripcion_corta": "",   # Primeros ~300 caracteres de la descripción
       "plataforma": "Nombre"     # Ejemplo: "Glassdoor", "CompuTrabajo"
   }
   ```
   > **Nota:** Si un dato no existe en la página, simplemente devuélvelo como un string vacío `""`. No lances un error.

3. **Usa Playwright (no BeautifulSoup ni requests)**
   Nuestra aplicación ya utiliza Playwright en la capa de `scraper/agent.py` para abrir la página usando tu sesión local (`headless=False`). Tu parser solo recibirá la página ya cargada (`page` object de Playwright) o su contenido.
   Asegúrate de usar los métodos de Playwright (ej. `page.locator()`, `page.text_content()`) para obtener la información.

4. **Ejemplo de Plantilla (Template) para un Parser**

   ```python
   # scraper/parsers/nueva_plataforma.py

   def parse_vacante(page):
       """
       Extrae los datos de una vacante de [Nombre de Plataforma].
       :param page: Objeto 'page' de Playwright con la URL ya cargada.
       :return: Diccionario con los datos extraídos.
       """
       datos = {
           "titulo": "",
           "empresa": "",
           "ubicacion": "",
           "modalidad": "",
           "turno": "",
           "nivel_experiencia": "",
           "salario": "",
           "tecnologias": "",
           "descripcion_corta": "",
           "plataforma": "Nueva Plataforma"
       }

       try:
           # Ejemplo de extracción del título
           if page.locator("h1.titulo-vacante").is_visible():
               datos["titulo"] = page.locator("h1.titulo-vacante").text_content().strip()

           # Ejemplo de extracción de la empresa
           if page.locator(".nombre-empresa").is_visible():
               datos["empresa"] = page.locator(".nombre-empresa").text_content().strip()

           # Agrega aquí la lógica para el resto de los campos...

       except Exception as e:
           print(f"Error parseando en Nueva Plataforma: {e}")

       return datos
   ```

5. **Integra tu parser en el Agente**
   Abre el archivo `scraper/agent.py` (o donde esté el enrutador de parsers) y asegúrate de agregar una condición para que, si la URL coincide con tu nueva plataforma, se mande llamar a tu función `parse_vacante`.

   ```python
   if "glassdoor" in url:
       from .parsers.glassdoor import parse_vacante
       return parse_vacante(page)
   ```

---

## 🛑 Reglas Importantes antes de hacer tu Pull Request

Por favor, revisa el archivo [JOBFLOW_CONTEXT.md](agents/JOBFLOW_CONTEXT.md) para entender las reglas del proyecto. Las más importantes son:

1. **No agregues nuevas librerías:** Solo usamos las que están en `requirements.txt` (Streamlit, Playwright, openpyxl, pandas, plotly). No agregues *Selenium*, *Scrapy*, *BeautifulSoup* ni *requests*.
2. **Sin bases de datos:** Todo se guarda localmente en `jobflow.xlsx`.
3. **No cambies el modo headless:** Playwright siempre debe correr con `headless=False` para aprovechar la sesión del navegador del usuario.

## ✅ Cómo enviar tu contribución

1. Haz un *Fork* del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/scraper-glassdoor`).
3. Prueba tu scraper con al menos 3 links diferentes de la plataforma.
4. Haz commit de tus cambios (`git commit -m 'feat: agrega scraper para Glassdoor'`).
5. Sube tus cambios a tu fork (`git push origin feature/scraper-glassdoor`).
6. Abre un **Pull Request** utilizando nuestro [Template de Pull Request](pull_request.md).

¡Gracias por ayudar a hacer JobFlow una herramienta más poderosa para todos!
