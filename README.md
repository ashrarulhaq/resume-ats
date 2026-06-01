# Resume Tailor

A desktop web app that tailors your resume to match job descriptions using local Gemini CLI.

## Features

- Upload resume (PDF, DOCX, TXT)
- Paste job description
- AI-powered tailoring with truth guardrails
- 5 ATS-friendly PDF layouts
- Keyword match score
- 100% local processing (no API keys needed)

## Prerequisites

1. **Python 3.10+** installed
2. **OpenRouter API key** (configured in the app UI):
   - Get an API key from https://openrouter.ai/keys
   - Enter it in the OpenRouter Configuration sidebar when running the app
3. **WeasyPrint system dependencies**:
   - **Windows**: Install GTK+ for Windows
   - **macOS**: `brew install pango cairo gdk-pixbuf libffi`
   - **Ubuntu/Debian**: `sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`

## Installation

```bash
# Clone the repository
cd resume-ats

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the app
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Project Structure

```
resume_tailor/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── core/                     # Core modules
│   ├── parser.py            # PDF/DOCX/TXT text extraction
│   ├── gemini_backend.py    # Gemini CLI wrapper
│   ├── validator.py         # Truth guardrails
│   ├── keyword_matcher.py   # JD keyword matching
│   └── pdf_engine.py        # PDF generation
├── models/                   # Pydantic models
│   └── resume_schema.py     # Resume JSON schema
├── templates/               # HTML/CSS layout templates
│   ├── layout_1_classic.*
│   ├── layout_2_modern.*
│   ├── layout_3_minimal.*
│   ├── layout_4_professional.*
│   └── layout_5_compact.*
├── prompts/                 # Gemini prompt templates
│   ├── tailor_resume.txt
│   └── extract_structure.txt
└── tests/                   # Unit tests
    ├── test_parser.py
    ├── test_validator.py
    └── test_pdf_engine.py
```

## Testing

```bash
# Run tests
pytest resume_tailor/tests/

# Run with coverage
pytest resume_tailor/tests/ --cov=resume_tailor
```

## Truth Guardrails

The app enforces strict truthfulness:
- Skills in output must exist in original resume (fuzzy match)
- Company names, titles, dates preserved exactly
- Invalid skills are automatically removed
- User is warned about any modifications

## License

MIT