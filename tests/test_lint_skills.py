"""Exercise native skill discovery, workflow titles and referenced CLI paths."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class NativeSkillLintTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "tools").mkdir()
        shutil.copy(REPO_ROOT / "tools/lint_skills.py", self.root / "tools/lint_skills.py")
        self.skill = self.root / ".agents/skills/example/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text("---\nname: example\ndescription: Example skill\n---\n", encoding="utf-8")
        self.workflow = self.root / ".agents/skills/argentina-job-search/references/workflows/setup.md"
        self.workflow.parent.mkdir(parents=True)
        self.workflow.write_text("# Completar perfil\n", encoding="utf-8")

    def run_linter(self):
        return subprocess.run([sys.executable, str(self.root / "tools/lint_skills.py")],
                              capture_output=True, text=True, encoding="utf-8")

    def test_native_tree_without_settings_passes_and_is_not_double_counted(self):
        result = self.run_linter()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 skills, 1 workflow references", result.stdout)

    def test_frontmatter_shapes_fail_cleanly(self):
        for contents in ("# Missing frontmatter", "---\nname: example\n", "---\n- list\n---\n", "---\nname: example\ndescription:\n---\n"):
            with self.subTest(contents=contents):
                self.skill.write_text(contents, encoding="utf-8")
                result = self.run_linter()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_missing_cli_path_fails_and_existing_path_passes(self):
        self.skill.write_text("---\nname: example\ndescription: Example\nallowed-tools: Bash(bun run .agents/skills/example/cli.ts *)\n---\n", encoding="utf-8")
        result = self.run_linter()
        self.assertEqual(result.returncode, 1)
        self.assertIn("references a missing file", result.stdout)
        (self.skill.parent / "cli.ts").write_text("// fixture\n", encoding="utf-8")
        self.assertEqual(self.run_linter().returncode, 0)

    def test_custom_fields_belong_in_metadata_and_enabled_is_boolean(self):
        for fields in ("enabled: false", "version: 1.0.0", "metadata:\n  enabled: perhaps"):
            with self.subTest(fields=fields):
                self.skill.write_text("---\nname: example\ndescription: Example\n" + fields + "\n---\n", encoding="utf-8")
                self.assertEqual(self.run_linter().returncode, 1)
        self.skill.write_text("---\nname: example\ndescription: Example\nmetadata:\n  version: '1.0.0'\n  enabled: false\n---\n", encoding="utf-8")
        self.assertEqual(self.run_linter().returncode, 0)

    def test_empty_native_skill_root_fails_even_if_workflows_exist(self):
        self.skill.unlink()
        result = self.run_linter()
        self.assertEqual(result.returncode, 1)
        self.assertIn("no SKILL.md files found", result.stdout)

    def test_empty_workflow_root_fails(self):
        self.workflow.unlink()
        self.assertEqual(self.run_linter().returncode, 1)

    def test_wrong_skill_name_and_workflow_alias_fail(self):
        self.skill.write_text("---\nname: other\ndescription: Example\n---\n", encoding="utf-8")
        self.workflow.write_text("# /different - Wrong alias\n", encoding="utf-8")
        result = self.run_linter()
        self.assertEqual(result.returncode, 1)
        self.assertIn("reviewed alias", result.stdout)
        self.assertIn("does not match filename", result.stdout)

    def test_workflow_needs_a_title_without_requiring_slash_syntax(self):
        self.workflow.write_text("No heading\n", encoding="utf-8")
        self.assertEqual(self.run_linter().returncode, 1)

    def test_local_links_resolve_and_missing_links_fail(self):
        self.workflow.write_text("# Completar perfil\n\n[Datos](data.md)\n", encoding="utf-8")
        self.assertIn("broken local link", self.run_linter().stdout)
        (self.workflow.parent / "data.md").write_text("# Datos\n", encoding="utf-8")
        self.assertEqual(self.run_linter().returncode, 0)

    def test_cli_paths_cannot_escape_the_repository(self):
        self.skill.write_text("---\nname: example\ndescription: Example\nallowed-tools: Bash(bun run ../outside.ts *)\n---\n", encoding="utf-8")
        self.assertIn("must stay inside the repository", self.run_linter().stdout)

    def test_legacy_runtime_is_not_treated_as_a_native_skill(self):
        (self.root / ".claude").mkdir()
        self.assertIn("legacy runtime path", self.run_linter().stdout)


if __name__ == "__main__":
    unittest.main()
