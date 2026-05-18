import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Elegant Color Palette (Blue and Cyan)
COLOR_RESPONDED = "#06b6d4"  # Cyan
COLOR_NO_RESPONSE = "#2563eb"  # Royal Blue
PALETTE_PLATFORMS = ["#2563eb", "#3b82f6", "#06b6d4", "#0891b2", "#1d4ed8"]

def get_response_rate_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a Pie Chart representing the response rate of job applications.
    """
    if df.empty:
        # Return empty placeholder figure
        fig = go.Figure()
        fig.update_layout(
            title="Sin datos disponibles",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
        
    counts = df['respondio'].value_counts()
    
    # Map Boolean keys to Spanish readable labels
    labels = {True: "Respondidas", False: "Sin Respuesta"}
    df_counts = pd.DataFrame({
        'Estado': [labels.get(k, str(k)) for k in counts.index],
        'Cantidad': counts.values
    })
    
    fig = px.pie(
        df_counts,
        names='Estado',
        values='Cantidad',
        title="Tasa de Respuesta",
        color='Estado',
        color_discrete_map={
            "Respondidas": COLOR_RESPONDED,
            "Sin Respuesta": COLOR_NO_RESPONSE
        },
        hole=0.4
    )
    
    fig.update_traces(textinfo='percent+value', textposition='inside')
    fig.update_layout(
        margin=dict(t=50, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3f4f6")
    )
    return fig

def get_applications_over_time_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a Bar/Line Chart showing the number of job applications submitted over time.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos disponibles", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
        
    # Standardize fecha_postulacion to date type
    df_dates = df.copy()
    df_dates['fecha_postulacion'] = pd.to_datetime(df_dates['fecha_postulacion']).dt.date
    
    # Group by date
    timeline = df_dates.groupby('fecha_postulacion').size().reset_index(name='Postulaciones')
    timeline = timeline.sort_values('fecha_postulacion')
    
    fig = px.bar(
        timeline,
        x='fecha_postulacion',
        y='Postulaciones',
        title="Postulaciones por Día",
        labels={'fecha_postulacion': 'Fecha', 'Postulaciones': 'Cantidad'}
    )
    
    fig.update_traces(marker_color="#3b82f6", marker_line_color="#1d4ed8", marker_line_width=1.5, opacity=0.85)
    fig.update_layout(
        margin=dict(t=50, b=10, l=10, r=10),
        xaxis_tickformat='%Y-%m-%d',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3f4f6"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#374151")
    )
    return fig

def get_platform_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generates a horizontal Bar Chart showing the distribution of platforms of the vacancies.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos disponibles", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
        
    # Count by platform
    counts = df['plataforma'].value_counts().reset_index(name='Cantidad')
    counts.rename(columns={'index': 'Plataforma'}, inplace=True)
    
    fig = px.bar(
        counts,
        x='Cantidad',
        y='plataforma',
        orientation='h',
        title="Postulaciones por Plataforma",
        labels={'Cantidad': 'Cantidad', 'plataforma': 'Plataforma'},
        color='plataforma',
        color_discrete_sequence=PALETTE_PLATFORMS
    )
    
    fig.update_layout(
        margin=dict(t=50, b=10, l=10, r=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3f4f6"),
        xaxis=dict(showgrid=True, gridcolor="#374151"),
        yaxis=dict(showgrid=False)
    )
    return fig

def get_top_skills_chart(df: pd.DataFrame) -> go.Figure:
    """
    Parses the technologies column and plots the top 10 most common skills.
    """
    if df.empty or 'tecnologias' not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Sin datos disponibles", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
        
    # Split all skills
    all_skills = []
    for entry in df['tecnologias'].dropna():
        if isinstance(entry, str) and entry.strip():
            skills = [s.strip() for s in entry.split(',') if s.strip()]
            all_skills.extend(skills)
            
    if not all_skills:
        fig = go.Figure()
        fig.update_layout(title="Sin tecnologías detectadas aún", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
        
    # Count frequencies
    counter = Counter(all_skills)
    top_10 = counter.most_common(10)
    
    df_skills = pd.DataFrame(top_10, columns=['Tecnología', 'Frecuencia'])
    # Sort for horizontal bar chart
    df_skills = df_skills.sort_values('Frecuencia', ascending=True)
    
    fig = px.bar(
        df_skills,
        x='Frecuencia',
        y='Tecnología',
        orientation='h',
        title="Top 10 Tecnologías Más Requeridas",
        labels={'Frecuencia': 'Vacantes', 'Tecnología': 'Tecnología'}
    )
    
    fig.update_traces(marker_color="#06b6d4", marker_line_color="#0891b2", marker_line_width=1.5, opacity=0.85)
    fig.update_layout(
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3f4f6"),
        xaxis=dict(showgrid=True, gridcolor="#374151", dtick=1),
        yaxis=dict(showgrid=False)
    )
    return fig
