# Resume Tailor

AI-powered resume optimization using the Mistral API. 100% truthful. ATS-ready PDFs.

## Prerequisites

1. **Python 3.10+**
2. **Mistral API key** entered in the app sidebar
3. **WeasyPrint system dependencies**
   - **macOS:** `brew install pango cairo gdk-pixbuf libffi`
   - **Ubuntu/Debian:** `sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
   - **Windows:** See the WeasyPrint Windows install guide

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Upload your resume as PDF, DOCX, or TXT
2. Paste the job description
3. Enter your Mistral API key in the sidebar
4. Click `Tailor Resume`
5. Review the result, choose a layout, and export the PDF

## Features

- Local resume parsing
- Mistral-powered tailoring
- Truth guardrails
- 5 ATS-friendly PDF layouts
- Keyword match scoring
