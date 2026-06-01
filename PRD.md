# Resume Tailor — Product Requirements Document

## 1. Product Overview

**Product Name:** Resume Tailor  
**Version:** 1.0.0  
**Date:** 2026-05-27  
**Author:** Product Owner  

### 1.1 Vision
A single-user desktop web app that takes a resume and a job description, uses local Gemini CLI to intelligently tailor the resume content to match the job description (without adding fake skills), and generates a professional ATS-friendly PDF in one of five predefined visual layouts.

### 1.2 Target User
Job seekers who want to optimize their existing resume for specific job applications while maintaining 100% factual honesty.

### 1.3 Core Value Proposition
- **Truthful Optimization:** Only restructures and rephrases existing content; never invents experience
- **ATS-First:** Every layout is tested for Applicant Tracking System compatibility
- **Zero API Costs:** Uses locally-installed Gemini CLI; no OpenAI/Anthropic API keys
- **Instant PDF Export:** One-click generation of interview-ready PDFs

---

## 2. Functional Requirements

### 2.1 Must-Have (MVP)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Upload resume via drag-and-drop (PDF, DOCX, TXT) | P0 |
| FR-02 | Paste job description into text area | P0 |
| FR-03 | Extract text from uploaded files | P0 |
| FR-04 | Execute Gemini CLI locally via shell subprocess | P0 |
| FR-05 | Receive structured JSON resume from Gemini | P0 |
| FR-06 | Validate that output skills exist in input (truth guardrail) | P0 |
| FR-07 | Display tailored resume in preview pane | P0 |
| FR-08 | Generate ATS-friendly PDF using 5 predefined layouts | P0 |
| FR-09 | Download generated PDF | P0 |
| FR-10 | Show keyword match score (JD keywords vs. resume) | P1 |

### 2.2 Should-Have (V1)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-11 | Live HTML preview of selected layout before PDF generation | P1 |
| FR-12 | Layout selector with visual thumbnails | P1 |
| FR-13 | Export tailored resume as JSON for manual editing | P1 |
| FR-14 | Download original parsed text for verification | P2 |
| FR-15 | Session history (last 10 tailoring operations) | P2 |

### 2.3 Won't-Have (Now)
- Job description URL scraping
- User accounts / cloud storage
- Multi-language support (English only for MVP)
- AI-powered cover letter generation
- LinkedIn profile import

---

## 3. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | App startup time | < 3 seconds |
| NFR-02 | PDF generation time | < 5 seconds |
| NFR-03 | Gemini CLI response time | < 30 seconds (depends on hardware) |
| NFR-04 | ATS parsing compatibility | 100% text selectable, single-column |
| NFR-05 | No internet required after setup | Fully local |
| NFR-06 | Max resume file size | 10MB |
| NFR-07 | Max job description length | 10,000 characters |

---

## 4. User Flow

```
[Launch App]
    ↓
[Step 1: Upload Resume] → Parse text → Show extracted text
    ↓
[Step 2: Paste Job Description] → Show character count
    ↓
[Step 3: Click "Tailor Resume"]
    ↓
[Show Loading Spinner] → Execute Gemini CLI
    ↓
[Step 4: Review Results]
    ├── Keyword Match Score
    ├── Changes Summary
    ├── Before / After comparison
    └── Layout Selector (5 options)
    ↓
[Step 5: Preview Selected Layout] → Live HTML render
    ↓
[Step 6: Generate & Download PDF]
```

---

## 5. Data Model

### 5.1 Resume JSON Schema (Gemini Output)

```json
{
  "name": "string (required)",
  "contact": {
    "email": "string",
    "phone": "string",
    "linkedin": "string",
    "location": "string",
    "website": "string"
  },
  "summary": "string",
  "skills": ["string"],
  "experience": [
    {
      "company": "string",
      "title": "string",
      "dates": "string",
      "location": "string",
      "bullets": ["string"]
    }
  ],
  "education": [
    {
      "school": "string",
      "degree": "string",
      "dates": "string",
      "location": "string"
    }
  ],
  "certifications": ["string"],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "technologies": ["string"]
    }
  ]
}
```

### 5.2 Keyword Match Result

```json
{
  "overall_score": 85,
  "matched_keywords": [
    {"keyword": "Python", "source": "skills", "context": "Used Python for data analysis"}
  ],
  "missing_keywords": [
    {"keyword": "Kubernetes", "reason": "Not found in original resume"}
  ],
  "suggested_replacements": [
    {"jd_keyword": "Kubernetes", "resume_equivalent": "Docker", "suggestion": "Container orchestration (Docker, Kubernetes-adjacent)"}
  ]
}
```

---

## 6. Constraints & Guardrails

### 6.1 Truth Guardrails (CRITICAL)
1. **Skill Validation:** Post-process Gemini output; every skill in `skills` array must exist in original resume text (fuzzy match allowed)
2. **Experience Lock:** Company names, job titles, dates, and degrees must be preserved exactly
3. **No Hallucination Prompt:** Gemini prompt must contain explicit "DO NOT ADD FAKE SKILLS" instruction with penalty framing
4. **User Confirmation:** Show "Changes Made" section highlighting only rephrasing and reordering

### 6.2 ATS Constraints
1. Single-column layout only
2. Standard section headers: "Professional Experience", "Education", "Skills", "Summary"
3. No text in headers/footers
4. Standard fonts: Helvetica, Arial, Georgia, Times New Roman
5. No images, icons, or graphics that contain text
6. Dates in consistent format (Month YYYY – Month YYYY)

---

## 7. Error Handling

| Scenario | User Message | Recovery |
|----------|--------------|----------|
| Gemini CLI not installed | "Gemini CLI not found. Please install: https://github.com/google-gemini/gemini-cli" | Link to install docs |
| File upload too large | "File exceeds 10MB limit. Please compress or use a smaller file." | Allow re-upload |
| Unsupported file type | "Only PDF, DOCX, and TXT files are supported." | Allow re-upload |
| Gemini timeout (>60s) | "Gemini is taking longer than expected. Try again with a shorter job description." | Retry button |
| Invalid JSON from Gemini | "AI response format error. Retrying with stricter instructions..." | Auto-retry once, then show raw output |
| Truth validation fails | "Warning: AI suggested skills not in your resume. These have been removed." | Show filtered output |
| PDF generation fails | "PDF generation error. Try a different layout or check your installation." | Log error, allow retry |

---

## 8. Success Metrics

- PDF successfully generated on first try: > 95%
- No fake skills in output: 100% (enforced by validator)
- User completes full flow in < 2 minutes
- ATS parse test: 100% of text extractable by standard parsers

---

## 9. Open Questions

1. Should we support DOCX export in addition to PDF? (Post-MVP)
2. Should we allow users to edit the JSON before PDF generation? (V1)
3. Gemini CLI model selection — default or allow user to choose? (V1)
