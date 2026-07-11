import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "demo_video_script.md"


class DemoVideoScriptTest(unittest.TestCase):
    def test_demo_video_script_covers_one_minute_flow_and_interview_pitch(self):
        self.assertTrue(SCRIPT.exists())
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in [
            "Career Copilot Agent MVP 演示",
            "0-10秒",
            "10-20秒",
            "20-35秒",
            "35-50秒",
            "50-60秒",
            "保存本次分析",
            "导出 Markdown 报告",
            "面试讲稿",
            "不是一开始就做 Agent",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
