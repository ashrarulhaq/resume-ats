# Resume Tailor — Vibe Coding Agent Instructions

## Your Mission

Build a complete, working Resume Tailor application using the provided PRD, Tech Spec, UI Design, Prompts, and Layouts documents. This app uses OpenRouter API to tailor resumes and WeasyPrint to generate PDFs.

**Stack:** Python + Streamlit + WeasyPrint + Jinja2 + Pydantic + pdfplumber + python-docx

---

## CRITICAL RULES

1. **NO FAKE SKILLS EVER** — The app must never add skills not in the original resume. Implement the truth validator strictly.
2. **OPENROUTER API KEY VIA UI** — API key is configured through Streamlit UI sidebar. Never hardcode keys in source code.
3. **5 PDF LAYOUTS** — All layouts must work and generate actual PDFs via WeasyPrint.
4. **ATS COMPATIBLE** — Every PDF must be single-column, standard fonts, selectable text.
5. **SIMPLE UI** — Streamlit only. No React, no Vue, no complex frontend.

---

## Implementation Order

Build in this exact order. Do NOT skip steps.

### Phase 1: Project Scaffold (Files 1-4)

#### File 1: `requirements.txt`
```
streamlit>=1.32.0
pdfplumber>=0.10.0
python-docx>=1.1.0
weasyprint>=60.0
Jinja2>=3.1.0
pydantic>=2.5.0
thefuzz>=0.22.0
python-Levenshtein>=0.23.0
requests>=2.25.0
```

#### File 2: `models/resume_schema.py`
Implement these EXACT Pydantic v2 models:

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
    bullets: List[str] = Field(default_factory=list)

class Education(BaseModel):
    school: str
    degree: str
    dates: str
    location: Optional[str] = None

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)

class Resume(BaseModel):
    name: str
    contact: Contact = Field(default_factory=Contact)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
