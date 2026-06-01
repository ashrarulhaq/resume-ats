import pytest
from resume_tailor.core.keyword_matcher import extract_keywords_from_jd, calculate_match_score

def test_extract_keywords_basic():
    """Test that keywords are extracted from a job description."""
    jd = "Looking for a Python developer with AWS experience."
    keywords = extract_keywords_from_jd(jd)
    assert "Python" in keywords or "python" in [k.lower() for k in keywords]
    assert "AWS" in keywords or "aws" in [k.lower() for k in keywords]

def test_extract_keywords_filters_stopwords():
    """Test that common stopwords are filtered out."""
    jd = "We are looking for a candidate with the ability to work in a team"
    keywords = extract_keywords_from_jd(jd)
    stopwords_found = [k for k in keywords if k.lower() in ['the', 'a', 'an', 'is', 'are', 'we', 'to', 'in', 'with']]
    assert len(stopwords_found) == 0

def test_extract_keywords_max_limit():
    """Test that keywords are limited to 20."""
    jd = " ".join([f"Word{i}" for i in range(50)])
    keywords = extract_keywords_from_jd(jd)
    assert len(keywords) <= 20

def test_extract_keywords_empty():
    """Test with empty job description."""
    keywords = extract_keywords_from_jd("")
    assert keywords == []

def test_extract_keywords_filters_filler_words():
    """Test that filler words like 'plus', 'including' are filtered."""
    jd = "Experience in Python plus including using AWS and Docker"
    keywords = extract_keywords_from_jd(jd)
    lower = [k.lower() for k in keywords]
    assert 'plus' not in lower
    assert 'including' not in lower

def test_calculate_match_score_basic():
    """Test basic score calculation."""
    score = calculate_match_score("Python JavaScript React", ["Python", "Java"])
    assert score['score'] == 50
    assert "Python" in score['matched']
    assert "Java" in score['missing']

def test_calculate_match_score_empty_keywords():
    """Test with empty keywords."""
    score = calculate_match_score("Python JavaScript", [])
    assert score['score'] == 0
    assert score['matched'] == []
    assert score['missing'] == []

def test_calculate_match_score_case_insensitive():
    """Test case-insensitive matching."""
    score = calculate_match_score("I know PYTHON", ["Python"])
    assert score['score'] == 100

def test_calculate_match_score_no_partial_match():
    """Test that 'Java' does not match 'JavaScript'."""
    score = calculate_match_score("I know JavaScript", ["Java"])
    assert score['score'] == 0
    assert "Java" in score['missing']

def test_calculate_match_score_all_match():
    """Test perfect score."""
    score = calculate_match_score("Python JavaScript React", ["Python", "JavaScript", "React"])
    assert score['score'] == 100
    assert score['missing'] == []
