"""Public profile scaffolds remain generic; user profiles are checked separately."""
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]


class PublicProfileTemplateTests(unittest.TestCase):
    def test_candidate_template_keeps_unknown_identity_and_no_user_biography(self):
        text = (REPO / "templates/profile/candidate.md").read_text(encoding="utf-8")
        for field in ("Nombre", "Ciudad y país de residencia", "Correo de contacto", "Profesión y puestos objetivo"):
            self.assertIn(f"- **{field}:** pendiente.", text)
        for section in ("## Experiencia profesional", "## Educación", "## Idiomas laborales", "## Proyectos independientes"):
            self.assertIn(section, text)

    def test_every_public_profile_template_is_shippable_while_private_profiles_are_ignored(self):
        templates = sorted((REPO / "templates/profile").glob("*.md"))
        self.assertGreaterEqual(len(templates), 5)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", folder], check=True, capture_output=True)
            (root / ".gitignore").write_text((REPO / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8")
            for template in templates:
                public = template.relative_to(REPO).as_posix()
                private = f"profile/{template.name}"
                for path, ignored in ((public, False), (private, True)):
                    result = subprocess.run(["git", "-C", folder, "check-ignore", "-q", path], capture_output=True)
                    self.assertEqual(result.returncode == 0, ignored, path)

    def test_ci_runs_the_template_guards_for_every_fork(self):
        text = (REPO / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover -s tests -t . -v", text)
        self.assertNotIn("check profile/candidate.md", text)
        self.assertNotIn("name: Placeholder integrity (upstream template only)", text)


if __name__ == "__main__":
    unittest.main()
