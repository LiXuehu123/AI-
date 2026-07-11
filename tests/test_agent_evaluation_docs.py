import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "agent_evaluation.md"


class AgentEvaluationDocTest(unittest.TestCase):
    def read_doc(self):
        self.assertTrue(DOC.exists(), "docs/agent_evaluation.md should document V2.1 output evaluation")
        return DOC.read_text(encoding="utf-8")

    def test_agent_evaluation_doc_exists_with_three_realistic_cases(self):
        text = self.read_doc()
        for role in ["AI产品实习生", "产品运营 / 商业化运营实习生", "数据运营 / 数据产品实习生"]:
            self.assertIn(role, text)
        for payload_field in ["jd_text", "resume_text", "user_profile", "task"]:
            self.assertIn(payload_field, text)

    def test_agent_evaluation_doc_records_quality_dimensions_and_outputs(self):
        text = self.read_doc()
        for dimension in [
            "JD解析是否准确",
            "简历匹配评分是否合理",
            "matched_evidence 是否真实",
            "missing_evidence 是否具体",
            "投递材料是否可用",
            "quality_review 是否发现风险",
            "recommended_next_action 是否具体",
        ]:
            self.assertIn(dimension, text)
        for output_marker in ["overall_score", "priority_level", "quality_review", "recommended_next_action"]:
            self.assertIn(output_marker, text)


if __name__ == "__main__":
    unittest.main()
