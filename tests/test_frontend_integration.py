import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class FrontendIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_agent_button_and_panel_exist(self):
        self.assertIn("一键运行 Career Copilot Agent", self.html)
        self.assertIn('id="tab-agent"', self.html)
        self.assertIn('id="agentOutput"', self.html)
        self.assertIn("runCareerAgent()", self.html)

    def test_frontend_calls_configured_agent_run_endpoint(self):
        self.assertIn("API_BASE_URL", self.html)
        self.assertIn("CAREER_COPILOT_CONFIG", self.html)
        self.assertIn("http://127.0.0.1:8001", self.html)
        self.assertIn("https://xxx.onrender.com", self.html)
        self.assertIn("/api/agent/run", self.html)
        self.assertIn("fetch(`${apiBase}/api/agent/run`", self.html)
        self.assertNotIn("http://127.0.0.1:8000/docs</b>", self.html)

    def test_payload_uses_backend_schema_field_names(self):
        build_payload = re.search(r"function buildAgentPayload\(\)\{(?P<body>.*?)function validateAgentPayload", self.html, re.S)
        self.assertIsNotNone(build_payload)
        body = build_payload.group("body")
        for field in ["jd_text", "resume_text", "user_profile", "task"]:
            self.assertIn(field, body)
        for frontend_only_field in ["jdText:", "resumeText:"]:
            self.assertNotIn(frontend_only_field, body)

    def test_renders_all_agent_result_sections(self):
        for label in [
            "JD 解析结果",
            "简历匹配评分",
            "投递优先级",
            "投递材料",
            "质量审核",
            "下一步行动建议",
        ]:
            self.assertIn(label, self.html)

    def test_loading_error_and_no_api_key(self):
        self.assertIn("setAgentLoading", self.html)
        self.assertIn("renderAgentError", self.html)
        self.assertNotIn("sk-", self.html)
        self.assertNotIn("OPENAI_API_KEY", self.html)

    def test_agent_save_and_export_controls_exist(self):
        for label in ["保存本次分析", "导出分析报告"]:
            self.assertIn(label, self.html)
        for function_name in [
            "saveCurrentAgentAnalysis",
            "exportCurrentAgentReport",
            "buildAgentMarkdownReport",
        ]:
            self.assertIn(f"function {function_name}", self.html)

    def test_agent_result_can_be_persisted_and_exported(self):
        self.assertIn("lastAgentPayload", self.html)
        self.assertIn("lastAgentResult", self.html)
        self.assertIn("careerCopilotAgentAnalyses", self.html)
        self.assertIn("localStorage.setItem('careerCopilotAgentAnalyses'", self.html)
        for section in [
            "# Career Copilot Agent 分析报告",
            "## JD 解析",
            "## 简历匹配",
            "## 投递优先级",
            "## 投递材料",
            "## 质量审核",
            "## 下一步行动建议",
        ]:
            self.assertIn(section, self.html)

    def test_showcase_agent_architecture_module_exists(self):
        for label in [
            "项目说明 / Agent 架构",
            "V2.3：线上部署适配",
            "项目定位：AI 求职投递 Agent",
            "JD解析 → 简历匹配 → 优先级判断 → 材料生成 → 质量审核",
            "HTML 前端 + FastAPI 后端 + Skills 工作流 + LocalStorage",
            "后端上线、数据库记忆、多 Agent 协作",
        ]:
            self.assertIn(label, self.html)


if __name__ == "__main__":
    unittest.main()


