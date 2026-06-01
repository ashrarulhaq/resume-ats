# Graph Report - .  (2026-05-30)

## Corpus Check
- Corpus is ~27,996 words - fits in a single context window. You may not need a graph.

## Summary
- 341 nodes · 536 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Validation Logic|Validation Logic]]
- [[_COMMUNITY_Tests and API|Tests and API]]
- [[_COMMUNITY_Project Documentation|Project Documentation]]
- [[_COMMUNITY_React Frontend UI|React Frontend UI]]
- [[_COMMUNITY_Keyword Matching|Keyword Matching]]
- [[_COMMUNITY_React Package Config|React Package Config]]
- [[_COMMUNITY_PDF Rendering Engine|PDF Rendering Engine]]
- [[_COMMUNITY_Resume Parsing|Resume Parsing]]
- [[_COMMUNITY_Gemini Backend|Gemini Backend]]
- [[_COMMUNITY_Streamlit and OpenRouter|Streamlit and OpenRouter]]
- [[_COMMUNITY_PWA Manifest|PWA Manifest]]
- [[_COMMUNITY_React Entry and SW|React Entry and SW]]
- [[_COMMUNITY_React Logos|React Logos]]
- [[_COMMUNITY_Claude Settings|Claude Settings]]
- [[_COMMUNITY_Startup Script|Startup Script]]
- [[_COMMUNITY_CRA Index Template|CRA Index Template]]
- [[_COMMUNITY_Service Worker|Service Worker]]

## God Nodes (most connected - your core abstractions)
1. `Resume` - 20 edges
2. `run_truth_guardrails()` - 18 edges
3. `validate_dates()` - 16 edges
4. `generate_pdf()` - 14 edges
5. `calculate_match_score()` - 13 edges
6. `parse_resume()` - 13 edges
7. `extract_keywords_from_jd()` - 12 edges
8. `validate_skills()` - 12 edges
9. `validate_companies()` - 12 edges
10. `get_layout_preview_html()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `UploadFile` --uses--> `Resume`  [INFERRED]
  resume-ats-react/api/main.py → resume_tailor/models/resume_schema.py
- `BackgroundTasks` --uses--> `Resume`  [INFERRED]
  resume-ats-react/api/main.py → resume_tailor/models/resume_schema.py
- `_SessionState` --uses--> `Resume`  [INFERRED]
  resume-ats-react/api/main.py → resume_tailor/models/resume_schema.py
- `ExtractKeywordsRequest` --uses--> `Resume`  [INFERRED]
  resume-ats-react/api/main.py → resume_tailor/models/resume_schema.py
- `CalculateMatchRequest` --uses--> `Resume`  [INFERRED]
  resume-ats-react/api/main.py → resume_tailor/models/resume_schema.py

## Hyperedges (group relationships)
- **Five PDF Layouts** — classic_layout, modern_layout, minimal_layout, professional_layout, compact_layout [EXTRACTED 0.95]
- **Resume Tailor Dependency Stack** — streamlit_framework, pdfplumber_parser, python_docx_parser, weasyprint_pdf_generation, jinja2_template_engine, pydantic_resume_schema, thefuzz_matching, requests_http_client [INFERRED 0.82]
- **API Dependency Stack** — fastapi_framework, uvicorn_server, python_multipart_uploads, pdfplumber_parser, python_docx_parser, xhtml2pdf_renderer, jinja2_template_engine, pydantic_resume_schema, thefuzz_matching, requests_http_client [INFERRED 0.78]

## Communities (24 total, 4 thin omitted)

### Community 0 - "Validation Logic"
Cohesion: 0.05
Nodes (60): _extract_companies_from_text(), _extract_dates_from_text(), extract_skills_from_text(), Extract potential company names from text., Verify all company names in experience exist in original text (substring check)., Run all validations.     If invalid skills found: remove them from tailored_resu, Check that every skill in tailored_resume['skills'] exists in original_text., Extract date-like patterns from text. (+52 more)

### Community 1 - "Tests and API"
Cohesion: 0.09
Nodes (37): calculate_match_endpoint(), CalculateMatchRequest, _cleanup_file(), extract_keywords_endpoint(), ExtractKeywordsRequest, generate_pdf_endpoint(), GeneratePdfRequest, get_preview_html_endpoint() (+29 more)

### Community 2 - "Project Documentation"
Cohesion: 0.08
Nodes (45): Agent Instructions, API Requirements, ATS Compatibility, Classic Layout, Compact Layout, Extract Keywords Prompt, Extract Structure Prompt, Fallback Structure Prompt (+37 more)

### Community 3 - "React Frontend UI"
Cohesion: 0.08
Nodes (10): layouts, renderStatus(), ResultsSection(), keywordService, pdfService, resumeService, tailoringService, validationService (+2 more)

### Community 4 - "Keyword Matching"
Cohesion: 0.11
Nodes (25): calculate_match_score(), extract_keywords_from_jd(), Extract top technical/role keywords from job description.     Simple implementat, Calculate percentage of JD keywords found in resume.     Returns: {"score": 85,, any, str, Test that common stopwords are filtered out., Test that keywords are limited to 20. (+17 more)

### Community 5 - "React Package Config"
Cohesion: 0.10
Nodes (19): browserslist, development, production, dependencies, cra-template-pwa, react, react-dom, react-scripts (+11 more)

### Community 6 - "PDF Rendering Engine"
Cohesion: 0.18
Nodes (17): get_layout_name(), get_layout_preview_html(), load_template(), Load Jinja2 HTML template and CSS path for given layout.     layout_number: 1-5, Map layout number to layout name., Inject resume data into HTML template, return HTML string., Generate HTML for live preview (no PDF conversion)., render_html() (+9 more)

### Community 7 - "Resume Parsing"
Cohesion: 0.19
Nodes (15): extract_text_from_docx(), extract_text_from_pdf(), extract_text_from_txt(), parse_resume(), Extract text from PDF using pdfplumber., Extract text from DOCX using python-docx., Read plain text file., Router: dispatch to correct extractor based on file extension. (+7 more)

### Community 8 - "Gemini Backend"
Cohesion: 0.18
Nodes (15): build_tailor_prompt(), call_gemini(), check_gemini_installed(), extract_json_from_response(), _find_gemini_cmd(), Find the gemini command, trying gemini.cmd on Windows as fallback., Parse JSON from Gemini response.     Handles markdown code blocks (```json ... `, Full pipeline:     1. Build prompt     2. Call Gemini     3. Extract JSON     4. (+7 more)

### Community 9 - "Streamlit and OpenRouter"
Cohesion: 0.18
Nodes (14): build_tailor_prompt(), call_openrouter(), check_openrouter_installed(), extract_json_from_response(), Parse JSON from OpenRouter response.     Handles markdown code blocks (```json ., Verify OpenRouter API key is set in session state., Full pipeline:     1. Build prompt     2. Call OpenRouter     3. Extract JSON, Load prompt template and inject resume + JD. (+6 more)

