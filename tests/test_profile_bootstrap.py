"""First-run portability, private-data preservation and truthful diagnostics."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import bootstrap, doctor


REPO = Path(__file__).resolve().parents[1]
AVAILABLE = {name: {"available": True, "version": "test"} for name in doctor.DEPENDENCIES.values()}


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "AGENTS.md").write_text("# Test workspace\n", encoding="utf-8")
        shutil.copytree(REPO / "templates/profile", self.root / "templates/profile")

    def test_first_run_copies_complete_generic_profile_without_runtime(self):
        result = bootstrap.bootstrap(self.root, profile_only=True)
        self.assertEqual(len(result["created"]), len(bootstrap.PROFILE_FILES))
        self.assertFalse((self.root / ".runtime").exists())
        for name in bootstrap.PROFILE_FILES:
            self.assertEqual(
                (self.root / "profile" / name).read_bytes(),
                (self.root / "templates/profile" / name).read_bytes(),
            )
        candidate = (self.root / "profile/candidate.md").read_text(encoding="utf-8")
        for section in ("Identidad y contacto", "Idiomas laborales", "Experiencia profesional", "Educación", "Habilidades técnicas", "Fuentes y pendientes"):
            self.assertIn(section, candidate)

    def test_repeat_preserves_profile_credentials_and_custom_runtime_byte_for_byte(self):
        bootstrap.bootstrap(self.root, profile_only=True)
        private = self.root / "profile/candidate.md"
        private.write_bytes(b"TEST_PRIVATE_PERSON_37\nUser supplied history\n")
        runtime = self.root / ".runtime/runtime.local.json"
        runtime.parent.mkdir()
        runtime.write_bytes(b'{"python":"/custom/python", "private_key":"sentinel"}\n')
        credentials = self.root / ".env"
        credentials.write_bytes(b"SECRET_SENTINEL=must-stay\n")
        before = {path: path.read_bytes() for path in (private, runtime, credentials)}
        result = bootstrap.bootstrap(self.root)
        self.assertFalse(result["created"])
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        for source in (self.root / "templates/profile").glob("*.md"):
            self.assertNotIn("TEST_PRIVATE_PERSON_37", source.read_text(encoding="utf-8"))

    def test_runtime_discovery_uses_current_python_and_path(self):
        executable = self.root / "bun-from-test-path"
        executable.write_text("test", encoding="utf-8")
        with patch.object(bootstrap.shutil, "which", side_effect=lambda name: str(executable) if name == "bun" else None) as lookup:
            result = bootstrap.bootstrap(self.root, runtime_only=True)
        config = json.loads((self.root / ".runtime/runtime.local.json").read_text(encoding="utf-8"))
        self.assertEqual(config["python"], str(Path(sys.executable).resolve()))
        self.assertEqual(config["bun"], str(executable.resolve()))
        self.assertIsNone(config["codex"])
        self.assertEqual({call.args[0] for call in lookup.call_args_list}, {"bun", "node", "codex"})
        self.assertEqual(result["missing_optional"], ["node", "codex"])
        self.assertFalse((self.root / "profile").exists())

    def test_missing_template_fails_before_creating_any_profile(self):
        (self.root / "templates/profile/interview.md").unlink()
        with self.assertRaisesRegex(bootstrap.BootstrapError, "interview.md"):
            bootstrap.bootstrap(self.root, profile_only=True)
        self.assertFalse((self.root / "profile").exists())

    def test_existing_malformed_runtime_is_not_repaired_or_replaced(self):
        runtime = self.root / ".runtime/runtime.local.json"
        runtime.parent.mkdir()
        runtime.write_bytes(b"user-managed, not JSON\n")
        result = bootstrap.bootstrap(self.root, runtime_only=True)
        self.assertIn(".runtime/runtime.local.json", result["preserved"])
        self.assertEqual(runtime.read_bytes(), b"user-managed, not JSON\n")

    def test_bundled_bun_is_detected_without_a_user_specific_absolute_path(self):
        bundled = self.root / ".runtime/bun/bun-windows-x64/bun.exe"
        bundled.parent.mkdir(parents=True)
        bundled.write_bytes(b"local executable fixture")
        with patch.object(bootstrap.shutil, "which", return_value=None):
            runtime = bootstrap.detect_runtime(self.root)
        self.assertEqual(runtime["bun"], str(bundled.resolve()))

    def test_generic_templates_have_no_biography_urls_or_machine_paths(self):
        for source in (REPO / "templates/profile").glob("*.md"):
            text = source.read_text(encoding="utf-8")
            with self.subTest(source=source.name):
                self.assertIn("pendiente", text.casefold())
                self.assertNotIn("linkedin.com/in/", text)
                self.assertNotIn("C:/Users/", text)
                self.assertNotIn("C:\\Users\\", text)
                self.assertNotIn(".runtime/runtime.local.json", text)


class DoctorTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for relative in (
            "AGENTS.md", ".agents/skills/argentina-job-search/SKILL.md",
            "tools/render_application.py",
            ".agents/skills/job-application-assistant/05-cv-templates.md",
            ".agents/skills/job-application-assistant/06-cover-letter-templates.md",
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Test installation\n", encoding="utf-8")
        shutil.copytree(REPO / "templates/profile", self.root / "templates/profile")
        bootstrap.bootstrap(self.root, profile_only=True)
        self.config = {
            "schema_version": 1, "locale": "es-AR", "country_code": "AR",
            "profile_sources": ["profile/candidate.md"],
            "market": {"portals_config": "config/portals.json"},
            "templates": {
                "cv": "templates/cv/test/template.json",
                "cover_letter": "templates/cover_letters/test/template.json",
            },
            "pdf": {"renderer": "tools/render_application.py", "cv_page_range": [1, 2], "cover_letter_pages": 1},
        }
        (self.root / "config").mkdir()
        self.write_config()
        (self.root / "config/portals.json").write_text('{"primary_portals":[]}', encoding="utf-8")
        for relative in self.config["templates"].values():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"person":{"name":"[NAME]"}}', encoding="utf-8")
            (path.parent / "TEMPLATE.md").write_text("# Test manifest\n", encoding="utf-8")

    def write_config(self):
        (self.root / "config/argentina.json").write_text(json.dumps(self.config), encoding="utf-8")

    def run_doctor(self, dependencies=AVAILABLE):
        with patch.object(doctor, "dependency_status", return_value=dependencies), patch.object(doctor.shutil, "which", return_value=None):
            return doctor.diagnose(self.root)

    def test_no_bun_or_codex_cli_allows_app_and_web_fallback(self):
        result = self.run_doctor()
        self.assertTrue(result["ok"], result)
        checks = {item["name"]: item for item in result["checks"]}
        self.assertEqual(checks["opcional.bun"]["status"], "warning")
        self.assertEqual(checks["opcional.codex"]["status"], "warning")
        self.assertEqual(checks["perfil.estado"]["status"], "warning")
        self.assertIn("app", checks["opcional.codex"]["detail"])

    def test_missing_pdf_dependency_fails_even_when_cli_tools_are_optional(self):
        dependencies = {**AVAILABLE, "pypdf": {"available": False}}
        result = self.run_doctor(dependencies)
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["name"] == "dependencia.pypdf" and item["status"] == "error" for item in result["checks"]))

    def test_profile_state_is_not_deduced_from_a_section_heading(self):
        (self.root / "profile/candidate.md").write_text(
            "# Perfil\n\n## Estado\nRevisado con el usuario.\n\n## Fuentes y pendientes de verificación\nSin observaciones.\n",
            encoding="utf-8",
        )
        result = self.run_doctor()
        check = next(item for item in result["checks"] if item["name"] == "perfil.estado")
        self.assertEqual(check["status"], "ok")

    def test_config_cannot_redirect_templates_outside_project(self):
        self.config["templates"]["cv"] = "../private.json"
        self.write_config()
        result = self.run_doctor()
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["name"] == "plantilla.cv" and "sale del proyecto" in item["detail"] for item in result["checks"]))

    def test_malformed_market_json_and_missing_manifest_are_errors(self):
        (self.root / "config/argentina.json").write_text("{", encoding="utf-8")
        self.assertFalse(self.run_doctor()["ok"])
        self.write_config()
        (self.root / "templates/cv/test/TEMPLATE.md").unlink()
        self.assertFalse(self.run_doctor()["ok"])

    def test_biography_source_must_not_point_to_shared_methodology(self):
        self.config["profile_sources"] = [".agents/skills/job-application-assistant/SKILL.md"]
        self.write_config()
        result = self.run_doctor()
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["name"] == "mercado.profile_sources" and item["status"] == "error" for item in result["checks"]))

    def test_runtime_checks_dependency_interpreter_selected_in_local_config(self):
        selected = self.root / "python-from-local-config"
        selected.write_text("interpreter test fixture", encoding="utf-8")
        runtime = self.root / ".runtime/runtime.local.json"
        runtime.parent.mkdir()
        runtime.write_text(json.dumps({"python": str(selected.resolve())}), encoding="utf-8")
        with patch.object(doctor, "dependency_status", return_value=AVAILABLE) as probe:
            result = doctor.diagnose(self.root)
        self.assertTrue(result["ok"])
        probe.assert_called_once_with(str(selected.resolve()))
        self.assertEqual(result["python"], str(selected.resolve()))

    def test_dependency_probe_never_runs_codex_login_or_a_shell(self):
        selected = self.root / "different-python"
        completed = subprocess.CompletedProcess([], 0, json.dumps(AVAILABLE), "")
        with patch.object(doctor.subprocess, "run", return_value=completed) as execute:
            self.assertEqual(doctor.dependency_status(selected), AVAILABLE)
        args, kwargs = execute.call_args
        self.assertEqual(args[0][:2], [str(selected), "-c"])
        self.assertNotIn("shell", kwargs)
        self.assertNotIn("codex", args[0][2])
        self.assertNotIn("login", args[0][2])


if __name__ == "__main__":
    unittest.main()
