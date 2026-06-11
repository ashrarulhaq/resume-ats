import logging
import streamlit as st
import os
import tempfile
import sys
import textwrap
from pathlib import Path

_npm_bin = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm")
if _npm_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _npm_bin + os.pathsep + os.environ.get("PATH", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from resume_tailor.core.parser import parse_resume
from resume_tailor.core.mistral_backend import tailor_resume
from resume_tailor.core.validator import run_truth_guardrails
from resume_tailor.core.keyword_matcher import extract_keywords_from_jd, calculate_match_score
from resume_tailor.core.pdf_engine import get_layout_preview_html, generate_pdf
from resume_tailor.models.resume_schema import Resume


def resume_to_text(resume: dict) -> str:
    if not isinstance(resume, dict):
        return ""
    parts = []
    def add(value):
        if value:
            parts.append(str(value))
    def add_joined(values):
        text = ' '.join(str(v) for v in values if v)
        if text:
            parts.append(text)
    add(resume.get('name'))
    add(resume.get('summary'))
    contact = resume.get('contact')
    if isinstance(contact, dict):
        add(' '.join(str(v) for v in contact.values() if v))
    if isinstance(resume.get('skills'), list):
        add(' '.join(str(v) for v in resume['skills'] if v))
    if isinstance(resume.get('certifications'), list):
        add(' '.join(str(v) for v in resume['certifications'] if v))
    for experience in resume.get('experience', []) if isinstance(resume.get('experience'), list) else []:
        if isinstance(experience, dict):
            add_joined([
                experience.get('company'),
                experience.get('title'),
                experience.get('dates'),
                experience.get('location'),
                ' '.join(str(v) for v in experience.get('bullets', []) if v),
            ])
    for education in resume.get('education', []) if isinstance(resume.get('education'), list) else []:
        if isinstance(education, dict):
            add_joined([
                education.get('school'),
                education.get('degree'),
                education.get('dates'),
                education.get('location'),
                education.get('cgpa'),
                education.get('percentage'),
            ])
    for project in resume.get('projects', []) if isinstance(resume.get('projects'), list) else []:
        if isinstance(project, dict):
            add_joined([
                project.get('name'),
                project.get('description'),
                ' '.join(str(v) for v in project.get('technologies', []) if v),
            ])
    return '\n'.join(parts)


st.set_page_config(
    page_title="Resume Tailor",
    page_icon="\u2699\ufe0f",
    layout="wide",
    initial_sidebar_state="collapsed"
)

for key, default in [
    ('original_text', ""),
    ('job_description', ""),
    ('tailored_resume', None),
    ('validation_report', None),
    ('keyword_score', None),
    ('selected_layout', 2),
    ('preview_html', ""),
    ('pdf_path', ""),
    ('processing', False),
    ('mistral_api_key', ""),
    ('mistral_model', "mistral-medium-3-5"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Dark Editorial Theme
# ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --amber: #d97706;
    --amber-light: #f59e0b;
    --amber-glow: rgba(217, 119, 6, 0.25);
    --amber-dim: rgba(217, 119, 6, 0.12);
    --emerald: #059669;
    --emerald-light: #10b981;
    --emerald-dim: rgba(5, 150, 105, 0.12);
    --red: #dc2626;
    --red-dim: rgba(220, 38, 38, 0.12);
    --blue: #2563eb;
    --blue-dim: rgba(37, 99, 235, 0.12);
    --bg: #09090b;
    --bg-surface: #111113;
    --bg-raised: #18181b;
    --bg-hover: #1f1f23;
    --bg-elevated: #27272b;
    --text: #fafafa;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --border: rgba(255, 255, 255, 0.06);
    --border-light: rgba(255, 255, 255, 0.10);
    --radius: 14px;
    --radius-sm: 10px;
    --radius-xs: 6px;
    --shadow: 0 2px 16px rgba(0,0,0,0.3);
    --font-serif: 'DM Serif Display', Georgia, serif;
    --font-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}}

#root > div:first-child > div:first-child {{
    background: var(--bg);
}}

.stApp, .stApp header {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-sans);
}}

div[data-testid="stAppViewContainer"] {{
    background: var(--bg);
}}