### Community 10 - "PWA Manifest"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 11 - "React Entry and SW"
Cohesion: 0.29
Nodes (4): root, isLocalhost, register(), registerValidSW()

### Community 12 - "React Logos"
Cohesion: 0.50
Nodes (4): React Logo 192, React Logo 512, React Logo, React Logo SVG

## Ambiguous Edges - Review These
- `React Logo 192` → `React Logo`  [AMBIGUOUS]
  resume-ats-react/public/logo192.png · relation: semantically_similar_to
- `React Logo 512` → `React Logo`  [AMBIGUOUS]
  resume-ats-react/public/logo512.png · relation: semantically_similar_to

## Knowledge Gaps
- **46 isolated node(s):** `allow`, `name`, `version`, `private`, `cra-template-pwa` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `React Logo 192` and `React Logo`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `React Logo 512` and `React Logo`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `run_truth_guardrails()` connect `Validation Logic` to `Tests and API`, `Streamlit and OpenRouter`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `parse_resume()` connect `Resume Parsing` to `Tests and API`, `Streamlit and OpenRouter`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `calculate_match_score()` connect `Keyword Matching` to `Tests and API`, `Streamlit and OpenRouter`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Resume` (e.g. with `CalculateMatchRequest` and `ExtractKeywordsRequest`) actually correct?**
  _`Resume` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `# TODO: Could also use tailored resume text for matching`, `allow`, `name` to the rest of the system?**
  _127 weakly-connected nodes found - possible documentation gaps or missing edges._