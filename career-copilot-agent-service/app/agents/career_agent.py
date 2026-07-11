from app.schemas.contracts import AgentRunRequest, AgentRunResponse
from app.skills.generate_material import generate_material
from app.skills.match_resume import match_resume
from app.skills.parse_jd import parse_jd
from app.skills.priority_decision import decide_priority
from app.skills.quality_review import review_quality


class CareerCopilotAgent:
    """Single-agent MVP orchestration for the job application workflow."""

    def run(self, request: AgentRunRequest) -> AgentRunResponse:
        trace = []

        jd_analysis = parse_jd(request.jd_text)
        trace.append({"step": "parse_jd", "status": "completed"})

        resume_match = match_resume(jd_analysis, request.resume_text, request.user_profile)
        trace.append({"step": "match_resume", "status": "completed"})

        priority_decision = decide_priority(jd_analysis, resume_match)
        trace.append({"step": "decide_priority", "status": "completed"})

        generated_materials = generate_material(
            jd_analysis,
            resume_match,
            request.resume_text,
            request.user_profile,
        )
        trace.append({"step": "generate_material", "status": "completed"})

        quality_review = review_quality(generated_materials, jd_analysis, resume_match)
        trace.append({"step": "quality_review", "status": "completed"})

        if quality_review.final_safety_level == "blocked":
            next_action = "材料存在阻断风险，请先修改后再投递"
        elif priority_decision.priority_level == "P0":
            next_action = "请人工确认材料内容，确认后可投递并写入投递看板"
        else:
            next_action = priority_decision.next_action

        return AgentRunResponse(
            jd_analysis=jd_analysis,
            resume_match=resume_match,
            priority_decision=priority_decision,
            generated_materials=generated_materials,
            quality_review=quality_review,
            recommended_next_action=next_action,
            trace=trace,
        )

