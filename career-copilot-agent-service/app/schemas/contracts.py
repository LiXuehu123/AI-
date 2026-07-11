from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserProfile(StrictModel):
    identity: Optional[str] = Field(default=None, description="求职者身份，例如应届生、实习生、转行求职者。")
    target_roles: List[str] = Field(default_factory=list, description="目标岗位方向。")
    target_cities: List[str] = Field(default_factory=list, description="目标城市。")
    availability: Optional[str] = Field(default=None, description="到岗频率、实习时长或入职时间约束。")
    skills_summary: Optional[str] = Field(default=None, description="用户提供的真实技能摘要。")
    portfolio_url: Optional[str] = Field(default=None, description="作品集链接。")


class JDParseRequest(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "jd_text": "公司：星河科技\n岗位：AI产品实习生\n岗位类型：实习\n职责：参与AI求职助手的用户调研、竞品分析、Prompt设计、数据看板搭建和需求文档整理。\n要求：熟悉Python、SQL、Excel，能进行需求分析和原型设计，每周到岗4天，可实习3个月以上。\n加分：有AI产品作品集、数据分析项目或大模型应用Demo。\n风险提示：节奏较快，需要主动推进跨部门沟通。"
                }
            ]
        },
    )

    jd_text: str = Field(..., min_length=10, description="原始 JD 文本。")


class JDAnalysis(StrictModel):
    job_title: str = Field(default="", description="岗位名称。")
    company: str = Field(default="", description="公司名称。")
    job_type: str = Field(default="", description="岗位类型，例如实习、全职、校招。")
    core_tasks: List[str] = Field(default_factory=list, description="核心工作任务。")
    hard_requirements: List[str] = Field(default_factory=list, description="硬性要求。")
    soft_requirements: List[str] = Field(default_factory=list, description="软性要求。")
    bonus_points: List[str] = Field(default_factory=list, description="加分项。")
    ats_keywords: List[str] = Field(default_factory=list, description="适合前端高亮或简历优化的 ATS 关键词。")
    risk_points: List[str] = Field(default_factory=list, description="需要求职者注意的风险点或约束。")


class ResumeMatchRequest(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "jd_analysis": {
                        "job_title": "AI产品实习生",
                        "company": "星河科技",
                        "job_type": "实习",
                        "core_tasks": ["用户调研", "竞品分析", "Prompt设计", "数据看板搭建"],
                        "hard_requirements": ["Python", "SQL", "Excel", "每周到岗4天"],
                        "soft_requirements": ["沟通", "主动性"],
                        "bonus_points": ["AI产品作品集", "大模型应用Demo"],
                        "ats_keywords": ["AI产品", "Prompt", "Python", "SQL", "Excel", "用户调研", "竞品分析", "数据看板"],
                        "risk_points": ["节奏较快，需要主动推进跨部门沟通"],
                    },
                    "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成和投递看板；使用Python整理岗位数据，用SQL做基础查询分析，用Excel制作指标表；曾完成用户访谈、竞品分析和Prompt迭代，并整理过PRD草稿。每周可到岗4天，可实习3个月以上。作品集：https://example.com/portfolio",
                    "user_profile": {
                        "identity": "应届生",
                        "target_roles": ["AI产品", "数据产品"],
                        "target_cities": ["上海", "杭州"],
                        "availability": "每周4天，可实习3个月以上",
                        "skills_summary": "Python, SQL, Excel, Prompt, 用户调研, 竞品分析, PRD",
                        "portfolio_url": "https://example.com/portfolio",
                    },
                }
            ]
        },
    )

    jd_analysis: JDAnalysis
    resume_text: str = Field(..., min_length=10, description="用户提供的真实简历文本。")
    user_profile: UserProfile = Field(default_factory=UserProfile)


class DimensionScores(StrictModel):
    role_fit: int = Field(default=0, ge=0, le=100)
    skill_fit: int = Field(default=0, ge=0, le=100)
    project_fit: int = Field(default=0, ge=0, le=100)
    ai_product_fit: int = Field(default=0, ge=0, le=100)
    availability_fit: int = Field(default=0, ge=0, le=100)


class ResumeMatch(StrictModel):
    overall_score: int = Field(default=0, ge=0, le=100)
    dimension_scores: DimensionScores = Field(default_factory=DimensionScores)
    matched_evidence: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    resume_improvement_suggestions: List[str] = Field(default_factory=list)
    application_recommendation: Literal[
        "strong_apply", "apply_after_revision", "not_recommended"
    ] = "apply_after_revision"


