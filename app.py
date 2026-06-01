import logging
import streamlit as st
import os
import tempfile
import sys
from pathlib import Path

# Ensure npm global bin is in PATH (needed for gemini CLI on Windows)
_npm_bin = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm")
if _npm_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _npm_bin + os.pathsep + os.environ.get("PATH", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules
from resume_tailor.core.parser import parse_resume
from resume_tailor.core.openrouter_backend import check_openrouter_installed, tailor_resume
from resume_tailor.core.validator import run_truth_guardrails
from resume_tailor.core.keyword_matcher import extract_keywords_from_jd, calculate_match_score
from resume_tailor.core.pdf_engine import get_layout_preview_html, generate_pdf
from resume_tailor.models.resume_schema import Resume


def resume_to_text(resume: dict) -> str:
    if not isinstance(resume, dict):
        return ""

    parts = []

    def add(value):
        if value:
            parts.append(str(value))

    def add_joined(values):
        text = ' '.join(str(v) for v in values if v)
        if text:
            parts.append(text)

    add(resume.get('name'))
    add(resume.get('summary'))

    contact = resume.get('contact')
    if isinstance(contact, dict):
        add(' '.join(str(v) for v in contact.values() if v))

    if isinstance(resume.get('skills'), list):
        add(' '.join(str(v) for v in resume['skills'] if v))
    if isinstance(resume.get('certifications'), list):
        add(' '.join(str(v) for v in resume['certifications'] if v))

    for experience in resume.get('experience', []) if isinstance(resume.get('experience'), list) else []:
        if isinstance(experience, dict):
            add_joined([
                experience.get('company'),
                experience.get('title'),
                experience.get('dates'),
                experience.get('location'),
                ' '.join(str(v) for v in experience.get('bullets', []) if v),
            ])

    for education in resume.get('education', []) if isinstance(resume.get('education'), list) else []:
        if isinstance(education, dict):
            add_joined([
                education.get('school'),
                education.get('degree'),
                education.get('dates'),
                education.get('location'),
                education.get('cgpa'),
                education.get('percentage'),
            ])

    for project in resume.get('projects', []) if isinstance(resume.get('projects'), list) else []:
        if isinstance(project, dict):
            add_joined([
                project.get('name'),
                project.get('description'),
                ' '.join(str(v) for v in project.get('technologies', []) if v),
            ])

    return '\n'.join(parts)

# Page config
st.set_page_config(
    page_title="Resume Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'tailored_resume' not in st.session_state:
    st.session_state.tailored_resume = None
if 'validation_report' not in st.session_state:
    st.session_state.validation_report = None
if 'keyword_score' not in st.session_state:
    st.session_state.keyword_score = None
if 'selected_layout' not in st.session_state:
    st.session_state.selected_layout = 2  # Default: Modern
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = ""
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'openrouter_api_key' not in st.session_state:
    st.session_state.openrouter_api_key = ""
if 'openrouter_model' not in st.session_state:
    st.session_state.openrouter_model = "openrouter/gpt-3.5-turbo"

# Header
st.title("📄 Resume Tailor")
st.markdown("**Tailor your resume to match job descriptions while staying 100% truthful**")

# Sidebar for OpenRouter configuration
with st.sidebar:
    st.header("🔧 OpenRouter Configuration")

    # API Key input
    api_key = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.openrouter_api_key,
        type="password",
        help="Get your API key from https://openrouter.ai/keys"
    )
    if api_key != st.session_state.openrouter_api_key:
        st.session_state.openrouter_api_key = api_key
        st.rerun()

    # Model input
    model = st.text_input(
        "Model Name",
        value=st.session_state.openrouter_model,
        help="Enter any valid OpenRouter model name (e.g., openrouter/gpt-3.5-turbo, google/gemini-pro)"
    )
    if model != st.session_state.openrouter_model:
        st.session_state.openrouter_model = model
        st.rerun()

    st.divider()
    st.caption("💡 Get your API key from https://openrouter.ai/keys")

    # Check if API key is configured
    if not st.session_state.openrouter_api_key:
        st.warning("⚠️ Please enter your OpenRouter API key to continue")
        st.stop()

# Main UI
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Step 1: Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx", "txt"],
        help="Upload PDF, DOCX, or TXT file (max 10MB)"
    )

    if uploaded_file is not None:
        # Check file size (10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File exceeds 10MB limit. Please compress or use a smaller file.")
        else:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Extract text
            file_extension = uploaded_file.name.split('.')[-1].lower()
            with st.spinner("Extracting text from resume..."):
                extracted_text = parse_resume(tmp_file_path, file_extension)
                st.session_state.original_text = extracted_text

            # Clean up temp file
            os.unlink(tmp_file_path)

            if st.session_state.original_text:
                st.success(f"✅ Extracted {len(st.session_state.original_text)} characters from resume")
                with st.expander("View extracted text"):
                    st.text_area("Resume text", st.session_state.original_text, height=200, disabled=True)
            else:
                st.error("Failed to extract text from the file. Please check the file format and try again.")

with col2:
    st.header("Step 2: Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste the full job description...",
        help="Maximum 10,000 characters"
    )

    if job_description:
        st.session_state.job_description = job_description
        char_count = len(job_description)
        if char_count > 10000:
            st.error(f"Job description too long: {char_count}/10,000 characters")
        else:
            st.caption(f"Character count: {char_count}/10,000")

            # Extract and show keywords
            if st.session_state.original_text:
                keywords = extract_keywords_from_jd(job_description)
                if keywords:
                    with st.expander("Extracted keywords from JD"):
                        st.write(", ".join(keywords))

# Step 3: Tailor Button
st.header("Step 3: Tailor Resume")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    tailor_button = st.button(
        "🚀 Tailor Resume",
        type="primary",
        disabled=not (st.session_state.original_text and st.session_state.job_description),
        use_container_width=True
    )

