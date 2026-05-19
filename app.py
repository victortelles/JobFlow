import streamlit as st
import pandas as pd
import datetime

# Import project modules
from storage import load_data, save_data, add_postulacion
from scraper import scrape_job, run_manual_login, check_session_status
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
    
    /* Sidebar Login Button (Solid Blue) */
    div[data-testid="stSidebar"] div.stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background: #1d4ed8 !important;
        transform: scale(1.02) !important;
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
if 'parsed_job' not in st.session_state:
    st.session_state['parsed_job'] = None
if 'scraped_url' not in st.session_state:
    st.session_state['scraped_url'] = ""
if 'session_checked' not in st.session_state:
    st.session_state['session_checked'] = False
if 'linkedin_active' not in st.session_state:
    st.session_state['linkedin_active'] = False
if 'indeed_active' not in st.session_state:
    st.session_state['indeed_active'] = False

# ----------------- NAVIGATION (SIDEBAR) -----------------
with st.sidebar:
    # Render Sidebar Logo Image
    st.image("public/JobFlow.png", use_container_width=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin-top: -0.5rem;'>Gestor Local de Postulaciones</p>", unsafe_allow_html=True)
    st.write("---")
    
    menu = st.radio(
        "Navegación",
        ["➕ Nueva postulación", "📋 Mis postulaciones", "📊 Dashboard"],
        index=0
    )
    
    st.write("---")
    
    # --- SESSION STATUS & MANUAL LOGIN ---
    st.markdown("<p style='font-size: 0.95rem; font-weight: 600; color: #06b6d4; margin-bottom: 0.5rem;'>🔑 Estado de Sesiones</p>", unsafe_allow_html=True)
    
    li_status = "🟢 Activo" if st.session_state['linkedin_active'] else ("🔴 Inactivo" if st.session_state['session_checked'] else "⏳ Sin verificar")
    ind_status = "🟢 Activo" if st.session_state['indeed_active'] else ("🔴 Inactivo" if st.session_state['session_checked'] else "⏳ Sin verificar")
    
    st.markdown(f"""
    <div style='background: rgba(30, 41, 59, 0.4); padding: 0.75rem; border-radius: 8px; border: 1px solid #1e293b; font-size: 0.8rem; margin-bottom: 0.8rem;'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
            <span>LinkedIn:</span> <strong style='color: {"#10b981" if st.session_state["linkedin_active"] else ("#f43f5e" if st.session_state["session_checked"] else "#94a3b8")};'>{li_status}</strong>
        </div>
        <div style='display: flex; justify-content: space-between;'>
            <span>Indeed:</span> <strong style='color: {"#10b981" if st.session_state["indeed_active"] else ("#f43f5e" if st.session_state["session_checked"] else "#94a3b8")};'>{ind_status}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- ACTIONS: VERIFICATION & CONDITIONAL MANUAL LOGIN ---
    if st.button("🔍 Verificar Estado", key="btn_verify_sessions", use_container_width=True):
        with st.spinner("Comprobando..."):
            try:
                res = check_session_status()
                st.session_state['linkedin_active'] = res['linkedin']
                st.session_state['indeed_active'] = res['indeed']
                st.session_state['session_checked'] = True
                st.rerun()
            except Exception as e:
                st.error("Error al verificar. Cierra otras ventanas de Chrome de JobFlow.")
                
    if st.session_state['session_checked']:
        has_inactive = not st.session_state['linkedin_active'] or not st.session_state['indeed_active']
        
        if has_inactive:
            inactive_services = []
            if not st.session_state['linkedin_active']:
                inactive_services.append("LinkedIn")
            if not st.session_state['indeed_active']:
                inactive_services.append("Indeed")
                
            services_str = " e ".join(inactive_services)
            
            # Informative warning message
            st.markdown(f"""
            <div style='background: rgba(244, 63, 94, 0.12); padding: 0.8rem; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.25); font-size: 0.8rem; color: #fda4af; margin-top: 0.8rem; margin-bottom: 0.8rem;'>
                <strong>⚠️ Sesión inactiva en {services_str}:</strong><br>
                Inicia sesión manualmente para heredar las credenciales correctas a Playwright.
            </div>
            """, unsafe_allow_html=True)
            
            # Show manual login button stacked vertically
            if st.button("🌐 Iniciar Sesión Manual", key="btn_manual_login", use_container_width=True):
                with st.spinner("Abriendo Chrome..."):
                    try:
                        run_manual_login()
                        # Auto-check after manual login
                        res = check_session_status()
                        st.session_state['linkedin_active'] = res['linkedin']
                        st.session_state['indeed_active'] = res['indeed']
                        st.session_state['session_checked'] = True
                        st.rerun()
                    except Exception as e:
                        st.error("Error al abrir Chrome. Cierra otras ventanas de JobFlow.")
        else:
            # Both active - Success Card
            st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.12); padding: 0.8rem; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.25); font-size: 0.8rem; color: #a7f3d0; margin-top: 0.8rem; margin-bottom: 0.8rem; text-align: center;'>
                <strong>🟢 ¡Sesiones Activas!</strong><br>
                Todo listo para la extracción de vacantes.
            </div>
            """, unsafe_allow_html=True)
            
                    
    # --- FOOTER / DEVELOPER CREDITS ---
    st.markdown("""
    <div style='margin-top: 2rem; text-align: center;'>
        <hr style='border-color: #1e293b; margin-bottom: 1rem;' />
        <p style='font-size: 0.75rem; color: #64748b; margin: 0;'>Desarrollado por</p>
        <a href='https://github.com/AHTyler' target='_blank' style='color: #06b6d4; text-decoration: none; font-weight: 600; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 6px;'>
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="1.1em" width="1.1em" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>
            AHTyler
        </a>
    </div>
    """, unsafe_allow_html=True)

# ----------------- APP HEADER -----------------
col_logo_left, col_logo_center, col_logo_right = st.columns([1, 1.2, 1])
with col_logo_center:
    st.image("public/JobFlow.png", use_container_width=True)
st.markdown("<div class='app-subtitle' style='margin-top: -1rem;'>Seguimiento inteligente y automático de tu búsqueda de empleo</div>", unsafe_allow_html=True)

# ----------------- VIEW 1: NUEVA POSTULACIÓN -----------------
if menu == "➕ Nueva postulación":
    st.markdown("<div class='section-header'>➕ Registrar Nueva Postulación</div>", unsafe_allow_html=True)
    
    # 1. Extraction Section
    st.markdown("##### Pegar enlace de la vacante")
    col_input, col_plat, col_btn = st.columns([3, 1.2, 0.8])
    
    with col_input:
        url_input = st.text_input(
            "URL de la vacante", 
            placeholder="Pega la URL de LinkedIn, Indeed o cualquier otra web de empleo...",
            label_visibility="collapsed",
            key="url_input"
        )
    with col_plat:
        platform_override_link = st.selectbox(
            "Plantilla / Plataforma:",
            ["Auto-detectar", "LinkedIn", "Indeed", "Otro"],
            key="link_platform_override",
            label_visibility="collapsed"
        )
    with col_btn:
        extract_clicked = st.button("🔍 Analizar Enlace", key="btn_extract_link", width="stretch")
        
    if extract_clicked:
        if not url_input.strip():
            st.error("Por favor, ingresa una URL válida.")
        else:
            with st.spinner("Abriendo navegador local (Playwright) y extrayendo detalles..."):
                scraped_data = scrape_job(url_input, platform_override=platform_override_link)
                st.session_state['parsed_job'] = scraped_data
                st.session_state['scraped_url'] = url_input
                st.success("¡Enlace analizado! Por favor verifica y edita la información abajo antes de guardar.")

    st.write("---")
    
    # 2. Form Section
    if st.session_state['parsed_job'] is not None:
        job_data = st.session_state['parsed_job']
        
        # --- DUPLICATE CHECKER ---
        df_existing = load_data()
        is_duplicate = False
        duplicate_id = None
        duplicate_date = None
        
        target_title = job_data.get('titulo', '').strip().lower()
        target_company = job_data.get('empresa', '').strip().lower()
        target_url = job_data.get('url_vacante', '').strip()
        
        if not df_existing.empty and target_title and target_company:
            matches = df_existing[
                (df_existing['titulo'].str.strip().str.lower() == target_title) &
                (df_existing['empresa'].str.strip().str.lower() == target_company)
            ]
            
            if not matches.empty:
                is_duplicate = True
                duplicate_row = matches.iloc[0]
                duplicate_id = duplicate_row['id']
                duplicate_date = duplicate_row['fecha_postulacion']
            elif target_url and target_url != "Texto Pegado Manualmente" and target_url != "":
                url_matches = df_existing[df_existing['url_vacante'] == target_url]
                if not url_matches.empty:
                    is_duplicate = True
                    duplicate_row = url_matches.iloc[0]
                    duplicate_id = duplicate_row['id']
                    duplicate_date = duplicate_row['fecha_postulacion']
                    
        if is_duplicate:
            st.warning(
                f"⚠️ **¡Alerta de Vacante Duplicada!** Ya tienes registrada esta postulación en tu historial:\n\n"
                f"*   **Puesto**: {job_data.get('titulo')}\n"
                f"*   **Empresa**: {job_data.get('empresa')}\n"
                f"*   **ID en Registro**: {duplicate_id}\n"
                f"*   **Fecha de Registro**: {duplicate_date}\n\n"
                f"Puedes guardarlo de todas formas si es un puesto diferente o actualizar tus notas desde **📋 Mis postulaciones**."
            )
        else:
            st.info("✨ ¡Nueva vacante detectada! Confirma y edita la información abajo para guardarla.")
            
        st.markdown("##### 📝 Confirmar y Editar Detalles de la Vacante")
        
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
                turns = ["Tiempo completo", "Medio tiempo", "Por tiempo indeterminado", "Por proyecto", "Prácticas", "No especificado"]
                current_turn = job_data.get('turno', 'No especificado')
                turn_idx = turns.index(current_turn) if current_turn in turns else 5
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
            width="stretch"
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
            st.plotly_chart(get_response_rate_chart(df), width="stretch")
        with row1_col2:
            # Let the user choose grouping between Weeks and Months
            group_by = st.selectbox("Agrupar postulaciones por:", ["Semanas", "Meses"], index=0, key="group_by_chart")
            group_param = "Semana" if group_by == "Semanas" else "Mes"
            st.plotly_chart(get_applications_over_time_chart(df, group_by=group_param), width="stretch")
            
        st.write("---")
        
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(get_platform_distribution_chart(df), width="stretch")
        with row2_col2:
            st.plotly_chart(get_top_skills_chart(df), width="stretch")
