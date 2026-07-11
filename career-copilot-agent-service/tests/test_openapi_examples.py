import unittest
import warnings

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
    category=Warning,
)

from fastapi.testclient import TestClient

from app.main import app


class OpenApiExamplesTest(unittest.TestCase):
    def test_input_schemas_include_realistic_examples(self):
        schemas = TestClient(app).get("/openapi.json").json()["components"]["schemas"]
        for schema_name in [
            "JDParseRequest",
            "ResumeMatchRequest",
            "MaterialGenerateRequest",
            "AgentRunRequest",
        ]:
            self.assertIn("examples", schemas[schema_name])
            self.assertTrue(schemas[schema_name]["examples"])


if __name__ == "__main__":
    unittest.main()
