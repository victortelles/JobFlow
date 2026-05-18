import streamlit as st
import pandas as pd
import datetime

# Import project modules
from storage import load_data, save_data, add_postulacion
from scraper import scrape_job
from charts import (
    get_response_rate_chart,
    get_applications_over_time_chart,
    get_platform_distribution_chart,
    get_top_skills_chart
)

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="JobFlow — Gestor de Postulaciones",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM STYLE INJECTION (Rich Aesthetics) -----------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Global Background and Style */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #0f2537 100%);
        color: #f3f4f6;
    }
    
    /* Custom Headers */
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .app-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    /* Modern Card Component */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(6, 182, 212, 0.4);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #93c5fd 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-lbl {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Styled Sub-headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #f8fafc;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Buttons Customization */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45) !important;
    }
    
    /* Secondary/Submit Buttons */
    .stForm div.stButton > button {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
if 'parsed_job' not in st.session_state:
    st.session_state['parsed_job'] = None
if 'scraped_url' not in st.session_state:
    st.session_state['scraped_url'] = ""

# ----------------- NAVIGATION (SIDEBAR) -----------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #06b6d4;'>💼 JobFlow</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>Gestor Local de Postulaciones</p>", unsafe_allow_html=True)
    st.write("---")
    
    menu = st.radio(
        "Navegación",
        ["➕ Nueva postulación", "📋 Mis postulaciones", "📊 Dashboard"],
        index=0
    )
    
    st.write("---")
    st.markdown("""
    <div style='background: rgba(30,41,59,0.5); padding: 1rem; border-radius: 8px; border: 1px solid #334155; font-size: 0.8rem; color: #94a3b8;'>
        <strong>💡 Tip de Uso:</strong><br>
        Asegúrate de tener iniciada sesión en tu navegador normal para que Playwright herede tus cookies de LinkedIn/Glassdoor sin captchas.
    </div>
    """, unsafe_allow_html=True)

# ----------------- APP HEADER -----------------
st.markdown("<div class='app-title'>JobFlow</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Seguimiento inteligente y automático de tu búsqueda de empleo</div>", unsafe_allow_html=True)

# ----------------- VIEW 1: NUEVA POSTULACIÓN -----------------
if menu == "➕ Nueva postulación":
    st.markdown("<div class='section-header'>➕ Registrar Nueva Postulación</div>", unsafe_allow_html=True)
    
    # 1. Scraping Section
    st.markdown("##### 🔗 Pegar enlace de la vacante")
    col_input, col_btn = st.columns([4, 1])
    
    with col_input:
        url_input = st.text_input(
            "URL de la vacante", 
            placeholder="Pega la URL de LinkedIn, Glassdoor, Indeed o cualquier otra web de empleo...",
            label_visibility="collapsed"
        )
    with col_btn:
        extract_clicked = st.button("🔍 Analizar Vacante")
        
    if extract_clicked:
        if not url_input.strip():
            st.error("Por favor, ingresa una URL válida.")
        else:
            with st.spinner("Abriendo navegador local (Playwright) y extrayendo detalles..."):
                scraped_data = scrape_job(url_input)
                st.session_state['parsed_job'] = scraped_data
                st.session_state['scraped_url'] = url_input
                st.success("¡Datos extraídos! Por favor verifica y edita la información abajo antes de guardar.")

    st.write("---")
    
    # 2. Form Section
    if st.session_state['parsed_job'] is not None:
        st.markdown("##### 📝 Confirmar y Editar Detalles de la Vacante")
        
        job_data = st.session_state['parsed_job']
        
        with st.form("job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Título del Puesto*", value=job_data.get('titulo', ''))
                company = st.text_input("Empresa*", value=job_data.get('empresa', ''))
                location = st.text_input("Ubicación", value=job_data.get('ubicacion', ''))
                
                modalities = ["Remoto", "Híbrido", "Presencial", "No especificada"]
                current_modal = job_data.get('modalidad', 'No especificada')
                modal_idx = modalities.index(current_modal) if current_modal in modalities else 3
                modality = st.selectbox("Modalidad", modalities, index=modal_idx)
                
            with col2:
                turns = ["Tiempo completo", "Medio tiempo", "Por proyecto", "No especificado"]
                current_turn = job_data.get('turno', 'No especificado')
                turn_idx = turns.index(current_turn) if current_turn in turns else 3
                turn = st.selectbox("Turno / Tipo de Contrato", turns, index=turn_idx)
                
                exp_levels = ["Junior", "Mid", "Senior", "No especificado"]
                current_exp = job_data.get('nivel_experiencia', 'No especificado')
                exp_idx = exp_levels.index(current_exp) if current_exp in exp_levels else 3
                experience = st.selectbox("Nivel de Experiencia", exp_levels, index=exp_idx)
                
                salary = st.text_input("Rango Salarial", value=job_data.get('salario', ''))
                
                # Format or resolve Date
                pub_date_raw = job_data.get('fecha_publicacion', '')
                try:
                    if isinstance(pub_date_raw, str) and pub_date_raw:
                        pub_date = datetime.datetime.strptime(pub_date_raw[:10], "%Y-%m-%d").date()
                    elif isinstance(pub_date_raw, datetime.date):
                        pub_date = pub_date_raw
                    else:
                        pub_date = datetime.date.today()
                except Exception:
                    pub_date = datetime.date.today()
                    
                publication_date = st.date_input("Fecha de Publicación", value=pub_date)
                
            # Full width fields
            technologies = st.text_area(
                "Tecnologías / Habilidades Requeridas (separadas por comas)", 
                value=job_data.get('tecnologias', ''),
                help="Ejemplo: Python, React, SQL, AWS"
            )
            
            description = st.text_area(
                "Descripción Corta (Extracto)", 
                value=job_data.get('descripcion_corta', ''),
                max_chars=500
            )
            
            notes = st.text_area(
                "Notas Personales / Comentarios adicionales", 
                value=job_data.get('notas', ''),
                placeholder="Preguntas preparadas, nombre del reclutador, etc."
            )
            
            st.markdown("<p style='color:#ef4444; font-size:0.85rem;'>* Campos obligatorios</p>", unsafe_allow_html=True)
            
            # Submit button
            submit_btn = st.form_submit_button("💾 Guardar en Registro Local")
            
            if submit_btn:
                if not title.strip() or not company.strip():
                    st.error("El Título del Puesto y la Empresa son obligatorios.")
                else:
                    new_job = {
                        'titulo': title.strip(),
                        'empresa': company.strip(),
                        'ubicacion': location.strip(),
                        'modalidad': modality,
                        'turno': turn,
                        'nivel_experiencia': experience,
                        'salario': salary.strip(),
                        'tecnologias': technologies.strip(),
                        'descripcion_corta': description.strip(),
                        'url_vacante': st.session_state['scraped_url'],
                        'plataforma': job_data.get('plataforma', 'Otro'),
                        'fecha_publicacion': publication_date,
                        'notas': notes.strip()
                    }
                    try:
                        new_id = add_postulacion(new_job)
                        st.success(f"🎉 ¡Postulación de '{title}' en {company} guardada con ID: {new_id}!")
                        # Reset state
                        st.session_state['parsed_job'] = None
                        st.session_state['scraped_url'] = ""
                    except Exception as e:
                        st.error(f"Error al guardar la postulación: {e}")

# ----------------- VIEW 2: MIS POSTULACIONES -----------------
elif menu == "📋 Mis postulaciones":
    st.markdown("<div class='section-header'>📋 Registro Completo de Postulaciones</div>", unsafe_allow_html=True)
    
    # Load DataFrame
    df = load_data()
    
    if df.empty:
        st.info("Aún no has registrado ninguna postulación. ¡Dirígete a 'Nueva postulación' para agregar la primera!")
    else:
        st.markdown("""
        <p style='color:#94a3b8;'>
            En esta tabla puedes editar directamente si la empresa te <b>respondió</b> o actualizar tus <b>notas</b>. 
            Haz doble clic en una casilla para editarla y luego haz clic en el botón <b>Guardar Cambios</b> abajo.
        </p>
        """, unsafe_allow_html=True)
        
        # Configure st.data_editor to disable other columns for security
        disabled_cols = [col for col in df.columns if col not in ['respondio', 'notas']]
        
        # We also want to configure columns format
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
                "titulo": st.column_config.TextColumn("Puesto", disabled=True),
                "empresa": st.column_config.TextColumn("Empresa", disabled=True),
                "ubicacion": st.column_config.TextColumn("Ubicación", disabled=True),
                "modalidad": st.column_config.TextColumn("Modalidad", disabled=True),
                "turno": st.column_config.TextColumn("Turno", disabled=True),
                "nivel_experiencia": st.column_config.TextColumn("Experiencia", disabled=True),
                "salario": st.column_config.TextColumn("Salario", disabled=True),
                "tecnologias": st.column_config.TextColumn("Tecnologías", disabled=True),
                "descripcion_corta": st.column_config.TextColumn("Descripción", disabled=True),
                "url_vacante": st.column_config.LinkColumn("Enlace", disabled=True),
                "plataforma": st.column_config.TextColumn("Plataforma", disabled=True),
                "fecha_publicacion": st.column_config.DateColumn("Publicado", disabled=True, format="YYYY-MM-DD"),
                "fecha_postulacion": st.column_config.DateColumn("Postulado", disabled=True, format="YYYY-MM-DD"),
                "respondio": st.column_config.CheckboxColumn("¿Respuesta?", default=False),
                "notas": st.column_config.TextColumn("Notas Personales")
            },
            disabled=disabled_cols,
            hide_index=True,
            use_container_width=True
        )
        
        col_space, col_save = st.columns([4, 1])
        with col_save:
            save_clicked = st.button("💾 Guardar Cambios")
            
        if save_clicked:
            try:
                save_data(edited_df)
                st.success("¡Cambios guardados con éxito en jobflow.xlsx!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar los cambios: {e}")

