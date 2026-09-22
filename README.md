# CareerFit

CareerFit is an AI-powered job matching application that analyzes a CV against a job posting and identifies which requirements are supported by the candidate's skills and experience.

Video demo: https://www.youtube.com/watch?v=MZTtQAxfWko

Live demo: https://careerfit-frontend-ghh4.onrender.com

## Features

- Upload a CV as a PDF or paste it as text
- Paste a full job posting or just its requirements
- AI-powered requirement-by-requirement matching
- Classifies requirements as **matched**, **partial**, **missing**, or **address elsewhere**
- Provides explanations and supporting CV evidence
- Generates a small project recommendation targeting identified skill gaps

## Tech Stack

- **Frontend:** Next.js
- **Backend:** FastAPI
- **AI:** OpenAI SDK, prompt engineering
- **Workflow:** LangGraph
- **Deployment:** Docker, Render

## Overview

CareerFit uses a LangGraph pipeline to analyze the candidate and job posting, extract requirements, evaluate each requirement against explicit CV evidence, and generate a targeted project recommendation.

The application uses engineered prompts and Pydantic schemas to produce consistent, structured AI outputs while avoiding assumptions about experience that is not explicitly supported by the CV.

The application is containerized with Docker and deployed on Render, with the frontend and backend running as separate services. This made it straightforward to keep the development environment consistent and deploy updates directly from the repository.

The frontend was largely developed by vibe-coding, using AI tools to quickly build and iterate on the UI. The backend and AI workflow were developed more deliberately, with structured schemas and a LangGraph pipeline used to keep the different stages of the analysis organized and maintainable.