div[data-testid="stAppViewContainer"] > .main {{
    background: var(--bg);
    padding: 1.5rem 3rem 3rem;
}}

.stApp > header {{
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
}}

/* ─── Block Container ─── */
.block-container {{
    max-width: 1280px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
}}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {{
    background: var(--bg-surface);
    border-right: 1px solid var(--border);
}}

section[data-testid="stSidebar"] .stSidebarContent {{
    background: var(--bg-surface);
}}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] label {{
    color: var(--text-secondary);
}}

section[data-testid="stSidebar"] .stTextInput input {{
    background: var(--bg-raised);
    border-color: var(--border-light);
    color: var(--text);
}}

section[data-testid="stSidebar"] hr {{
    border-color: var(--border);
}}

/* ─── Typography ─── */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-serif);
    color: var(--text);
    font-weight: 400;
    letter-spacing: -0.02em;
}}

h1 {{
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    line-height: 1.15;
}}

h2 {{
    font-size: clamp(1.2rem, 2.5vw, 1.6rem);
    margin-bottom: 0.25rem;
}}

.stMarkdown p {{
    color: var(--text-secondary);
    line-height: 1.6;
}}

.caption-text {{
    color: var(--text-muted);
    font-size: 0.85rem;
}}

/* ─── Custom Step Card ─── */
.step-card {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.2s, box-shadow 0.3s;
}}

.step-card:hover {{
    border-color: var(--border-light);
}}

.step-card .card-label {{
    font-family: var(--font-serif);
    font-size: 1.15rem;
    color: var(--text);
    margin-bottom: 0.6rem;
}}

.step-card .card-subtitle {{
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
}}

.step-card.dimmed {{
    opacity: 0.5;
    pointer-events: none;
}}

/* ─── Progress Stepper ─── */
.stepper {{
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0;
    margin: 0 0 2.5rem;
    padding: 1.5rem 2rem;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    position: relative;
    overflow: hidden;
}}

.stepper::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--amber-dim), var(--amber), var(--amber-dim), transparent);
}}

.step-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    min-width: 0;
}}

.step-item:not(:last-child)::after {{
    content: '';
    position: absolute;
    top: 18px;
    left: 55%;
    right: -45%;
    height: 2px;
    background: var(--border);
    transition: background 0.4s;
}}

.step-item.completed:not(:last-child)::after {{
    background: var(--amber);
    box-shadow: 0 0 8px var(--amber-glow);
}}

.step-item.active:not(:last-child)::after {{
    background: linear-gradient(90deg, var(--amber), var(--border));
}}

.step-circle {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-size: 0.8rem;
    font-weight: 500;
    background: var(--bg-elevated);
    border: 2px solid var(--border);
    color: var(--text-muted);
    position: relative;
    z-index: 1;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}}

.step-item.completed .step-circle {{
    background: var(--amber);
    border-color: var(--amber);
    color: #09090b;
    box-shadow: 0 0 16px var(--amber-glow);
}}

.step-item.active .step-circle {{
    border-color: var(--amber);
    color: var(--amber);
    box-shadow: 0 0 12px var(--amber-glow);
    animation: pulse-ring 2s ease-in-out infinite;
}}

@keyframes pulse-ring {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.3); }}
    50% {{ box-shadow: 0 0 0 8px rgba(217, 119, 6, 0); }}
}}

.step-label {{
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    text-align: center;
    line-height: 1.2;
    white-space: nowrap;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.step-item.completed .step-label {{
    color: var(--amber);
}}

.step-item.active .step-label {{
    color: var(--text);
}}

/* ─── Buttons ─── */
div.stButton > button {{
    font-family: var(--font-sans);
    font-weight: 500;
    border-radius: var(--radius-sm);
    padding: 0.6rem 1.5rem;
    border: 1px solid var(--border-light);
    background: var(--bg-raised);
    color: var(--text);
    transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: none;
    height: auto;
    line-height: 1.4;
}}

div.stButton > button:hover {{
    background: var(--bg-hover);
    border-color: var(--text-muted);
    color: var(--text);
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
}}

div.stButton > button:active {{
    transform: scale(0.97);
}}

div.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, var(--amber) 0%, #b45309 100%);
    color: #09090b;
    border: none;
    font-weight: 600;
    box-shadow: 0 0 0 0 var(--amber-glow);
}}

