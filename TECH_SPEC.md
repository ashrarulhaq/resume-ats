# Resume Tailor — Technical Specification

## 1. Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **Frontend UI** | Streamlit | Single-file Python UI, drag-and-drop built-in, fastest MVP |
| **Document Parsing** | `pdfplumber` (PDF), `python-docx` (DOCX) | Pure Python, text extraction accuracy |
| **AI Backend** | Gemini CLI via `subprocess` | Local execution, no API keys, free |
| **JSON Validation** | `pydantic` v2 | Schema enforcement, type safety |
| **PDF Generation** | `WeasyPrint` | HTML/CSS -> PDF, easy layout templating |
| **Template Engine** | Jinja2 | HTML template rendering with data injection |
| **Fuzzy Matching** | `thefuzz` (fuzzywuzzy) | Skill validation between original and output |
| **Environment** | Python 3.10+ | Compatibility with all dependencies |

## 2. System Architecture

```
+-------------------------------------------------------------+
|                     STREAMLIT UI (app.py)                    |
|  +--------------+  +--------------+  +---------------------+  |
|  | File Upload  |  | JD Text Area |  | Layout Selector     |  |
|  +--------------+  +--------------+  +---------------------+  |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
|                  DOCUMENT PARSER (parser.py)                 |
|         pdfplumber -> text    python-docx -> text            |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
|              GEMINI BACKEND (gemini_backend.py)              |
|  subprocess.run(["gemini", "generate", "--prompt", ...])      |
|  -> JSON output -> Pydantic validation -> Truth check        |
+--------------------------+----------------------------------+
                           |
+--------------------------v----------------------------------+
|              PDF ENGINE (pdf_engine.py)                        |
|  Jinja2 template + WeasyPrint -> PDF file                    |
|  5 layouts: Classic, Modern, Minimal, Professional, Compact    |
+-------------------------------------------------------------+
```

## 3. File Structure

```
resume_tailor/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Setup & run instructions
│
├── core/
│   ├── __init__.py
│   ├── parser.py                   # PDF/DOCX/TXT text extraction
│   ├── gemini_backend.py           # Gemini CLI wrapper + prompt builder
│   ├── validator.py                # Truth guardrail + JSON schema validation
│   ├── keyword_matcher.py          # JD keyword extraction + matching
│   └── pdf_engine.py               # HTML template -> PDF renderer
│
├── models/
│   ├── __init__.py
│   └── resume_schema.py            # Pydantic models for resume JSON
│
├── templates/
│   ├── layout_1_classic.html       # Classic layout HTML template
│   ├── layout_1_classic.css        # Classic layout styles
│   ├── layout_2_modern.html        # Modern layout HTML template
│   ├── layout_2_modern.css         # Modern layout styles
│   ├── layout_3_minimal.html       # Minimal layout HTML template
│   ├── layout_3_minimal.css        # Minimal layout styles
│   ├── layout_4_professional.html  # Professional layout HTML template
│   ├── layout_4_professional.css   # Professional layout styles
│   ├── layout_5_compact.html       # Compact layout HTML template
│   └── layout_5_compact.css        # Compact layout styles
│
├── prompts/
│   ├── tailor_resume.txt           # Main Gemini prompt template
│   └── extract_structure.txt       # Fallback: extract JSON from messy text
│
├── assets/
│   └── fonts/                      # Custom fonts if needed (optional)
│
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_validator.py
    └── test_pdf_engine.py
```

## 4. Module Specifications

### 4.1 `core/parser.py`

**Responsibility:** Extract plain text from uploaded files.

**Functions:**

```python
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    ...

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    ...

def extract_text_from_txt(file_path: str) -> str:
    """Read plain text file."""
    ...

def parse_resume(file_path: str, file_type: str) -> str:
    """Router: dispatch to correct extractor based on file extension."""
    ...
```

**Error Handling:**
- Return empty string with warning if PDF is image-based (no text layer)
- Strip excessive whitespace (>3 newlines -> 2 newlines)
- Max output length: 20,000 characters (truncate with warning)

### 4.2 `core/gemini_backend.py`

**Responsibility:** Interface with Gemini CLI.

**Functions:**

```python
import subprocess
import json
from typing import Optional

def check_gemini_installed() -> bool:
    """Verify 'gemini' command exists in PATH."""
    ...

def build_tailor_prompt(resume_text: str, job_description: str) -> str:
    """Load prompt template and inject resume + JD."""
    ...

def call_gemini(prompt: str, timeout: int = 60) -> str:
    """
    Execute Gemini CLI subprocess.
    Command: gemini generate --prompt "{prompt}"
    Returns raw stdout string.
    """
    ...

def extract_json_from_response(raw_response: str) -> Optional[dict]:
    """
    Parse JSON from Gemini response.
    Handles markdown code blocks (```json ... ```).
    Returns dict or None if parsing fails.
    """
    ...

def tailor_resume(resume_text: str, job_description: str) -> dict:
    """
    Full pipeline:
    1. Build prompt
    2. Call Gemini
    3. Extract JSON
    4. Return dict
    Raises exception if any step fails.
    """
    ...
```

**Gemini CLI Command Format:**
```bash
gemini generate --prompt "<prompt_text>"
```

**Fallback Strategy:**
If JSON extraction fails, retry once with stricter prompt: `"Return ONLY valid JSON. No markdown, no explanations."`

### 4.3 `core/validator.py`

**Responsibility:** Ensure AI output doesn't hallucinate skills/experience.

**Functions:**

