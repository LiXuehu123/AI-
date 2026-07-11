from app.schemas.contracts import GeneratedMaterials, JDAnalysis, ResumeMatch, UserProfile


def _safe_company(company: str) -> str:
    return company if company and not company.startswith("待补充") else "贵公司"


def generate_material(jd_analysis: JDAnalysis, resume_match: ResumeMatch, resume_text: str, user_profile: UserProfile) -> GeneratedMaterials:
    company = _safe_company(jd_analysis.company)
    title = jd_analysis.job_title or "目标岗位"
    evidence = "；".join(resume_match.matched_evidence[:3]) or "可补充：与岗位相关的真实项目证据"
    portfolio = user_profile.portfolio_url or "可补充：作品集链接"
    skills = "、".join(jd_analysis.ats_keywords[:5]) or "可补充：岗位关键词"

    email_subject = f"应聘{title}-作品集/简历投递"
    email_body = (
        f"您好，我想应聘{company}{title}。\n\n"
        f"我与岗位相关的已提供证据包括：{evidence}。"
        f"这些经历可对应岗位中的{skills}等要求。\n\n"
        f"作品集链接：{portfolio}\n"
        "附件为我的简历，期待有机会进一步沟通。谢谢。"
    )
    boss_message = (
        f"您好，我关注到{title}岗位。我的简历中已有这些相关证据：{evidence}。"
        f"作品集：{portfolio}。想进一步了解岗位要求，期待沟通。"
    )
    referral_message = (
        f"您好，我想请您帮忙内推{company}{title}。"
        f"我目前能提供的匹配证据是：{evidence}。作品集：{portfolio}。"
    )
    follow_up_message = (
        f"您好，我此前投递了{title}岗位，想确认简历是否已收到。"
        "如需要补充作品集、项目说明或到岗时间，我可以继续提供。"
    )
    attachment_name = f"简历_{title}_作品集版.pdf".replace("/", "-")

    return GeneratedMaterials(
        email_subject=email_subject,
        email_body=email_body,
        boss_message=boss_message,
        referral_message=referral_message,
        follow_up_message=follow_up_message,
        attachment_name=attachment_name,
    )
