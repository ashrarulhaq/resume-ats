import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from resume_tailor.core.pdf_engine import render_html, get_layout_preview_html, generate_pdf

def test_render_html():
    """Test that HTML rendering works with sample data."""
    resume_data = {
        "name": "John Doe",
        "contact": {
            "email": "john@example.com",
            "phone": "123-456-7890"
        },
        "summary": "Experienced developer",
        "skills": ["Data Analysis & Reporting: Python, JavaScript"],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "dates": "2020 - Present",
                "location": "Remote",
                "bullets": ["Built web applications"]
            }
        ],
        "education": []
    }

    html = render_html(resume_data, 1)
    assert "John Doe" in html
    assert "john@example.com" in html
    assert "<strong>Data Analysis &amp; Reporting:</strong> Python, JavaScript" in html or "<strong>Data Analysis & Reporting:</strong> Python, JavaScript" in html


def test_get_layout_preview_html():
    """Test that preview HTML generation works."""
    resume_data = {
        "name": "Jane Smith",
        "contact": {},
        "skills": ["React"],
        "experience": [],
        "education": []
    }

    html = get_layout_preview_html(resume_data, 1)
    assert "Jane Smith" in html


def test_generate_pdf_creates_non_empty_pdf():
    resume_data = {
        "name": "Test User",
        "contact": {"email": "test@test.com"},
        "summary": "A test summary",
        "skills": ["Python"],
        "experience": [],
        "education": []
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "resume.pdf"
        result_path = generate_pdf(resume_data, 1, str(output_path))

        assert result_path == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        with output_path.open("rb") as f:
            assert f.read(4) == b"%PDF"


def test_generate_pdf_classic_layout_works():
    resume_data = {
        "name": "Classic User",
        "contact": {
            "location": "Remote",
            "phone": "123-456-7890",
            "email": "classic@example.com",
        },
        "summary": "Classic layout smoke test",
        "skills": ["Python"],
        "experience": [],
        "education": [],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "classic_resume.pdf"
        result_path = generate_pdf(resume_data, 1, str(output_path))

        assert result_path == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_render_html_all_sections():
    """Test that all sections render correctly."""
    resume_data = {
        "name": "Test User",
        "contact": {"email": "test@test.com", "phone": "555-1234", "linkedin": "testuser", "location": "NYC"},
        "summary": "A test summary",
        "skills": ["Data Analysis: Python, SQL", "Tools: Excel, Power BI"],
        "experience": [
            {
                "title": "Dev",
                "company": "Co",
                "dates": "2020-2022",
                "location": "Remote",
                "bullets": ["Did work"]
            }
        ],
        "education": [
            {"school": "MIT", "degree": "BS", "dates": "2016-2020"}
        ],
        "certifications": ["AWS - 2024"],
        "projects": []
    }
    html = render_html(resume_data, 1)
    assert "Test User" in html
    assert "test@test.com" in html
    assert "PROFESSIONAL SUMMARY" in html or "Professional Summary" in html
    assert "EDUCATION" in html or "Education" in html
    assert "CORE COMPETENCIES" in html or "Core Competencies" in html
    assert "EXPERIENCE" in html or "Experience" in html
    assert "CERTIFICATIONS" in html or "Certifications" in html
