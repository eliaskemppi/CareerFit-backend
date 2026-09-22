import os
from dotenv import load_dotenv

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from graph import graph_app


load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
frontend_origin = os.environ["FRONTEND_ORIGIN"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# A function that does the analysis and returns a the required information
@app.post("/analyze")
async def analyze(
    cv: str = Form(""),
    job: str = Form(...),
    cv_file: UploadFile | None = File(None),
):
    cv_file_id = None

    if cv_file:
        if cv_file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="CV must be a PDF file.",
            )

        uploaded_file = client.files.create(
            file=(
                cv_file.filename,
                await cv_file.read(),
                cv_file.content_type,
            ),
            purpose="user_data",
        )

        cv_file_id = uploaded_file.id

    result = graph_app.invoke({
        "cv": cv,
        "cv_file_id": cv_file_id,
        "job": job,
        "candidate": None,
        "job_profile": None,
        "requirements": [],
        "requirement_matches": [],
        "project_recommendation": None,
    })

    return {
        "candidate": result["candidate"],
        "job": result["job_profile"],
        "job_text": job,
        "requirements": [
            {
                "id": requirement.id,
                "text": requirement.text,
                "source_text": requirement.source_text,
                "category": requirement.category,
                "importance": requirement.importance,
                "evidence_type": requirement.evidence_type,
                "status": next(
                    match.status
                    for match in result["requirement_matches"]
                    if match.requirement_id == requirement.id
                ),
                "explanation": next(
                    match.explanation
                    for match in result["requirement_matches"]
                    if match.requirement_id == requirement.id
                ),
                "evidence": next(
                    match.evidence
                    for match in result["requirement_matches"]
                    if match.requirement_id == requirement.id
                ),
            }
            for requirement in result["requirements"]
        ],
        "project_recommendation": result["project_recommendation"],
    }