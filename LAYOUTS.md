# Resume Tailor — PDF Layout Templates Specification

## Overview

All 5 layouts are implemented as **Jinja2 HTML templates + CSS files**, rendered to PDF via WeasyPrint.

**Design Constraints (All Layouts):**
- Single-column only (ATS compatibility)
- Standard fonts: Helvetica, Arial, Georgia, Times New Roman
- No text in headers/footers (ATS strips them)
- No images, icons, or graphics containing text
- All text must be selectable in the PDF
- Page size: US Letter (8.5in x 11in)
- Margins: 0.5in - 0.75in depending on layout

---

## Layout 1: Classic

**Style:** Traditional, conservative, black & white  
**Best For:** Law, finance, government, academia  
**Font:** Georgia (serif) for headings, Helvetica for body  
**Accent:** None (pure black #000000 on white)

### Visual Structure
```
+--------------------------------------------------+
|                                                  |
|              JOHN DOE                            |
|         john@email.com | (555) 123-4567          |
|              New York, NY                          |
|                                                  |
|  PROFESSIONAL SUMMARY                            |
|  ------------------------------------------------|
|  Results-driven professional with 5+ years...      |
|                                                  |
|  PROFESSIONAL EXPERIENCE                         |
|  ------------------------------------------------|
|  Senior Developer | TechCorp                     |
|  New York, NY | January 2020 – Present          |
|  • Led development of microservices architecture |
|    using Python and Docker, improving throughput   |
|    by 40%                                         |
|  • Implemented CI/CD pipelines reducing deploy   |
|    time from 2 hours to 15 minutes               |
|                                                  |
|  Developer | Startup Inc                         |
|  San Francisco, CA | June 2017 – December 2019   |
|  • Built RESTful APIs serving 1M+ daily requests |
|                                                  |
|  EDUCATION                                       |
|  ------------------------------------------------|
|  BS Computer Science, Stanford University        |
|  Stanford, CA | 2013 – 2017                       |
|                                                  |
|  SKILLS                                          |
|  ------------------------------------------------|
|  Python • JavaScript • Docker • AWS • SQL • Agile |
|                                                  |
+--------------------------------------------------+
```

### HTML Template (`templates/layout_1_classic.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ resume.name }} - Resume</title>
    <link rel="stylesheet" href="layout_1_classic.css">
</head>
<body>
    <div class="resume-container">
        <header class="header">
            <h1 class="name">{{ resume.name }}</h1>
            <div class="contact-line">
                {% if resume.contact.email %}{{ resume.contact.email }}{% endif %}
                {% if resume.contact.phone %} | {{ resume.contact.phone }}{% endif %}
                {% if resume.contact.linkedin %} | {{ resume.contact.linkedin }}{% endif %}
                {% if resume.contact.location %} | {{ resume.contact.location }}{% endif %}
            </div>
        </header>

        {% if resume.summary %}
        <section class="section">
            <h2 class="section-title">Professional Summary</h2>
            <hr class="divider">
            <p class="summary-text">{{ resume.summary }}</p>
        </section>
        {% endif %}

        {% if resume.experience %}
        <section class="section">
            <h2 class="section-title">Professional Experience</h2>
            <hr class="divider">
            {% for job in resume.experience %}
            <div class="job">
                <div class="job-header">
                    <span class="job-title">{{ job.title }}</span>
                    <span class="job-company"> | {{ job.company }}</span>
                </div>
                <div class="job-meta">
                    {% if job.location %}{{ job.location }} | {% endif %}{{ job.dates }}
                </div>
                <ul class="bullet-list">
                    {% for bullet in job.bullets %}
                    <li>{{ bullet }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        {% if resume.education %}
        <section class="section">
            <h2 class="section-title">Education</h2>
            <hr class="divider">
            {% for edu in resume.education %}
            <div class="education-item">
                <div class="edu-header">
                    <span class="edu-degree">{{ edu.degree }}</span>
                    <span class="edu-school">, {{ edu.school }}</span>
                </div>
                <div class="edu-meta">
                    {% if edu.location %}{{ edu.location }} | {% endif %}{{ edu.dates }}
                </div>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        {% if resume.skills %}
        <section class="section">
            <h2 class="section-title">Skills</h2>
            <hr class="divider">
            <p class="skills-text">{{ resume.skills | join(' • ') }}</p>
        </section>
        {% endif %}

        {% if resume.certifications %}
        <section class="section">
            <h2 class="section-title">Certifications</h2>
            <hr class="divider">
            <ul class="cert-list">
                {% for cert in resume.certifications %}
                <li>{{ cert }}</li>
                {% endfor %}
            </ul>
        </section>
        {% endif %}
    </div>
</body>
</html>
```

### CSS (`templates/layout_1_classic.css`)

```css
@page {
    size: letter;
    margin: 0.75in;
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 10.5pt;
    line-height: 1.4;
    color: #000000;
    background: #ffffff;
}

.resume-container {
    max-width: 100%;
}

.header {
    text-align: center;
    margin-bottom: 18pt;
}

.name {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 22pt;
    font-weight: bold;
    margin: 0 0 6pt 0;
    letter-spacing: 1pt;
    text-transform: uppercase;
}

.contact-line {
    font-size: 9.5pt;
    color: #333333;
}

.section {
    margin-bottom: 14pt;
}

.section-title {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 12pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    margin: 0 0 4pt 0;
    color: #000000;
}

.divider {
    border: none;
    border-top: 1pt solid #000000;
    margin: 0 0 8pt 0;
}

.summary-text {
    text-align: justify;
    margin: 0;
}

.job {
    margin-bottom: 10pt;
}

.job-header {
    font-weight: bold;
    font-size: 10.5pt;
}

.job-title {
    font-style: italic;
}

.job-company {
    font-weight: normal;
}

.job-meta {
    font-size: 9.5pt;
    color: #444444;
    font-style: italic;
    margin-bottom: 4pt;
}

.bullet-list {
    margin: 0;
    padding-left: 18pt;
}

.bullet-list li {
    margin-bottom: 3pt;
}

.education-item {
    margin-bottom: 6pt;
}

.edu-header {
    font-weight: bold;
}

.edu-degree {
    font-style: italic;
}

.edu-meta {
    font-size: 9.5pt;
    color: #444444;
}

.skills-text {
    margin: 0;
}

.cert-list {
    margin: 0;
    padding-left: 18pt;
}
```

---

## Layout 2: Modern Clean

**Style:** Contemporary, sans-serif, subtle blue accent  
**Best For:** Tech, SaaS, startups, product roles  
**Font:** Helvetica Neue / Arial throughout  
**Accent:** Primary blue (#2563EB) for section titles and name underline

### Visual Structure
```
+--------------------------------------------------+
|                                                  |
|              J O H N   D O E                      |
|              =================                    |
|    San Francisco, CA  |  john@email.com           |
|    linkedin.com/in/johndoe  |  (555) 123-4567     |
|                                                  |
|  =================================================|
|  SUMMARY                                         |
|  =================================================|
|  Product Manager with 5+ years of experience...  |
|                                                  |
|  =================================================|
|  EXPERIENCE                                      |
|  =================================================|
|                                                  |
|  Senior Product Manager                          |
|  TechCorp — San Francisco, CA                    |
|  January 2020 – Present                          |
|                                                  |
|  • Led cross-functional team of 12 to launch     |
|    AI-powered recommendation engine, increasing    |
|    user engagement by 35%                        |
|  • Defined product roadmap using Agile/Scrum...    |
|                                                  |
|  =================================================|
|  SKILLS                                          |
|  =================================================|
|  [Product Strategy] [Agile] [SQL] [Figma]        |
|  [Data Analysis] [A/B Testing] [Python]          |
|                                                  |
+--------------------------------------------------+
```

### CSS Highlights (`templates/layout_2_modern.css`)

```css
@page {
    size: letter;
    margin: 0.6in;
}

body {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #1f2937;
}

.name {
    font-size: 24pt;
    font-weight: 300;
    letter-spacing: 3pt;
    text-align: center;
    text-transform: uppercase;
    margin-bottom: 4pt;
}

.name-underline {
    border: none;
    border-top: 2pt solid #2563EB;
    width: 60%;
    margin: 0 auto 8pt auto;
}

.contact-line {
    text-align: center;
    font-size: 9pt;
    color: #4b5563;
    margin-bottom: 14pt;
}

.section-title {
    font-size: 11pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5pt;
    color: #2563EB;
    margin: 14pt 0 6pt 0;
    border-bottom: 1pt solid #e5e7eb;
    padding-bottom: 3pt;
}

.job-title {
    font-size: 11pt;
    font-weight: 600;
    color: #111827;
}

.job-company {
    font-weight: 400;
    color: #4b5563;
}

.job-meta {
    font-size: 9pt;
    color: #6b7280;
    font-style: italic;
    margin-bottom: 5pt;
}

.skills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
}

.skill-tag {
    background: #eff6ff;
    border: 0.5pt solid #dbeafe;
    padding: 2pt 6pt;
    font-size: 8.5pt;
    color: #1e40af;
    border-radius: 2pt;
}
```

---

## Layout 3: Minimal

**Style:** Ultra-clean, typography-focused, no lines or boxes  
**Best For:** Design, creative, marketing, editorial roles  
**Font:** Helvetica Neue Light / Arial  
**Accent:** None (pure typography hierarchy)

### Visual Structure
```
+--------------------------------------------------+
|                                                  |
|  John Doe                                        |
|                                                  |
|  john@email.com                                  |
|  (555) 123-4567                                  |
|  New York, NY                                    |
|                                                  |
|  Product designer and developer with 8 years...  |
|                                                  |
|  Experience                                      |
|                                                  |
|  Design Lead, Creative Agency                    |
|  2019 – Present                                  |
|  Shaped brand identity for Fortune 500 clients.  |
|  Led design system implementation across 12      |
|  product teams.                                  |
|                                                  |
|  Senior Designer, Startup Inc                    |
|  2016 – 2019                                     |
|  Crafted user interfaces for mobile banking app  |
|  serving 2M+ users.                              |
|                                                  |
|  Education                                       |
|                                                  |
|  MFA Design, Rhode Island School of Design       |
|  2014 – 2016                                     |
|                                                  |
|  Skills                                          |
|                                                  |
|  Figma  Sketch  Adobe CC  HTML/CSS  User Research |
|  Design Systems  Prototyping  Brand Strategy     |
|                                                  |
+--------------------------------------------------+
```

### CSS Highlights (`templates/layout_3_minimal.css`)

```css
@page {
    size: letter;
    margin: 0.8in;
}

body {
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #222222;
    font-weight: 300;
}

.name {
    font-size: 20pt;
    font-weight: 400;
    margin-bottom: 8pt;
    letter-spacing: 0.5pt;
}

.contact-block {
    font-size: 9pt;
    color: #666666;
    line-height: 1.6;
    margin-bottom: 16pt;
}

.section-title {
    font-size: 9pt;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 2pt;
    color: #888888;
    margin: 18pt 0 8pt 0;
}

.job-title {
    font-size: 10.5pt;
    font-weight: 400;
    color: #000000;
}

.job-company {
    color: #555555;
}

.job-meta {
    font-size: 8.5pt;
    color: #999999;
    margin: 2pt 0 6pt 0;
}

.bullet-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.bullet-list li {
    margin-bottom: 4pt;
    padding-left: 0;
}

.bullet-list li::before {
    content: "- ";
    color: #aaaaaa;
}

.skills-text {
    line-height: 1.8;
    word-spacing: 8pt;
}
```

---

## Layout 4: Professional

**Style:** Two-tone header, structured grid feel  
**Best For:** Consulting, management, operations, sales  
**Font:** Arial / Helvetica  
**Accent:** Dark navy (#1e3a5f) header band with white text

### Visual Structure
```
+--------------------------------------------------+
|##################################################|
|#                                                #|
|#  JOHN DOE                                      #|
|#  Senior Operations Manager                     #|
|#                                                #|
|#  john@email.com | (555) 123-4567 | LinkedIn   #|
|#  Boston, MA                                    #|
|#                                                #|
|##################################################|
|                                                  |
|  SUMMARY                                         |
|  ----------------------------------------------  |
|  Operations leader with 10+ years scaling...     |
|                                                  |
|  EXPERIENCE                                      |
|  ----------------------------------------------  |
|                                                  |
|  Senior Operations Manager | Global Corp         |
|  Boston, MA | March 2018 – Present              |
|  • Managed $5M annual budget, reducing costs...  |
|  • Led team of 25 across 3 regional offices      |
|                                                  |
|  +------------------+  +-----------------------+  |
|  | EDUCATION        |  | SKILLS                |  |
|  | --------------   |  | -------------------   |  |
|  | MBA, Harvard     |  | Operations Management |  |
|  | 2010 – 2012      |  | Budgeting • Six Sigma |  |
|  |                  |  | • Supply Chain • SQL  |  |
|  +------------------+  +-----------------------+  |
|                                                  |
+--------------------------------------------------+
```

### CSS Highlights (`templates/layout_4_professional.css`)

```css
@page {
    size: letter;
    margin: 0;
}

body {
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #333333;
    margin: 0;
}

.header-band {
    background: #1e3a5f;
    color: #ffffff;
    padding: 20pt 0.75in;
    margin-bottom: 14pt;
}

.name {
    font-size: 22pt;
    font-weight: bold;
    margin: 0 0 4pt 0;
    letter-spacing: 0.5pt;
}

.title-tagline {
    font-size: 11pt;
    font-weight: 300;
    margin-bottom: 8pt;
    color: #b8d4f0;
}

.contact-line {
    font-size: 9pt;
    color: #d0e0f0;
}

.content-area {
    padding: 0 0.75in;
}

.section-title {
    font-size: 11pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1pt;
    color: #1e3a5f;
    border-bottom: 1pt solid #1e3a5f;
    padding-bottom: 3pt;
    margin: 12pt 0 8pt 0;
}

.two-column {
    display: flex;
    gap: 20pt;
}

.column {
    flex: 1;
}

.job-title {
    font-weight: bold;
    font-size: 10.5pt;
    color: #1e3a5f;
}
```

---

## Layout 5: Compact

**Style:** Dense, information-rich, guaranteed single-page  
**Best For:** 10+ year careers, academia, medical, government  
**Font:** Arial Narrow / Helvetica Condensed  
**Accent:** Minimal (thin gray lines)

### Visual Structure
```
+--------------------------------------------------+
|JOHN DOE | Senior Software Engineer | 12+ Years  |
|john@email.com | (555) 123-4567 | linkedin.com/in|
|San Francisco, CA                                 |
|--------------------------------------------------|
|SUMMARY: Full-stack engineer specializing in...    |
|--------------------------------------------------|
|EXPERIENCE                                         |
|Staff Engineer | BigTech | SF | 2021-Pres          |
|• Architected distributed system handling 10M req/day|
|• Mentored team of 8 engineers on best practices    |
|Senior Engineer | MidTech | NYC | 2017-2021       |
|• Led migration from monolith to microservices      |
|• Reduced infrastructure costs by 30%              |
|Engineer | SmallTech | Austin | 2013-2017         |
|• Built core payment processing system             |
|--------------------------------------------------|
|EDUCATION: MS CS, MIT, 2011-2013 | BS CS, UT, 07-11|
|--------------------------------------------------|
|SKILLS: Python Go Kubernetes AWS PostgreSQL React  |
|Docker gRPC Redis Kafka Terraform CI/CD Microservices
|--------------------------------------------------|
|CERTS: AWS Solutions Architect | CKA | PMP          |
+--------------------------------------------------+
```

### CSS Highlights (`templates/layout_5_compact.css`)

```css
@page {
    size: letter;
    margin: 0.4in;
}

body {
    font-family: 'Arial Narrow', 'Arial', 'Helvetica', sans-serif;
    font-size: 9pt;
    line-height: 1.25;
    color: #000000;
}

.header-compact {
    margin-bottom: 6pt;
}

.name-compact {
    font-size: 14pt;
    font-weight: bold;
    display: inline;
}

.header-meta {
    font-size: 9pt;
    color: #444444;
}

.contact-compact {
    font-size: 8.5pt;
    color: #555555;
    margin-bottom: 4pt;
}

.divider-thin {
    border: none;
    border-top: 0.5pt solid #aaaaaa;
    margin: 4pt 0;
}

.section-title-compact {
    font-size: 9pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    margin: 6pt 0 3pt 0;
}

.job-compact {
    margin-bottom: 4pt;
}

.job-header-compact {
    font-weight: bold;
    font-size: 9pt;
}

.job-meta-compact {
    font-size: 8pt;
    color: #555555;
    font-style: italic;
}

.bullet-list-compact {
    margin: 2pt 0;
    padding-left: 12pt;
}

.bullet-list-compact li {
    margin-bottom: 1pt;
}

.skills-compact {
    word-spacing: 4pt;
}
```

---

## Template Engine Integration

### Python Rendering Code (`core/pdf_engine.py`)

```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

def generate_pdf(resume_data, layout_number, output_path):
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    template_name = f"layout_{layout_number}_{get_layout_name(layout_number)}.html"
    template = env.get_template(template_name)

    html_string = template.render(resume=resume_data)

    css_name = f"layout_{layout_number}_{get_layout_name(layout_number)}.css"
    css_path = os.path.join(template_dir, css_name)

    HTML(string=html_string).write_pdf(
        output_path,
        stylesheets=[CSS(filename=css_path)] if os.path.exists(css_path) else []
    )

    return output_path

def get_layout_name(n):
    names = {1: "classic", 2: "modern", 3: "minimal", 4: "professional", 5: "compact"}
    return names.get(n, "modern")

def get_layout_preview_html(resume_data, layout_number):
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template_name = f"layout_{layout_number}_{get_layout_name(layout_number)}.html"
    template = env.get_template(template_name)
    return template.render(resume=resume_data)
```

---

## Layout Selection Metadata

| # | File Prefix | Name | Font | Margins | Density | Best For |
|---|-------------|------|------|---------|---------|----------|
| 1 | layout_1_classic | Classic | Georgia + Helvetica | 0.75in | Medium | Conservative industries |
| 2 | layout_2_modern | Modern | Helvetica | 0.6in | Medium | Tech, startups |
| 3 | layout_3_minimal | Minimal | Helvetica Light | 0.8in | Low | Creative, design |
| 4 | layout_4_professional | Professional | Arial | 0.75in | Medium | Consulting, management |
| 5 | layout_5_compact | Compact | Arial Narrow | 0.4in | High | Long careers, academia |

---

## ATS Verification Checklist

For each layout, verify:
- [ ] All text selectable in PDF reader
- [ ] No images containing text
- [ ] Single column (no side-by-side content that confuses parsers)
- [ ] Standard fonts embedded or system-standard
- [ ] No headers/footers with critical contact info
- [ ] Section titles use common ATS keywords (Experience, Education, Skills)
- [ ] Dates in consistent, parseable format
- [ ] File size under 2MB
