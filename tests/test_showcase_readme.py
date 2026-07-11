import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


class ShowcaseReadmeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def test_readme_describes_demo_to_agent_upgrade_path(self):
        for section in [
            "从 Demo 到 Agent MVP 的升级路径",
            "V2.0 版本进一步引入 FastAPI 后端",
            "V2.1 版本加入真实岗位输出评估",
            "V2.2：Agent MVP Showcase",
        ]:
            self.assertIn(section, self.text)

    def test_readme_includes_mermaid_architecture_and_workflow(self):
        self.assertGreaterEqual(self.text.count("```mermaid"), 2)
        for diagram_term in [
            "前端工作台",
            "Agent 联调面板",
            "POST /api/agent/run",
            "Career Copilot Agent",
            "JD Parse Skill",
            "Resume Match Skill",
            "Priority Decision Skill",
            "Material Generate Skill",
            "Quality Review Skill",
            "保存到 LocalStorage",
            "导出 Markdown 报告",
            "JD 输入",
            "质量审核",
        ]:
            self.assertIn(diagram_term, self.text)

    def test_readme_explains_agent_not_prompt_demo_and_evaluation_method(self):
        for phrase in [
            "为什么这是 Agent，而不是普通 Prompt Demo",
            "不是单次 Prompt 文案生成",
            "多个可执行 Skill",
            "结构化输出",
            "输出质量评估方法",
            "docs/agent_evaluation.md",
        ]:
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
