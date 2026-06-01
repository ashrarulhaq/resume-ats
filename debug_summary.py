import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

# Test with just the problematic summary text
summary_text = "Analytical and results-driven Business Analysis Associate skilled in data collection, organization, and analysis from multiple sources. Experienced in preparing dashboards, reports, and visualizations using Excel, Power BI, and SQL. Adept at exploratory data analysis (EDA), identifying trends, anomalies, and patterns to improve business performance. Proven success in cross-functional collaboration, requirements gathering, and process optimization — including 30% lead generation growth and 20% registration increase in an EdTech environment. Familiar with automation of reporting processes, Python scripting, and BI tools."

print("Summary text:")
print(repr(summary_text))
print()
print("Length:", len(summary_text))

# Check for problematic characters
for i, char in enumerate(summary_text):
    if ord(char) > 127:  # Non-ASCII character
        print(f"Non-ASCII at position {i}: {repr(char)} (Unicode {hex(ord(char))})")

# Create a minimal resume
sample_resume = Resume(
    name="Test User",
    contact=Contact(
        email="test@example.com",
        phone="123-456-7890",
        linkedin="linkedin.com/in/test",
        location="Test City",
        github="github.com/test"
    ),
    summary=summary_text,
    experience=[],
    education=[],
    certifications=[],
    projects=[]
)

# Convert to dict for the PDF engine
resume_dict = sample_resume.model_dump()

# Test layout 1
output_path = "debug_summary.pdf"
try:
    generate_pdf(resume_dict, 1, output_path)
    print(f"[SUCCESS] Generated {output_path}")
except Exception as e:
    print(f"[FAILED] Failed to generate {output_path}: {e}")
    import traceback
    traceback.print_exc()