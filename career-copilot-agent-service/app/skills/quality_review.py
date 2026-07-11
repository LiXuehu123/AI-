from app.schemas.contracts import GeneratedMaterials, JDAnalysis, QualityReview, ResumeMatch

RISKY_WORDS = ["第一", "顶尖", "精通", "保证", "显著提升", "千万", "百万", "独立负责全部"]
MARKETING_TONE_WORDS = ["强烈推荐", "完美匹配", "巨大价值", "立刻沟通", "不可错过", "非常优秀"]


def review_quality(materials: GeneratedMaterials, jd_analysis: JDAnalysis, resume_match: ResumeMatch) -> QualityReview:
    combined = "\n".join([
        materials.email_subject,
        materials.email_body,
        materials.boss_message,
        materials.referral_message,
        materials.follow_up_message,
    ])
    exaggeration_items = [word for word in RISKY_WORDS if word in combined]
    tone_issues = [word for word in MARKETING_TONE_WORDS if word in combined]
    missing_keywords = [keyword for keyword in jd_analysis.ats_keywords if keyword not in combined]
    fabrication_items = []

    if "可补充" in combined:
        fabrication_items.append("材料中存在待补充信息，占位内容发送前需人工确认")
    if any(item in combined for item in ["伪造", "虚构"]):
        fabrication_items.append("材料中出现伪造或虚构相关表述，必须阻断")

    final_level = "safe"
    if fabrication_items or exaggeration_items or tone_issues or len(missing_keywords) > 3:
        final_level = "needs_review"
    if any(item in combined for item in ["伪造", "虚构"]):
        final_level = "blocked"

    suggestions = []
    if missing_keywords:
        suggestions.append("发送前检查是否需要补充 JD 关键词的真实证据")
    if fabrication_items:
        suggestions.append("将“可补充”内容替换为用户真实信息，或删除该句")
    if exaggeration_items:
        suggestions.append("删除或改写夸大词，避免承诺无法证明的结果")
    if tone_issues:
        suggestions.append("降低过度营销语气，改为基于证据的客观表述")

    return QualityReview(
        has_fabrication_risk=bool(fabrication_items),
        fabrication_items=fabrication_items,
        has_exaggeration_risk=bool(exaggeration_items),
        exaggeration_items=exaggeration_items,
        missing_keywords=missing_keywords,
        tone_issues=tone_issues,
        revision_suggestions=suggestions,
        final_safety_level=final_level,
    )
