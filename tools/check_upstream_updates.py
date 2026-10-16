#!/usr/bin/env python3
"""Report native framework differences against historical upstream paths.

Only Git fetch (unless --no-fetch) changes remote-tracking refs. This tool never
merges, overwrites files or reads personal profile/. Upstream versions are
review signals, not instructions to replace the customized Codex framework.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_REPO_SLUG = "MadsLorentzen/ai-job-search"
# Local -> historical upstream path. Legacy strings below are Git object paths,
# never runtime discovery roots. Personal profile/ is deliberately absent.
UPSTREAM_PATH_MAP = {
    "templates/profile/candidate.md": ".claude/skills/job-application-assistant/01-candidate-profile.md",
    "templates/profile/behavioral.md": ".claude/skills/job-application-assistant/02-behavioral-profile.md",
    **{f".agents/skills/job-application-assistant/{name}": f".claude/skills/job-application-assistant/{name}"
       for name in ("03-writing-style.md", "04-job-evaluation.md", "05-cv-templates.md",
                    "06-cover-letter-templates.md", "07-interview-prep.md",
                    "08-application-forms.md", "09-web-research.md", "SKILL.md")},
    "AGENTS.md": "AGENTS.md",
}
FRAMEWORK_FILES = list(UPSTREAM_PATH_MAP)


def run_git(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    return result.returncode, result.stdout, result.stderr


def get_remote_url(remote_name: str) -> str:
    code, text, _ = run_git(["remote", "get-url", remote_name])
    return text.strip() if code == 0 else ""


def is_template_remote(url: str) -> bool:
    """Accept the exact GitHub repository, not lookalike or fork URLs."""
    normalized = url.strip().lower()
    if normalized.startswith("git@github.com:"):
        path = normalized.split(":", 1)[1]
    else:
        parsed = urlsplit(normalized)
        if parsed.hostname != "github.com" or parsed.scheme not in {"https", "ssh"}:
            return False
        path = parsed.path.lstrip("/")
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return path == UPSTREAM_REPO_SLUG.lower()


def get_framework_version_from_text(text: str) -> str | None:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "framework_version":
            return value.strip().strip('"').strip("'")
    return None


def parse_semver(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        raise ValueError(f"invalid framework_version {value!r}; expected X.Y.Z")
    return tuple(map(int, match.groups()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", default="upstream")
    parser.add_argument("--branch", default="master")
    parser.add_argument("--no-fetch", action="store_true")
    args = parser.parse_args()
    _, text, _ = run_git(["remote"])
    remote = args.remote
    if remote not in text.splitlines():
        if "origin" not in text.splitlines():
            print("Error: No usable Git remote found.")
            return 1
        print(f"Warning: Remote '{remote}' not found. Falling back to 'origin'.")
        remote = "origin"
    errors = []
    if not is_template_remote(get_remote_url(remote)):
        errors.append(f"Remote '{remote}' does not point to the ai-job-search template repo ({UPSTREAM_REPO_SLUG}); cannot establish upstream freshness.")
    if not args.no_fetch:
        code, _, message = run_git(["fetch", remote])
        if code:
            errors.append(f"Failed to fetch '{remote}'; cached comparison only: {message.strip()}")
    ref = f"{remote}/{args.branch}"
    if run_git(["rev-parse", "--verify", ref])[0]:
        print(f"Error: Ref '{ref}' does not exist. Fetch the remote and check --branch.")
        return 1
    print(f"Review-only comparison against {ref}; personal profile/ is never read or overwritten.\n")
    updates = []
    missing_upstream = []
    for local, upstream in UPSTREAM_PATH_MAP.items():
        path = ROOT / local
        if not path.is_file():
            errors.append(f"Local framework file missing: {local}. Run bootstrap for personal profiles only; public framework templates must be restored from this fork.")
            continue
        local_text = path.read_text(encoding="utf-8")
        code, upstream_text, message = run_git(["show", f"{ref}:{upstream}"])
        if code:
            if "does not exist" in message or "exists on disk, but not in" in message:
                missing_upstream.append(f"{local} -> {upstream}")
            else:
                errors.append(f"Cannot read {ref}:{upstream}: {message.strip()}")
            continue
        local_ver = get_framework_version_from_text(local_text)
        upstream_ver = get_framework_version_from_text(upstream_text)
        if not local_ver:
            if local.startswith("templates/profile/"):
                if local_text.replace("\r\n", "\n") != upstream_text.replace("\r\n", "\n"):
                    updates.append((local, upstream, "generic profile template differs; review content manually"))
                continue
            errors.append(f"Local file {local} is missing 'framework_version' in frontmatter.")
            continue
        if not upstream_ver:
            errors.append(f"Upstream file {upstream} is missing 'framework_version'; comparison incomplete.")
            continue
        try:
            if parse_semver(upstream_ver) > parse_semver(local_ver):
                updates.append((local, upstream, f"local {local_ver} < upstream {upstream_ver}"))
        except ValueError as exc:
            errors.append(f"{local}: {exc}")
    for local, upstream, reason in updates:
        print(f"[REVIEW] {local}: {reason}")
        print(f"  Historical source: git show {ref}:{upstream}")
    if missing_upstream:
        print("Files missing from the upstream ref (possibly renamed/deleted):")
        for path in missing_upstream:
            print(f"  - {path}")
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    if errors or missing_upstream:
        print(f"[WARNING] Framework check incomplete against {ref}; do not assume it is up to date.")
    elif not updates:
        print(f"[OK] All mapped framework versions are up to date with {ref}.")
    else:
        print("Review and port relevant methodology manually; never overwrite profile/ from upstream.")
    print(f"\nCommit triage: python tools/upstream_triage.py --remote {remote}")
    return 1 if errors or missing_upstream else 0


if __name__ == "__main__":
    sys.exit(main())