```python
from thefuzz import fuzz
from typing import List, Tuple

def extract_skills_from_text(text: str) -> List[str]:
    """Naive skill extraction: look for capitalized technical terms, comma-separated lists under 'Skills' section."""
    ...

def validate_skills(original_text: str, tailored_resume: dict, threshold: int = 80) -> Tuple[bool, List[str]]:
    """
    Check that every skill in tailored_resume['skills'] exists in original_text.
    Uses fuzzy matching (fuzz.partial_ratio).
    Returns: (is_valid, list_of_invalid_skills)
    """
    ...

def validate_dates(original_text: str, tailored_resume: dict) -> bool:
    """Verify all dates in experience/education exist in original text."""
    ...

def validate_companies(original_text: str, tailored_resume: dict) -> bool:
    """Verify all company names exist in original text."""
    ...

def run_truth_guardrails(original_text: str, tailored_resume: dict) -> dict:
    """
    Run all validations.
    If invalid skills found: remove them from tailored_resume['skills'].
    If invalid experiences found: flag for user review.
    Returns cleaned resume dict + validation report.
    """
    ...
```

### 4.4 `core/keyword_matcher.py`

**Responsibility:** Analyze keyword overlap between JD and resume.

**Functions:**

```python
def extract_keywords_from_jd(job_description: str) -> List[str]:
    """Use Gemini or simple NLP to extract top technical/role keywords from JD."""
    ...

def calculate_match_score(resume_text: str, keywords: List[str]) -> dict:
    """
    Calculate percentage of JD keywords found in resume.
    Returns: {"score": 85, "matched": [...], "missing": [...]}
    """
    ...
```

### 4.5 `core/pdf_engine.py`

**Responsibility:** Render JSON resume into PDF using HTML templates.

**Functions:**

```python
from weasyprint import HTML, CSS
from jinja2 import Template
import os

def load_template(layout_number: int) -> Tuple[Template, str]:
    """
    Load Jinja2 HTML template and CSS path for given layout.
    layout_number: 1-5
    Returns: (template_obj, css_path)
    """
    ...

def render_html(resume_data: dict, layout_number: int) -> str:
    """Inject resume data into HTML template, return HTML string."""
    ...

def generate_pdf(resume_data: dict, layout_number: int, output_path: str) -> str:
    """
    Full pipeline: render HTML -> apply CSS -> write PDF.
    Returns output file path.
    """
    ...

def get_layout_preview_html(resume_data: dict, layout_number: int) -> str:
    """Generate HTML for live preview (no PDF conversion)."""
    ...
```

### 4.6 `models/resume_schema.py`

**Pydantic Models:**

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

class Experience(BaseModel):
    company: str
    title: str
    dates: str
    location: Optional[str] = None
    bullets: List[str]

class Education(BaseModel):
    school: str
    degree: str
    dates: str
    location: Optional[str] = None

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = []

class Resume(BaseModel):
    name: str
    contact: Contact
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    certifications: List[str] = []
    projects: List[Project] = []
```

## 5. Dependencies (`requirements.txt`)

```
streamlit>=1.32.0
pdfplumber>=0.10.0
python-docx>=1.1.0
weasyprint>=60.0
Jinja2>=3.1.0
pydantic>=2.5.0
thefuzz>=0.22.0
python-Levenshtein>=0.23.0
```

## 6. Environment Requirements

### 6.1 Prerequisites
1. **Python 3.10+** installed
2. **Gemini CLI** installed and in PATH:
   ```bash
   # Verify installation
   gemini --version
   ```
3. **WeasyPrint system dependencies** (platform-specific):
   - **macOS:** `brew install pango cairo gdk-pixbuf libffi`
   - **Ubuntu/Debian:** `sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
   - **Windows:** Install GTK+ for Windows (WeasyPrint docs)

### 6.2 Gemini CLI Setup
- User must authenticate Gemini CLI independently:
  ```bash
  gemini auth login
  ```
- App checks for CLI presence on startup; shows setup instructions if missing.

## 7. Streamlit App Structure (`app.py`)

```python
import streamlit as st

# Page config
st.set_page_config(
    page_title="Resume Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""
if 'tailored_resume' not in st.session_state:
    st.session_state.tailored_resume = None
if 'selected_layout' not in st.session_state:
    st.session_state.selected_layout = 2  # Default: Modern

# UI Sections:
# 1. Header + Description
# 2. Step 1: File Upload
# 3. Step 2: Job Description Input
# 4. Step 3: Tailor Button + Loading
# 5. Step 4: Results (Keyword Score + Changes)
# 6. Step 5: Layout Selector
# 7. Step 6: Live Preview + PDF Download
```

## 8. State Management

Streamlit `st.session_state` handles all state:

| Key | Type | Purpose |
|-----|------|---------|
| `original_text` | str | Raw extracted text from uploaded resume |
| `job_description` | str | Pasted job description |
| `tailored_resume` | dict | Validated JSON from Gemini |
| `validation_report` | dict | Truth guardrail results |
| `keyword_score` | dict | JD match analysis |
| `selected_layout` | int | 1-5 layout choice |
| `preview_html` | str | Rendered HTML for preview |
| `pdf_path` | str | Path to generated PDF file |

## 9. Security & Privacy

- **No data leaves the machine** (except Gemini CLI's own network calls to Google)
- Uploaded files are stored in a temporary directory, deleted after session
- No logging of resume content to disk (only temporary processing files)
- Gemini CLI handles its own auth; app never touches API keys

## 10. Testing Strategy

| Test | Method |
|------|--------|
| Parser accuracy | Unit tests with sample PDF/DOCX files |
| JSON schema validation | Pydantic model tests |
| Truth guardrails | Inject fake skills, verify removal |
| PDF generation | Generate all 5 layouts, verify text extractable |
| ATS compatibility | Use `pdfplumber` to extract text from generated PDFs |
| Gemini CLI mocking | Mock subprocess for offline testing |
