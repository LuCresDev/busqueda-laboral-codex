"""Native onboarding preserves private data boundaries and template anchors."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / ".agents/skills/argentina-job-search/references/workflows/setup.md"
TEMPLATES = ROOT / "templates/profile"


class NativeOnboardingTests(unittest.TestCase):
    def setUp(self):
        self.text = FLOW.read_text(encoding="utf-8")

    def test_generated_destinations_are_exactly_public_profile_templates(self):
        step = self.text.split("## Step 3: Write Personal Files Only", 1)[1].split("## Step 4:", 1)[0]
        destinations = set(re.findall(r"^\d+\. (profile/[a-z-]+\.md)", step, re.M))
        expected = {"profile/" + path.name for path in TEMPLATES.glob("*.md")}
        self.assertEqual(len(expected), 5)
        self.assertEqual(destinations, expected)
        self.assertIn("No escribir datos", step)
        self.assertIn("template.json", step)
        self.assertIn("cv/main_example.tex", step)

    def test_behavioral_inference_targets_real_public_headings(self):
        bullet = next(line for line in self.text.splitlines() if line.startswith("- **`profile/behavioral.md`"))
        targets = re.findall(r'"([^"]+)"', bullet)
        headings = {line[3:].strip() for line in (TEMPLATES / "behavioral.md").read_text(encoding="utf-8").splitlines() if line.startswith("## ")}
        self.assertTrue(targets)
        self.assertTrue(set(targets).issubset(headings), set(targets) - headings)

    def test_project_and_personal_note_anchors_exist(self):
        cases = {
            "candidate.md": "Proyectos independientes",
            "writing-style.md": "Referencias aportadas por el usuario",
            "evaluation.md": "Calibración con resultados reales",
            "interview.md": "Experiencias candidatas para STAR",
        }
        for filename, heading in cases.items():
            with self.subTest(filename=filename):
                self.assertIn("## " + heading, (TEMPLATES / filename).read_text(encoding="utf-8"))
                self.assertIn("## " + heading, self.text)

    def test_import_keeps_projects_conflicts_provenance_and_confirmation(self):
        for required in ("documents/", "projects/", "measurable outcomes", "Cross-Reference", "Conflicting changes", "confirm", "procedencia"):
            with self.subTest(required=required):
                self.assertIn(required.casefold(), self.text.casefold())

    def test_initialization_does_not_claim_to_overwrite_existing_profile(self):
        self.assertIn("tools/bootstrap.py --profile-only", self.text)
        self.assertIn("no sobrescribe", self.text)
        self.assertIn("búsqueda amplia", self.text.casefold())
        self.assertNotIn("into **tracked** files", self.text)

if __name__ == "__main__":
    unittest.main()
