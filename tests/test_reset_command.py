"""Reset's documented delete scope is complete and excludes public resources."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / ".agents/skills/argentina-job-search/references/workflows/reset.md"
SETUP = FLOW.with_name("setup.md")


class NativeResetTests(unittest.TestCase):
    def setUp(self):
        self.text = FLOW.read_text(encoding="utf-8")

    def test_profile_scope_covers_every_bootstrap_template(self):
        names = {path.name for path in (ROOT / "templates/profile").glob("*.md")}
        self.assertEqual(len(names), 5)
        profile_scope = self.text.split("- Perfil:", 1)[1].split("- Documentos:", 1)[0]
        for name in names:
            self.assertIn("profile/" + name, profile_scope)
        self.assertIn("templates/profile/", profile_scope)
        self.assertIn("No escribir fuera de profile/", profile_scope)

    def test_document_scope_includes_all_tracked_personal_drop_folders(self):
        output = subprocess.run(["git", "ls-files", "documents/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        folders = {line.split("/")[1] for line in output.splitlines() if len(line.split("/")) >= 3}
        self.assertGreaterEqual(len(folders), 5)
        scope = self.text.split("- Documentos:", 1)[1].split("- Estado:", 1)[0]
        for folder in folders:
            self.assertIn("documents/" + folder + "/", scope)
        self.assertIn(".gitkeep", scope)
        self.assertIn("README", scope)

    def test_reset_and_onboarding_share_personal_destinations(self):
        setup = SETUP.read_text(encoding="utf-8").split("## Step 3:", 1)[1].split("## Step 4:", 1)[0]
        targets = set(re.findall(r"^\d+\. (profile/[a-z-]+\.md)", setup, re.M))
        self.assertEqual(len(targets), 5)
        self.assertTrue(all(target in self.text for target in targets))

    def test_destructive_actions_require_concrete_scope_and_bounded_paths(self):
        for required in ("alcance", "Enumerar", "rutas absolutas", "carpetas autorizadas", "LiteralPath", "enlaces simbólicos", "esperar la decisión", "estado parcial"):
            self.assertIn(required, self.text)
        self.assertNotRegex(self.text, r"rm\s+-rf\s+(?:\.agents|templates|\.git)")

    def test_public_resources_and_external_services_are_preserved(self):
        for required in ("No modificar AGENTS.md", ".agents/skills/", "templates", "No borrar .git", "No tocar Gmail, Notion", "no sobrescribe existentes"):
            self.assertIn(required, self.text)
        self.assertIn("Estado: solo si", self.text)

if __name__ == "__main__":
    unittest.main()