class MaterialGenerateRequest(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "jd_analysis": {
                        "job_title": "AI产品实习生",
                        "company": "星河科技",
                        "job_type": "实习",
                        "core_tasks": ["用户调研", "竞品分析", "Prompt设计", "数据看板搭建"],
                        "hard_requirements": ["Python", "SQL", "Excel", "每周到岗4天"],
                        "soft_requirements": ["沟通", "主动性"],
                        "bonus_points": ["AI产品作品集"],
                        "ats_keywords": ["AI产品", "Prompt", "Python", "SQL", "Excel", "用户调研", "竞品分析", "数据看板"],
                        "risk_points": ["节奏较快，需要主动推进跨部门沟通"],
                    },
                    "resume_match": {
                        "overall_score": 86,
                        "dimension_scores": {
                            "role_fit": 90,
                            "skill_fit": 88,
                            "project_fit": 85,
                            "ai_product_fit": 90,
                            "availability_fit": 85,
                        },
                        "matched_evidence": ["简历中出现 JD 关键词：AI产品", "简历中出现 JD 关键词：Python"],
                        "missing_evidence": ["缺少 JD 关键词或证据：数据看板"],
                        "resume_improvement_suggestions": ["补充与“数据看板”相关的真实项目证据"],
                        "application_recommendation": "strong_apply",
                    },
                    "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成和投递看板；使用Python整理岗位数据，用SQL做基础查询分析，用Excel制作指标表。",
                    "user_profile": {
                        "identity": "应届生",
                        "target_roles": ["AI产品"],
                        "target_cities": ["上海"],
                        "availability": "每周4天，可实习3个月以上",
                        "skills_summary": "Python, SQL, Excel, Prompt",
                        "portfolio_url": "https://example.com/portfolio",
                    },
                }
            ]
        },
    )

    jd_analysis: JDAnalysis
    resume_match: ResumeMatch
    resume_text: str = Field(..., min_length=10)
    user_profile: UserProfile = Field(default_factory=UserProfile)


class GeneratedMaterials(StrictModel):
    email_subject: str = ""
    email_body: str = ""
    boss_message: str = ""
    referral_message: str = ""
    follow_up_message: str = ""
    attachment_name: str = ""


class QualityReview(StrictModel):
    has_fabrication_risk: bool = False
    fabrication_items: List[str] = Field(default_factory=list)
    has_exaggeration_risk: bool = False
    exaggeration_items: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    tone_issues: List[str] = Field(default_factory=list)
    revision_suggestions: List[str] = Field(default_factory=list)
    final_safety_level: Literal["safe", "needs_review", "blocked"] = "safe"


class AgentRunRequest(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "user_profile": {
                        "identity": "应届生",
                        "target_roles": ["AI产品", "数据产品"],
                        "target_cities": ["上海", "杭州"],
                        "availability": "每周4天，可实习3个月以上",
                        "skills_summary": "Python, SQL, Excel, Prompt, 用户调研, 竞品分析, PRD",
                        "portfolio_url": "https://example.com/portfolio",
                    },
                    "resume_text": "我是信息管理与信息系统专业应届生，目标方向是AI产品实习。做过AI求职投递助手Demo，包含JD解析、简历匹配、材料生成和投递看板；使用Python整理岗位数据，用SQL做基础查询分析，用Excel制作指标表；曾完成用户访谈、竞品分析和Prompt迭代，并整理过PRD草稿。每周可到岗4天，可实习3个月以上。作品集：https://example.com/portfolio",
                    "jd_text": "公司：星河科技\n岗位：AI产品实习生\n岗位类型：实习\n职责：参与AI求职助手的用户调研、竞品分析、Prompt设计、数据看板搭建和需求文档整理。\n要求：熟悉Python、SQL、Excel，能进行需求分析和原型设计，每周到岗4天，可实习3个月以上。\n加分：有AI产品作品集、数据分析项目或大模型应用Demo。\n风险提示：节奏较快，需要主动推进跨部门沟通。",
                    "task": "判断是否值得投递，并生成投递材料",
                }
            ]
        },
    )

    user_profile: UserProfile = Field(default_factory=UserProfile)
    resume_text: str = Field(..., min_length=10)
    jd_text: str = Field(..., min_length=10)
    task: str = "判断是否值得投递，并生成投递材料"


class PriorityDecision(StrictModel):
    priority_level: Literal["P0", "P1", "P2", "P3"] = "P2"
    decision: str = "修改后再投递"
    reasoning_summary: str = ""
    next_action: str = ""


class AgentRunResponse(StrictModel):
    jd_analysis: JDAnalysis
    resume_match: ResumeMatch
    priority_decision: PriorityDecision
    generated_materials: GeneratedMaterials
    quality_review: QualityReview
    recommended_next_action: str
    trace: List[Dict[str, Any]] = Field(default_factory=list)
