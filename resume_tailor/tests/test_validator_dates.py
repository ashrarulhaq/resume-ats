import pytest
from resume_tailor.core.validator import validate_dates, validate_companies, run_truth_guardrails

# --- Date validation tests ---

def test_validate_dates_valid():
    """Test that matching dates pass validation."""
    original = "Worked from Jan 2020 to Mar 2022 at Tech Corp"
    tailored = {"experience": [{"dates": "Jan 2020 - Mar 2022"}]}
    assert validate_dates(original, tailored) is True

def test_validate_dates_invalid_years():
    """Test that dates with years NOT in original text fail validation.
    This was the critical bug where regex group capture returned only '20'
    for all years, causing all dates to pass."""
    original = "Worked from Jan 2020 to Mar 2022 at Tech Corp"
    tailored = {"experience": [{"dates": "Jan 2019 - Dec 2025"}]}
    assert validate_dates(original, tailored) is False

def test_validate_dates_edu_valid():
    """Test education date validation passes."""
    original = "BS Computer Science, MIT, 2013-2017"
    tailored = {"education": [{"dates": "2013-2017"}]}
    assert validate_dates(original, tailored) is True

def test_validate_dates_edu_invalid():
    """Test education date validation fails for fake dates."""
    original = "BS Computer Science, MIT, 2013-2017"
    tailored = {"education": [{"dates": "2014-2019"}]}
    assert validate_dates(original, tailored) is False

def test_validate_dates_no_experience():
    """Test with no experience/education."""
    assert validate_dates("some text", {}) is True

def test_validate_dates_no_dates_field():
    """Test with experience that has no dates field."""
    original = "2020-2022"
    tailored = {"experience": [{"title": "Dev", "company": "Co"}]}
    assert validate_dates(original, tailored) is True

def test_validate_dates_distinguishes_adjacent_years():
    """Test that year 2020 is NOT confused with 2021 or 2019."""
    original = "2020"
    tailored = {"experience": [{"dates": "2021"}]}
    assert validate_dates(original, tailored) is False

def test_validate_dates_year_boundary():
    """Test that 1999 and 2023 are distinguished."""
    original = "1999-2023"
    tailored = {"experience": [{"dates": "1999-2023"}]}
    assert validate_dates(original, tailored) is True

    tailored2 = {"experience": [{"dates": "1998-2024"}]}
    assert validate_dates(original, tailored2) is False


# --- Company validation tests ---

def test_validate_companies_valid():
    """Test that existing company names pass."""
    original = "Worked at Tech Corp and Google"
    tailored = {"experience": [{"company": "Tech Corp"}]}
    assert validate_companies(original, tailored) is True

def test_validate_companies_invalid():
    """Test that fake company names fail."""
    original = "Worked at Tech Corp"
    tailored = {"experience": [{"company": "FakeCorp"}]}
    assert validate_companies(original, tailored) is False

def test_validate_companies_empty():
    """Test that empty company names fail validation."""
    original = "Worked at Tech Corp"
    tailored = {"experience": [{"company": ""}]}
    assert validate_companies(original, tailored) is False

def test_validate_companies_whitespace():
    """Test that whitespace-only company names fail validation."""
    original = "Worked at Tech Corp"
    tailored = {"experience": [{"company": "  "}]}
    assert validate_companies(original, tailored) is False

def test_validate_companies_no_experience():
    """Test with no experience."""
    assert validate_companies("some text", {}) is True


# --- Full guardrail tests ---

def test_guardrails_date_validation():
    """Test that full guardrails catch invalid dates."""
    original = "Worked Python at Tech Corp, 2020-2022"
    tailored = {
        "name": "Test",
        "skills": ["Python"],
        "experience": [{"company": "Tech Corp", "title": "Dev", "dates": "2019-2025", "bullets": ["x"]}]
    }
    result = run_truth_guardrails(original, tailored)
    assert result['validation_report']['dates_valid'] is False

def test_guardrails_company_validation():
    """Test that full guardrails catch fake companies."""
    original = "Worked Python at Tech Corp, 2020-2022"
    tailored = {
        "name": "Test",
        "skills": ["Python"],
        "experience": [{"company": "FakeCorp", "title": "Dev", "dates": "2020-2022", "bullets": ["x"]}]
    }
    result = run_truth_guardrails(original, tailored)
    assert result['validation_report']['companies_valid'] is False

def test_guardrails_skills_and_dates_together():
    """Test that all validators run together."""
    original = "Python developer at Google, 2020-2023"
    tailored = {
        "name": "Test",
        "skills": ["Python", "Kubernetes"],
        "experience": [{"company": "Google", "title": "Dev", "dates": "2018-2025", "bullets": ["x"]}]
    }
    result = run_truth_guardrails(original, tailored, threshold=90)
    # Skills: Kubernetes should be invalid
    assert result['validation_report']['skills_valid'] is False
    assert "Kubernetes" in result['validation_report']['invalid_skills']
    # Dates: 2018 and 2025 not in original
    assert result['validation_report']['dates_valid'] is False
    # Companies: Google is in original
    assert result['validation_report']['companies_valid'] is True
