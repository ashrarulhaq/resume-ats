import re
from typing import List, Dict

def extract_keywords_from_jd(job_description: str) -> List[str]:
    """
    Extract top technical/role keywords from job description.
    Simple implementation: extract nouns and technical terms.
    For MVP, we'll extract words that are likely to be skills/technologies.
    """
    # Convert to lowercase for processing
    text = job_description.lower()

    # Define common stopwords to filter out
    stopwords = set([
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
        'could', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'this', 'that', 'these', 'those', 'as', 'from', 'up',
        'down', 'out', 'so', 'then', 'than', 'too', 'very', 'just', 'also',
        'only', 'like', 'what', 'which', 'who', 'whom', 'when', 'where', 'why',
        'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than',
        'too', 'very', 's', 't', 'don', 'now', 'd', 'll', 'm', 'o', 're',
        've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn',
        'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn',
        'wasn', 'weren', 'won', 'wouldn', 'experience', 'years', 'year',
        'required', 'preferred', 'prefer', 'skill', 'skills',
        'ability', 'able', 'work', 'working', 'team', 'teams', 'job', 'role',
        'position', 'looking', 'seek', 'seeking', 'candidate', 'candidates',
        'hire', 'hiring', 'employer', 'employment', 'position', 'title',
        'plus', 'including', 'using', 'based', 'related', 'strong',
        'good', 'great', 'well', 'knowledge', 'understanding', 'familiar',
        'etc', 'eg', 'ie', 'one', 'two', 'three', 'four', 'five', 'six',
        'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third',
        'new', 'old', 'large', 'small', 'high', 'low', 'long', 'short',
        'make', 'made', 'come', 'came', 'take', 'took', 'get', 'got',
        'go', 'went', 'see', 'seen', 'give', 'gave', 'find', 'found',
        'thought', 'say', 'said', 'tell', 'told', 'became',
        'leave', 'left', 'put', 'set', 'keep', 'kept', 'let', 'began', 'begin',
        'seemed', 'helped', 'showed', 'heard', 'played', 'ran', 'moved',
        'tried', 'asked', 'number', 'part', 'area',
        'provide', 'support', 'understand', 'develop', 'ensure',
        'manage', 'join', 'meet', 'apply', 'include', 'need', 'want',
        'help', 'use', 'within', 'across', 'among', 'between',
        'through', 'during', 'before', 'after', 'above', 'below',
        'about', 'against', 'over', 'under', 'again', 'further', 'once',
        'here', 'there', 'every', 'time', 'way', 'people'
    ])

    # Extract words (sequences of alphanumeric characters and certain special chars like +, #, .)
    # This will catch things like C++, .NET, etc.
    words = re.findall(r'\b[a-zA-Z0-9][a-zA-Z0-9\+#\.]*\b', job_description)

    # Filter: keep words that are not stopwords and have length > 1
    keywords = []
    for word in words:
        word_lower = word.lower()
        if word_lower not in stopwords and len(word) > 1:
            # Avoid adding duplicates (case-insensitive)
            if word_lower not in [k.lower() for k in keywords]:
                keywords.append(word)

    # Limit to top 20 keywords to avoid too many
    return keywords[:20]

def calculate_match_score(resume_text: str, keywords: List[str]) -> Dict[str, any]:
    """
    Calculate percentage of JD keywords found in resume.
    Returns: {"score": 85, "matched": [...], "missing": [...]}
    """
    if not keywords:
        return {"score": 0, "matched": [], "missing": []}

    resume_lower = resume_text.lower()
    matched = []
    missing = []

    for keyword in keywords:
        # Use word-boundary regex to avoid partial matches
        # (e.g. "Java" should not match "JavaScript").
        # Escape special regex chars in the keyword, then wrap with \b.
        escaped = re.escape(keyword)
        pattern = r'(?i)\b' + escaped + r'\b'
        if re.search(pattern, resume_lower):
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = int((len(matched) / len(keywords)) * 100) if keywords else 0

    return {
        "score": score,
        "matched": matched,
        "missing": missing
    }