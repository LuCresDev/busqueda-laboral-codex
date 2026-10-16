import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARD_SCRIPT = REPO_ROOT / "tools" / "security_guards.py"

sys.path.insert(0, str(REPO_ROOT / "tools"))
import security_guards  # noqa: E402  (imported for its allowlist constants)


def run_guards(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "tools" / "security_guards.py")],
        capture_output=True,
        text=True,
    )


class GuardRepoFixture(unittest.TestCase):
    """Run the real guard in a temporary native repository tree."""
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "tools").mkdir()
        shutil.copy(GUARD_SCRIPT, self.root / "tools/security_guards.py")
        self.gitignore = self.root / ".gitignore"
        self.write_gitignore(security_guards.REQUIRED_IGNORE_RULES)
        self.manifest = self.root / ".agents/skills/example-search/cli/package.json"
        self.manifest.parent.mkdir(parents=True)
        self.write_manifest({"name": "example-cli", "scripts": {"start": "bun run src/cli.ts"}})

    def write_gitignore(self, rules):
        self.gitignore.write_text("\n".join(rules) + "\n", encoding="utf-8")

    def write_manifest(self, data, path=None):
        (path or self.manifest).write_text(json.dumps(data), encoding="utf-8")


class NativeRuntimeGuardTests(GuardRepoFixture):
    def test_clean_native_tree_passes_without_permission_settings(self):
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("security_guards: OK", result.stdout)

    def test_legacy_runtime_is_rejected_regardless_of_its_permissions(self):
        for target in (".claude/settings.json", "CLAUDE.md", ".agents/settings.json"):
            with self.subTest(target=target):
                path = self.root / target
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}", encoding="utf-8")
                result = run_guards(self.root)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("legacy runtime or unsupported permission file", result.stdout)
                path.unlink()
                if target.startswith(".claude/"):
                    path.parent.rmdir()

    def test_historical_upstream_path_strings_are_allowed_as_data(self):
        (self.root / "tools/upstream_map.py").write_text(
            'HISTORICAL_PATH = ".claude/skills/example/SKILL.md"\n', encoding="utf-8"
        )
        self.assertEqual(run_guards(self.root).returncode, 0)

    def test_private_profile_and_runtime_cannot_be_force_tracked(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        for target in ("profile/candidate.md", ".runtime/runtime.local.json", ".env.local"):
            with self.subTest(target=target):
                path = self.root / target
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private fixture", encoding="utf-8")
                subprocess.run(["git", "-C", str(self.root), "add", "-f", "--", target], check=True, capture_output=True)
                result = run_guards(self.root)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("private data is tracked by Git", result.stdout)
                self.assertIn(target, result.stdout)
                subprocess.run(["git", "-C", str(self.root), "rm", "--cached", "--", target], check=True, capture_output=True)


class GitignoreGuardTests(GuardRepoFixture):
    def test_each_missing_personal_data_rule_fails(self):
        for rule in security_guards.REQUIRED_IGNORE_RULES:
            with self.subTest(rule=rule):
                remaining = [r for r in security_guards.REQUIRED_IGNORE_RULES if r != rule]
                self.write_gitignore(remaining)
                result = run_guards(self.root)
                self.assertEqual(result.returncode, 1)
                self.assertIn("required personal-data rule missing", result.stdout)
                self.assertIn(rule, result.stdout)
        self.write_gitignore(security_guards.REQUIRED_IGNORE_RULES)

    def test_extra_rules_are_allowed(self):
        self.write_gitignore(list(security_guards.REQUIRED_IGNORE_RULES) + ["*.bak", "scratch/"])
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_report_rules_are_required(self):
        # Reports are generated from the user's tracker and application archive,
        # so losing these ignore rules can expose personal job-search history.
        sensitive_outputs = ["reports/", "upskill/*.md", "**/upskill/report-*.md"]
        remaining = [
            rule
            for rule in security_guards.REQUIRED_IGNORE_RULES
            if rule not in sensitive_outputs
        ]
        self.write_gitignore(remaining)

        result = run_guards(self.root)

        self.assertEqual(result.returncode, 1)
        self.assertIn("reports/", result.stdout)
        self.assertIn("upskill/*.md", result.stdout)
        self.assertIn("**/upskill/report-*.md", result.stdout)


class GitignorePatternBehaviorTests(unittest.TestCase):
    """Pin the match semantics of the shipped .gitignore, not just rule presence.

    The guard checks that a rule exists; it never checks what the rule matches.
    These cases run real `git check-ignore` over the shipped file, for paths the
    framework actually writes.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        subprocess.run(
            ["git", "init", "-q", str(self.root)], check=True, capture_output=True
        )
        shutil.copy(REPO_ROOT / ".gitignore", self.root / ".gitignore")

    def test_upskill_reports_ignored_at_depth_but_skill_md_stays_tracked(self):
        # The upskill skill resolves `upskill/` relative to its own directory
        # (the same observed behavior the **/job_scraper rules exist for), so a
        # report must be ignored at that depth too. The skill's own SKILL.md
        # lives in a directory that shares the `upskill` name, so a broad
        # `**/upskill/*.md` would ignore the template's own skill file - this
        # pins that it stays tracked.
        cases = {
            "upskill/report-2026-08-11.md": True,
            ".agents/skills/upskill/upskill/report-2026-08-11.md": True,
            ".agents/skills/upskill/upskill/report-2026-08-11-acme-engineer.md": True,
            ".agents/skills/upskill/SKILL.md": False,
        }
        for path, expect_ignored in cases.items():
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "-C", str(self.root), "check-ignore", "-q", path],
                    capture_output=True,
                )
                self.assertEqual(
                    result.returncode == 0,
                    expect_ignored,
                    f"{path}: expected ignored={expect_ignored}",
                )

    def test_native_profiles_backups_and_secrets_are_ignored_but_templates_ship(self):
        for path, ignored in {
            "profile/candidate.md": True,
            "profile/interview.md": True,
            ".runtime/backups/old/CLAUDE.md": True,
            ".runtime/runtime.local.json": True,
            ".env.local": True,
            "templates/profile/candidate.md": False,
            ".agents/skills/argentina-job-search/SKILL.md": False,
        }.items():
            with self.subTest(path=path):
                result = subprocess.run(["git", "-C", str(self.root), "check-ignore", "-q", path], capture_output=True)
                self.assertEqual(result.returncode == 0, ignored, path)

    def test_interview_prep_pack_is_ignored_at_the_path_the_command_writes(self):
        # Derived, never copied: a hardcoded prep-pack path pins only that
        # documents/applications/** still matches that shape - which the
        # presence guard already catches - and stays green if /interview moves
        # its output, leaving .gitignore's comment stale exactly the way #336
        # found it. Reading the path back from the command spec is what makes
        # the move fail here instead.
        # Two fragments, not one literal: #329 split the path across Step 1
        # (which derives the archive folder) and Step 3 (which names the file),
        # so either half can move independently and each must be pinned.
        folder = "documents/applications/<company>_<role>/"
        filename = "interview_prep_<stage>.md"
        spec = (REPO_ROOT / ".agents" / "skills" / "argentina-job-search" / "references" / "workflows" / "interview.md").read_text(encoding="utf-8")
        for fragment in (folder, filename):
            # assertTrue, not assertIn: the haystack is the whole command spec,
            # and dumping it buries the one sentence explaining the failure.
            self.assertTrue(
                fragment in spec,
                f"/interview no longer writes {fragment}; .gitignore's comment is now stale",
            )

        path = folder.replace("<company>_<role>", "acme_data_scientist") + filename.replace(
            "<stage>", "technical"
        )
        result = subprocess.run(
            ["git", "-C", str(self.root), "check-ignore", "-v", path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"{path}: not ignored by the shipped .gitignore")
        self.assertIn("documents/applications/**", result.stdout)


class GitignoreNegationTests(GuardRepoFixture):
    def test_negation_reincluding_personal_data_fails(self):
        # .gitignore is order-sensitive: `!salary_data.json` after the
        # `salary_data.json` rule re-includes the file, so the required rule is
        # still present but no longer takes effect. Set membership on the
        # required rules cannot see this, so the negation must be rejected.
        self.write_gitignore(list(security_guards.REQUIRED_IGNORE_RULES) + ["!salary_data.json"])
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("negation rule not in the reviewed allowlist", result.stdout)
        self.assertIn("!salary_data.json", result.stdout)

    def test_allowlisted_negations_pass(self):
        # The template's own benign negations (example CV/cover letter, fonts,
        # .gitkeep placeholders) must keep passing.
        self.write_gitignore(
            list(security_guards.REQUIRED_IGNORE_RULES)
            + sorted(security_guards.ALLOWED_IGNORE_NEGATIONS)
        )
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ManifestGuardTests(GuardRepoFixture):
    def test_each_lifecycle_script_fails(self):
        for script in sorted(security_guards.FORBIDDEN_SCRIPTS):
            with self.subTest(script=script):
                # The guard flags the script KEY; the value is never inspected,
                # so it must stay benign: attack-shaped values (curl-pipe-to-sh
                # etc.) written to disk trip AV heuristics - Windows Defender
                # quarantines the fixture mid-test and the suite goes flaky.
                self.write_manifest(
                    {"name": "example-cli", "scripts": {script: "echo test"}}
                )
                result = run_guards(self.root)
                self.assertEqual(result.returncode, 1)
                self.assertIn("lifecycle script", result.stdout)
                self.assertIn(script, result.stdout)
        self.write_manifest({"name": "example-cli", "scripts": {}})

    def test_trusted_dependencies_fails(self):
        self.write_manifest({"name": "example-cli", "trustedDependencies": ["left-pad"]})
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("trustedDependencies", result.stdout)

    def test_malformed_manifest_shape_fails_cleanly(self):
        for data, message in [
            ([], "top-level JSON value must be an object"),
            ({"name": "example-cli", "scripts": []}, "scripts must be an object"),
        ]:
            with self.subTest(data=data):
                self.write_manifest(data)
                result = run_guards(self.root)
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_benign_scripts_pass(self):
        self.write_manifest(
            {"name": "example-cli", "scripts": {"start": "bun run src/cli.ts", "test": "bun test", "typecheck": "tsc --noEmit"}}
        )
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_node_modules_manifests_are_ignored(self):
        # Installed dependencies are not repo-tracked code; a hostile manifest
        # inside node_modules must not fail the guard (and bun blocks its
        # lifecycle scripts anyway).
        nm = self.manifest.parent / "node_modules" / "some-dep" / "package.json"
        nm.parent.mkdir(parents=True)
        self.write_manifest({"name": "some-dep", "scripts": {"postinstall": "echo test"}}, path=nm)
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_manifests_at_all_fails(self):
        self.manifest.unlink()
        result = run_guards(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no package.json files found", result.stdout)


class RealRepoTests(unittest.TestCase):
    def test_guards_pass_on_this_repo(self):
        # The live check CI runs: the actual repo tree must satisfy its own guards.
        result = run_guards(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
