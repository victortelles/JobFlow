import re
import datetime
from bs4 import BeautifulSoup
from .generic import clean_html, detect_technologies

def parse_relative_date(date_text: str) -> str:
    """
    Converts relative LinkedIn publication dates (e.g. 'Hace 2 días', 'Hace 1 semana', '2 days ago')
    to absolute ISO calendar dates (YYYY-MM-DD) so they pre-fill the form correctly.
    """
    txt = date_text.strip().lower()
    today = datetime.date.today()
    
    # Match "hace X días" / "hace X día" / "hace X d" or "X days ago" / "X day ago"
    match_days = re.search(r'(?:hace\s+)?(\d+)\s*(?:día|dia|d|day|days)(?:\s+ago)?', txt)
    if match_days:
        days = int(match_days.group(1))
        return (today - datetime.timedelta(days=days)).isoformat()
        
    # Match "hace X semanas" / "hace X semana" or "X weeks ago" / "X week ago"
    match_weeks = re.search(r'(?:hace\s+)?(\d+)\s*(?:semana|sem|week|weeks)(?:\s+ago)?', txt)
    if match_weeks:
        weeks = int(match_weeks.group(1))
        return (today - datetime.timedelta(weeks=weeks)).isoformat()
        
    # Match "hace X meses" or "X months ago"
    match_months = re.search(r'(?:hace\s+)?(\d+)\s*(?:mes|meses|month|months)(?:\s+ago)?', txt)
    if match_months:
        months = int(match_months.group(1))
        return (today - datetime.timedelta(days=months * 30)).isoformat()
        
    # Match "hace unas horas" / "hours ago"
    if "hora" in txt or "hour" in txt or "hace poco" in txt or "justo ahora" in txt or "just now" in txt:
        return today.isoformat()
        
    return today.isoformat()

