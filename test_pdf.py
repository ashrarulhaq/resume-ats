import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

# Create a sample resume for testing
sample_resume = Resume(
    name="John Doe",
    contact=Contact(
        email="john.doe@example.com",
        phone="+1-234-567-890",
        linkedin="linkedin.com/in/johndoe",
        location="San Francisco, CA",
        website="johndoe.com",
        github="github.com/johndoe"
    ),
    summary="Experienced software engineer with 5+ years of experience in full-stack development, specializing in React and Node.js.",
    skills=["JavaScript", "TypeScript", "React", "Node.js", "Python", "AWS", "Docker"],
    experience=[
        Experience(
            company="Tech Corp",
            title="Senior Software Engineer",
            dates="Jan 2020 – Present",
            location="San Francisco, CA",
            bullets=[
                "Led development of customer-facing web applications using React and Node.js",
                "Implemented RESTful APIs serving 10K+ daily active users",
                "Reduced page load times by 40% through optimization and caching strategies",
                "Mentored 3 junior engineers in frontend and backend best practices"
            ]
        ),
        Experience(
            company="Startup Inc",
            title="Software Engineer",
            dates="Jun 2018 – Dec 2019",
            location="Remote",
            bullets=[
                "Developed microservices architecture using Python and AWS Lambda",
                "Created CI/CD pipelines reducing deployment time from hours to minutes",
                "Collaborated with product team to define and implement new features"
            ]
        )
    ],
    education=[
        Education(
            school="University of California, Berkeley",
            degree="Bachelor of Science in Computer Science",
            dates="2014 – 2018",
            location="Berkeley, CA"
        )
    ],
    certifications=["AWS Certified Solutions Architect", "Google Cloud Professional Developer"],
    projects=[
        {
            "name": "E-commerce Platform",
            "description": "Built a full-stack e-commerce platform with payment processing",
            "technologies": ["React", "Node.js", "PostgreSQL", "Stripe"]
        }
    ]
)

# Convert to dict for the PDF engine
resume_dict = sample_resume.model_dump()

# Test all layouts
for layout_num in range(1, 6):
    output_path = f"test_resume_layout_{layout_num}.pdf"
    try:
        generate_pdf(resume_dict, layout_num, output_path)
        print(f"Generated {output_path}")
    except Exception as e:
        print(f"Failed to generate {output_path}: {e}")

print("PDF generation test complete!")