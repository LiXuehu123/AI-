import unittest

from app.agents.career_agent import CareerCopilotAgent
from app.schemas.contracts import (
    AgentRunRequest,
    JDAnalysis,
    MaterialGenerateRequest,
    ResumeMatch,
    ResumeMatchRequest,
    UserProfile,
)
from app.skills.generate_material import generate_material
from app.skills.match_resume import match_resume
from app.skills.parse_jd import parse_jd


class ApiContractTest(unittest.TestCase):
    def test_parse_jd_returns_structured_analysis(self):
        data = parse_jd(
            "公司：星河科技\n岗位：AI产品实习生\n职责：负责用户调研、竞品分析、Prompt设计和数据看板。\n要求：会Python、SQL，能每周到岗4天。加分：有AI产品作品集。"
        )

        self.assertEqual(data.job_title, "AI产品实习生")
        self.assertEqual(data.company, "星河科技")
        self.assertTrue(any("Prompt" in task for task in data.core_tasks))
        self.assertIn("Python", data.ats_keywords)
        self.assertIsInstance(data.risk_points, list)

    def test_match_resume_returns_score_evidence_and_recommendation(self):
        request = ResumeMatchRequest(
            jd_analysis=JDAnalysis(
                job_title="AI产品实习生",
                company="星河科技",
                job_type="实习",
                core_tasks=["用户调研", "竞品分析", "Prompt设计"],
                hard_requirements=["Python", "SQL"],
                soft_requirements=["沟通"],
                bonus_points=["AI产品作品集"],
                ats_keywords=["Python", "SQL", "Prompt", "用户调研"],
                risk_points=[],
            ),
            resume_text="我做过AI求职助手作品集，使用Python和SQL分析数据，并完成用户调研与竞品分析。",
            user_profile=UserProfile(availability="每周4天"),
        )
        data = match_resume(request.jd_analysis, request.resume_text, request.user_profile)

        self.assertGreaterEqual(data.overall_score, 0)
        self.assertLessEqual(data.overall_score, 100)
        self.assertTrue(data.matched_evidence)
        self.assertIn(
            data.application_recommendation,
            ["strong_apply", "apply_after_revision", "not_recommended"],
        )


    def test_non_ai_ops_role_requires_role_specific_evidence(self):
        jd_analysis = JDAnalysis(
            job_title="商业化产品运营实习生",
            company="光合增长",
            job_type="实习",
            core_tasks=["商业化活动配置", "用户分层", "转化漏斗分析"],
            hard_requirements=["Excel", "SQL"],
            soft_requirements=["沟通"],
            bonus_points=["电商运营", "活动运营", "数据复盘"],
            ats_keywords=["SQL", "Excel"],
            risk_points=[],
        )
        resume_text = "我做过AI求职助手Demo，使用Python、SQL和Excel整理岗位数据，并完成Prompt迭代和PRD草稿。"
        user_profile = UserProfile(target_roles=["产品运营", "商业化运营"], availability="每周4天")

        data = match_resume(jd_analysis, resume_text, user_profile)

        self.assertLess(data.overall_score, 85)
        self.assertNotEqual(data.application_recommendation, "strong_apply")
        self.assertTrue(any("商业化" in item or "用户分层" in item or "转化" in item for item in data.missing_evidence))

    def test_generate_material_uses_only_supplied_information(self):
        request = MaterialGenerateRequest(
            jd_analysis=JDAnalysis(
                job_title="AI产品实习生",
                company="星河科技",
                job_type="实习",
                ats_keywords=["Python", "SQL", "Prompt"],
            ),
            resume_match=ResumeMatch(
                overall_score=82,
                matched_evidence=["简历中提到AI求职助手作品集", "简历中提到Python和SQL"],
                missing_evidence=[],
                application_recommendation="strong_apply",
            ),
            resume_text="我做过AI求职助手作品集，使用Python和SQL分析数据。",
            user_profile=UserProfile(portfolio_url="https://example.com/portfolio"),
        )
        data = generate_material(
            request.jd_analysis,
            request.resume_match,
            request.resume_text,
            request.user_profile,
        )

        self.assertIn("AI产品实习生", data.email_subject)
        self.assertNotIn("可补充", data.email_subject)
        self.assertIn("https://example.com/portfolio", data.email_body)
        self.assertTrue(data.attachment_name.endswith(".pdf"))


    def test_agent_run_uses_revision_next_action_for_p1(self):
        data = CareerCopilotAgent().run(
            AgentRunRequest(
                user_profile=UserProfile(
                    identity="应届生",
                    target_roles=["产品运营", "商业化运营"],
                    availability="每周4天",
                    portfolio_url="https://example.com/portfolio",
                ),
                resume_text="我做过AI求职助手Demo，使用Python、SQL和Excel整理岗位数据，并完成Prompt迭代和PRD草稿。",
                jd_text="公司：光合增长\n岗位：商业化产品运营实习生\n职责：支持商业化活动配置、商家运营、用户分层和转化漏斗分析。\n要求：Excel、SQL。加分：电商运营和活动复盘经验。",
                task="判断是否值得投递，并生成投递材料",
            )
        )

        self.assertEqual(data.priority_decision.priority_level, "P1")
        self.assertEqual(data.recommended_next_action, data.priority_decision.next_action)
        self.assertIn("补强", data.recommended_next_action)

    def test_agent_run_orchestrates_full_workflow(self):
        data = CareerCopilotAgent().run(
            AgentRunRequest(
                user_profile=UserProfile(
                    identity="应届生",
                    target_roles=["AI产品"],
                    availability="每周4天",
                    portfolio_url="https://example.com/portfolio",
                ),
                resume_text="我做过AI求职助手作品集，使用Python和SQL分析数据，并完成用户调研与Prompt设计。",
                jd_text="公司：星河科技\n岗位：AI产品实习生\n职责：负责用户调研、Prompt设计和数据看板。\n要求：Python、SQL。加分：AI产品作品集。",
                task="判断是否值得投递，并生成投递材料",
            )
        )

        self.assertEqual(data.jd_analysis.job_title, "AI产品实习生")
        self.assertGreaterEqual(data.resume_match.overall_score, 60)
        self.assertTrue(data.generated_materials.email_subject)
        self.assertIn(data.quality_review.final_safety_level, ["safe", "needs_review", "blocked"])
        self.assertTrue(data.recommended_next_action)
        self.assertEqual([step["step"] for step in data.trace], [
            "parse_jd",
            "match_resume",
            "decide_priority",
            "generate_material",
            "quality_review",
        ])


if __name__ == "__main__":
    unittest.main()



