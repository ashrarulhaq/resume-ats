import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from resume_tailor.core.pdf_engine import generate_pdf
from resume_tailor.models.resume_schema import Resume, Contact, Experience, Education

# Create a sample resume closely matching the user's requested format
sample_resume = Resume(
    name="Jane Smith",
    contact=Contact(
        email="jane.smith@email.com",
        phone="555-123-4567",
        linkedin="linkedin.com/in/janesmith",
        location="New York, NY",
        website="janesmith.com"
    ),
    summary="Experienced marketing professional with 8+ years of expertise in digital marketing, campaign management, and brand strategy, seeking to leverage skills in a dynamic growth environment.",
    skills=["Digital Marketing", "Campaign Management", "Brand Strategy", "SEO/SEM", "Google Analytics", "Social Media Advertising"],
    experience=[
        Experience(
            company="Tech Solutions Inc",
            title="Senior Marketing Manager",
            dates="March 2020 – Present",
            location="New York, NY",
            bullets=[
                "Led end-to-end digital marketing campaigns across multiple channels increasing ROI by 35%",
                "Managed $500K annual marketing budget optimizing spend across paid search, social, and display",
                "Developed and executed brand strategy resulting in 25% increase in brand awareness",
                "Implemented marketing automation improving lead generation efficiency by 40%"
            ]
        ),
        Experience(
            company="Creative Agency Ltd",
            title="Marketing Specialist",
            dates="June 2017 – February 2020",
            location="Remote",
            bullets=[
                "Executed integrated marketing campaigns for B2B and B2C clients across various industries",
                "Conducted market research and competitor analysis informing strategic marketing decisions",
                "Created compelling content for email marketing, social media, and website driving engagement",
                "Analyzed campaign performance using Google Analytics providing actionable insights"
            ]
        )
    ],
    education=[
        Education(
            school="New York University",
            degree="Bachelor of Business Administration in Marketing",
            dates="2013 – 2017",
            location="New York, NY"
        )
    ],
    certifications=[
        "Google Ads Certification — Google (Skillshop)",
        "HubSpot Content Marketing Certification — HubSpot (HubSpot Academy)",
        "Facebook Blueprint Certification — Meta (Meta Blueprint)"
    ],
    projects=[
        {
            "name": "Customer Segmentation Project",
            "description": "Developed customer segmentation model using clustering algorithms to improve targeting",
            "technologies": ["Python", "Scikit-learn", "Pandas", "Tableau"]
        }
    ]
)

# Convert to dict for the PDF engine
resume_dict = sample_resume.model_dump()

# Test all layouts
for layout_num in range(1, 6):
    output_path = f"verify_layout_{layout_num}.pdf"
    try:
        generate_pdf(resume_dict, layout_num, output_path)
        print(f"[PASS] Generated {output_path}")
    except Exception as e:
        print(f"[FAIL] Failed to generate {output_path}: {e}")

print("PDF generation verification complete!")