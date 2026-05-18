import re
from .generic import parse_json_ld, clean_html, detect_technologies

def parse(html_content: str, url: str) -> dict:
    """
    LinkedIn specific parser.
    Attempts JSON-LD first (which is very common in public and private LinkedIn views),
    then falls back to specific HTML selector heuristics.
    """
    # 1. Try JSON-LD first
    data = parse_json_ld(html_content)
    
    # 2. Extract values using HTML selectors if JSON-LD is missing fields
    if not data.get('titulo'):
        # Try to find class based title patterns
        # Public: .top-card-layout__title, .topcard__title
        # Premium/Logged in: .jobs-unified-top-card__job-title, .job-details-jobs-unified-top-card__job-title
        title_patterns = [
            r'class="[^"]*(?:top-card-layout__title|topcard__title|jobs-unified-top-card__job-title|job-details-jobs-unified-top-card__job-title)[^"]*"[^>]*>\s*(.*?)\s*</',
            r'<h1[^>]*class="[^"]*t-24[^"]*"[^>]*>\s*(.*?)\s*</h1>'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                data['titulo'] = clean_html(match.group(1))
                break
                
    if not data.get('empresa'):
        company_patterns = [
            r'class="[^"]*(?:topcard__flavor|top-card-normal-creator__name|jobs-unified-top-card__company-name|job-details-jobs-unified-top-card__company-name)[^"]*"[^>]*>\s*(.*?)\s*</',
            r'<a[^>]*href="[^"]*/company/[^"]*"[^>]*>\s*(.*?)\s*</a>'
        ]
        for pattern in company_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                data['empresa'] = clean_html(match.group(1))
                break
                
    if not data.get('ubicacion'):
        location_patterns = [
            r'class="[^"]*(?:topcard__flavor--bullet|top-card-layout__first-subline|jobs-unified-top-card__bullet|job-details-jobs-unified-top-card__bullet)[^"]*"[^>]*>\s*(.*?)\s*</',
            r'class="[^"]*(?:topcard__flavor--bullet|jobs-unified-top-card__bullet)[^"]*"[^>]*>\s*(.*?)\s*</'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                data['ubicacion'] = clean_html(match.group(1))
                break

    if not data.get('descripcion_corta'):
        desc_patterns = [
            r'id="job-details"[^>]*>\s*(.*?)\s*</div>',
            r'class="[^"]*(?:jobs-box__html-content|description__text)[^"]*"[^>]*>\s*(.*?)\s*</div>'
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                data['descripcion_corta'] = clean_html(match.group(1))[:300]
                break

    # Determine modality
    location = data.get('ubicacion', '').lower()
    if 'remoto' in location or 'remote' in location or 'híbrido' in location or 'hibrido' in location or 'hybrid' in location:
        if 'remoto' in location or 'remote' in location:
            data['modalidad'] = 'Remoto'
        else:
            data['modalidad'] = 'Híbrido'
    else:
        # Check in HTML for tags
        if re.search(r'\bremoto\b|\bremote\b', html_content, re.IGNORECASE):
            data['modalidad'] = 'Remoto'
        elif re.search(r'\bhíbrido\b|\bhybrid\b', html_content, re.IGNORECASE):
            data['modalidad'] = 'Híbrido'
        else:
            data['modalidad'] = 'Presencial'

    # Level of experience heuristics
    if not data.get('nivel_experiencia') or data.get('nivel_experiencia') == 'No especificado':
        if re.search(r'\bjunior\b|\bjr\b|\bsin experiencia\b', html_content, re.IGNORECASE):
            data['nivel_experiencia'] = 'Junior'
        elif re.search(r'\bsenior\b|\bsr\b|\blead\b', html_content, re.IGNORECASE):
            data['nivel_experiencia'] = 'Senior'
        elif re.search(r'\bmid\b|\bsemisenior\b|\bssr\b', html_content, re.IGNORECASE):
            data['nivel_experiencia'] = 'Mid'
        else:
            data['nivel_experiencia'] = 'No especificado'

    # Cleanup and normalize
    data['titulo'] = data.get('titulo') or "LinkedIn Job Posting"
    data['empresa'] = data.get('empresa') or "LinkedIn Employer"
    data['ubicacion'] = data.get('ubicacion') or "No especificada"
    data['descripcion_corta'] = data.get('descripcion_corta') or "Ver detalles en LinkedIn"
    data['tecnologias'] = detect_technologies(html_content)
    data['url_vacante'] = url
    data['plataforma'] = "LinkedIn"
    data['turno'] = data.get('turno') or "Tiempo completo"
    data['salario'] = data.get('salario', "")
    data['fecha_publicacion'] = data.get('fecha_publicacion', "")
    
    return data
