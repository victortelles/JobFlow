import os
from playwright.sync_api import sync_playwright
from .parsers import parse_job_by_platform

# Determine Chrome user profile path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_DIR = os.path.join(BASE_DIR, '.chrome_profile')

def detect_platform(url: str) -> str:
    """
    Detects job board platform from the URL domain.
    """
    url_lower = url.lower()
    if 'linkedin.com' in url_lower:
        return 'LinkedIn'
    elif 'glassdoor.com' in url_lower:
        return 'Glassdoor'
    elif 'indeed.com' in url_lower:
        return 'Indeed'
    else:
        return 'Otro'

def scrape_job(url: str) -> dict:
    """
    Launches Playwright Chromium in headless=False mode, reuses the local profile,
    fetches the page DOM content and passes it to the corresponding parser.
    
    Args:
        url (str): The URL of the job opening to scrape.
        
    Returns:
        dict: Parsed job posting dictionary matching the scheme.
    """
    platform = detect_platform(url)
    
    # Ensure profile directory exists
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    html_content = ""
    
    with sync_playwright() as p:
        try:
            # Launch persistent browser context to retain sessions and credentials
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,  # Headless=False is mandatory per context guidelines
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled" # Helps reduce captchas
                ],
                no_viewport=True,
                timeout=15000  # 15 seconds timeout
            )
            
            # Open a new page or grab the first active one
            page = context.pages[0] if context.pages else context.new_page()
            
            # Navigate to the job listing page
            page.goto(url, wait_until="load", timeout=15000)
            
            # Allow a short period (3 seconds) for lazy loaded dynamic blocks to render
            page.wait_for_timeout(3000)
            
            # Capture the DOM snapshot
            html_content = page.content()
            
            # Close the context
            context.close()
            
        except Exception as e:
            print(f"Error scraping url {url} with Playwright: {e}")
            # If Playwright fails or page timeouts, we return a dictionary with minimal fields
            # and allow the user to fill the rest manually.
            return {
                'titulo': '',
                'empresa': '',
                'ubicacion': '',
                'modalidad': 'No especificada',
                'turno': 'No especificado',
                'nivel_experiencia': 'No especificado',
                'salario': '',
                'tecnologias': '',
                'descripcion_corta': f"No se pudo extraer automáticamente: {str(e)}",
                'url_vacante': url,
                'plataforma': platform,
                'fecha_publicacion': '',
                'fecha_postulacion': '',
                'respondio': False,
                'notas': ''
            }
            
    # Extract the details using platform routing
    parsed_data = parse_job_by_platform(html_content, url, platform)
    
    # If the platform was indeed.com but parsed by generic, overwrite it back to Indeed
    if platform == 'Indeed':
        parsed_data['plataforma'] = 'Indeed'
        
    return parsed_data
