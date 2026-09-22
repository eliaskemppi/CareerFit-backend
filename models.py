from typing import Literal, TypedDict
from pydantic import BaseModel

# Used for a candidate's profile extracted from their CV

class WorkExperience(BaseModel):
    title: str
    organization: str | None = None
    duration_years: float | None = None
    description: str
    skills: list[str]

class WorkExperiences(BaseModel):
    items: list[WorkExperience]

class Project(BaseModel):
    name: str
    description: str
    technologies: list[str]
    skills: list[str]

class Projects(BaseModel):
    items: list[Project]

class CandidateProfile(BaseModel):
    name: str
    skills: list[str]
    work_experience: list[WorkExperience]
    projects: list[Project]
    education: list[str]


# Used for a job profile extracted from a job description

class JobProfile(BaseModel):
    title: str
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    years_experience_required: float | None
    education_required: str | None

class Requirement(BaseModel):
    id: str
    text: str
    source_text: str
    category: Literal[
        "skill",
        "experience",
        "education",
        "responsibility",
    ]
    importance: Literal["required", "preferred"]
    evidence_type: Literal[
        "cv_relevant",
        "better_addressed_elsewhere",
    ]

class Requirements(BaseModel):
    items: list[Requirement]


# Used for matching candidate skills / experience to the jobs requirements

class RequirementMatch(BaseModel):
    requirement_id: str
    status: Literal["matched", "partial", "missing"]
    explanation: str
    evidence: list[str]

class RequirementMatches(BaseModel):
    items: list[RequirementMatch]


# Used for getting a project recommendation to fill the skill gaps

class ProjectRecommendation(BaseModel):
    title: str
    description: str
    skills_demonstrated: list[str]
    requirements_addressed: list[str]
    why_it_helps: str


# Used for the stateful LangGraph graph

class JobMatchState(TypedDict):
    cv: str
    cv_file_id: str | None
    job: str
    candidate: CandidateProfile | None
    job_profile: JobProfile | None
    requirements: list[Requirement]
    requirement_matches: list[RequirementMatch]
    project_recommendation: ProjectRecommendation | None