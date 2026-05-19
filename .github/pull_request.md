# Pull Request

## Description
<!-- Provide a clear and concise description of what this PR accomplishes -->

## Related Issue
<!-- Link the issue this PR addresses. Use "Closes #N" to auto-close -->
Closes #

---

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] New Scraper / Parser (Adds support for a new job platform)
- [ ] Refactoring (code improvement without changing functionality)
- [ ] Documentation update

---

## Modules Affected
<!-- Check every module this PR touches -->

- [ ] UI (Streamlit - `app.py`)
- [ ] Web Scraping (Playwright - `scraper/agent.py`)
- [ ] Parsers (`scraper/parsers/`)
- [ ] Data Storage (`storage/excel_handler.py`)
- [ ] Dashboard / Charts (`charts/dashboard.py`)

---

## Changes Made
<!-- List the specific changes introduced in this PR -->

- 
- 
- 

### New Scraper Checklist
<!-- If this PR adds a new scraper, please verify the following -->
- [ ] The parser extracts all possible fields without failing if some are missing.
- [ ] Fallbacks are implemented for dynamic elements (e.g., waiting for load).
- [ ] The new parser is registered in the main agent flow.
- [ ] The returned dictionary matches the expected data schema (`JOBFLOW_CONTEXT.md`).

---

## Testing

### Test Coverage

- [ ] The scraper works consistently for at least 3 different vacantes from the platform.
- [ ] No required external libraries were added (only the ones in `requirements.txt`).
- [ ] Local manual testing completed (UI displays the extracted data correctly).

### Testing Environment
- OS: <!-- e.g., Windows 11, macOS, Ubuntu -->
- Python version: <!-- e.g., 3.11 -->

---

## AI-Generated Code
<!-- Was any part of this PR generated or assisted by AI tools? -->

- [ ] **No AI-generated code** in this PR
- [ ] **Yes, AI-assisted code is included** (complete the checklist below)

### AI Code Review Checklist
- [ ] All AI-generated code has been **read and understood** line by line
- [ ] AI suggestions respect the project context (`JOBFLOW_CONTEXT.md`)
- [ ] No hallucinated imports (e.g., `requests`, `BeautifulSoup` when we use Playwright)

**AI tools used:** <!-- e.g., GitHub Copilot, ChatGPT, Claude, Gemini -->

---

## Code Quality Checklist

- [ ] All code, comments, and variable names in **English** (except UI texts if applicable)
- [ ] **No new dependencies** added (or approved beforehand)
- [ ] **No database connections** (only `jobflow.xlsx` via `openpyxl`)
- [ ] **No headless mode in Playwright** (`headless=False`)

---

## Screenshots
<!-- If applicable, attach screenshots demonstrating the change (e.g., the UI with the new scraper's data) -->

N/A

---
