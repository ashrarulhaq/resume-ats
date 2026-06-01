from copy import deepcopy
from thefuzz import fuzz
from typing import List, Tuple, Dict, Any
import re

def extract_skills_from_text(text: str) -> List[str]:
    """Naive skill extraction: look for capitalized technical terms, comma-separated lists under 'Skills' section."""
    skills = []

    # Look for a Skills section
    skills_section_match = re.search(r'(?i)^\s*skills?\s*:?\s*\n(.+?)(?:\n\s*\n|\n\s*[A-Z]|$)', text, re.MULTILINE | re.DOTALL)
    if skills_section_match:
        skills_text = skills_section_match.group(1)
        # Split by common delimiters: comma, semicolon, newline
        potential_skills = re.split(r'[,;\n]', skills_text)
        for skill in potential_skills:
            skill = skill.strip()
            # Filter out empty strings and very short strings
            if skill and len(skill) > 1:
                skills.append(skill)

    # Also look for capitalized technical terms throughout the text
    # This is a simple approach - looking for words that are mostly uppercase or title case
    words = re.findall(r'\b[A-Z][a-zA-Z0-9\+#\.]+\b', text)
    for word in words:
        if len(word) > 1 and word not in ['I', 'A']:  # Filter out common false positives
            skills.append(word)

    # Deduplicate while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)

    return unique_skills

def validate_skills(original_text: str, tailored_resume: Dict[str, Any], threshold: int = 80) -> Tuple[bool, List[str]]:
    """
    Check that every skill in tailored_resume['skills'] exists in original_text.
    Uses fuzzy matching (fuzz.partial_ratio).
    Returns: (is_valid, list_of_invalid_skills)
    """
    if 'skills' not in tailored_resume or not isinstance(tailored_resume['skills'], list):
        return True, []  # No skills to validate

    original_skills = extract_skills_from_text(original_text)
    tailored_skills = tailored_resume['skills']

    invalid_skills = []

    for tailored_skill in tailored_skills:
        # Find best match in original skills
        best_score = 0
        for original_skill in original_skills:
            score = fuzz.partial_ratio(tailored_skill.lower(), original_skill.lower())
            if score > best_score:
                best_score = score

        if best_score < threshold:
            invalid_skills.append(tailored_skill)

    return len(invalid_skills) == 0, invalid_skills

def _extract_dates_from_text(text: str) -> List[str]:
    """Extract date-like patterns from text."""
    # Pattern for dates like "Jan 2020 - Mar 2022" or "2020-2022" or "Jan 2020 – Present"
    date_patterns = [
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]\s*(?:Present|Current|Now)\b',
        r'\b\d{4}\s*[-–]\s*\d{4}\b',
        r'\b\d{4}\s*[-–]\s*(?:Present|Current|Now)\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)

    return dates

def validate_dates(original_text: str, tailored_resume: Dict[str, Any]) -> bool:
    """Verify all dates in experience/education exist in original text."""
    original_dates = _extract_dates_from_text(original_text)
    original_text_lower = original_text.lower()

    # Also extract normalized year tokens for fuzzy matching
    original_years = set(re.findall(r'\b(?:19|20)\d{2}\b', original_text))

    def _date_is_valid(date_str: str) -> bool:
        """Check if a date or its component years appear in the original."""
        if date_str.lower() in original_text_lower:
            return True
        # Extract years from the date string and check they exist in original
        years_in_date = re.findall(r'\b(?:19|20)\d{2}\b', date_str)
        return all(y in original_years for y in years_in_date)

    # Check experience dates
    if 'experience' in tailored_resume and isinstance(tailored_resume['experience'], list):
        for exp in tailored_resume['experience']:
            if 'dates' in exp and isinstance(exp['dates'], str):
                if not _date_is_valid(exp['dates']):
                    return False

    # Check education dates
    if 'education' in tailored_resume and isinstance(tailored_resume['education'], list):
        for edu in tailored_resume['education']:
            if 'dates' in edu and isinstance(edu['dates'], str):
                if not _date_is_valid(edu['dates']):
                    return False

    return True

def _extract_companies_from_text(text: str) -> List[str]:
    """Extract potential company names from text."""
    # Look for patterns that might indicate company names
    # This is tricky without NER, so we'll use a simple approach
    lines = text.split('\n')
    companies = []

    # Common company suffixes
    company_suffixes = ['Inc', 'LLC', 'Corp', 'Corporation', 'Company', 'Co', 'Ltd', 'Limited', 'PLC', 'Group']

    for line in lines:
        line = line.strip()
        # Look for lines that might contain company names
        # Often experience lines have format: "Company Name - Title - Dates"
        # Or just contain company names with suffixes
        for suffix in company_suffixes:
            if suffix in line:
                # Extract potential company name (simplified)
                # This is a naive approach
                companies.append(line)
                break

    return companies

def validate_companies(original_text: str, tailored_resume: Dict[str, Any]) -> bool:
    """Verify all company names in experience exist in original text (substring check)."""
    original_text_lower = original_text.lower()

    if 'experience' in tailored_resume and isinstance(tailored_resume['experience'], list):
        for exp in tailored_resume['experience']:
            if 'company' in exp and isinstance(exp['company'], str):
                company = exp['company'].strip()
                if not company:
                    return False
                if company.lower() not in original_text_lower:
                    return False

    return True

def run_truth_guardrails(original_text: str, tailored_resume: Dict[str, Any], threshold: int = 80) -> Dict[str, Any]:
    """
    Run all validations.
    If invalid skills found: remove them from tailored_resume['skills'].
    If invalid experiences found: flag for user review.
    Returns cleaned resume dict + validation report.
    Deep-copies the input to avoid mutating the caller's dict.
    """
    tailored_resume = deepcopy(tailored_resume)

    validation_report = {
        'skills_valid': True,
        'invalid_skills': [],
        'dates_valid': True,
        'companies_valid': True,
        'warnings': []
    }

    # Validate skills
    skills_valid, invalid_skills = validate_skills(original_text, tailored_resume, threshold=threshold)
    validation_report['skills_valid'] = skills_valid
    validation_report['invalid_skills'] = invalid_skills

    if not skills_valid and invalid_skills:
        # Remove invalid skills from tailored resume
        if 'skills' in tailored_resume and isinstance(tailored_resume['skills'], list):
            tailored_resume['skills'] = [
                skill for skill in tailored_resume['skills']
                if skill not in invalid_skills
            ]
        validation_report['warnings'].append(
            f"Removed {len(invalid_skills)} invalid skills: {', '.join(invalid_skills)}"
        )

    # Validate dates (placeholder - always returns True for now)
    dates_valid = validate_dates(original_text, tailored_resume)
    validation_report['dates_valid'] = dates_valid
    if not dates_valid:
        validation_report['warnings'].append("Some dates may not match original resume")

    # Validate companies (placeholder - always returns True for now)
    companies_valid = validate_companies(original_text, tailored_resume)
    validation_report['companies_valid'] = companies_valid
    if not companies_valid:
        validation_report['warnings'].append("Some company names may not match original resume")

    return {
        'cleaned_resume': tailored_resume,
        'validation_report': validation_report
    }