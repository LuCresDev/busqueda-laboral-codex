#!/usr/bin/env python3
"""Ensure native methodology files carry valid, increasing framework versions.

Personal profiles are intentionally excluded: editing private biographical data
never requires changing a public framework release marker.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".agents/skills/job-application-assistant"
VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def run_git(args: list[str]) -> tuple[int, str, str]:
    res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    return res.returncode, res.stdout, res.stderr


def get_base_commit() -> str | None:
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if base_ref:
        for ref in (f"origin/{base_ref}", base_ref):
            if run_git(["rev-parse", "--verify", ref])[0] == 0:
                # A PR gate compares from the merge base, not unrelated changes
                # that happened only on the target branch after branching.
                rc, commit, _ = run_git(["merge-base", "HEAD", ref])
                return commit.strip() if rc == 0 else ref
    if os.environ.get("GITHUB_ACTIONS") and run_git(["rev-parse", "--verify", "HEAD~1"])[0] == 0:
        return "HEAD~1"
    if run_git(["rev-parse", "--verify", "HEAD"])[0] == 0:
        return "HEAD"
    return None


def frontmatter_from_text(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def parse_frontmatter(path: Path) -> dict[str, str]:
    return frontmatter_from_text(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_version(value: str | None) -> tuple[int, int, int] | None:
    match = VERSION.fullmatch(value or "")
    return tuple(map(int, match.groups())) if match else None


def base_text(path: Path, base_commit: str) -> str | None:
    local = path.relative_to(ROOT).as_posix()
    # Historical Git-only mapping allows reviewing the migration's actual base.
    # It does not restore a legacy runtime or write any personal profile.
    candidates = [local]
    if local.startswith(".agents/skills/job-application-assistant/"):
        candidates.append(local.replace(".agents/", ".claude/", 1))
    for candidate in candidates:
        rc, text, _ = run_git(["show", f"{base_commit}:{candidate}"])
        if rc == 0:
            return text.replace("\r\n", "\n")
    return None  # New framework files need a valid initial version, not a bump.


def meaningful_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines()
                     if line.strip() and line.strip() != "---"
                     and not re.match(r"^\s*framework_version\s*:", line))


def has_non_trivial_changes(file_path: Path, base_commit: str) -> bool:
    before = base_text(file_path, base_commit)
    if before is None:
        return False
    after = file_path.read_text(encoding="utf-8")
    if meaningful_text(before) == meaningful_text(after):
        return False
    old = parse_version(frontmatter_from_text(before).get("framework_version"))
    new = parse_version(frontmatter_from_text(after).get("framework_version"))
    return old is not None and (new is None or new <= old)


def main() -> int:
    errors = []
    files = sorted(SKILL_DIR.glob("*.md"))
    if not files:
        errors.append("no native methodology files found under .agents/skills/job-application-assistant/")
    if (ROOT / "AGENTS.md").exists():
        files.append(ROOT / "AGENTS.md")
    for path in files:
        marker = parse_frontmatter(path).get("framework_version")
        if marker is None:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: missing 'framework_version' in frontmatter")
        elif parse_version(marker) is None:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: invalid framework_version {marker!r}; expected X.Y.Z")
    base = get_base_commit()
    if base:
        print(f"Comparing working tree against base commit: {base}")
        for path in files:
            if has_non_trivial_changes(path, base):
                errors.append(f"{path.relative_to(ROOT).as_posix()}: modified without bumping 'framework_version'; the new version must increase")
    else:
        print("No base commit found; validating version markers without a diff comparison.")
    if errors:
        print("Framework Version Check Failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"Framework Version Check: OK ({len(files)} native files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