if tailor_button:
    if not st.session_state.original_text:
        st.error("Please upload a resume first")
    elif not st.session_state.job_description:
        st.error("Please paste a job description")
    else:
        st.session_state.processing = True
        with st.spinner("Tailoring resume with OpenRouter API... This may take up to 30 seconds"):
            try:
                # Call Gemini backend
                tailored_dict = tailor_resume(
                    st.session_state.original_text,
                    st.session_state.job_description
                )

                # Validate against pydantic schema
                try:
                    validated = Resume.model_validate(tailored_dict)
                    tailored_dict = validated.model_dump()
                except Exception as schema_err:
                    logger.warning(f"Gemini output didn't match schema, using as-is: {schema_err}")

                # Apply truth guardrails
                validation_result = run_truth_guardrails(
                    st.session_state.original_text,
                    tailored_dict
                )

                st.session_state.tailored_resume = validation_result['cleaned_resume']
                st.session_state.validation_report = validation_result['validation_report']

                # Calculate keyword match score
                if st.session_state.tailored_resume and 'skills' in st.session_state.tailored_resume:
                    resume_text_for_matching = resume_to_text(st.session_state.tailored_resume)
                    keywords = extract_keywords_from_jd(st.session_state.job_description)
                    st.session_state.keyword_score = calculate_match_score(resume_text_for_matching, keywords)

                # Generate preview HTML
                if st.session_state.tailored_resume:
                    st.session_state.preview_html = get_layout_preview_html(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout
                    )

                st.success("✅ Resume tailored successfully!")

            except Exception as e:
                st.error(f"❌ Error tailoring resume: {str(e)}")
            finally:
                st.session_state.processing = False

# Step 4: Results
if st.session_state.tailored_resume:
    st.header("Step 4: Review Results")

    # Keyword match score
    if st.session_state.keyword_score:
        score_col1, score_col2 = st.columns([1, 3])
        with score_col1:
            score = st.session_state.keyword_score['score']
            st.metric("Keyword Match Score", f"{score}%")
            if score >= 80:
                st.success("Excellent match!")
            elif score >= 60:
                st.warning("Good match")
            else:
                st.info("Consider adding more relevant keywords")

        with score_col2:
            matched = st.session_state.keyword_score['matched']
            missing = st.session_state.keyword_score['missing']
            if matched:
                st.caption(f"✅ Matched: {', '.join(matched[:5])}{'...' if len(matched) > 5 else ''}")
            if missing:
                st.caption(f"❌ Missing: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}")

    # Validation report
    if st.session_state.validation_report:
        report = st.session_state.validation_report
        if not report['skills_valid'] and report['invalid_skills']:
            st.warning(f"⚠️ {report['warnings'][0] if report['warnings'] else 'Some skills were removed for accuracy'}")
        elif report['warnings']:
            for warning in report['warnings']:
                st.info(f"ℹ️ {warning}")

    # Before/After comparison
    with st.expander("🔍 Before/After Comparison", expanded=True):
        before_col, after_col = st.columns(2)

        with before_col:
            st.subheader("Original Resume")
            st.text_area("Original", st.session_state.original_text, height=300, disabled=True, label_visibility="collapsed")

        with after_col:
            st.subheader("Tailored Resume")
            # Display as formatted JSON for review
            tailored_json = st.session_state.tailored_resume
            st.json(tailored_json)

    # Changes summary
    with st.expander("📝 Changes Summary"):
        st.info("""
        The AI has restructured and rephrased your existing content to better match the job description.
        No fake skills or experiences were added. All company names, titles, and dates are preserved.
        """)
        if st.session_state.validation_report and 'warnings' in st.session_state.validation_report:
            for warning in st.session_state.validation_report['warnings']:
                st.write(f"• {warning}")

# Step 5: Layout Selector
if st.session_state.tailored_resume:
    st.header("Step 5: Select Layout")

    layout_options = {
        1: "Classic",
        2: "Modern",
        3: "Minimal",
        4: "Professional",
        5: "Compact"
    }

    cols = st.columns(5)
    for i, (layout_num, layout_name) in enumerate(layout_options.items()):
        with cols[i]:
            if st.button(
                layout_name,
                key=f"layout_{layout_num}",
                type="primary" if st.session_state.selected_layout == layout_num else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_layout = layout_num
                # Regenerate preview with new layout
                if st.session_state.tailored_resume:
                    st.session_state.preview_html = get_layout_preview_html(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout
                    )

    # Show selected layout
    st.caption(f"Selected layout: {layout_options[st.session_state.selected_layout]}")

# Step 6: Preview and Download
if st.session_state.tailored_resume and st.session_state.preview_html:
    st.header("Step 6: Preview & Download")

    preview_col, download_col = st.columns([3, 1])

    with preview_col:
        st.subheader("Live Preview")
        # Display the HTML preview
        st.components.v1.html(st.session_state.preview_html, height=800, scrolling=True)

    with download_col:
        st.subheader("Download PDF")
        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    # Create temporary file for PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        pdf_path = tmp_file.name

                    # Generate PDF
                    generate_pdf(
                        st.session_state.tailored_resume,
                        st.session_state.selected_layout,
                        pdf_path
                    )

                    # Read PDF for download
                    with open(pdf_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()

                    # Clean up temp file
                    os.unlink(pdf_path)

                    # Provide download
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_data,
                        file_name="tailored_resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                    st.success("PDF generated successfully!")

                except Exception as e:
                    st.error(f"Failed to generate PDF: {str(e)}")

# Footer
st.divider()
st.caption("""
Resume Tailor v1.0.0 | Built with Streamlit | Uses OpenRouter API | 100% private - only API calls leave your machine
""")
