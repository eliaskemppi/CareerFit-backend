import os
from dotenv import load_dotenv

from openai import OpenAI

from models import (
    CandidateProfile,
    JobProfile,
    Requirements,
    RequirementMatches,
    ProjectRecommendation,
)
from models import JobMatchState

# Client for the responses api
load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# AI extracts skills / experience / projects from CV
# result: candidate profile parsed (defined in models)
def analyze_cv(state: JobMatchState):
    prompt = """
Extract the candidate's information from this CV.

Return:
- candidate name
- general skills
- detailed work experience
- projects
- education

For each work experience:
- Extract the job title.
- Extract the organization when available.
- Extract the duration in years when available.
- Summarize the responsibilities and achievements stated in the CV in a few words.
- Extract skills demonstrated in that role. They can be soft skills too.

For each project:
- Extract the project name.
- Summarize what was built or done very briefy. No full description is needed.
- Extract technologies used.
- Extract skills demonstrated.

Rules:
- Only use information present in the CV.
- Do not invent skills, responsibilities, technologies, achievements,
  organizations, or project details.
- Preserve concrete evidence from the CV.
- If information is not available, use an empty list or null where
  appropriate.
"""

    if state["cv_file_id"]:
        response = client.responses.parse(
            model="gpt-5.6-luna",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                        {
                            "type": "input_file",
                            "file_id": state["cv_file_id"],
                        },
                    ],
                }
            ],
            text_format=CandidateProfile,
        )
    else:
        response = client.responses.parse(
            model="gpt-5.6-luna",
            input=f"""
{prompt}

CV:
{state["cv"]}
""",
            text_format=CandidateProfile,
        )

    return {"candidate": response.output_parsed}


# AI extracts job information including required / preferred skills, experience, education, reponsibilities
# result: job profile parsed (defined in models)
def analyze_job(state: JobMatchState):
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=f"""
Extract the job profile from this job description.

Job Description:
{state["job"]}

Rules:
- Extract required skills.
- Extract preferred/nice-to-have skills.
- Extract responsibilities.
- Extract required years of experience if stated.
- Extract required education if stated.
- Do not invent information.
- Preserve the distinction between required and preferred items.
- Preserve the distinction between skills, experience, education, and responsibilities.
""",
        text_format=JobProfile,
    )

    return {
        "job_profile": response.output_parsed
    }


# Extract job requirements
# result: Requirement parsed (defined in models)
def extract_requirements(state: JobMatchState):
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=f"""
Extract the individual requirements from this job posting.

Job Profile:
{state["job_profile"]}

Original Job Description:
{state["job"]}

Rules:
- Create one requirement for each distinct skill, experience,
  education, or responsibility.
- Keep "text" concise and normalized.
- "source_text" MUST contain the exact wording from the original
  job description that expresses the requirement.
- Do not paraphrase or rewrite source_text.
- source_text should be a contiguous piece of text from the original
  job description.
- Mark something as "required" if it is listed under requirements.
- Mark something as "preferred" if it is listed under
  nice-to-have, preferred, or similar sections.
- Keep it strict. For example, if the job gives a hard requirement for a MSc, do not mark a BSc as partial. Or if the job requires 5 years of relevant experience, do not mark 3 years as partial.
- The responsibility category should default to "preferred" unless the job posting explicitly states that it is required.
- Do not invent requirements that are not present in the job posting.
- Every requirement must have a unique id.

Classify each requirement (evience_type) as either:
- cv_relevant:
  The CV can reasonably provide evidence for this requirement. For example BSc, PyTorch, leadership, etc.
- better_addressed_elsewhere:
  The requirement is difficult to meaningfully establish from a CV
  and is better demonstrated through a cover letter, concrete example,
  interview, or other context. For example, fast learner, good communicator, team player, etc.

Do not classify something as better_addressed_elsewhere merely because
it is a soft skill. Use it when the requirement genuinely cannot be
meaningfully evaluated from a typical CV.
""",
        text_format=Requirements,
    )

    return {
        "requirements": response.output_parsed.items
    }


# AI checks if the candidate skills etc. match to the job requirements
# result: RequirementMatch parsed (defined in models)
def match_requirements(state: JobMatchState):
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=f"""
Evaluate how well the candidate satisfies each job requirement.

Candidate Profile:
{state["candidate"]}

Requirements:
{state["requirements"]}

For every requirement, return exactly one result.

Use evidence from:
- candidate skills
- work experience
- projects
- education

Status meanings:

- matched: the CV provides clear evidence that the candidate satisfies it
- partial: the CV contains related evidence, but it is incomplete,
  indirect, or not explicit enough
- missing: there is no relevant evidence in the CV

Important:
- Do not assume experience that is not stated in the CV.
- Use the candidate's actual evidence.
- Explain briefly why the requirement received its status.
- Include relevant CV evidence when available.
""",
        text_format=RequirementMatches,
    )

    return {
        "requirement_matches": response.output_parsed.items
    }


# AI recommends a project to fill the skill gaps
# ProjectRecommendation parsed (defined in models)
def recommend_project(state: JobMatchState):
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=f"""
Recommend one practical portfolio project that would help this
candidate address their biggest gaps for this job.

Candidate:
{state["candidate"]}

Job requirements:
{state["requirements"]}

Requirement matches:
{state["requirement_matches"]}

Rules:
- Focus primarily on requirements marked "missing" or "partial".
- Prefer ONE project that demonstrates multiple missing skills.
- Only recommend skills relevant to this job.
- Do not recommend a project that simply repeats something the candidate
  has already demonstrated strongly.
- Make the project realistic for a portfolio.
- Do not claim that completing the project gives the candidate
  professional experience.
- Keep the recommendation concise.
""",
        text_format=ProjectRecommendation,
    )

    return {
        "project_recommendation": response.output_parsed
    }