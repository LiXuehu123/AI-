import re
from typing import Iterable, List

from app.schemas.contracts import JDAnalysis

KNOWN_KEYWORDS = [
    "AI产品", "数据产品", "Prompt", "Python", "SQL", "Excel", "用户调研", "竞品分析",
    "数据看板", "A/B测试", "需求分析", "原型", "PRD", "机器学习", "大模型", "LLM",
]

TASK_HINTS = ["负责", "参与", "完成", "推进", "设计", "分析", "搭建", "优化", "调研"]
REQUIREMENT_HINTS = ["要求", "熟悉", "掌握", "具备", "能够", "本科", "每周", "到岗"]
BONUS_HINTS = ["加分", "优先", "作品集", "实习经历", "项目经验"]
RISK_HINTS = ["抗压", "强度", "加班", "出差", "自带资源", "无薪", "试用"]


def _extract_after_labels(text: str, labels: Iterable[str]) -> str:
    for label in labels:
        match = re.search(rf"{label}[：:]\s*([^\n，,。；;]+)", text)
        if match:
            return match.group(1).strip()
    return ""


def _split_phrases(text: str) -> List[str]:
    pieces = re.split(r"[\n。；;，,、]", text)
    return [piece.strip() for piece in pieces if piece.strip()]


def _sentences_containing(text: str, hints: Iterable[str]) -> List[str]:
    results: List[str] = []
    for piece in _split_phrases(text):
        if any(hint in piece for hint in hints):
            cleaned = re.sub(r"^(职责|要求|加分|岗位|公司)[：:]", "", piece).strip()
            if cleaned and cleaned not in results:
                results.append(cleaned)
    return results


def parse_jd(jd_text: str) -> JDAnalysis:
    text = jd_text.strip()
    job_title = _extract_after_labels(text, ["岗位", "职位", "岗位名称", "职位名称"])
    company = _extract_after_labels(text, ["公司", "企业", "公司名称"])

    job_type = ""
    if "实习" in text:
        job_type = "实习"
    elif "全职" in text:
        job_type = "全职"
    elif "校招" in text:
        job_type = "校招"

    core_tasks = _sentences_containing(text, TASK_HINTS)
    hard_requirements = _sentences_containing(text, REQUIREMENT_HINTS)
    bonus_points = _sentences_containing(text, BONUS_HINTS)
    risk_points = _sentences_containing(text, RISK_HINTS)

    ats_keywords = [keyword for keyword in KNOWN_KEYWORDS if keyword.lower() in text.lower()]
    soft_requirements = [item for item in ["沟通", "协作", "学习能力", "逻辑", "主动性"] if item in text]

    if not job_title:
        title_match = re.search(r"([\w\u4e00-\u9fa5]+(?:产品|运营|数据|算法|分析)[\w\u4e00-\u9fa5]*(?:实习生|经理|专员|助理)?)", text)
        job_title = title_match.group(1) if title_match else "待补充岗位名称"

    return JDAnalysis(
        job_title=job_title,
        company=company or "待补充公司名称",
        job_type=job_type or "待判断",
        core_tasks=core_tasks[:8],
        hard_requirements=hard_requirements[:8],
        soft_requirements=soft_requirements[:6],
        bonus_points=bonus_points[:6],
        ats_keywords=ats_keywords,
        risk_points=risk_points[:6],
    )