div.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, var(--amber-light) 0%, var(--amber) 100%);
    box-shadow: 0 0 24px var(--amber-glow);
}}

div.stButton > button[kind="primary"]:disabled {{
    background: var(--bg-elevated);
    color: var(--text-muted);
    box-shadow: none;
    opacity: 0.5;
    pointer-events: none;
}}

div.stButton > button[kind="secondary"] {{
    background: transparent;
    border: 1px solid var(--border-light);
    color: var(--text-secondary);
}}

div.stButton > button[kind="secondary"]:hover {{
    background: var(--bg-hover);
    color: var(--text);
}}

/* ─── Text Inputs & Text Areas ─── */
div.stTextInput input,
div.stTextArea textarea {{
    background: var(--bg-raised) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}

div.stTextInput input:focus,
div.stTextArea textarea:focus {{
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-dim) !important;
}}

div.stTextInput label,
div.stTextArea label,
div.stFileUploader label {{
    color: var(--text-secondary) !important;
    font-weight: 500;
    font-size: 0.85rem;
}}

div.stTextInput p,
div.stTextArea p {{
    color: var(--text-muted);
}}

/* Placeholder styling */
div.stTextArea textarea::placeholder,
div.stTextInput input::placeholder {{
    color: var(--text-muted) !important;
    opacity: 0.6;
}}

/* ─── File Uploader ─── */
div.stFileUploader {{
    background: var(--bg-raised);
    border: 1px dashed var(--border-light);
    border-radius: var(--radius-sm);
    padding: 1rem;
    transition: border-color 0.2s, background 0.2s;
}}

div.stFileUploader:hover {{
    border-color: var(--amber-dim);
    background: var(--bg-hover);
}}

div.stFileUploader section {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

div.stFileUploader div[data-testid="stFileUploadDropzone"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.75rem !important;
}}

div.stFileUploader div[data-testid="stFileUploadDropzone"] svg {{
    color: var(--amber);
}}

div.stFileUploader div[data-testid="stFileUploadDropzone"] p {{
    color: var(--text-secondary);
}}

div.stFileUploader div[data-testid="stFileUploadDropzone"] small {{
    color: var(--text-muted);
}}

/* ─── Expander ─── */
div.stExpander {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    overflow: hidden;
}}

div.stExpander > details {{
    background: transparent;
}}

div.stExpander > details > summary {{
    padding: 0.75rem 1rem;
    font-family: var(--font-sans);
    font-weight: 500;
    color: var(--text);
    background: transparent;
    border-radius: var(--radius-sm);
}}

div.stExpander > details > summary:hover {{
    background: var(--bg-hover);
}}

div.stExpander > details[open] > summary {{
    border-bottom: 1px solid var(--border);
}}

div.stExpander > details > div {{
    padding: 1rem;
    background: transparent;
}}

/* ─── Alert / Info / Warning / Error ─── */
div.stAlert {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
}}

div.stAlert[data-baseweb="notification"] {{
    background: var(--bg-raised);
    border-radius: var(--radius-sm);
}}

div.stAlert[data-baseweb="notification"] .stAlertContent {{
    color: var(--text);
}}

div[data-testid="stNotification"] {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
}}

div[data-testid="stNotification"] p {{
    color: var(--text-secondary);
}}

/* Success alert */
div.stAlert:has(div[data-testid="stNotification"] svg[data-baseweb="icon"][color="#09AB3B"]),
div.stAlert:has(svg[data-testid="stNotificationIcon"][color="#09AB3B"]) {{
    border-left: 3px solid var(--emerald);
}}

/* Error alert */  
div.stAlert:has(div[data-testid="stNotification"] svg[data-baseweb="icon"][color="#FF2B2B"]),
div.stAlert:has(svg[data-testid="stNotificationIcon"][color="#FF2B2B"]) {{
    border-left: 3px solid var(--red);
}}

/* Info alert */
div.stAlert:has(div[data-testid="stNotification"] svg[data-baseweb="icon"][color="#58C4FF"]),
div.stAlert:has(svg[data-testid="stNotificationIcon"][color="#58C4FF"]) {{
    border-left: 3px solid var(--blue);
}}

