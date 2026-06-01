import pytest
from resume_tailor.core.validator import validate_skills, run_truth_guardrails

def test_validate_skills_valid():
    """Test that valid skills pass validation."""
    original_text = "Python JavaScript React Node.js"
    tailored_resume = {"skills": ["Python", "JavaScript"]}

    is_valid, invalid_skills = validate_skills(original_text, tailored_resume)
    assert is_valid is True
    assert len(invalid_skills) == 0

def test_validate_skills_invalid():
    """Test that invalid skills are detected."""
    original_text = "Python JavaScript"
    tailored_resume = {"skills": ["Python", "Kubernetes"]}

    is_valid, invalid_skills = validate_skills(original_text, tailored_resume, threshold=90)
    assert is_valid is False
    assert "Kubernetes" in invalid_skills

def test_validate_skills_empty():
    """Test validation with empty skills."""
    original_text = "Some text"
    tailored_resume = {"skills": []}

    is_valid, invalid_skills = validate_skills(original_text, tailored_resume)
    assert is_valid is True

def test_run_truth_guardrails():
    """Test the full truth guardrails pipeline."""
    original_text = "Python JavaScript React"
    tailored_resume = {
        "name": "Test User",
        "skills": ["Python", "Kubernetes"],
        "experience": []
    }

    result = run_truth_guardrails(original_text, tailored_resume)
    assert 'cleaned_resume' in result
    assert 'validation_report' in result

def test_run_truth_guardrails_removes_invalid_skills():
    """Test that invalid skills are removed from cleaned resume."""
    original_text = "Python JavaScript React"
    tailored_resume = {
        "name": "Test User",
        "skills": ["Python", "Kubernetes", "AWS"],
        "experience": []
    }

    result = run_truth_guardrails(original_text, tailored_resume, threshold=90)
    cleaned_skills = result['cleaned_resume']['skills']
    # Kubernetes and AWS should be removed
    assert "Python" in cleaned_skills
    assert "Kubernetes" not in cleaned_skills