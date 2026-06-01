"""
FastAPI backend for Resume Tailor.
Wraps the existing Python core modules from the parent directory.
"""

import sys
import os

# Add repo root to sys.path so we can import from resume_tailor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tempfile
import logging
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Streamlit shim: openrouter_backend uses st.session_state for API key/model.
# We install a mock before importing so the import succeeds without Streamlit,
# and we inject the values into session_state before each tailor call.
# ---------------------------------------------------------------------------
import types

_st = types.ModuleType("streamlit")


class _SessionState(dict):
    """Minimal dict-like session state compatible with st.session_state usage."""
    def get(self, key, default=None):
        return super().get(key, default)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


_st.session_state = _SessionState()
sys.modules["streamlit"] = _st

# Now import the core modules
from resume_tailor.core.parser import parse_resume
from resume_tailor.core.keyword_matcher import extract_keywords_from_jd, calculate_match_score
from resume_tailor.core.validator import run_truth_guardrails
from resume_tailor.core.pdf_engine import get_layout_preview_html, generate_pdf
from resume_tailor.core.openrouter_backend import tailor_resume as _tailor_resume_streamlit
from resume_tailor.models.resume_schema import Resume

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Resume Tailor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("resume_tailor_api")

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class ExtractKeywordsRequest(BaseModel):
    job_description: str


class CalculateMatchRequest(BaseModel):
    resume_text: str
    keywords: List[str]


class TailorResumeRequest(BaseModel):
    resume_text: str
    job_description: str


class ValidateResumeRequest(BaseModel):
    original_text: str
    tailored_resume: dict


class PreviewHtmlRequest(BaseModel):
    resume_data: dict
    layout_number: int = 1


class GeneratePdfRequest(BaseModel):
    resume_data: dict
    layout_number: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/parse-resume")
async def parse_resume_endpoint(
    file: UploadFile = File(...),
    fileType: str = Form(...),
):
    """Accepts a multipart form upload, saves to a temp file, parses it, returns extracted text."""
    suffix_map = {
        "pdf": ".pdf",
        "docx": ".docx",
        "doc": ".doc",
        "txt": ".txt",
    }
    suffix = suffix_map.get(fileType.lower(), ".tmp")

    tmp_path = None
    try:
        # Write uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        text = parse_resume(tmp_path, fileType)

        if not text:
            raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file.")

        return {"success": True, "text": text}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


@app.post("/api/extract-keywords")
async def extract_keywords_endpoint(req: ExtractKeywordsRequest):
    """Extract keywords from a job description."""
    try:
        keywords = extract_keywords_from_jd(req.job_description)
        return {"success": True, "keywords": keywords}
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate-match")
async def calculate_match_endpoint(req: CalculateMatchRequest):
    """Calculate match score between resume text and JD keywords."""
    try:
        result = calculate_match_score(req.resume_text, req.keywords)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error calculating match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tailor-resume")
async def tailor_resume_endpoint(
    req: TailorResumeRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_model: Optional[str] = Header(None, alias="X-Model"),
):
    """
    Tailor a resume to a job description using OpenRouter LLM.
    Reads API key and model from X-API-Key and X-Model headers,
    sets them as env vars and in the Streamlit shim session state,
    then calls the core tailor_resume function.
    """
    if not x_api_key:
        raise HTTPException(status_code=400, detail="X-API-Key header is required.")

    # Set environment variables (for any code that reads from os.environ)
    os.environ["OPENROUTER_API_KEY"] = x_api_key
    if x_model:
        os.environ["OPENROUTER_MODEL"] = x_model

    # Inject into the Streamlit shim so the core module can read them
    _st.session_state["openrouter_api_key"] = x_api_key
    _st.session_state["openrouter_model"] = x_model or "openrouter/gpt-3.5-turbo"

    try:
        tailored_resume = _tailor_resume_streamlit(req.resume_text, req.job_description)
        return {"success": True, "tailored_resume": tailored_resume}
    except Exception as e:
        logger.error(f"Error tailoring resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-resume")
async def validate_resume_endpoint(req: ValidateResumeRequest):
    """Run truth guardrails: validate skills, dates, companies."""
    try:
        result = run_truth_guardrails(req.original_text, req.tailored_resume)
        return {
            "success": True,
            "result": result,
            "validationReport": result.get("validation_report"),
            "cleanedResume": result.get("cleaned_resume"),
            "validation_report": result.get("validation_report"),
            "cleaned_resume": result.get("cleaned_resume"),
        }
    except Exception as e:
        logger.error(f"Error validating resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/get-preview-html")
async def get_preview_html_endpoint(req: PreviewHtmlRequest):
    """Generate an HTML preview of the resume for a given layout."""
    try:
        html = get_layout_preview_html(req.resume_data, req.layout_number)
        return {"success": True, "html": html}
    except Exception as e:
        logger.error(f"Error generating preview HTML: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _cleanup_file(path: str):
    """Background task to delete a temp file after the response is sent."""
    try:
        if os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass


@app.post("/api/generate-pdf")
async def generate_pdf_endpoint(req: GeneratePdfRequest, background_tasks: BackgroundTasks):
    """Generate a PDF file for the resume and return it as a download."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        output_path = generate_pdf(req.resume_data, req.layout_number, tmp_path)

        # Schedule cleanup after the response is sent
        background_tasks.add_task(_cleanup_file, output_path)

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename="tailored_resume.pdf",
        )
    except Exception as e:
        # Clean up on error immediately
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
