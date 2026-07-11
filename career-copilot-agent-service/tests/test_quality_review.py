import unittest

from app.schemas.contracts import GeneratedMaterials, JDAnalysis, ResumeMatch
from app.skills.quality_review import review_quality


class QualityReviewTest(unittest.TestCase):
    def test_flags_fabrication_exaggeration_missing_keywords_and_marketing_tone(self):
        review = review_quality(
            materials=GeneratedMaterials(
                email_subject="强烈推荐我，完美匹配AI产品实习生",
                email_body="我保证能带来巨大价值，可补充：真实数据。作品覆盖Python。",
                boss_message="我精通AI产品，期待立刻沟通。",
                referral_message="请帮我内推。",
                follow_up_message="谢谢。",
                attachment_name="简历_AI产品实习生.pdf",
            ),
            jd_analysis=JDAnalysis(
                job_title="AI产品实习生",
                company="星河科技",
                job_type="实习",
                ats_keywords=["Python", "SQL", "Prompt"],
            ),
            resume_match=ResumeMatch(
                overall_score=70,
                matched_evidence=["简历中出现 JD 关键词：Python"],
                missing_evidence=["缺少 JD 关键词或证据：SQL", "缺少 JD 关键词或证据：Prompt"],
            ),
        )

        self.assertTrue(review.has_fabrication_risk)
        self.assertTrue(review.has_exaggeration_risk)
        self.assertIn("SQL", review.missing_keywords)
        self.assertTrue(review.tone_issues)
        self.assertEqual(review.final_safety_level, "needs_review")


if __name__ == "__main__":
    unittest.main()