# ----------------- VIEW 3: DASHBOARD -----------------
else:
    st.markdown("<div class='section-header'>📊 Dashboard y Estadísticas</div>", unsafe_allow_html=True)
    
    # Load DataFrame
    df = load_data()
    
    if df.empty:
        st.info("No hay datos disponibles para mostrar estadísticas. ¡Agrega postulaciones primero!")
    else:
        # Calculate KPI Values
        total_postulaciones = len(df)
        respuestas = df['respondio'].sum()
        sin_respuesta = total_postulaciones - respuestas
        tasa_respuesta = (respuestas / total_postulaciones * 100) if total_postulaciones > 0 else 0.0
        
        # Display KPI Grid
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-val' style='background: linear-gradient(135deg, #93c5fd 0%, #3b82f6 100%); -webkit-background-clip: text;'>{total_postulaciones}</div>
                <div class='metric-lbl'>Total Postulaciones</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-val' style='background: linear-gradient(135deg, #67e8f9 0%, #06b6d4 100%); -webkit-background-clip: text;'>{respuestas}</div>
                <div class='metric-lbl'>Respuestas Recibidas</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-val' style='background: linear-gradient(135deg, #93c5fd 0%, #2563eb 100%); -webkit-background-clip: text;'>{sin_respuesta}</div>
                <div class='metric-lbl'>Pendientes de Respuesta</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-val' style='background: linear-gradient(135deg, #38bdf8 0%, #0369a1 100%); -webkit-background-clip: text;'>{tasa_respuesta:.1f}%</div>
                <div class='metric-lbl'>Tasa de Respuesta</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        
        # Display Charts in grid
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(get_response_rate_chart(df), use_container_width=True)
        with row1_col2:
            st.plotly_chart(get_applications_over_time_chart(df), use_container_width=True)
            
        st.write("---")
        
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(get_platform_distribution_chart(df), use_container_width=True)
        with row2_col2:
            st.plotly_chart(get_top_skills_chart(df), use_container_width=True)
