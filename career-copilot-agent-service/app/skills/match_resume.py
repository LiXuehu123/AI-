from app.schemas.contracts import DimensionScores, JDAnalysis, ResumeMatch, UserProfile


ROLE_SIGNAL_TERMS = {
    "ai": ["AI", "大模型", "Prompt", "LLM", "智能体", "Agent"],
    "ops": ["运营", "商业化", "增长", "活动", "转化", "用户分层", "商家", "漏斗", "电商"],
    "data": ["数据", "BI", "指标", "看板", "SQL", "Python", "数据产品", "可视化", "异常"],
}

ROLE_EVIDENCE_TERMS = {
    "ai": ["AI", "大模型", "Prompt", "Agent", "智能体", "PRD", "用户调研", "竞品分析"],
    "ops": ["商业化", "用户分层", "转化", "漏斗", "商家", "活动", "增长", "电商", "复盘"],
    "data": ["SQL", "Python", "Excel", "BI", "看板", "指标", "数据分析", "数据产品", "可视化", "异常"],
}


def _contains(text: str, keyword: str) -> bool:
    return keyword.lower() in text.lower()


def _score_by_hits(hits: int, total: int, base: int = 40) -> int:
    if total <= 0:
        return base
    return min(100, round(base + (hits / total) * (100 - base)))


def _jd_context(jd_analysis: JDAnalysis) -> str:
    return "\n".join([
        jd_analysis.job_title or "",
        jd_analysis.company or "",
        jd_analysis.job_type or "",
        "\n".join(jd_analysis.core_tasks or []),
        "\n".join(jd_analysis.hard_requirements or []),
        "\n".join(jd_analysis.soft_requirements or []),
        "\n".join(jd_analysis.bonus_points or []),
        "\n".join(jd_analysis.ats_keywords or []),
    ])


def _active_role_categories(jd_text: str) -> list[str]:
    categories = []
    for category, signals in ROLE_SIGNAL_TERMS.items():
        if any(_contains(jd_text, signal) for signal in signals):
            categories.append(category)
    return categories


def _role_specific_terms(jd_text: str, categories: list[str]) -> list[str]:
    terms: list[str] = []
    for category in categories:
        for term in ROLE_EVIDENCE_TERMS[category]:
            if _contains(jd_text, term) and term not in terms:
                terms.append(term)
    return terms


def match_resume(jd_analysis: JDAnalysis, resume_text: str, user_profile: UserProfile) -> ResumeMatch:
    resume = resume_text.strip()
    jd_text = _jd_context(jd_analysis)
    keywords = jd_analysis.ats_keywords or []
    matched_keywords = [keyword for keyword in keywords if _contains(resume, keyword)]
    missing_keywords = [keyword for keyword in keywords if keyword not in matched_keywords]

    categories = _active_role_categories(jd_text)
    role_terms = _role_specific_terms(jd_text, categories)
    matched_role_terms = [term for term in role_terms if _contains(resume, term)]
    missing_role_terms = [term for term in role_terms if term not in matched_role_terms]

    role_hit = 1 if jd_analysis.job_title and any(role in jd_analysis.job_title for role in user_profile.target_roles) else 0
    generic_project_hit = 1 if any(word in resume for word in ["作品集", "项目", "Demo", "上线", "看板"]) else 0
    availability_hit = 1 if user_profile.availability and any(token in resume + user_profile.availability for token in ["4天", "5天", "到岗", "实习"] ) else 0

    if role_terms:
        project_fit = _score_by_hits(len(matched_role_terms), len(role_terms), base=45)
        role_context_fit = _score_by_hits(len(matched_role_terms), len(role_terms), base=50)
    else:
        project_fit = 85 if generic_project_hit else 55
        role_context_fit = 68 if generic_project_hit else 55

    ai_role = "ai" in categories
    if ai_role:
        ai_hit = 1 if any(_contains(resume, word) for word in ROLE_EVIDENCE_TERMS["ai"][:5]) else 0
        ai_product_fit = 88 if ai_hit else 50
    else:
        # Keep the existing schema field stable, but do not let AI Demo evidence boost non-AI roles.
        ai_product_fit = role_context_fit

    dimension_scores = DimensionScores(
        role_fit=70 + role_hit * 20 if user_profile.target_roles else 65,
        skill_fit=_score_by_hits(len(matched_keywords), len(keywords), base=35),
        project_fit=project_fit,
        ai_product_fit=ai_product_fit,
        availability_fit=85 if availability_hit else 60,
    )
    overall = round(
        dimension_scores.role_fit * 0.2
        + dimension_scores.skill_fit * 0.3
        + dimension_scores.project_fit * 0.2
        + dimension_scores.ai_product_fit * 0.2
        + dimension_scores.availability_fit * 0.1
    )

    matched_evidence = [f"简历中出现 JD 关键词：{keyword}" for keyword in matched_keywords]
    matched_evidence.extend([f"简历中出现岗位场景证据：{term}" for term in matched_role_terms if term not in matched_keywords])
    if generic_project_hit:
        matched_evidence.append("简历中包含项目/作品集证据，可用于支撑产品能力")
    if availability_hit:
        matched_evidence.append("求职画像或简历中包含到岗时间/实习约束信息")

    missing_evidence = [f"缺少 JD 关键词或证据：{keyword}" for keyword in missing_keywords]
    missing_evidence.extend([f"缺少岗位场景证据：{term}" for term in missing_role_terms if term not in missing_keywords])
    suggestions = [f"补充与“{keyword}”相关的真实项目证据" for keyword in (missing_keywords + missing_role_terms)[:5]]
    if not matched_evidence:
        matched_evidence.append("当前简历可用证据较少，需补充真实经历后再生成材料")

    recommendation = "strong_apply" if overall >= 85 else "apply_after_revision" if overall >= 60 else "not_recommended"

    return ResumeMatch(
        overall_score=overall,
        dimension_scores=dimension_scores,
        matched_evidence=matched_evidence,
        missing_evidence=missing_evidence,
        resume_improvement_suggestions=suggestions,
        application_recommendation=recommendation,
    )

