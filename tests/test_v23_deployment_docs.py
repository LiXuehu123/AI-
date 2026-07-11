import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHECKLIST = ROOT / "docs" / "deployment_checklist.md"


class DeploymentDocsTest(unittest.TestCase):
    def test_readme_documents_8001_local_fallback(self):
        text = README.read_text(encoding="utf-8")
        for phrase in [
            "若 8000 端口出现 WinError 10013 权限问题，可改用 8001 启动后端",
            "python -m uvicorn app.main:app --host 127.0.0.1 --port 8001",
            "前端 Agent 联调面板中的 API 地址同步填写",
            "http://127.0.0.1:8001",
            "本地可运行版本验收通过",
            "后端端口：8001",
            "前端端口：5500",
        ]:
            self.assertIn(phrase, text)

    def test_deployment_checklist_covers_v23_preflight(self):
        self.assertTrue(CHECKLIST.exists())
        text = CHECKLIST.read_text(encoding="utf-8")
        for phrase in [
            "V2.3 部署预检查",
            "前端 API 地址",
            "避免写死 127.0.0.1",
            "python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT",
            ".env.example",
            "没有提交真实 .env",
            "CORS",
            "requirements.txt",
            "不要新增复杂业务功能",
            "不要改 Agent 工作流",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

