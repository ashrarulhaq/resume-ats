# Resume Tailor — Gemini Prompts Library

## 1. Main Tailoring Prompt (`prompts/tailor_resume.txt`)

This is the primary prompt sent to Gemini CLI. It must be loaded as a template and injected with resume text and job description.

```
You are an expert ATS Resume Optimizer and professional career coach.
Your task is to rewrite a resume to better match a specific job description while maintaining 100% factual accuracy.

=== CRITICAL RULES (VIOLATION IS UNACCEPTABLE) ===
1. TRUTH ONLY: You may ONLY rephrase, reorder, or restructure existing content. You MUST NEVER invent skills, job titles, companies, dates, degrees, certifications, or achievements that do not appear in the original resume.
2. SKILL MAPPING: If the job description asks for a skill the candidate doesn't have, you may NOT add it. However, if the candidate has a related skill, you may describe it using terminology from the job description (e.g., "Docker experience" can be described as "Containerization" if the JD asks for that term).
3. DATE PRESERVATION: All employment dates, graduation dates, and company names must remain EXACTLY as they appear in the original resume.
4. NO HALLUCINATION: If you are unsure whether a skill or experience exists in the original resume, you must OMIT it rather than guess.
5. METRIC PRESERVATION: Only use numbers, percentages, and metrics that appear in the original resume. Do not invent quantified achievements.

=== ATS OPTIMIZATION RULES ===
1. Use standard section headings: "Professional Summary", "Professional Experience", "Education", "Skills", "Certifications"
2. Incorporate exact keywords and phrases from the job description where they truthfully apply
3. Lead bullet points with strong action verbs (Led, Developed, Implemented, Architected, Optimized)
4. Prioritize experiences most relevant to the job description (reorder if needed)
5. Ensure clean, scannable formatting in the output structure
6. Use consistent date formatting: "Month YYYY – Month YYYY" or "Month YYYY – Present"

=== OUTPUT FORMAT ===
Return ONLY a valid JSON object matching this exact schema. Do NOT wrap in markdown code blocks. Do NOT add explanations before or after the JSON.

{
  "name": "Full Name",
  "contact": {
    "email": "email@example.com",
    "phone": "+1-234-567-8900",
    "linkedin": "linkedin.com/in/username",
    "location": "City, State",
    "website": "portfolio.com"
  },
  "summary": "2-3 sentence professional summary incorporating JD keywords where applicable",
  "skills": ["Skill 1", "Skill 2", "Skill 3"],
  "experience": [
    {
      "company": "Company Name (EXACTLY as original)",
      "title": "Job Title (EXACTLY as original or slightly standardized)",
      "dates": "Month YYYY – Month YYYY",
      "location": "City, State",
      "bullets": [
        "Led [specific project] resulting in [metric from original] using [JD keyword that applies]",
        "Developed [system/feature] with [technology from original], aligning with [JD requirement]"
      ]
    }
  ],
  "education": [
    {
      "school": "University Name (EXACTLY as original)",
      "degree": "Degree Name (EXACTLY as original)",
      "dates": "YYYY – YYYY",
      "location": "City, State"
    }
  ],
  "certifications": ["Certification Name"],
  "projects": [
    {
      "name": "Project Name",
      "description": "Brief description using JD keywords if applicable",
      "technologies": ["Tech from original resume only"]
    }
  ]
}

=== TRUTH VERIFICATION ===
After generating the JSON, perform a self-check:
- List every skill in the output. Verify each one appears in the original resume text.
- List every company and date. Verify each matches the original exactly.
- If any item fails verification, remove it from the output.

=== INPUTS ===

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

=== FINAL INSTRUCTION ===
Generate the JSON now. Remember: TRUTHFUL OPTIMIZATION ONLY. No fake skills. No invented experience.
```

## 2. Keyword Extraction Prompt (`prompts/extract_keywords.txt`)

Used to extract top keywords from the job description for match scoring.

```
Extract the top 20 most important technical skills, tools, and qualifications from the following job description.

Return ONLY a JSON array of strings. No markdown, no explanations.

Focus on:
- Hard skills (programming languages, software, methodologies)
- Required qualifications (degrees, certifications)
- Key responsibilities that indicate core competencies
- Industry-specific terminology

Exclude:
- Soft skills ("communication", "teamwork") unless explicitly emphasized
- Generic corporate language ("fast-paced environment", "detail-oriented")
- Company benefits or culture descriptions

JOB DESCRIPTION:
{job_description}

OUTPUT FORMAT:
["keyword1", "keyword2", "keyword3", ...]
```

