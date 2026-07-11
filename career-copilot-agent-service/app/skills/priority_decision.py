from app.schemas.contracts import JDAnalysis, PriorityDecision, ResumeMatch


def decide_priority(jd_analysis: JDAnalysis, resume_match: ResumeMatch) -> PriorityDecision:
    score = resume_match.overall_score
    if score >= 85:
        level = "P0"
        decision = "建议优先投递"
        next_action = "直接检查材料并投递，投递后写入看板跟进"
    elif score >= 70:
        level = "P1"
        decision = "可以投递"
        next_action = "补强简历关键词后投递"
    elif score >= 55:
        level = "P2"
        decision = "修改后再投递"
        next_action = "先补充缺失证据，再重新生成材料"
    else:
        level = "P3"
        decision = "不建议投递"
        next_action = "优先寻找更匹配的岗位"

    risk_summary = "；".join(jd_analysis.risk_points) if jd_analysis.risk_points else "未发现明显风险点"
    return PriorityDecision(
        priority_level=level,
        decision=decision,
        reasoning_summary=f"匹配分为{score}，风险检查：{risk_summary}",
        next_action=next_action,
    )
