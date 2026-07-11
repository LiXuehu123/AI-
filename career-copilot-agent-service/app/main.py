from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.career_agent import CareerCopilotAgent
from app.schemas.contracts import (
    AgentRunRequest,
    AgentRunResponse,
    GeneratedMaterials,
    JDAnalysis,
    JDParseRequest,
    MaterialGenerateRequest,
    ResumeMatch,
    ResumeMatchRequest,
)
from app.skills.generate_material import generate_material
from app.skills.match_resume import match_resume
from app.skills.parse_jd import parse_jd

app = FastAPI(
    title="Career Copilot Agent Service",
    description="Agent MVP backend for AI job application workflow.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = CareerCopilotAgent()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "career-copilot-agent-service"}


@app.post("/api/jd/parse", response_model=JDAnalysis)
async def api_parse_jd(request: JDParseRequest) -> JDAnalysis:
    return parse_jd(request.jd_text)


@app.post("/api/resume/match", response_model=ResumeMatch)
async def api_match_resume(request: ResumeMatchRequest) -> ResumeMatch:
    return match_resume(request.jd_analysis, request.resume_text, request.user_profile)


@app.post("/api/material/generate", response_model=GeneratedMaterials)
async def api_generate_material(request: MaterialGenerateRequest) -> GeneratedMaterials:
    return generate_material(
        request.jd_analysis,
        request.resume_match,
        request.resume_text,
        request.user_profile,
    )


@app.post("/api/agent/run", response_model=AgentRunResponse)
async def api_run_agent(request: AgentRunRequest) -> AgentRunResponse:
    return agent.run(request)

