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
    elif 'indeed.com' in url_lower:
        return 'Indeed'
    else:
        return 'Otro'

def scrape_job(url: str, platform_override: str = "Auto-detectar") -> dict:
    """
    Launches Playwright Chromium in headless=False mode, reuses the local profile,
    performs platform-specific structural actions (like expanding text or scrolling),
    and routes the captured DOM to the correct template parser.
    """
    if platform_override == "Auto-detectar":
        platform = detect_platform(url)
    else:
        platform = platform_override
    
    # Ensure profile directory exists
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    html_content = ""
    
    with sync_playwright() as p:
        try:
            # Launch persistent browser context to retain sessions and credentials
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled"
                ],
                no_viewport=True,
                timeout=15000  # 15 seconds timeout
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            # Navigate using 'domcontentloaded' to avoid hanging on infinite websocket/tracking scripts
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
            except Exception as goto_err:
                print(f"Page navigation warning (ignored): {goto_err}")
                
            page.wait_for_timeout(2000)
            
            # --- TEMPLATE-SPECIFIC BROWSER ACTIONS ---
            if platform == 'LinkedIn':
                try:
                    # Helper to close any modal overlays using JS (prevents Playwright physical click scroll loops)
                    def close_overlays_js():
                        # Standard CSS selectors only (cannot contain Playwright pseudo-selectors like :has-text)
                        selectors = [
                            "button.modal__dismiss",
                            "button.contextual-sign-in-modal__modal-dismiss",
                            "button[aria-label='Dismiss']",
                            "button[data-tracking-control-name*='dismiss']"
                        ]
                        for selector in selectors:
                            # Click via JS evaluation to bypass viewport/scroll state checks
                            clicked = page.evaluate(f"""() => {{
                                const el = document.querySelector("{selector}");
                                if (el) {{
                                    el.click();
                                    return true;
                                }}
                                return false;
                            }}""")
                            if clicked:
                                print(f"Cerrado modal de LinkedIn con JS click: {selector}")
                                page.wait_for_timeout(500)
                                return True
                                
                        # Pure JS fallback to locate the dismiss/close button by text content
                        clicked_by_text = page.evaluate("""() => {
                            const btns = Array.from(document.querySelectorAll("button"));
                            const target = btns.find(b => {
                                const txt = b.textContent.toLowerCase();
                                return txt.includes("dismiss") || txt.includes("cerrar") || txt.includes("close") || txt.includes("x");
                            });
                            if (target && target.offsetParent !== null) {
                                target.click();
                                return true;
                            }
                            return false;
                        }""")
                        if clicked_by_text:
                            print("Cerrado modal de LinkedIn buscando botón por texto.")
                            page.wait_for_timeout(500)
                            return True
                        return False

                    # Check before expanding
                    close_overlays_js()

                    # Click 'ver más' or 'Mostrar más' to expand the description using JS
                    # This prevents Playwright from auto-scrolling the viewport down, avoiding sticky header loops
                    show_more_selectors = [
                        "button.jobs-description__footer-button",
                        "button.jobs-description-panels__expand-button",
                        "button[aria-label*='ver más']",
                        "button[aria-label*='show more']",
                        "button.show-more-less-html__button--more",
                        "button.show-more-less-html__button",
                        ".show-more-less-html__button--more",
                        ".show-more-less-html__button"
                    ]
                    for selector in show_more_selectors:
                        clicked = page.evaluate(f"""() => {{
                            const el = document.querySelector("{selector}");
                            if (el) {{
                                el.click();
                                return true;
                            }}
                            return false;
                        }}""")
                        if clicked:
                            print(f"Expandida descripción de LinkedIn con JS click: {selector}")
                            page.wait_for_timeout(1000)
                            break

                    # Check after expanding just in case
                    close_overlays_js()
                except Exception as e:
                    print(f"LinkedIn JS actions skipped: {e}")
                    
            elif platform == 'Indeed':
                try:
                    # Scroll to trigger lazy-loaded sections (like salary/description)
                    page.evaluate("window.scrollTo(0, 500)")
                    page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"Indeed scroll skipped: {e}")
                    

            
            # Capture the DOM snapshot
            html_content = page.content()
            context.close()
            
        except Exception as e:
            print(f"Error scraping url {url} with Playwright: {e}")
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
    
    # Overwrite platform in final dict if explicitly selected by the user
    if platform_override != "Auto-detectar":
        parsed_data['plataforma'] = platform_override
    elif platform == 'Indeed':
        parsed_data['plataforma'] = 'Indeed'
        
    return parsed_data
