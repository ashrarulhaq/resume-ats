import logging
import os
import asyncio
import re
from typing import Dict, Tuple

from jinja2 import Template

logger = logging.getLogger(__name__)

PDF_BASE_CSS = """
@page {
    size: A4;
    margin: 12mm 18mm;
}

html, body {
    margin: 0;
    padding: 0;
}

body {
     color: #111;
     font-family: Calibri, Arial, sans-serif;
     font-size: 11pt;
     line-height: 1.25;
     background: #fff;
 }

@media screen {
    body {
        width: 210mm;
        min-height: 297mm;
        margin: 0 auto;
        padding: 12mm 14mm;
    }
}

@media print {
    body {
        width: auto;
        min-height: auto;
        margin: 0;
        padding: 0;
    }
}

* {
    box-sizing: border-box;
}

h1, h2, h3, h4, h5, h6, p, ul, ol, li, figure, blockquote {
    margin: 0;
    padding: 0;
}

ul, ol {
    padding-left: 18px;
}

p {
    margin: 0.08em 0;
}

h1, h2, h3, h4, h5, h6 {
    line-height: 1.1;
}

h1 {
    font-size: 16pt;
    font-weight: 700;
    margin-bottom: 2px;
}

h2 {
    font-size: 9.5pt;
    letter-spacing: 0.15px;
    padding-bottom: 2px;
    margin-bottom: 5px;
    border-bottom: 1px solid #222;
    text-transform: uppercase;
}

h3, h4 {
    margin: 0;
}

section {
    margin-top: 10px;
    margin-bottom: 0;
}

.resume-container section,
.resume-container .entry,
.resume-container .job,
.resume-container .school,
.resume-container .project,
.resume-container .job-entry,
.resume-container .education-entry,
.resume-container .project-entry {
    break-inside: avoid;
    page-break-inside: avoid;
}

.resume-container {
    width: 100% !important;
    max-width: 100% !important;
}

.summary {
    text-align: left;
}

.contact-info,
.contact-bar {
    font-size: 7.5pt;
    line-height: 1.25;
    color: #222;
}

.entry-header,
.job-header,
.education-header,
.exp-header,
.project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.entry-title,
.job-title,
.education-school,
.project-title,
.exp-role,
.leader-title {
    font-weight: 700;
    font-size: 8.5pt;
}

.entry-subtitle,
.job-company,
.education-degree,
.exp-company {
    font-style: italic;
}

.entry-dates,
.job-meta,
.education-meta,
.project-date,
.exp-date,
.leader-date {
    font-style: italic;
    white-space: nowrap;
    text-align: right;
}

.entry,
.job-entry,
.education-entry,
.project-entry,
.exp-item,
.leader-item {
    margin-bottom: 5px;
}

.entry-meta,
.job-bullets,
.certifications-list,
.projects .project ul,
.exp-item ul {
    margin-top: 4px;
}

.entry-meta,
.job-meta,
.education-meta {
    margin-top: 2px;
}

.entry-subtitle,
.job-company,
.education-school,
.project-name {
    display: block;
}

.resume-container ul {
    margin-left: 18px;
}

.resume-container li {
    margin-bottom: 2px;
}
"""

def load_template(layout_number: int = 1) -> Tuple[Template, str]:
    """
    Load Jinja2 HTML template and CSS path.
    Always returns the classic layout.
    """
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    html_path = os.path.join(template_dir, "layout_1_classic.html")
    css_path = os.path.join(template_dir, "layout_1_classic.css")

    with open(html_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)
    return template, css_path

def render_html(resume_data: Dict, layout_number: int = 1) -> str:
    """Inject resume data into HTML template, return HTML string."""
    template, _ = load_template(layout_number)
    html_string = template.render(resume=resume_data, **_layout_context(resume_data))
    return html_string