/* Warning alert */
div.stAlert:has(div[data-testid="stNotification"] svg[data-baseweb="icon"][color="#FFCA28"]),
div.stAlert:has(svg[data-testid="stNotificationIcon"][color="#FFCA28"]) {{
    border-left: 3px solid var(--amber);
}}

/* ─── Metric ─── */
div[data-testid="stMetric"] {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1rem 1.25rem;
}}

div[data-testid="stMetric"] label {{
    color: var(--text-muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-family: var(--font-mono);
    font-size: 1.8rem;
    font-weight: 500;
    color: var(--amber);
}}

div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
    color: var(--text-secondary);
    font-size: 0.85rem;
}}

/* ─── Spinner ─── */
div.stSpinner > div > div {{
    border-color: var(--amber) transparent transparent transparent !important;
}}

div.stSpinner p {{
    color: var(--text-secondary);
}}

/* ─── Divider ─── */
hr.stDivider {{
    border-color: var(--border);
    margin: 1.5rem 0;
}}

/* ─── Code / JSON ─── */
.stJson {{
    background: var(--bg-raised) !important;
    border-radius: var(--radius-sm);
}}

.stJson code {{
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
}}

/* ─── Tabs (if used) ─── */
div[data-testid="stTabs"] button {{
    color: var(--text-muted);
    font-family: var(--font-sans);
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: var(--amber);
}}

/* ─── Checkbox ─── */
div[data-testid="stCheckbox"] label {{
    color: var(--text-secondary);
}}

div[data-testid="stCheckbox"] svg {{
    color: var(--amber);
}}

/* ─── Caption ─── */
.stCaption, .caption {{
    color: var(--text-muted) !important;
    font-size: 0.8rem;
}}

/* ─── Custom containers ─── */
.glow-card {{
    background: var(--bg-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    transition: all 0.3s;
}}

.glow-card:hover {{
    border-color: var(--border-light);
    box-shadow: var(--shadow);
}}

.keyword-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    font-family: var(--font-sans);
    transition: all 0.15s;
}}

.keyword-pill.matched {{
    background: var(--emerald-dim);
    color: var(--emerald-light);
    border: 1px solid rgba(16, 185, 129, 0.2);
}}

.keyword-pill.missing {{
    background: var(--red-dim);
    color: var(--red);
    border: 1px solid rgba(220, 38, 38, 0.2);
}}

.keyword-pill.neutral {{
    background: var(--bg-elevated);
    color: var(--text-secondary);
    border: 1px solid var(--border);
}}

.score-ring {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}}

.score-ring .ring-value {{
    font-family: var(--font-mono);
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--amber);
    line-height: 1;
}}

.score-ring .ring-label {{
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}



/* ─── Preview Frame ─── */
.preview-frame {{
    background: white;
    border-radius: var(--radius-sm);
    overflow: hidden;
    border: 1px solid var(--border);
    min-height: 600px;
}}

.preview-frame iframe {{
    width: 100%;
    min-height: 600px;
    border: none;
}}

/* ─── Keyword Match Section ─── */
.match-bar {{
    width: 100%;
    height: 6px;
    background: var(--bg-elevated);
    border-radius: 99px;
    overflow: hidden;
}}

.match-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
    background: linear-gradient(90deg, var(--amber), var(--emerald));
}}

/* ─── Responsive ─── */
@media (max-width: 1100px) {{
    .layout-grid {{
        grid-template-columns: repeat(3, 1fr);
    }}
    .stepper {{
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 1rem;
    }}
    .step-item {{
        flex: 0 0 calc(33.33% - 0.5rem);
    }}
    .step-item:not(:last-child)::after {{
        display: none;
    }}
}}

@media (max-width: 768px) {{
    div[data-testid="stAppViewContainer"] > .main {{
        padding: 1rem;
    }}
    .layout-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    div[data-testid="column"] {{
        min-width: 100%;
    }}
    .step-item {{
        flex: 0 0 calc(50% - 0.5rem);
    }}
}}

