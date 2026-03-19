from __future__ import annotations

import unittest

from dailyinsight.html import render_html
from dailyinsight.llm import MockLLMClient
from dailyinsight.orchestrator import DailyInsightOrchestrator
from dailyinsight.render import render_markdown


class OrchestratorTest(unittest.TestCase):
    def test_mock_pipeline_generates_report(self) -> None:
        orchestrator = DailyInsightOrchestrator(MockLLMClient())
        insight, outputs = orchestrator.run("examples/sample_brief.json")
        content = render_markdown(insight, outputs)
        html = render_html(insight, outputs)

        self.assertIn("Daily Master Report", content)
        self.assertIn("Source Validation", content)
        self.assertIn("Probability and Future View", content)
        self.assertIn("Emerging and Less-Obvious Candidates", content)
        self.assertIn("Final Report Review", content)
        self.assertIn("https://www.reuters.com/", content)
        self.assertIn("Confidence", content)
        self.assertEqual(insight.date, "2026-03-19")
        self.assertGreater(len(insight.executive_summary), 0)
        self.assertIn("scout", outputs)
        self.assertIn("source_gate", outputs)
        self.assertIn("report_verifier", outputs)
        self.assertIn("<html", html)
        self.assertIn("Decision Dashboard", html)


if __name__ == "__main__":
    unittest.main()