```

#### File 3: `core/parser.py`
Implement these EXACT functions:

```python
import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "
"
    return _clean_text(text)

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return _clean_text("
".join(paragraphs))

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return _clean_text(f.read())

def parse_resume(file_path: str, file_type: str) -> str:
    file_type = file_type.lower()
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def _clean_text(text: str) -> str:
    import re
    text = re.sub(r'
{3,}', '

', text)
    text = re.sub(r'[ 	]+', ' ', text)
    return text.strip()
```

#### File 4: `core/openrouter_backend.py`
Implement these EXACT functions:

```python
import logging
import os
import json
import re
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)

# Default model - can be overridden by OPENROUTER_MODEL environment variable
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/gpt-3.5-turbo")
# Optional: allow fallback models
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

def check_openrouter_installed() -> bool:
    """Verify OpenRouter API key is set."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return bool(api_key and api_key.strip())

def build_tailor_prompt(resume_text: str, job_description: str) -> str:
    """Load prompt template and inject resume + JD."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "tailor_resume.txt")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        # Fallback template if file not found
        template = """You are an expert resume tailorer. Your task is to tailor the resume to match the job description while maintaining 100% factual honesty.

Rules:
1. Only restructure and rephrase existing content; never invent experience, skills, or qualifications.
2. Preserve all company names, job titles, dates, and degrees exactly.
3. Output must be valid JSON matching the Resume schema.
4. If you cannot tailor a section honestly, leave it as is.

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY the tailored resume in JSON format. Do not include any explanations, markdown, or additional text."""

    return template.replace("{resume_text}", resume_text).replace("{job_description}", job_description)

def call_openrouter(prompt: str, timeout: int = 60) -> str:
    """
    Call OpenRouter API via HTTP.
    Returns raw response string.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional: provide HTTP referer and title for OpenRouter stats
        "HTTP-Referer": "https://resume-tailor.local",
        "X-Title": "Resume Tailor"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Consider adding parameters for deterministic output if needed
        "temperature": 0.1,
        "max_tokens": 4000
    }

    try:
        response = requests.post(
            f"{OPENROUTER_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        # Extract the assistant's message content
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            return message.get("content", "")
        else:
            raise RuntimeError(f"Unexpected OpenRouter response format: {result}")
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        raise RuntimeError(f"OpenRouter API failed: {str(e)}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse OpenRouter response: {e}")
        raise RuntimeError(f"Failed to parse OpenRouter response: {str(e)}")

def extract_json_from_response(raw_response: str) -> Optional[Dict]:
    """
    Parse JSON from OpenRouter response.
    Handles markdown code blocks (```json ... ```).
    Returns dict or None if parsing fails.
    """
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
    if json_match:
        json_str = json_match.group(1)
    else:
        # If no code block, assume the entire response is JSON
        json_str = raw_response.strip()

    # Try to parse JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON object with regex (simple attempt)
        # Look for content between first { and last }
        start = json_str.find('{')
        end = json_str.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = json_str[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        return None

def tailor_resume(resume_text: str, job_description: str) -> Dict:
    """
    Full pipeline:
    1. Build prompt
    2. Call OpenRouter
    3. Extract JSON
    4. Return dict
    Raises exception if any step fails.
    """
    prompt = build_tailor_prompt(resume_text, job_description)
    raw_response = call_openrouter(prompt)
    tailored_dict = extract_json_from_response(raw_response)
    if tailored_dict is None:
        # Fallback: retry once with stricter prompt
        strict_prompt = "Return ONLY valid JSON. No markdown, no explanations.\n\n" + prompt
        raw_response = call_openrouter(strict_prompt)
        tailored_dict = extract_json_from_response(raw_response)
        if tailored_dict is None:
            raise ValueError("Failed to extract JSON from OpenRouter response after two attempts")
    return tailored_dict
```

**IMPORTANT:** The `build_tailor_prompt` function must load the FULL prompt text from `prompts/tailor_resume.txt`. Create that file with the complete prompt from PROMPTS.md.

---

### Phase 2: Truth Guardrails (File 5)

#### File 5: `core/validator.py`

```python
from thefuzz import fuzz
from typing import List, Tuple, Dict, Any

def extract_skills_from_text(text: str) -> List[str]:
    import re
    skills = []
    skills_match = re.search(
        r'(?:Skills|Technical Skills|Core Competencies)[\s:]*([\s\S]*?)(?=

|
[A-Z]|$)',
        text,
        re.IGNORECASE
    )
    if skills_match:
        skills_text = skills_match.group(1)
        raw_skills = re.split(r'[,•|\-
]+', skills_text)
        skills = [s.strip() for s in raw_skills if len(s.strip()) > 1]
    return skills

def validate_skills(original_text: str, tailored_resume: Dict[str, Any], threshold: int = 80) -> Tuple[bool, List[str]]:
    original_skills = extract_skills_from_text(original_text)
    original_text_lower = original_text.lower()
    invalid_skills = []

    for skill in tailored_resume.get("skills", []):
        skill_lower = skill.lower()
        if skill_lower in original_text_lower:
            continue

        matched = False
        for orig_skill in original_skills:
            if fuzz.partial_ratio(skill_lower, orig_skill.lower()) >= threshold:
                matched = True
                break

        if not matched and fuzz.partial_ratio(skill_lower, original_text_lower) >= threshold:
            matched = True

        if not matched:
            invalid_skills.append(skill)

    return len(invalid_skills) == 0, invalid_skills

def validate_dates(original_text: str, tailored_resume: Dict[str, Any]) -> bool:
    import re
    original_dates = set(re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}', original_text, re.IGNORECASE))
    original_dates.update(re.findall(r'\d{4}\s*-\s*(?:\d{4}|Present)', original_text, re.IGNORECASE))

    for job in tailored_resume.get("experience", []):
        if job.get("dates") and job["dates"] not in original_text:
            if not any(job["dates"] in d or d in job["dates"] for d in original_dates):
                return False

    for edu in tailored_resume.get("education", []):
        if edu.get("dates") and edu["dates"] not in original_text:
            if not any(edu["dates"] in d or d in edu["dates"] for d in original_dates):
                return False

    return True

def run_truth_guardrails(original_text: str, tailored_resume: Dict[str, Any]) -> Dict[str, Any]:
    validation_report = {
        "skills_valid": True,
        "removed_skills": [],
        "dates_valid": True,
        "overall_pass": True
    }

    skills_valid, invalid_skills = validate_skills(original_text, tailored_resume)
    if not skills_valid:
        validation_report["skills_valid"] = False
        validation_report["removed_skills"] = invalid_skills
        tailored_resume["skills"] = [
            s for s in tailored_resume.get("skills", [])
            if s not in invalid_skills
        ]

    if not validate_dates(original_text, tailored_resume):
        validation_report["dates_valid"] = False

    validation_report["overall_pass"] = validation_report["skills_valid"] and validation_report["dates_valid"]

    return {
        "cleaned_resume": tailored_resume,
        "validation_report": validation_report
    }
```

---

### Phase 3: PDF Engine (File 6)

#### File 6: `core/pdf_engine.py`

```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

def get_layout_name(n: int) -> str:
    names = {1: "classic", 2: "modern", 3: "minimal", 4: "professional", 5: "compact"}
    return names.get(n, "modern")

def generate_pdf(resume_data: dict, layout_number: int, output_path: str) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    layout_name = get_layout_name(layout_number)
    template_name = f"layout_{layout_number}_{layout_name}.html"
    template = env.get_template(template_name)

    html_string = template.render(resume=resume_data)

    css_name = f"layout_{layout_number}_{layout_name}.css"
    css_path = os.path.join(template_dir, css_name)

    stylesheets = []
    if os.path.exists(css_path):
        stylesheets.append(CSS(filename=css_path))

    HTML(string=html_string).write_pdf(output_path, stylesheets=stylesheets)
    return output_path

def get_layout_preview_html(resume_data: dict, layout_number: int) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    layout_name = get_layout_name(layout_number)
    template_name = f"layout_{layout_number}_{layout_name}.html"
    template = env.get_template(template_name)

    return template.render(resume=resume_data)
```

---

### Phase 4: Keyword Matcher (File 7)

#### File 7: `core/keyword_matcher.py`

```python
from typing import List, Dict, Any
import re

def extract_keywords_from_jd(job_description: str) -> List[str]:
    text = job_description.lower()

    tech_keywords = [
        'python', 'javascript', 'java', 'go', 'rust', 'typescript', 'react', 'angular', 'vue',
        'node', 'django', 'flask', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'kafka', 'elasticsearch', 'ci/cd',
        'agile', 'scrum', 'git', 'github', 'linux', 'html', 'css', 'rest', 'api', 'graphql',
        'microservices', 'serverless', 'lambda', 's3', 'ec2', 'rds', 'pandas', 'numpy',
        'tensorflow', 'pytorch', 'spark', 'hadoop', 'airflow', 'tableau', 'powerbi',
        'excel', 'r', 'scala', 'kotlin', 'swift', 'c++', 'c#', '.net', 'spring',
        'jenkins', 'github actions', 'prometheus', 'grafana', 'splunk', 'ansible',
        'nginx', 'apache', 'webpack', 'babel', 'jest', 'pytest', 'selenium', 'cypress',
        'jira', 'confluence', 'notion', 'slack', 'teams', 'zoom', 'figma', 'sketch',
        'adobe', 'photoshop', 'illustrator', 'indesign', 'xd', 'premiere', 'after effects',
        'blender', 'maya', 'unity', 'unreal', 'godot', 'flutter', 'react native',
        'swiftui', 'jetpack compose', 'ionic', 'cordova', 'xamarin', 'maui',
        'product management', 'project management', 'data analysis', 'machine learning',
        'deep learning', 'nlp', 'computer vision', 'data science', 'business intelligence',
        'devops', 'sre', 'platform engineering', 'cloud architecture',
        'solution architecture', 'technical lead', 'engineering manager', 'team lead',
        'scrum master', 'product owner', 'ux design', 'ui design', 'user research',
        'interaction design', 'visual design', 'brand design', 'motion design', 'graphic design',
        'content strategy', 'copywriting', 'technical writing', 'documentation',
        'sales', 'business development', 'account management', 'customer success',
        'marketing', 'growth', 'seo', 'sem', 'social media', 'content marketing',
        'email marketing', 'marketing automation', 'crm', 'salesforce', 'hubspot',
        'accounting', 'finance', 'fp&a', 'financial modeling', 'valuation',
        'investment banking', 'private equity', 'venture capital', 'consulting',
        'strategy', 'operations', 'supply chain', 'logistics', 'procurement',
        'hr', 'recruiting', 'talent acquisition', 'people operations',
        'legal', 'compliance', 'regulatory', 'risk management', 'audit',
        'healthcare', 'clinical', 'pharmaceutical', 'biotech', 'medical device',
        'research', 'r&d', 'laboratory', 'quality assurance', 'quality control',
        'manufacturing', 'production', 'lean', 'six sigma', 'iso', 'fda',
        'teaching', 'curriculum', 'instructional design', 'e-learning',
        'nonprofit', 'fundraising', 'grant writing', 'program management',
        'policy', 'government', 'public administration', 'international relations',
        'journalism', 'reporting', 'editing', 'publishing', 'broadcasting',
        'cybersecurity', 'penetration testing', 'ethical hacking', 'forensics',
        'incident response', 'threat intelligence', 'vulnerability management',
        'compliance', 'gdpr', 'hipaa', 'sox', 'pci dss', 'nist', 'iso 27001'
    ]

    found = [kw for kw in tech_keywords if kw in text]
    compound = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', job_description)
    keywords = list(set([k.lower() for k in found] + [c.lower() for c in compound if len(c) > 3]))
    return keywords[:30]

def calculate_match_score(resume_text: str, keywords: List[str]) -> Dict[str, Any]:
    resume_lower = resume_text.lower()
    matched = []
    missing = []

    for keyword in keywords:
        if keyword in resume_lower:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = int((len(matched) / len(keywords)) * 100) if keywords else 0

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "total_keywords": len(keywords)
    }
```

---

### Phase 5: Templates (Files 8-17)

Create ALL 5 HTML templates and ALL 5 CSS files exactly as specified in LAYOUTS.md.

**Files to create:**
- `templates/layout_1_classic.html`
- `templates/layout_1_classic.css`
- `templates/layout_2_modern.html`
- `templates/layout_2_modern.css`
- `templates/layout_3_minimal.html`
- `templates/layout_3_minimal.css`
- `templates/layout_4_professional.html`
- `templates/layout_4_professional.css`
- `templates/layout_5_compact.html`
- `templates/layout_5_compact.css`

**CRITICAL:** Each HTML template must use Jinja2 syntax with `{{ resume.name }}`, `{% for job in resume.experience %}`, etc. Each must be a COMPLETE, VALID HTML file.

---

### Phase 6: Prompts File (File 18)

#### File 18: `prompts/tailor_resume.txt`

Copy the ENTIRE "Main Tailoring Prompt" from PROMPTS.md into this file. It must include:
- CRITICAL RULES section
- ATS OPTIMIZATION RULES section
- OUTPUT FORMAT with exact JSON schema
- TRUTH VERIFICATION section
- INPUTS placeholders
- FINAL INSTRUCTION

---

### Phase 7: Main App (File 19)

#### File 19: `app.py`

This is the Streamlit UI. Implement it with these EXACT sections:

```python
import streamlit as st
import os
import tempfile
from core.parser import parse_resume
from core.openrouter_backend import check_openrouter_installed, tailor_resume
from core.validator import run_truth_guardrails
from core.keyword_matcher import extract_keywords_from_jd, calculate_match_score
from core.pdf_engine import generate_pdf, get_layout_preview_html, get_layout_name
from models.resume_schema import Resume

st.set_page_config(
    page_title="Resume Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

for key in ['original_text', 'job_description', 'tailored_resume', 'validation_report', 
            'keyword_score', 'selected_layout', 'preview_html', 'pdf_path']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['tailored_resume', 'validation_report', 
                                                  'keyword_score', 'preview_html', 'pdf_path'] else ""
if st.session_state.selected_layout is None:
    st.session_state.selected_layout = 2

st.title("📄 Resume Tailor")
st.markdown("AI-powered resume optimization. **100% truthful.** ATS-ready.")

if check_gemini_installed():
    st.success("✅ Gemini CLI connected")
else:
    st.error("❌ Gemini CLI not found. Install: `npm install -g @google/gemini-cli` then `gemini auth login`")
    st.stop()

st.header("Step 1: Upload Your Resume")
uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    file_ext = uploaded_file.name.split('.')[-1].lower()

    with st.spinner("Parsing resume..."):
        try:
            text = parse_resume(tmp_path, file_ext)
            st.session_state.original_text = text
            st.success(f"✅ Parsed {len(text)} characters from {uploaded_file.name}")
            with st.expander("Preview extracted text"):
                st.text(text[:1000] + ("..." if len(text) > 1000 else ""))
        except Exception as e:
            st.error(f"Parse error: {e}")
        finally:
            os.unlink(tmp_path)

st.header("Step 2: Paste Job Description")
st.session_state.job_description = st.text_area(
    "Job Description",
    value=st.session_state.job_description,
    height=250,
    placeholder="Paste the full job description here..."
)

jd_len = len(st.session_state.job_description)
st.caption(f"{jd_len} characters")

st.header("Step 3: Generate Tailored Resume")
tailor_disabled = not st.session_state.original_text or not st.session_state.job_description

if st.button("🎯 Tailor My Resume", disabled=tailor_disabled, type="primary"):
    progress = st.progress(0)
    status = st.status("Analyzing job description...", expanded=True)

    try:
        status.write("Extracting keywords from job description...")
        keywords = extract_keywords_from_jd(st.session_state.job_description)
        st.session_state.keyword_score = calculate_match_score(st.session_state.original_text, keywords)
        progress.progress(25)

        status.write("Optimizing resume with Gemini AI...")
        raw_tailored = tailor_resume(st.session_state.original_text, st.session_state.job_description)
        progress.progress(60)

        status.write("Running truth guardrails...")
        result = run_truth_guardrails(st.session_state.original_text, raw_tailored)
        st.session_state.tailored_resume = result["cleaned_resume"]
        st.session_state.validation_report = result["validation_report"]
        progress.progress(85)

        try:
            resume_model = Resume(**st.session_state.tailored_resume)
            st.session_state.tailored_resume = resume_model.model_dump()
        except Exception as e:
            st.warning(f"Schema validation warning: {e}")

        progress.progress(100)
        status.update(label="Resume tailored successfully!", state="complete", expanded=False)
        st.rerun()

    except Exception as e:
        status.update(label=f"Error: {e}", state="error")
        st.error(f"Tailoring failed: {e}")

if st.session_state.tailored_resume:
    st.header("Step 4: Review Results")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Keyword Match Score")
        if st.session_state.keyword_score:
            score = st.session_state.keyword_score["score"]
            st.metric("Match Score", f"{score}%")

            with st.expander(f"Matched ({len(st.session_state.keyword_score['matched'])})"):
                for kw in st.session_state.keyword_score['matched']:
                    st.markdown(f"✅ {kw}")

            with st.expander(f"Missing ({len(st.session_state.keyword_score['missing'])})"):
                for kw in st.session_state.keyword_score['missing']:
                    st.markdown(f"❌ {kw}")

    with col2:
        st.subheader("Truth Verification")
        report = st.session_state.validation_report or {}

        if report.get("overall_pass"):
            st.success("✅ All guardrails passed")
        else:
            st.warning("⚠️ Issues found and fixed")

        if report.get("removed_skills"):
            st.markdown("**Removed hallucinated skills:**")
            for skill in report["removed_skills"]:
                st.markdown(f"- ~~{skill}~~")

    with st.expander("View Tailored Resume JSON"):
        st.json(st.session_state.tailored_resume)

if st.session_state.tailored_resume:
    st.header("Step 5: Choose Layout")

    layout_cols = st.columns(5)
    layout_names = {1: "Classic", 2: "Modern", 3: "Minimal", 4: "Professional", 5: "Compact"}

    for i, col in enumerate(layout_cols, 1):
        with col:
            selected = st.session_state.selected_layout == i
            if st.button(
                f"{'●' if selected else '○'} {layout_names[i]}",
                key=f"layout_{i}",
                type="primary" if selected else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_layout = i
                st.rerun()

    st.subheader("Preview")
    try:
        preview_html = get_layout_preview_html(st.session_state.tailored_resume, st.session_state.selected_layout)
        st.components.v1.html(preview_html, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Preview error: {e}")

    st.header("Step 6: Export")
    if st.button("📥 Generate & Download PDF", type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    pdf_path = generate_pdf(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout,
                        tmp.name
                    )
                    st.session_state.pdf_path = pdf_path

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Download PDF",
                        data=f,
                        file_name=f"{st.session_state.tailored_resume.get('name', 'resume').replace(' ', '_')}_tailored.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
                st.info("Make sure WeasyPrint system dependencies are installed (see README)")

st.divider()
st.caption("Built with Streamlit + Gemini CLI + WeasyPrint. All processing happens locally.")
```

---

### Phase 8: README (File 20)

#### File 20: `README.md`

```markdown
# Resume Tailor

AI-powered resume optimization using local Gemini CLI. 100% truthful. ATS-ready PDFs.

## Prerequisites

1. **Python 3.10+**
2. **Gemini CLI** installed and authenticated:
   ```bash
   npm install -g @google/gemini-cli
   gemini auth login
   ```
3. **WeasyPrint system dependencies**:
   - **macOS:** `brew install pango cairo gdk-pixbuf libffi`
   - **Ubuntu/Debian:** `sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
   - **Windows:** See [WeasyPrint Windows install guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Upload your resume (PDF, DOCX, or TXT)
2. Paste the job description
3. Click "Tailor My Resume"
4. Review keyword match score and truth verification
5. Select a layout (Classic, Modern, Minimal, Professional, Compact)
6. Preview and download your ATS-friendly PDF

## Features

- ✅ Local AI processing (Gemini CLI — no API keys)
- ✅ Truth guardrails (never adds fake skills)
- ✅ 5 professional PDF layouts
- ✅ ATS-optimized formatting
- ✅ Keyword match scoring
- ✅ Before/after comparison
```

---

## Testing Checklist

After building, verify:

1. [ ] `streamlit run app.py` starts without errors
2. [ ] Upload a PDF resume -> text extracts correctly
3. [ ] Paste a job description -> "Tailor" button enables
4. [ ] Click "Tailor" -> Gemini CLI executes successfully
5. [ ] JSON response parses into Pydantic Resume model
6. [ ] Truth validator runs and reports status
7. [ ] Keyword score displays (matched vs missing)
8. [ ] All 5 layout buttons render
9. [ ] Preview pane shows HTML render of selected layout
10. [ ] "Generate PDF" creates a downloadable PDF file
11. [ ] PDF text is selectable (not an image)
12. [ ] PDF uses single-column layout
13. [ ] Uploading a DOCX file also works
14. [ ] Uploading a TXT file also works
15. [ ] If Gemini CLI is missing, app shows clear error with install instructions

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `gemini: command not found` | Run `npm install -g @google/gemini-cli` and `gemini auth login` |
| `OSError: cannot load library` | Install WeasyPrint system deps (pango, cairo) |
| `JSON decode error` | Check Gemini CLI output; retry with shorter inputs |
| `PDF text not selectable` | Ensure WeasyPrint is generating text, not rasterizing |
| `Skills removed by validator` | This is correct behavior — the app is protecting against hallucination |

---

## File Count Summary

You should create exactly these 22 files:
1. `requirements.txt`
2. `models/__init__.py` (empty)
3. `models/resume_schema.py`
4. `core/__init__.py` (empty)
5. `core/parser.py`
6. `core/gemini_backend.py`
7. `core/validator.py`
8. `core/keyword_matcher.py`
9. `core/pdf_engine.py`
10. `templates/layout_1_classic.html`
11. `templates/layout_1_classic.css`
12. `templates/layout_2_modern.html`
13. `templates/layout_2_modern.css`
14. `templates/layout_3_minimal.html`
15. `templates/layout_3_minimal.css`
16. `templates/layout_4_professional.html`
17. `templates/layout_4_professional.css`
18. `templates/layout_5_compact.html`
19. `templates/layout_5_compact.css`
20. `prompts/tailor_resume.txt`
21. `app.py`
22. `README.md`

**Total: 22 files**