## 3. Fallback JSON Extraction Prompt (`prompts/extract_structure.txt`)

Used when the main prompt returns messy text instead of clean JSON.

```
The following text contains resume information but may not be in proper JSON format.

Your task: Extract the resume data and format it into the exact JSON schema below.

RULES:
- Preserve all factual information exactly as stated
- Do NOT add information not present in the text
- Use empty strings or empty arrays for missing fields
- Standardize section names to the schema fields

INPUT TEXT:
{raw_text}

OUTPUT SCHEMA:
{
  "name": "string",
  "contact": {"email":"", "phone":"", "linkedin":"", "location":"", "website":""},
  "summary": "string",
  "skills": ["string"],
  "experience": [{"company":"", "title":"", "dates":"", "location":"", "bullets":[""]}],
  "education": [{"school":"", "degree":"", "dates":"", "location":""}],
  "certifications": ["string"],
  "projects": [{"name":"", "description":"", "technologies":[""]}]
}

Return ONLY valid JSON. No markdown code blocks. No extra text.
```

## 4. Changes Summary Prompt (Optional Enhancement)

If we want Gemini to also explain what changes it made:

```
Given the original resume and the tailored resume below, generate a concise summary of changes made.

For each change, specify:
- What changed (bullet rephrased, section reordered, keyword added)
- Why it helps (matches JD requirement X, improves ATS score)
- Truth verification (confirm this change uses only existing information)

ORIGINAL:
{original_resume_text}

TAILORED:
{tailored_resume_json}

OUTPUT FORMAT (JSON):
{
  "changes": [
    {
      "type": "rephrase|reorder|keyword_injection|section_restructure",
      "section": "experience|skills|summary|education",
      "before": "original text",
      "after": "new text",
      "reason": "explanation",
      "truth_verified": true
    }
  ],
  "keyword_score": {
    "before": 45,
    "after": 82,
    "added_keywords": ["keyword1", "keyword2"]
  }
}
```

## 5. Prompt Engineering Guidelines

### 5.1 Temperature & Settings
Since Gemini CLI may not expose temperature directly, we rely on prompt structure:
- Use explicit formatting instructions ("Return ONLY JSON")
- Use delimiters (=== SECTION ===) to structure long prompts
- Use negative constraints ("Do NOT...") to prevent hallucination
- Use self-verification steps ("After generating, check...")

### 5.2 Context Window Management
- Resume text: typically 2,000-5,000 characters
- Job description: typically 3,000-8,000 characters
- Prompt template: ~2,000 characters
- Total: usually within Gemini's context window
- If resume is very long, truncate to most recent 10 years of experience with a note

### 5.3 Retry Prompts

**Retry 1 (if JSON parsing fails):**
```
Your previous response contained valid information but was not in the correct format.

Please reformat the same resume data into this EXACT JSON structure.
Do not change any of the content. Only change the format.

Return ONLY the JSON object. No markdown. No explanations.

{previous_response_content}
```

**Retry 2 (if still failing):**
```
Extract resume data from the text below and output ONLY valid JSON.

Text:
{combined_input_text}

JSON Schema:
{schema_definition}
```

## 6. Prompt Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{resume_text}` | `core/parser.py` output | Plain text extracted from uploaded file |
| `{job_description}` | Streamlit text area | User-pasted job description |
| `{raw_text}` | Gemini output | Messy text needing structure extraction |
| `{original_resume_text}` | Session state | Original text for comparison |
| `{tailored_resume_json}` | Validated JSON | Tailored resume for change analysis |
| `{previous_response_content}` | Gemini output | Previous attempt for reformatting |

## 7. Safety Prompts

### 7.1 PII Handling
Gemini CLI handles its own data policies. The app does not send data to third-party APIs. However, include this in the main prompt:
```
Note: This resume contains personal information. Handle it securely and do not include it in any training or logging.
```

### 7.2 Bias Prevention
```
Optimize based on skills and experience only. Do not infer or add information about gender, age, ethnicity, or other protected characteristics.
```