def parse(html_content: str, url: str) -> dict:
    """
    LinkedIn precise unified parser using BeautifulSoup.
    Works flawlessly on BOTH public guest view and private logged-in view.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}
    
    # 1. Job Title and Company Name from HTML <title>
    # The title tag always has format: "[Job Title] | [Company Name] | LinkedIn"
    title_tag = soup.find('title')
    if title_tag:
        title_txt = title_tag.get_text()
        parts = []
        if ' | ' in title_txt:
            parts = [p.strip() for p in title_txt.split(' | ')]
        elif ' · ' in title_txt:
            parts = [p.strip() for p in title_txt.split(' · ')]
        elif ' - ' in title_txt:
            parts = [p.strip() for p in title_txt.split(' - ')]
            
        clean_parts = [p for p in parts if p.lower() != 'linkedin']
        if len(clean_parts) >= 2:
            data['titulo'] = clean_parts[0]
            data['empresa'] = clean_parts[1]
        elif len(clean_parts) == 1:
            data['titulo'] = clean_parts[0]
            
    # Fallback to standard DOM elements if <title> parsing is incomplete
    if not data.get('titulo'):
        title_el = (
            soup.select_one('h1.top-card-layout__title') or
            soup.select_one('h1.topcard__title') or
            soup.select_one('h1.jobs-unified-top-card__job-title') or
            soup.select_one('h1.job-details-jobs-unified-top-card__job-title') or
            soup.select_one('.top-card-layout__title') or
            soup.select_one('h1')
        )
        if title_el:
            data['titulo'] = clean_html(title_el.get_text())
            
    if not data.get('empresa'):
        company_el = (
            soup.select_one('a.topcard__org-name-link') or
            soup.select_one('.topcard__org-name-link') or
            soup.select_one('.top-card-layout__org-name') or
            soup.select_one('.top-card-layout__org-name a') or
            soup.select_one('.jobs-unified-top-card__company-name') or
            soup.select_one('.job-details-jobs-unified-top-card__company-name') or
            soup.select_one('.topcard__flavor a')
        )
        if company_el:
            data['empresa'] = clean_html(company_el.get_text())
            
    # 2. Location and Publication Date
    # We search the DOM semantically for any relative date span (e.g. "2 days ago" or "Hace 1 semana")
    # Its parent container or sibling holds the geographic location!
    location_text = ""
    date_text = ""
    
    date_el = None
    for el in soup.find_all(['span', 'p', 'li']):
        txt = el.get_text(strip=True).lower()
        if len(txt) < 30:
            if re.search(r'\b\d+\s+(?:days|day|hours|hour|weeks|week|months|month|días|día|dias|dia|semanas|semana|horas|hora|d|h|sem)\s+ago\b', txt) or re.search(r'\bhace\s+\d+', txt):
                date_el = el
                break
            
    if date_el:
        date_text = date_el.get_text(strip=True)
        data['fecha_publicacion'] = parse_relative_date(date_text)
        
        # Sibling search within parent container
        parent = date_el.parent
        if parent:
            siblings = [s.get_text(strip=True) for s in parent.find_all(recursive=False) if s.get_text(strip=True)]
            for sib in siblings:
                if sib != date_text and not any(w in sib.lower() for w in ['solicitud', 'solicitante', 'applicant', 'clicked', 'active', 'ago', 'hace', 'views', 'postulados']):
                    location_text = sib
                    break
                    
    # Fallback to standard elements if semantic search failed
    if not location_text:
        bullets = soup.select('span.topcard__flavor--bullet')
        for bullet in bullets:
            txt = bullet.get_text(strip=True)
            if not any(word in txt.lower() for word in ['solicitud', 'solicitante', 'hace', 'día', 'semana', 'mes', 'año', 'active', 'ago']):
                location_text = txt
                break
                
    if not location_text:
        fallback_loc = soup.select_one('.top-card-layout__first-subline .topcard__flavor')
        if fallback_loc:
            location_text = fallback_loc.get_text(strip=True)
            
    # Parse modality and clean location
    if location_text:
        # Parse modality inside parentheses if present (e.g. "(Presencial)", "(Hybrid)", "(Híbrido)")
        match_modal = re.search(r'\((presencial|remoto|híbrido|hibrido|remote|hybrid|on-site|on site|en oficinas)\)', location_text, re.IGNORECASE)
        if match_modal:
            modal_val = match_modal.group(1).lower()
            # Clean the location (remove parentheses)
            location_text = re.sub(r'\s*\([^)]+\)', '', location_text).strip()
            
            if 'remoto' in modal_val or 'remote' in modal_val:
                data['modalidad'] = 'Remoto'
            elif 'híbrido' in modal_val or 'hibrido' in modal_val or 'hybrid' in modal_val:
                data['modalidad'] = 'Híbrido'
            elif 'presencial' in modal_val or 'oficinas' in modal_val or 'on-site' in modal_val or 'on site' in modal_val:
                data['modalidad'] = 'Presencial'
        else:
            # Inline keyword search inside location text
            loc_lower = location_text.lower()
            if 'remoto' in loc_lower or 'remote' in loc_lower:
                data['modalidad'] = 'Remoto'
            elif 'híbrido' in loc_lower or 'hibrido' in loc_lower or 'hybrid' in loc_lower:
                data['modalidad'] = 'Híbrido'
            elif 'presencial' in loc_lower or 'on-site' in loc_lower or 'on site' in loc_lower:
                data['modalidad'] = 'Presencial'
                
        data['ubicacion'] = clean_html(location_text)
        
    # Global parenthetical modality check fallback (looks anywhere in small elements of the DOM)
    if not data.get('modalidad'):
        for el in soup.find_all(['span', 'p', 'li']):
            txt = el.get_text(strip=True)
            if len(txt) < 100:
                match_modal = re.search(r'\((presencial|remoto|híbrido|hibrido|remote|hybrid|on-site|on site|en oficinas)\)', txt, re.IGNORECASE)
                if match_modal:
                    modal_val = match_modal.group(1).lower()
                    if 'remoto' in modal_val or 'remote' in modal_val:
                        data['modalidad'] = 'Remoto'
                    elif 'híbrido' in modal_val or 'hibrido' in modal_val or 'hybrid' in modal_val:
                        data['modalidad'] = 'Híbrido'
                    elif 'presencial' in modal_val or 'on-site' in modal_val or 'on site' in modal_val or 'oficinas' in modal_val:
                        data['modalidad'] = 'Presencial'
                    break

    # Default Modality fallback if still not resolved
    if not data.get('modalidad'):
        body_text_lower = clean_html(html_content).lower()
        if 'remoto' in body_text_lower or 'remote' in body_text_lower:
            data['modalidad'] = 'Remoto'
        elif 'híbrido' in body_text_lower or 'hybrid' in body_text_lower:
            data['modalidad'] = 'Híbrido'
        else:
            data['modalidad'] = 'Presencial'
            
    # Default date if still empty
    if not data.get('fecha_publicacion'):
        pub_el = soup.select_one('span.posted-time-ago__text, .posted-time-ago__text, .topcard__flavor--metadata')
        if pub_el:
            data['fecha_publicacion'] = parse_relative_date(pub_el.get_text(strip=True))
            
    # 3. Full Job Description
    # Targets both public guest container and private logged-in flagship data-testid container
    desc_el = (
        soup.select_one('[data-testid*="expandable-text-box"]') or
        soup.select_one('div.show-more-less-html__markup') or
        soup.select_one('section.description') or
        soup.select_one('div.jobs-description-content') or
        soup.select_one('div.description__text') or
        soup.select_one('div#job-details')
    )
    if desc_el:
        data['descripcion_corta'] = clean_html(desc_el.get_text())[:450]
        
    # 4. Structured Criteria parsing (Tipo de empleo, Nivel de antigüedad)
    criteria_items = soup.select('li.description__job-criteria-item')
    for item in criteria_items:
        subheader_el = item.select_one('.description__job-criteria-subheader')
        value_el = item.select_one('.description__job-criteria-text--criteria') or item.select_one('.description__job-criteria-text')
        if subheader_el and value_el:
            subheader = subheader_el.get_text(strip=True).lower()
            value = value_el.get_text(strip=True)
            
            # Subheader maps
            if 'tipo de empleo' in subheader:
                jt = value.lower()
                if "completo" in jt or "jornada completa" in jt or "full-time" in jt:
                    data['turno'] = "Tiempo completo"
                elif "parcial" in jt or "media jornada" in jt or "jornada parcial" in jt or "part-time" in jt:
                    data['turno'] = "Medio tiempo"
                elif "indeterminado" in jt or "tiempo indeterminado" in jt:
                    data['turno'] = "Por tiempo indeterminado"
                elif "prácticas" in jt or "practicas" in jt or "intern" in jt or "becario" in jt:
                    data['turno'] = "Prácticas"
                elif "proyecto" in jt or "contrato" in jt:
                    data['turno'] = "Por proyecto"
                    
            elif 'nivel de antigüedad' in subheader or 'antigüedad' in subheader:
                exp_text = value.lower()
                if "sin experiencia" in exp_text or "prácticas" in exp_text or "entry" in exp_text or "junior" in exp_text or "becario" in exp_text:
                    data['nivel_experiencia'] = "Junior"
                elif "intermedio" in exp_text or "mid" in exp_text or "asociado" in exp_text:
                    data['nivel_experiencia'] = "Mid"
                elif "director" in exp_text or "ejecutivo" in exp_text or "senior" in exp_text or "sr" in exp_text:
                    data['nivel_experiencia'] = "Senior"
                    
    # Heuristics if criteria list didn't resolve experience or turn
    if not data.get('nivel_experiencia') or data.get('nivel_experiencia') == 'No especificado':
        title_lower = data.get('titulo', '').lower()
        desc_lower = data.get('descripcion_corta', '').lower()
        if "junior" in title_lower or "jr" in title_lower or "practicas" in title_lower or "intern" in title_lower or "becario" in title_lower or "practicas" in desc_lower or "internship" in desc_lower or "becario" in desc_lower:
            data['nivel_experiencia'] = "Junior"
        elif "senior" in title_lower or "sr" in title_lower or "lead" in title_lower:
            data['nivel_experiencia'] = "Senior"
        elif "mid" in title_lower or "semisenior" in title_lower:
            data['nivel_experiencia'] = "Mid"
        else:
            data['nivel_experiencia'] = "No especificado"
            
    if not data.get('turno'):
        title_lower = data.get('titulo', '').lower()
        desc_lower = data.get('descripcion_corta', '').lower()
        if "practicas" in title_lower or "intern" in title_lower or "becario" in title_lower or "practicas" in desc_lower or "internship" in desc_lower or "becario" in desc_lower or "intern" in desc_lower:
            data['turno'] = "Prácticas"
        else:
            data['turno'] = "Tiempo completo"

    # Cleanup and defaults
    data['titulo'] = data.get('titulo') or ""
    data['empresa'] = data.get('empresa') or ""
    data['ubicacion'] = data.get('ubicacion') or ""
    data['descripcion_corta'] = data.get('descripcion_corta') or ""
    data['tecnologias'] = detect_technologies(html_content)
    data['url_vacante'] = url
    data['plataforma'] = "LinkedIn"
    data['salario'] = data.get('salario', "")
    
    return data
