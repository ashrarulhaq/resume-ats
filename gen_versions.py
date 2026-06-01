import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

sample_resume = Resume(
    name="Ashrarul Haq",
    contact=Contact(
        email="ashrarulhaq02@gmail.com",
        phone="+91-95789-77072",
        linkedin="linkedin.com/in/ashrarulhaq",
        location="Tamil Nadu, India",
        website="",
        github="github.com/ashrarulhaq"
    ),
    summary="Analytical and results-driven Business Analysis Associate skilled in data collection, organization, and analysis from multiple sources. Experienced in preparing dashboards, reports, and visualizations using Excel, Power BI, and SQL. Adept at exploratory data analysis (EDA), identifying trends, anomalies, and patterns to improve business performance. Proven success in cross-functional collaboration, requirements gathering, and process optimization - including 30% lead generation growth and 20% registration increase in an EdTech environment. Familiar with automation of reporting processes, Python scripting, and BI tools.",
    skills=[],
    experience=[
        Experience(
            company="MyCaptain (EdTech)",
            title="Business Operations Executive",
            dates="Dec 2024 - Mar 2025",
            location="",
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
            location="",
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
            degree="B.Tech. Computer Science - Artificial Intelligence & ML",
            dates="2025",
            location="",
            cgpa="7.9"
        ),
        Education(
            school="Alpha Plus MHSS",
            degree="Higher Secondary Certificate",
            dates="2021",
            location="",
            percentage="84"
        )
    ],
    certifications=[
        "Business Analysis Fundamentals - Microsoft (Coursera)",
        "Agile Project Management - Google (Coursera)",
        "Python for Data Science, AI & Development - IBM"
    ],
    projects=[]
)

resume_dict = sample_resume.model_dump()
resume_dict["education"][0]["cgpa"] = "7.9"
resume_dict["education"][1]["percentage"] = "84"

output_path = "verify_layout_match_v3_spacer_divs.pdf"
try:
    generate_pdf(resume_dict, 1, output_path)
    print(f"[PASS] {output_path}")
except Exception as e:
    print(f"[FAIL] {output_path} - {e}")
