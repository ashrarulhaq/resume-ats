import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

# Create a minimal resume to test
sample_resume = Resume(
    name="Test User",
    contact=Contact(
        email="test@example.com",
        phone="123-456-7890",
        linkedin="linkedin.com/in/test",
        location="Test City",
        github="github.com/test"
    ),
    summary="Test summary with simple text.",
    experience=[
        Experience(
            company="Test Company",
            title="Test Title",
            dates="Jan 2020 - Dec 2020",
            location="",
            bullets=[
                "Simple bullet point"
            ]
        )
    ],
    education=[
        Education(
            school="Test University",
            degree="Test Degree",
            dates="2018 - 2020",
            location="",
            cgpa="3.5"
        )
    ],
    certifications=[
        "Test Cert"
    ],
    projects=[]
)

# Convert to dict for the PDF engine
resume_dict = sample_resume.model_dump()

# Test layout 1
output_path = "simple_test.pdf"
try:
    generate_pdf(resume_dict, 1, output_path)
    print(f"[SUCCESS] Generated {output_path}")
except Exception as e:
    print(f"[FAILED] Failed to generate {output_path}: {e}")
    import traceback
    traceback.print_exc()