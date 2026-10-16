"""Onboarding protects private files without modifying public methodology."""
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".agents/skills/argentina-job-search/references/workflows/setup.md"


class NativeOnboardingPrivacyTests(unittest.TestCase):
    def test_readme_explains_private_profile_before_public_export(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        for fragment in ("profile/", "templates/profile/", ".runtime/", "tools/export_public.py"):
            self.assertIn(fragment, text)
        self.assertLess(text.index("`profile/`"), text.index("python tools/export_public.py"))
        self.assertIn("historial", text)

    def test_installation_keeps_private_data_out_of_public_methodology(self):
        text = (REPO / "SETUP.md").read_text(encoding="utf-8")
        for fragment in ("profile/candidate.md", "templates/profile/", "nunca se personalizan", "no sobrescribe"):
            self.assertIn(fragment, text)

    def test_workflow_checks_tracking_before_importing_personal_data(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        guard = text.index("no estén rastreados")
        self.assertLess(guard, text.index("## Step 0:"))
        self.assertIn("No publicar ni hacer push", text[:text.index("## Step 0:")])
        self.assertIn("No personaliza skills", text)
        self.assertIn("templates", text)


if __name__ == "__main__":
    unittest.main()
