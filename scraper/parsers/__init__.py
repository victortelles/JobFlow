from . import linkedin
from . import glassdoor
from . import generic

def parse_job_by_platform(html_content: str, url: str, platform: str) -> dict:
    """
    Routes the HTML parsing to the appropriate parser based on platform.
    """
    normalized_platform = platform.lower()
    
    if "linkedin" in normalized_platform:
        return linkedin.parse(html_content, url)
    elif "glassdoor" in normalized_platform:
        return glassdoor.parse(html_content, url)
    else:
        return generic.parse(html_content, url)
