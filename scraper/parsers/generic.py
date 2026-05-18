import re
import json

# Common technologies list to auto-detect skills from the job description
TECH_KEYWORDS = [
    "Python", "Django", "Flask", "FastAPI", "PyTorch", "TensorFlow", "Pandas", "NumPy",
    "JavaScript", "TypeScript", "React", "Angular", "Vue", "Next.js", "Node.js", "Express",
    "HTML", "CSS", "Tailwind", "Java", "Spring Boot", "Kotlin", "C#", "ASP.NET", ".NET",
    "C++", "Go", "Rust", "Ruby", "Rails", "PHP", "Laravel", "SQL", "PostgreSQL", "MySQL",
    "MongoDB", "Redis", "Firebase", "SQLite", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "CI/CD", "Git", "GitHub", "GitLab", "Linux", "Scrum", "Agile"
]

def clean_html(raw_html: str) -> str:
    """Removes HTML tags and normalizes spaces."""
    if not raw_html:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', raw_html)
    return re.sub(r'\s+', ' ', clean).strip()

def detect_technologies(text: str) -> str:
    """Detects technologies from the given text and returns them as a comma-separated string."""
    if not text:
        return ""
    detected = []
    # Case-insensitive search with word boundary
    for tech in TECH_KEYWORDS:
        # Avoid matching partial words (e.g. Go inside Good)
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(tech)
    return ", ".join(detected)

def parse_json_ld(html_content: str) -> dict:
    """
    Extracts JobPosting metadata from application/ld+json script tags.
    """
    results = {}
    # Find all application/ld+json scripts
    pattern = re.compile(r'<script\s+[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(html_content)
    
    for match in matches:
        try:
            clean_match = match.strip()
            if clean_match.startswith("<!--"):
                clean_match = clean_match[4:]
            if clean_match.endswith("-->"):
                clean_match = clean_match[:-3]
                
            data = json.loads(clean_match.strip())
            
            blocks = []
            if isinstance(data, list):
                blocks = data
            elif isinstance(data, dict):
                if "@graph" in data:
                    blocks = data["@graph"]
                else:
                    blocks = [data]
                    
            for block in blocks:
                if isinstance(block, dict) and block.get("@type") == "JobPosting":
                    results['titulo'] = block.get('title', '')
                    
                    # Company
                    org = block.get('hiringOrganization', '')
                    if isinstance(org, dict):
                        results['empresa'] = org.get('name', '')
                    elif isinstance(org, str):
                        results['empresa'] = org
                        
                    # Location
                    loc = block.get('jobLocation', '')
                    if isinstance(loc, dict):
                        address = loc.get('address', '')
                        if isinstance(address, dict):
                            locality = address.get('addressLocality', '')
                            region = address.get('addressRegion', '')
                            country = address.get('addressCountry', '')
                            parts = [p for p in [locality, region, country] if p]
                            results['ubicacion'] = ", ".join(parts)
                        elif isinstance(address, str):
                            results['ubicacion'] = address
                            
                    # Employment type (turno)
                    emp_type = block.get('employmentType', '')
                    if isinstance(emp_type, list):
                        emp_type = ", ".join(emp_type)
                    results['turno'] = str(emp_type)
                    
                    # Description
                    desc = block.get('description', '')
                    results['descripcion_corta'] = clean_html(desc)[:300]
                    
                    # Date posted
                    results['fecha_publicacion'] = block.get('datePosted', '')
                    
                    # Salary
                    salary = block.get('baseSalary', '')
                    if isinstance(salary, dict):
                        value = salary.get('value', '')
                        currency = salary.get('currency', 'USD')
                        if isinstance(value, dict):
                            min_v = value.get('minValue', '')
                            max_v = value.get('maxValue', '')
                            unit = value.get('unitText', '')
                            results['salario'] = f"{min_v} - {max_v} {currency} ({unit})"
                        elif isinstance(value, (int, float, str)):
                            results['salario'] = f"{value} {currency}"
                    elif isinstance(salary, str):
                        results['salario'] = salary
                        
                    return results
        except Exception:
            continue
            
    return results

def parse(html_content: str, url: str) -> dict:
    """
    Fallback parser for generic website jobs.
    Uses JSON-LD if available, otherwise attempts parsing basic tags.
    """
    # 1. Try to parse JSON-LD first
    data = parse_json_ld(html_content)
    
    # 2. Heuristics fallback if JSON-LD is missing or incomplete
    if not data.get('titulo'):
        # Extract page title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            data['titulo'] = title_match.group(1).strip()
        else:
            data['titulo'] = "Vacante no especificada"
            
    if not data.get('empresa'):
        data['empresa'] = "No especificada"
        
    if not data.get('ubicacion'):
        # Simple heuristics for remote
        if re.search(r'\bremoto\b|\bremote\b', html_content, re.IGNORECASE):
            data['ubicacion'] = "Remoto"
        else:
            data['ubicacion'] = "No especificada"
            
    if not data.get('descripcion_corta'):
        # Just grab first few body texts
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
        if body_match:
            data['descripcion_corta'] = clean_html(body_match.group(1))[:300]
        else:
            data['descripcion_corta'] = clean_html(html_content)[:300]

    # Detect skills from the entire page or description
    desc = data.get('descripcion_corta', '')
    data['tecnologias'] = detect_technologies(html_content)
    
    # Fill in required standard metadata
    data['url_vacante'] = url
    data['plataforma'] = "Otro"
    
    # Default placeholder values if not found
    data['modalidad'] = "Remoto" if "remoto" in data.get('ubicacion', '').lower() else "No especificada"
    data['turno'] = data.get('turno', "No especificado")
    data['nivel_experiencia'] = "No especificado"
    data['salario'] = data.get('salario', "")
    data['fecha_publicacion'] = data.get('fecha_publicacion', "")
    
    return data
