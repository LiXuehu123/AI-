import inspect
import json
import unittest
import warnings
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.main import app, build_cors_allow_origins


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "sample_payloads"


class HttpContractTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _sample(self, filename: str) -> dict:
        with (SAMPLE_DIR / filename).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def assert_structured_json_object(self, response):
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["content-type"].split(";")[0], "application/json")
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertNotIn("message", data)
        self.assertNotIn("text", data)
        return data



    def test_health_endpoint_is_ready_for_platform_checks(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "career-copilot-agent-service")

    def test_cors_defaults_support_local_and_github_pages_frontends(self):
        origins = build_cors_allow_origins("")
        for origin in [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "https://lixuehu123.github.io",
        ]:
            self.assertIn(origin, origins)

    def test_cors_env_allows_future_online_frontend_domains(self):
        origins = build_cors_allow_origins("https://career-copilot.example.com, https://xxx.vercel.app")
        self.assertIn("https://career-copilot.example.com", origins)
        self.assertIn("https://xxx.vercel.app", origins)
        self.assertIn("http://127.0.0.1:5500", origins)

    def test_http_endpoints_are_async_for_uvicorn_runtime(self):
        endpoints = {
            route.path: route.endpoint
            for route in app.routes
            if getattr(route, "path", "") in {
                "/health",
                "/api/jd/parse",
                "/api/resume/match",
                "/api/material/generate",
                "/api/agent/run",
            }
        }
        for path in [
            "/health",
            "/api/jd/parse",
            "/api/resume/match",
            "/api/material/generate",
            "/api/agent/run",
        ]:
            self.assertIn(path, endpoints)
            self.assertTrue(inspect.iscoroutinefunction(endpoints[path]), path)
    def test_openapi_exposes_swagger_callable_contracts(self):
        openapi = self.client.get("/openapi.json").json()
        for path in [
            "/api/jd/parse",
            "/api/resume/match",
            "/api/material/generate",
            "/api/agent/run",
        ]:
            post_contract = openapi["paths"][path]["post"]
            self.assertIn("requestBody", post_contract)
            self.assertIn("application/json", post_contract["requestBody"]["content"])
            self.assertIn("200", post_contract["responses"])
            self.assertIn("application/json", post_contract["responses"]["200"]["content"])

    def test_swagger_payloads_call_all_endpoints(self):
        jd_analysis = self.assert_structured_json_object(
            self.client.post("/api/jd/parse", json=self._sample("jd_parse.json"))
        )
        self.assertEqual(
            sorted(jd_analysis.keys()),
            sorted([
                "job_title",
                "company",
                "job_type",
                "core_tasks",
                "hard_requirements",
                "soft_requirements",
                "bonus_points",
                "ats_keywords",
                "risk_points",
            ]),
        )

        resume_match = self.assert_structured_json_object(
            self.client.post("/api/resume/match", json=self._sample("resume_match.json"))
        )
        self.assertIn("dimension_scores", resume_match)
        self.assertIn("matched_evidence", resume_match)

        generated_materials = self.assert_structured_json_object(
            self.client.post("/api/material/generate", json=self._sample("material_generate.json"))
        )
        self.assertIn("email_subject", generated_materials)
        self.assertIn("attachment_name", generated_materials)

        agent_result = self.assert_structured_json_object(
            self.client.post("/api/agent/run", json=self._sample("agent_run.json"))
        )
        self.assertEqual(
            [item["step"] for item in agent_result["trace"]],
            [
                "parse_jd",
                "match_resume",
                "decide_priority",
                "generate_material",
                "quality_review",
            ],
        )
        self.assertIn("quality_review", agent_result)
        self.assertEqual(
            sorted(agent_result["quality_review"].keys()),
            sorted([
                "has_fabrication_risk",
                "fabrication_items",
                "has_exaggeration_risk",
                "exaggeration_items",
                "missing_keywords",
                "tone_issues",
                "revision_suggestions",
                "final_safety_level",
            ]),
        )


if __name__ == "__main__":
    unittest.main()



