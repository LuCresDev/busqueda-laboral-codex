"""The selected PDF renderer and workflow agree on actual page budgets."""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLY = ROOT / ".agents/skills/argentina-job-search/references/workflows/apply.md"
RENDERER = ROOT / "tools/render_application.py"


class ActiveTemplatePageLimitsTests(unittest.TestCase):
    def setUp(self):
        self.text = APPLY.read_text(encoding="utf-8")
        self.render = self.text.split("### 5a.", 1)[1].split("### 5b.", 1)[0]
        self.inspect = self.text.split("### 5b.", 1)[1].split("### 5c.", 1)[0]

    def test_runnable_render_commands_cover_both_actual_document_kinds(self):
        invocations = re.findall(r"'tools/render_application.py', '--kind', '(cv|cover)', '--input', '([^']+)', '--output', '([^']+)'", self.render)
        self.assertEqual({kind for kind, _, _ in invocations}, {"cv", "cover"})
        for kind, source, output in invocations:
            self.assertTrue(source.endswith(".json"), (kind, source))
            self.assertEqual(source[:-5] + ".pdf", output)
        module = ast.parse(RENDERER.read_text(encoding="utf-8"))
        limits = next(ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "LIMITS" for target in node.targets))
        self.assertEqual(limits, {"cv": 2, "cover": 1})
        self.assertIn("CV 1–2 pages", self.inspect)
        self.assertIn("cover letter 1 page", self.inspect)

    def test_one_page_cv_is_not_forced_to_two_pages(self):
        self.assertIn("do not force --pages 2", self.inspect)
        self.assertIn("letter use --pages 1", self.inspect)
        self.assertNotRegex(self.render, r"verify_pdf.py\s+cv/\S+\s+--pages\s+2")

    def test_inspection_and_degraded_layout_verdict_are_explicit(self):
        self.assertIn("Inspect every rendered page", self.inspect)
        self.assertIn("exit 2/skipped", self.inspect)
        self.assertIn("never an approved layout verdict", self.inspect)
        self.assertIn("do not present an older PDF", self.render)

if __name__ == "__main__":
    unittest.main()
