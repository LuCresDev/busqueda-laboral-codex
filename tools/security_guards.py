#!/usr/bin/env python3
"""Native Codex repository guards: private data, retired runtimes and package installs.

This repository does not ship runtime permissions. Skills are instructions, and
Codex approvals belong to the user's Codex configuration. Legacy .claude/ or
CLAUDE.md runtime files are rejected instead of validating fictitious permissions.
Historical upstream path mappings in Python are data and remain allowed.

Run from anywhere: python tools/security_guards.py (stdlib only).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

REQUIRED_IGNORE_RULES = [
    "salary_data.json",
    # Depth-independent: the job-scraper skill resolves `job_scraper/` relative
    # to its own directory, so the state file lands under .agents/skills/... and
    # a repo-rooted rule silently fails to match it.
    "**/job_scraper/seen_jobs.json",
    "**/job_scraper/notion_sync.json",
    "**/job_scraper/*.md",
    "*_BehavioralReport.pdf",
    "linkedin_Profile.pdf",
    "cv/main_*.*",
    "!cv/main_example.tex",
    # ATS text extractions (/apply step 5d) carry the CV's full text.
    "cv/*.txt",
    "cover_letters/cover_*.*",
    # /apply also recognizes the uppercase Cover_* naming variant.
    "cover_letters/Cover_*.*",
    "documents/cv/**",
    "documents/linkedin/**",
    "documents/diplomas/**",
    "documents/references/**",
    "documents/projects/**",
    "documents/applications/**",
    "documents/postings/**",
    # Belt-and-braces, not the primary guard: nothing writes here.
    # /interview's prep packs land under documents/applications/**, above.
    "documents/interview/**",
    "job_search_tracker.csv",
    "gmail_sync/",
    "reports/",
    "upskill/*.md",
    # Depth-independent twin of the rule above. The upskill *skill* resolves
    # `upskill/` relative to its own directory - the same observed behavior
    # the **/job_scraper rules exist for - so reports can land at
    # .agents/skills/upskill/upskill/*.md where the rooted rule cannot see
    # them. `**/upskill/*.md` would also ignore the skill's own SKILL.md
    # (the directory shares the name), so the report-file prefix is pinned.
    "**/upskill/report-*.md",
    # Not personal data but the same failure mode: /add-portal can generate a
    # skill for a portal that only returns usable content through a paid
    # fetching service, and that skill reads an API token from the environment.
    ".env",
    ".env.*",
    # Company research cache (/apply Step 3, /interview Step 2). Referenced
    # from commands, not a skill, so a plain rooted rule is correct here -
    # unlike the **/-prefixed job_scraper/upskill rules above.
    "company_research/*.json",
    # Canonical personal profiles and machine-local runtimes/backups/secrets.
    "profile/**",
    ".runtime/",
]


ALLOWED_IGNORE_NEGATIONS = {
    "!cover_letters/OpenFonts/fonts/**",
    "!cv/main_example.tex",
    "!cover_letters/cover_example.tex",
    "!documents/**/.gitkeep",
}


FORBIDDEN_SCRIPTS = {"preinstall", "install", "postinstall", "prepare", "prepack"}


def check_native_runtime() -> None:
    for target in (".claude", "CLAUDE.md", ".agents/settings.json"):
        if (ROOT / target).exists():
            errors.append(
                f"{target}: legacy runtime or unsupported permission file. "
                "Use .agents/skills, AGENTS.md and profile/; this repository does not grant Codex permissions."
            )


def check_gitignore() -> None:
    try:
        lines = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()]
    except OSError as exc:
        errors.append(f".gitignore: unreadable: {exc}")
        return
    for rule in REQUIRED_IGNORE_RULES:
        if rule not in lines:
            errors.append(f".gitignore: required personal-data rule missing: {rule!r}")
    for line in lines:
        if line.startswith("!") and line not in ALLOWED_IGNORE_NEGATIONS:
            errors.append(f".gitignore: negation rule not in the reviewed allowlist: {line!r}")


def check_tracked_private_data() -> None:
    """An ignore rule cannot protect a file that is already in the Git index."""
    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        # Extracted public bundles need not be Git checkouts. Never inspect an
        # ancestor checkout when the guard is tested from a temporary directory.
        if probe.returncode or Path(probe.stdout.strip()).resolve() != ROOT.resolve():
            return
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", "profile", ".runtime", ".env", ".env.*",
             "job_search_tracker.csv", "salary_data.json", "gmail_sync", "reports",
             "documents/cv", "documents/linkedin", "documents/diplomas", "documents/references",
             "documents/projects", "documents/applications", "documents/postings", "documents/interview"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError as exc:
        errors.append(f"private-data index check could not run Git: {exc}")
        return
    if tracked.returncode:
        errors.append(f"private-data index check failed: {tracked.stderr.strip()}")
        return
    for path in tracked.stdout.split("\0"):
        if path and not (path.startswith("documents/") and path.endswith("/.gitkeep")):
            errors.append(f"{path}: private data is tracked by Git; .gitignore does not protect tracked files")


def check_package_manifests() -> None:
    manifests = [
        p for p in ROOT.glob(".agents/**/package.json") if "node_modules" not in p.parts
    ]
    if not manifests:
        errors.append(".agents: no package.json files found - glob roots are wrong or the tree moved")
    for manifest in manifests:
        relpath = manifest.relative_to(ROOT)
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relpath}: unreadable or invalid JSON: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{relpath}: top-level JSON value must be an object")
            continue
        scripts = data.get("scripts", {})
        if not isinstance(scripts, dict):
            errors.append(f"{relpath}: scripts must be an object")
            continue
        bad = FORBIDDEN_SCRIPTS & set(scripts)
        if bad:
            errors.append(
                f"{relpath}: lifecycle script(s) {sorted(bad)} are forbidden - they execute "
                "arbitrary code during `bun install` on every fork user's machine."
            )
        if "trustedDependencies" in data:
            errors.append(
                f"{relpath}: trustedDependencies is forbidden - it re-enables dependency "
                "lifecycle scripts that bun blocks by default."
            )



def main() -> int:
    errors.clear()
    check_native_runtime()
    check_gitignore()
    check_tracked_private_data()
    check_package_manifests()
    if errors:
        print(f"security_guards: {len(errors)} failure(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("security_guards: OK (native runtime, private data, gitignore rules, package manifests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
