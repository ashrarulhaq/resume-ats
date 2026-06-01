import logging
import pdfplumber
import docx
import os
import re

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        # Clean excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Truncate if too long
        if len(text) > 20000:
            text = text[:20000] + "\n... [truncated]"
        return text.strip()
    except Exception as e:
        # Return empty string with warning (could log, but for simplicity return empty)
        logger.warning(f"Failed to extract text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        # Clean excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Truncate if too long
        if len(text) > 20000:
            text = text[:20000] + "\n... [truncated]"
        return text.strip()
    except Exception as e:
        logger.warning(f"Failed to extract text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path: str) -> str:
    """Read plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        # Clean excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Truncate if too long
        if len(text) > 20000:
            text = text[:20000] + "\n... [truncated]"
        return text.strip()
    except Exception as e:
        logger.warning(f"Failed to read text file: {e}")
        return ""

def parse_resume(file_path: str, file_type: str) -> str:
    """Router: dispatch to correct extractor based on file extension."""
    if not os.path.exists(file_path):
        return ""
    file_type = file_type.lower()
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:
        # Unsupported type
        logger.warning(f"Unsupported file type: {file_type}")
        return ""