/* ─── Animations ─── */
@keyframes fade-in {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.fade-in {{
    animation: fade-in 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}}

@keyframes glow-pulse {{
    0%, 100% {{ box-shadow: 0 0 18px var(--amber-glow); }}
    50% {{ box-shadow: 0 0 30px var(--amber-glow); }}
}}

.glow-pulse {{
    animation: glow-pulse 2.5s ease-in-out infinite;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# UTILITY: Render progress stepper
# ─────────────────────────────────────────────────────────────────────
def render_stepper():
    steps = [
        ("1", "Upload", st.session_state.original_text != ""),
        ("2", "Job Description", st.session_state.job_description != ""),
        ("3", "Tailor", st.session_state.tailored_resume is not None),
        ("4", "Review", st.session_state.tailored_resume is not None),
        ("5", "Layout", st.session_state.tailored_resume is not None),
        ("6", "Export", st.session_state.preview_html != ""),
    ]

    active_step = 0
    for i, (_, _, done) in enumerate(steps):
        if done:
            active_step = i + 1

    cols = st.columns(len(steps))
    for i, (num, label, done) in enumerate(steps):
        with cols[i]:
            is_active = i == active_step
            symbol = "✓" if done else num
            border = "var(--amber)" if done or is_active else "var(--border)"
            bg = "var(--amber-dim)" if done or is_active else "var(--bg-raised)"
            fg = "var(--amber)" if done or is_active else "var(--text-muted)"
            st.markdown(
                textwrap.dedent(f"""
                <div style="
                    background: {bg};
                    border: 1px solid {border};
                    border-radius: 14px;
                    padding: 0.9rem 0.75rem;
                    text-align: center;
                    min-height: 92px;
                ">
                    <div style="
                        width: 34px;
                        height: 34px;
                        margin: 0 auto 0.45rem;
                        border-radius: 50%;
                        border: 2px solid {border};
                        color: {fg};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 700;
                    ">{symbol}</div>
                    <div style="font-size: 0.78rem; color: {fg}; font-weight: 600;">{label}</div>
                </div>
                """),
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────
# CUSTOM HEADER
# ─────────────────────────────────────────────────────────────────────
st.markdown(
    textwrap.dedent("""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem;">
        <span style="font-size: 1.6rem; line-height: 1;">⚙️</span>
        <h1 style="margin: 0;">Resume Tailor</h1>
    </div>
    <p style="color: var(--text-secondary); margin: 0 0 1.5rem 0; font-size: 0.95rem;">
        Tailor your resume to match job descriptions — while staying 100% truthful
    </p>
    """),
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        textwrap.dedent("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
            <span style="font-size: 1.2rem;">⚙️</span>
            <span style="font-family: var(--font-serif); font-size: 1.1rem; color: var(--text);">Configuration</span>
        </div>
        """),
        unsafe_allow_html=True,
    )

    api_key = st.text_input(
        "Mistral API Key",
        value=st.session_state.mistral_api_key,
        type="password",
        help="Get your API key from https://console.mistral.ai/",
        placeholder="mistral-..."
    )
    if api_key != st.session_state.mistral_api_key:
        st.session_state.mistral_api_key = api_key
        st.rerun()

    model = st.text_input(
        "Model Name",
        value=st.session_state.mistral_model,
        help="e.g. mistral-medium-3-5, mistral-small-4"
    )
    if model != st.session_state.mistral_model:
        st.session_state.mistral_model = model
        st.rerun()

    st.divider()
    st.markdown(f'<p class="caption-text">💡 Get your API key at <a href="https://console.mistral.ai/" target="_blank" style="color: var(--amber);">console.mistral.ai</a></p>', unsafe_allow_html=True)

    if not st.session_state.mistral_api_key:
        st.markdown(
            textwrap.dedent("""
            <div style="
                background: var(--amber-dim);
                border: 1px solid rgba(217, 119, 6, 0.2);
                border-radius: var(--radius-sm);
                padding: 0.75rem 1rem;
                color: var(--amber-light);
                font-size: 0.85rem;
                margin-top: 0.75rem;
            ">
                ⚠️ Enter your Mistral API key to continue
            </div>
            """),
            unsafe_allow_html=True,
        )
        st.stop()


# ─────────────────────────────────────────────────────────────────────
# PROGRESS STEPPER
# ─────────────────────────────────────────────────────────────────────
render_stepper()


# ─────────────────────────────────────────────────────────────────────
# STEP 1 & 2 — UPLOAD + JOB DESCRIPTION
# ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="step-card fade-in">', unsafe_allow_html=True)
    st.markdown(
        textwrap.dedent("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <span style="
                display: inline-flex; align-items: center; justify-content: center;
                width: 28px; height: 28px; border-radius: 50%;
                background: var(--amber-dim); color: var(--amber);
                font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
            ">1</span>
            <div class="card-label" style="margin-bottom: 0;">Upload Resume</div>
        </div>
        <div class="card-subtitle">PDF, DOCX, or TXT — max 10MB</div>
        """),
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx", "txt"],
        help="Upload PDF, DOCX, or TXT file (max 10MB)",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File exceeds 10MB limit. Please compress or use a smaller file.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            file_extension = uploaded_file.name.split('.')[-1].lower()
            with st.spinner("Extracting text from resume..."):
                extracted_text = parse_resume(tmp_file_path, file_extension)
                st.session_state.original_text = extracted_text

            os.unlink(tmp_file_path)

            if st.session_state.original_text:
                st.markdown(f"""
                <div style="
                    display: inline-flex; align-items: center; gap: 0.4rem;
                    background: var(--emerald-dim); color: var(--emerald-light);
                    padding: 0.35rem 0.75rem; border-radius: 999px;
                    font-size: 0.8rem; font-weight: 500;
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    margin-bottom: 0.75rem;
                ">✓ {len(st.session_state.original_text)} characters extracted</div>
                """, unsafe_allow_html=True)

                with st.expander("View extracted text"):
                    st.text_area("Resume text", st.session_state.original_text, height=200, disabled=True, label_visibility="collapsed")
            else:
                st.error("Failed to extract text from the file. Please check the format.")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="step-card fade-in">', unsafe_allow_html=True)
    st.markdown(
        textwrap.dedent("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <span style="
                display: inline-flex; align-items: center; justify-content: center;
                width: 28px; height: 28px; border-radius: 50%;
                background: var(--amber-dim); color: var(--amber);
                font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
            ">2</span>
            <div class="card-label" style="margin-bottom: 0;">Job Description</div>
        </div>
        <div class="card-subtitle">Paste the job description you're targeting</div>
        """),
        unsafe_allow_html=True,
    )

    job_description = st.text_area(
        "Paste the job description here",
        value=st.session_state.job_description,
        height=220,
        placeholder="Paste the full job description here...",
        help="Maximum 10,000 characters",
        label_visibility="collapsed",
    )

    if job_description:
        st.session_state.job_description = job_description
        char_count = len(job_description)
        if char_count > 10000:
            st.error(f"Job description too long: {char_count}/10,000 characters")
        else:
            st.markdown(f'<p class="caption-text" style="margin-top: 0.5rem;">Character count: {char_count}/10,000</p>', unsafe_allow_html=True)

            if st.session_state.original_text:
                keywords = extract_keywords_from_jd(job_description)
                if keywords:
                    with st.expander("Extracted keywords from JD"):
                        pills = "".join(
                            f'<span class="keyword-pill neutral">{kw}</span>'
                            for kw in keywords
                        )
                        st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">{pills}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# STEP 3 — TAILOR BUTTON
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-card fade-in" style="text-align: center; padding: 2rem;">', unsafe_allow_html=True)
st.markdown(
    textwrap.dedent("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
        <span style="
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border-radius: 50%;
            background: var(--amber-dim); color: var(--amber);
            font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
        ">3</span>
        <div class="card-label" style="margin-bottom: 0;">Tailor Resume</div>
    </div>
    <div class="card-subtitle">The AI will rephrase your experience to match the JD — no fabrications</div>
    """),
    unsafe_allow_html=True,
)

col_b1, col_b2, col_b3 = st.columns([1, 1.5, 1])
with col_b2:
    tailor_button = st.button(
        "Tailor Resume",
        type="primary",
        disabled=not (st.session_state.original_text and st.session_state.job_description),
        use_container_width=True,
    )

if tailor_button:
    if not st.session_state.original_text:
        st.error("Please upload a resume first")
    elif not st.session_state.job_description:
        st.error("Please paste a job description")
    else:
        st.session_state.processing = True
        with st.spinner("Tailoring resume with Mistral API... This may take up to 30 seconds"):
            try:
                tailored_dict = tailor_resume(
                    st.session_state.original_text,
                    st.session_state.job_description
                )

                try:
                    validated = Resume.model_validate(tailored_dict)
                    tailored_dict = validated.model_dump()
                except Exception as schema_err:
                    logger.warning(f"Schema validation skipped: {schema_err}")

                validation_result = run_truth_guardrails(
                    st.session_state.original_text,
                    tailored_dict
                )

                st.session_state.tailored_resume = validation_result['cleaned_resume']
                st.session_state.validation_report = validation_result['validation_report']

                if st.session_state.tailored_resume and 'skills' in st.session_state.tailored_resume:
                    resume_text_for_matching = resume_to_text(st.session_state.tailored_resume)
                    keywords = extract_keywords_from_jd(st.session_state.job_description)
                    st.session_state.keyword_score = calculate_match_score(resume_text_for_matching, keywords)

                if st.session_state.tailored_resume:
                    st.session_state.preview_html = get_layout_preview_html(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout
                    )

                st.markdown("""
                <div style="
                    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
                    background: var(--emerald-dim); color: var(--emerald-light);
                    padding: 0.75rem 1.25rem; border-radius: var(--radius-sm);
                    font-weight: 500; margin-top: 1rem;
                    border: 1px solid rgba(16, 185, 129, 0.2);
                ">✓ Resume tailored successfully!</div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error tailoring resume: {str(e)}")
            finally:
                st.session_state.processing = False

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# STEP 4 — RESULTS
# ─────────────────────────────────────────────────────────────────────
if st.session_state.tailored_resume:
    st.markdown('<div class="step-card fade-in">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span style="
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border-radius: 50%;
            background: var(--amber-dim); color: var(--amber);
            font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
        ">4</span>
        <div class="card-label" style="margin-bottom: 0;">Review Results</div>
    </div>
    """, unsafe_allow_html=True)

    kw = st.session_state.keyword_score
    vr = st.session_state.validation_report

    # Score bar
    if kw:
        score = kw['score']
        matched = kw.get('matched', [])
        missing = kw.get('missing', [])

        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <div class="score-ring">
                <div class="ring-value">{score}%</div>
                <div class="ring-label">Match Score</div>
            </div>
            <div style="flex: 1; min-width: 150px;">
                <div class="match-bar">
                    <div class="match-bar-fill" style="width: {score}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.3rem;">
                    <span class="caption-text">0%</span>
                    <span class="caption-text">{'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Needs work'}</span>
                    <span class="caption-text">100%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_kw1, col_kw2 = st.columns(2)
        with col_kw1:
            if matched:
                pills = "".join(
                    f'<span class="keyword-pill matched">✓ {kw}</span>'
                    for kw in matched[:8]
                )
                st.markdown(f'<p class="caption-text" style="margin-bottom: 0.3rem;">Matched keywords</p><div style="display: flex; flex-wrap: wrap; gap: 0.35rem;">{pills}</div>', unsafe_allow_html=True)
        with col_kw2:
            if missing:
                pills = "".join(
                    f'<span class="keyword-pill missing">✗ {kw}</span>'
                    for kw in missing[:8]
                )
                st.markdown(f'<p class="caption-text" style="margin-bottom: 0.3rem;">Missing keywords</p><div style="display: flex; flex-wrap: wrap; gap: 0.35rem;">{pills}</div>', unsafe_allow_html=True)

    # Validation warnings
    if vr:
        if not vr.get('skills_valid') and vr.get('invalid_skills'):
            st.warning(f"⚠️ {vr['warnings'][0] if vr.get('warnings') else 'Some skills were removed for accuracy'}")
        elif vr.get('warnings'):
            for warn in vr['warnings']:
                st.info(f"ℹ️ {warn}")

    # Before/After
    with st.expander("Before / After Comparison", expanded=True):
        c_before, c_after = st.columns(2)
        with c_before:
            st.markdown('<p style="font-family: var(--font-serif); color: var(--text); font-size: 1rem; margin-bottom: 0.5rem;">Original</p>', unsafe_allow_html=True)
            st.text_area("Original", st.session_state.original_text, height=300, disabled=True, label_visibility="collapsed")
        with c_after:
            st.markdown('<p style="font-family: var(--font-serif); color: var(--text); font-size: 1rem; margin-bottom: 0.5rem;">Tailored</p>', unsafe_allow_html=True)
            tailored_json = st.session_state.tailored_resume
            st.json(tailored_json)

    with st.expander("Changes Summary"):
        st.markdown("""
        <p style="color: var(--text-secondary);">
        The AI has restructured and rephrased your existing content to better match the job description.
        No fake skills or experiences were added. All company names, titles, and dates are preserved.
        </p>
        """, unsafe_allow_html=True)
        if vr and 'warnings' in vr:
            for warn in vr['warnings']:
                st.write(f"• {warn}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# STEP 5 — LAYOUT SELECTOR
# ─────────────────────────────────────────────────────────────────────
if st.session_state.tailored_resume:
    st.markdown('<div class="step-card fade-in">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span style="
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border-radius: 50%;
            background: var(--amber-dim); color: var(--amber);
            font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
        ">5</span>
        <div class="card-label" style="margin-bottom: 0;">Select Layout</div>
    </div>
    <div class="card-subtitle">Choose a design for your tailored resume</div>
    """, unsafe_allow_html=True)

    layout_options = {
        1: ("Classic", "\U0001f4c4"),
        2: ("Modern", "\u2726"),
        3: ("Minimal", "\u25cb"),
        4: ("Professional", "\u25c6"),
        5: ("Compact", "\u25a3"),
    }

    layout_cols = st.columns(5)
    for i, (layout_num, (layout_name, icon)) in enumerate(layout_options.items()):
        with layout_cols[i]:
            active = st.session_state.selected_layout == layout_num
            label = f"{icon} {layout_name}"
            if st.button(
                label,
                key=f"layout_btn_{layout_num}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state.selected_layout = layout_num
                if st.session_state.tailored_resume:
                    st.session_state.preview_html = get_layout_preview_html(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout
                    )
                    st.rerun()

    st.markdown(f'<p class="caption-text" style="margin-top: 0.75rem;">Selected: {layout_options[st.session_state.selected_layout][0]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# STEP 6 — PREVIEW & EXPORT
# ─────────────────────────────────────────────────────────────────────
if st.session_state.tailored_resume and st.session_state.preview_html:
    st.markdown('<div class="step-card fade-in">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span style="
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border-radius: 50%;
            background: var(--amber-dim); color: var(--amber);
            font-family: var(--font-mono); font-size: 0.8rem; font-weight: 600;
        ">6</span>
        <div class="card-label" style="margin-bottom: 0;">Preview & Export</div>
    </div>
    """, unsafe_allow_html=True)

    col_preview, col_download = st.columns([3, 1])

    with col_preview:
        st.markdown(f'<p style="font-family: var(--font-serif); color: var(--text); font-size: 1rem; margin-bottom: 0.75rem;">Live Preview</p>', unsafe_allow_html=True)
        st.components.v1.html(st.session_state.preview_html, height=800, scrolling=True)

    with col_download:
        st.markdown(f'<p style="font-family: var(--font-serif); color: var(--text); font-size: 1rem; margin-bottom: 0.75rem;">Export</p>', unsafe_allow_html=True)

        if st.button("Generate PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        pdf_path = tmp_file.name

                    generate_pdf(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout,
                        pdf_path
                    )

                    with open(pdf_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()

                    os.unlink(pdf_path)

                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name="tailored_resume.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                    st.markdown("""
                    <div style="
                        display: inline-flex; align-items: center; gap: 0.4rem;
                        background: var(--emerald-dim); color: var(--emerald-light);
                        padding: 0.35rem 0.75rem; border-radius: 999px;
                        font-size: 0.8rem; font-weight: 500; margin-top: 0.5rem;
                        border: 1px solid rgba(16, 185, 129, 0.2);
                    ">✓ PDF generated</div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Failed to generate PDF: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
    <span class="caption-text">Resume Tailor v1.0.0</span>
    <span class="caption-text">Built with Streamlit · Mistral API · 100% private — only API calls leave your machine</span>
</div>
""", unsafe_allow_html=True)
