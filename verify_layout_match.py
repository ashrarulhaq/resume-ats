import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

# Create a resume that matches exactly what the user wants to see
sample_resume = Resume(
    name="Ashrarul Haq",
    contact=Contact(
        email="ashrarulhaq02@gmail.com",
        phone="+91-95789-77072",
        linkedin="linkedin.com/in/ashrarulhaq",
        location="Tamil Nadu, India",
        website="",  # Not in user's example
        github="github.com/ashrarulhaq"
    ),
    summary="Analytical and results-driven Business Analysis Associate skilled in data collection, organization, and analysis from multiple sources. Experienced in preparing dashboards, reports, and visualizations using Excel, Power BI, and SQL. Adept at exploratory data analysis (EDA), identifying trends, anomalies, and patterns to improve business performance. Proven success in cross-functional collaboration, requirements gathering, and process optimization - including 30% lead generation growth and 20% registration increase in an EdTech environment. Familiar with automation of reporting processes, Python scripting, and BI tools.",
    skills=[
        "Data Annotation & Quality: Data Annotation, Labelling, Content Analysis, Quality Assurance, Attention to Detail, Guideline Adherence",
        "Analytical & Problem-Solving: Analytical Thinking, Root Cause Analysis, Exploratory Data Analysis (EDA), Error Pattern Identification",
        "Communication & Reporting: Business Writing, Report Creation, Dashboard Development, Professional Correspondence",
        "Research & Information Synthesis: Research Skills, Information Gathering, Synthesizing Insights from Multiple Sources",
        "Tools & Languages: MS Excel, Power BI, SQL (Basic), Python (Basic); English (Fluent)",
    ],
    experience=[
        Experience(
            company="MyCaptain (EdTech)",
            title="Business Operations Executive",
            dates="Dec 2024 - Mar 2025",
            location="",  # Not shown in experience per user request
            bullets=[
                "Streamlined student counselling, onboarding, and query resolution via Zendesk, reducing response time by 25%",
                "Created Excel dashboards tracking key performance indicators (enrollment, attendance, feedback) for data-driven decisions",
                "Automated weekly reporting via Python scripts, saving 5+ hours/week manual effort",
                "Coordinated with marketing and sales teams to align campaigns with course delivery, improving lead-to-enrollment conversion by 15%"
            ]
        ),
        Experience(
            company="SRM IST",
            title="Student Body President",
            dates="Mar 2023 - Mar 2024",
            location="",  # Not shown in experience per user request
            bullets=[
                "Led a council of 50+ student representatives across clubs and hostels, overseeing budget allocation and event planning",
                "Organized Techfest 2023, a 3-day technical festival with 2000+ participants, managing logistics, sponsorships, and publicity",
                "Implemented a digital grievance redressal system via Google Forms, reducing resolution time from 7 days to 2 days",
                "Advocated for mental health awareness, collaborating with counseling department to conduct workshops and seminars"
            ]
        )
    ],
    education=[
        Education(
            school="SRM Institute of Science and Technology",
            degree="B.Tech. Computer Science — Artificial Intelligence & ML",
            dates="2025",
            location="",  # Not shown in education per user request
            cgpa="7.9"
        ),
        Education(
            school="Alpha Plus MHSS",
            degree="Higher Secondary Certificate",
            dates="2021",
            location="",  # Not shown in education per user request
            percentage="84"
        )
    ],
    certifications=[
        "Business Analysis Fundamentals — Microsoft (Coursera)",
        "Agile Project Management — Google (Coursera)",
        "Python for Data Science, AI & Development — IBM"
    ],
    projects=[]  # No projects per user request
)

# Convert to dict for the PDF engine
resume_dict = sample_resume.model_dump()

# Test layout 1 (the one we're focusing on)
output_path = "verify_layout_match.pdf"
try:
    generate_pdf(resume_dict, 1, output_path)
    print("[PASS] Generated verify_layout_match.pdf")
    print("Please check the PDF to verify it matches your requirements:")
    print("- Contact line: Tamil Nadu, India | +91-95789-77072 | ashrarulhaq02@gmail.com | linkedin.com/in/ashrarulhaq | github.com/ashrarulhaq")
    print("- Professional Summary: Exact BA-focused text")
    print("- Section order: Summary -> Education -> Core Competencies -> Experience -> Certifications")
    print("- Experience: Job title + company on line 1, dates on line 2 (no location)")
    print("- Education: Degree + uni on line 1, CGPA/percentage on line 2 (no location)")
    print("- Core Competencies: Categorized bullet list with bold headers")
    print("- Certifications: Bulleted list")
    print("- No Projects section")
    print("- GitHub link included in contact line")
except Exception as e:
    print(f"[FAILED] Failed to generate verify_layout_match.pdf: {e}")

print("Verification complete!")