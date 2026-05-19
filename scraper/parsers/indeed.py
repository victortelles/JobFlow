import re
from .generic import clean_html, detect_technologies

def parse(html_content: str, url: str) -> dict:
    """
    Indeed specific parser utilizing highly robust data-testid and id attributes.
    """
    data = {}
    
    # 1. Job Title
    title_patterns = [
        r'data-testid="jobsearch-JobInfoHeader-title"[^>]*>\s*(.*?)\s*</h1',
        r'class="[^"]*jobsearch-JobInfoHeader-title[^"]*"[^>]*>\s*(.*?)\s*</h1',
        r'<h1[^>]*class="[^"]*jobsearch-JobInfoHeader-title[^"]*"[^>]*>\s*(.*?)\s*</h1>',
        r'<h1[^>]*>\s*(.*?)\s*</h1>'
    ]
    for pattern in title_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            data['titulo'] = clean_html(match.group(1))
            break
            
    # 2. Company Name
    company_patterns = [
        r'data-testid="inlineHeader-companyName"[^>]*>\s*(.*?)\s*</',
        r'class="[^"]*jobsearch-InlineCompanyRating[^"]*"[^>]*>.*?<a[^>]*>\s*(.*?)\s*</a>',
        r'<a[^>]*href="[^"]*/cmp/[^"]*"[^>]*>\s*(.*?)\s*</a>'
    ]
    for pattern in company_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            raw_company = clean_html(match.group(1))
            # Strip sub-tags like reviews/rating links
            data['empresa'] = re.sub(r'<[^>]+>', '', raw_company).strip()
            break
            
    # 3. Location
    location_patterns = [
        r'data-testid="jobsearch-JobInfoHeader-companyLocation"[^>]*>\s*(.*?)\s*</',
        r'class="[^"]*jobsearch-JobInfoHeader-companyLocation[^"]*"[^>]*>\s*(.*?)\s*</',
        r'id="jobLocationSection"[^>]*>\s*(.*?)\s*</'
    ]
    for pattern in location_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            data['ubicacion'] = clean_html(match.group(1))
            break
            
    # 4. Salary and Job Type
    salary_patterns = [
        r'id="salaryInfoAndJobType"[^>]*>\s*(.*?)\s*</',
        r'class="[^"]*jobsearch-JobMetadataHeader[^"]*"[^>]*>\s*(.*?)\s*</'
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            data['salario'] = clean_html(match.group(1))
            break
            
    # 5. Full Description (ID 'jobDescriptionText' is extremely stable on Indeed)
    desc_patterns = [
        r'id="jobDescriptionText"[^>]*>\s*(.*?)\s*</div>',
        r'class="[^"]*jobsearch-jobDescriptionText[^"]*"[^>]*>\s*(.*?)\s*</div>'
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            data['descripcion_corta'] = clean_html(match.group(1))[:300]
            break
            
    # Determine Modality
    location = data.get('ubicacion', '').lower()
    if "casa" in location or "remoto" in location or "home office" in location or "desde tu casa" in location:
        data['modalidad'] = 'Remoto'
    elif "híbrido" in location or "hibrido" in location or "hybrid" in location:
        data['modalidad'] = 'Híbrido'
    else:
        # Check text body fallback
        if re.search(r'\bremoto\b|\bremote\b|\bdesde casa\b', html_content, re.IGNORECASE):
            data['modalidad'] = 'Remoto'
        elif re.search(r'\bhíbrido\b|\bhybrid\b', html_content, re.IGNORECASE):
            data['modalidad'] = 'Híbrido'
        else:
            data['modalidad'] = 'Presencial'
            
    # Turn (Job Type)
    data['turno'] = 'Tiempo completo'
    sal_lower = data.get('salario', '').lower()
    if 'medio tiempo' in sal_lower or 'part-time' in sal_lower or 'jornada parcial' in sal_lower:
        data['turno'] = 'Medio tiempo'
    elif 'proyecto' in sal_lower or 'contrato' in sal_lower:
        data['turno'] = 'Por proyecto'
        
    # Experience Level
    data['nivel_experiencia'] = 'No especificado'
    title_lower = data.get('titulo', '').lower()
    if "junior" in title_lower or "jr" in title_lower:
        data['nivel_experiencia'] = 'Junior'
    elif "senior" in title_lower or "sr" in title_lower or "lead" in title_lower:
        data['nivel_experiencia'] = 'Senior'
    elif "mid" in title_lower or "semisenior" in title_lower:
        data['nivel_experiencia'] = 'Mid'
        
    # Cleanup and defaults
    data['titulo'] = data.get('titulo') or ""
    data['empresa'] = data.get('empresa') or ""
    data['ubicacion'] = data.get('ubicacion') or ""
    data['descripcion_corta'] = data.get('descripcion_corta') or ""
    data['tecnologias'] = detect_technologies(html_content)
    data['url_vacante'] = url
    data['plataforma'] = "Indeed"
    data['salario'] = data.get('salario', "")
    data['fecha_publicacion'] = ""
    
    return data
