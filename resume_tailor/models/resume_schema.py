from pydantic import BaseModel, Field
from typing import List, Optional

class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None

class Experience(BaseModel):
    company: str
    title: str
    dates: str
    location: Optional[str] = None
    bullets: List[str]

class Education(BaseModel):
    school: str
    degree: str
    dates: Optional[str] = None
    location: Optional[str] = None
    cgpa: Optional[str] = None
    percentage: Optional[str] = None

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = []

class Resume(BaseModel):
    name: str
    contact: Contact
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    certifications: List[str] = []
    projects: List[Project] = []