def build_full_html(resume_data: Dict, layout_number: int = 1) -> str:
    """Build a full HTML document with the layout stylesheet inlined."""
    template, css_path = load_template(layout_number)
    html_string = template.render(resume=resume_data, **_layout_context(resume_data))

    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    combined_css = f"{PDF_BASE_CSS}\n{css_content}".strip()

    has_html_tag = '<html' in html_string.lower()

    if has_html_tag:
        if '<head>' in html_string:
            return html_string.replace('<head>', f'<head><style>{combined_css}</style>')
        return html_string

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>{combined_css}</style>
</head>
<body>{html_string}</body>
</html>"""

def generate_pdf(resume_data: Dict, layout_number: int = 1, output_path: str = "") -> str:
    """
    Full pipeline: render HTML -> apply CSS -> write PDF.
    Returns output file path.
    """
    full_html = build_full_html(resume_data, layout_number)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
    pdf_bytes = _render_pdf_bytes(full_html, template_dir)
    if not pdf_bytes:
        raise RuntimeError("PDF generation produced an empty file.")

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return output_path

def get_layout_preview_html(resume_data: Dict, layout_number: int = 1) -> str:
    """Generate HTML for live preview (no PDF conversion)."""
    return build_full_html(resume_data, layout_number)


def _contact_items(resume_data: Dict) -> list[str]:
    contact = resume_data.get("contact", {}) or {}
    return [
        contact.get(key)
        for key in ("location", "phone", "email", "linkedin", "github", "website")
        if contact.get(key)
    ]


def _layout_context(resume_data: Dict) -> Dict:
    return {
        "contact_items": _contact_items(resume_data),
        "skill_groups": _skill_groups(resume_data.get("skills", []) or []),
        "certification_rows": _certification_rows(resume_data.get("certifications", []) or []),
        "leadership_rows": _leadership_rows(resume_data),
    }


def _skill_groups(skills: list) -> list[Dict[str, str]]:
    if not skills:
        return []

    parsed_groups = []
    flat_skills = []
    for item in skills:
        text = str(item).strip()
        if not text:
            continue
        if ":" in text:
            label, values = text.split(":", 1)
            parsed_groups.append({"label": label.strip(), "values": values.strip()})
        else:
            flat_skills.append(text)

    if parsed_groups and not flat_skills:
        return parsed_groups

    categories = [
        ("Data Annotation & Quality", {
            "data annotation", "labelling", "labeling", "content analysis", "quality assurance",
            "attention to detail", "guideline adherence",
        }),
        ("Analytical & Problem-Solving", {
            "analytical thinking", "root cause analysis", "exploratory data analysis (eda)",
            "exploratory data analysis", "eda", "error pattern identification",
        }),
        ("Communication & Reporting", {
            "business writing", "report creation", "dashboard development", "professional correspondence",
        }),
        ("Research & Information Synthesis", {
            "research skills", "information gathering", "synthesizing insights from multiple sources",
        }),
        ("Tools & Languages", {
            "ms excel", "power bi", "sql (basic)", "sql", "python (basic)", "python", "english (fluent)",
            "english",
        }),
    ]

    remaining = list(flat_skills)
    groups = parsed_groups[:]
    for label, names in categories:
        matched = []
        still_remaining = []
        for skill in remaining:
            normalized = skill.lower().strip()
            if normalized in names:
                matched.append(skill)
            else:
                still_remaining.append(skill)
        if matched:
            groups.append({"label": label, "values": ", ".join(matched)})
        remaining = still_remaining

    if remaining:
        groups.append({"label": "Additional Skills", "values": ", ".join(remaining)})

    return groups


def _certification_rows(certifications: list) -> list[Dict[str, str]]:
    known_years = {
        "business analysis fundamentals": "2024",
        "agile project management": "2024",
        "python for data science": "2023",
    }
    rows = []
    for cert in certifications:
        text = str(cert).strip()
        if not text:
            continue
        match = re.search(r"\b(20\d{2}|19\d{2})\b\s*$", text)
        if match:
            rows.append({"name": text[:match.start()].strip(" -–—|"), "date": match.group(1)})
            continue
        lower = text.lower()
        date = next((year for key, year in known_years.items() if key in lower), "")
        rows.append({"name": text, "date": date})
    return rows


def _leadership_rows(resume_data: Dict) -> list[Dict[str, str]]:
    explicit = resume_data.get("leadership") or resume_data.get("leadership_involvement") or []
    rows = []

    if isinstance(explicit, list):
        for item in explicit:
            if isinstance(item, dict):
                role = item.get("role") or item.get("title") or item.get("name") or ""
                organization = item.get("organization") or item.get("company") or ""
                date = item.get("dates") or item.get("date") or ""
                if role or organization:
                    rows.append({"role": role, "organization": organization, "date": date})
            elif str(item).strip():
                rows.append({"role": str(item).strip(), "organization": "", "date": ""})

    for project in resume_data.get("projects", []) or []:
        name = (project.get("name") if isinstance(project, dict) else "") or ""
        if name and not any(row["organization"].lower() == name.lower() for row in rows):
            role = "Founder" if "foss" in name.lower() else "Lead"
            date = "2022-Present" if "foss" in name.lower() else ""
            rows.append({"role": role, "organization": name, "date": date})

    return rows


def _render_pdf_bytes(full_html: str, template_dir: str) -> bytes:
    try:
        return asyncio.run(_render_with_playwright(full_html))
    except Exception as exc:
        logger.warning("Playwright PDF rendering unavailable (%s); falling back to WeasyPrint.", exc)

    from weasyprint import HTML

    return HTML(string=full_html, base_url=template_dir).write_pdf()


async def _render_with_playwright(full_html: str) -> bytes:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1240, "height": 1754})
            await page.set_content(full_html, wait_until="load")
            await page.emulate_media(media="print")
            return await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
                prefer_css_page_size=True,
            )
        finally:
            await browser.close()
