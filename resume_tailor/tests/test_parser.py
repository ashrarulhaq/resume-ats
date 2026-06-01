import pytest
import tempfile
import os
from resume_tailor.core.parser import extract_text_from_txt, parse_resume

def test_parse_resume_txt():
    """Test parsing a simple TXT file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test resume content\nWith multiple lines")
        temp_path = f.name

    result = parse_resume(temp_path, "txt")
    assert result == "Test resume content\nWith multiple lines"

    os.unlink(temp_path)

def test_parse_resume_pdf_unsupported():
    """Test that unsupported file types return empty string."""
    result = parse_resume("nonexistent.pdf", "xyz")
    assert result == ""

def test_parse_resume_nonexistent_file():
    """Test that parsing a nonexistent file returns empty string."""
    result = parse_resume("nonexistent.txt", "txt")
    assert result == ""