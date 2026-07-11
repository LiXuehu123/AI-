from app.schemas.contracts import JDAnalysis


def save_pipeline_stub(jd_analysis: JDAnalysis, match_score: int, status: str = "待投递") -> dict:
    return {
        "company": jd_analysis.company,
        "position": jd_analysis.job_title,
        "match_score": match_score,
        "status": status,
        "note": "MVP 阶段不自动写入数据库，需用户确认后再保存。",
    }
