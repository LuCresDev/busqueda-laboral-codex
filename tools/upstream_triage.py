#!/usr/bin/env python3
"""Triage upstream commits this fork has not picked up yet.

Emits a Markdown report that sorts the behind-list into "worth reviewing" vs
"probably skip", so a human decides what to merge/port. It never merges,
pushes, or edits anything - it only reads git history and prints. This is the
deliberate report/act boundary: on a fork "applies cleanly" is not "correct" -
a commit for portals the fork dropped can cherry-pick fine and still be wrong,
and that silent-wrong case is worse than a conflict. So the report stops at
read-only git show lines; a human reviews them before porting changes into native paths.

This is the commit-level companion to check_upstream_updates.py. That tool
answers "which of my personalized framework files changed" (version stamps);
this one answers "which upstream commits deserve my attention" (commit history).
Two tools, two questions - each cross-references the other in its output.

Two signals drive the sort:

1. Already applied? A cherry-pick lands with a NEW sha but the same patch, so a
   raw sha comparison misreports it as missing. We compute git patch-ids for the
   fork-only commits and treat any upstream commit whose patch-id (or exact
   subject) matches as already applied.

2. Relevant to this fork? A commit that only touches files this fork deleted
   (e.g. removed demo portals) is almost certainly N/A. We check each commit's
   touched paths against the working tree and flag accordingly.

Usage: python tools/upstream_triage.py [--remote upstream] [--branch master]
Exits 0 always (a report, not a gate). Prints a note to stderr and exits 0 if
the upstream ref is unavailable, so a scheduled job degrades gracefully.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
    ).stdout


def rev_list(range_spec: str) -> list[str]:
    out = git("rev-list", "--no-merges", range_spec).strip()
    return out.splitlines() if out else []


def patch_id(sha: str) -> str | None:
    """Stable patch-id for a commit, or None if it has no diff."""
    show = subprocess.run(
        ["git", "show", sha], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
    ).stdout
    r = subprocess.run(
        ["git", "patch-id", "--stable"], cwd=ROOT, input=show, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    line = r.stdout.strip()
    return line.split()[0] if line else None


def subject(sha: str) -> str:
    return git("show", "-s", "--format=%s", sha).strip()


def files_touched(sha: str) -> list[str]:
    out = git("show", "--name-only", "--format=", sha).strip()
    return [f for f in out.splitlines() if f]


def native_path(path: str) -> str:
    """Historical upstream paths are review data, never runtime destinations."""
    profiles = {
        "CLAUDE.md": "templates/profile/candidate.md",
        ".claude/skills/job-application-assistant/01-candidate-profile.md": "templates/profile/candidate.md",
        ".claude/skills/job-application-assistant/02-behavioral-profile.md": "templates/profile/behavioral.md",
    }
    if path in profiles:
        return profiles[path]
    if path.startswith(".claude/commands/"):
        return path.replace(".claude/commands/", ".agents/skills/argentina-job-search/references/workflows/", 1)
    if path.startswith(".claude/skills/"):
        return path.replace(".claude/skills/", ".agents/skills/", 1)
    return path


def path_exists(path: str) -> bool:
    path = native_path(path)
    result = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{path}"], cwd=ROOT, capture_output=True
    )
    return result.returncode == 0 or (ROOT / path).is_file()


def remote_slug(remote: str) -> str | None:
    """owner/repo for a GitHub remote, or None if it can't be parsed."""
    try:
        url = git("remote", "get-url", remote).strip()
    except subprocess.CalledProcessError:
        return None
    for sep in ("github.com/", "github.com:"):
        if sep in url:
            path = url.split(sep, 1)[1]
            return path[:-4] if path.endswith(".git") else path
    return None


def load_wontport(path: str) -> list[str]:
    """SHA prefixes the fork has decided never to port; missing file -> []."""
    try:
        with open(ROOT / path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return []
    entries = []
    for line in raw.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            entries.append(line)
    return entries


def commit_cell(short: str, sha: str, slug: str | None) -> str:
    if slug:
        return f"[`{short}`](https://github.com/{slug}/commit/{sha})"
    return f"`{short}`"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", default="upstream")
    ap.add_argument("--branch", default="master")
    ap.add_argument("--wontport", default=".github/upstream-wontport.txt")
    args = ap.parse_args()
    ref = f"{args.remote}/{args.branch}"
    slug = remote_slug(args.remote)
    wontport = load_wontport(args.wontport)

    try:
        git("rev-parse", "--verify", ref)
    except subprocess.CalledProcessError:
        print(
            f"note: {ref} not available (add the remote and fetch it first); "
            "nothing to triage.",
            file=sys.stderr,
        )
        print(f"_Upstream ref `{ref}` was not available when this ran._")
        return 0

    behind = rev_list(f"HEAD..{ref}")
    if not behind:
        print(f"Up to date with `{ref}`. Nothing to review. :white_check_mark:")
        _print_crossref(ref)
        return 0

    fork_only = rev_list(f"{ref}..HEAD")
    fork_patch_ids = {p for p in (patch_id(s) for s in fork_only) if p}
    fork_subjects = {subject(s) for s in fork_only}

    review: list[tuple[str, str, str, list[str]]] = []
    skip: list[tuple[str, str, str, str]] = []

    for sha in behind:
        subj = subject(sha)
        short = sha[:9]
        if patch_id(sha) in fork_patch_ids or subj in fork_subjects:
            skip.append((short, sha, subj, "already applied (cherry-picked)"))
            continue
        if any(sha.startswith(e) for e in wontport):
            skip.append((short, sha, subj, "on the fork's won't-port list"))
            continue
        touched = files_touched(sha)
        present = [native_path(f) for f in touched if path_exists(f)]
        # A commit whose only surviving footprint is the changelog is one whose
        # real change lives in files this fork removed - the code doesn't apply,
        # only a doc line would. Low signal; demote it.
        substantive = [f for f in present if f != "CHANGELOG.md"]
        if touched and not present:
            skip.append((short, sha, subj, "touches only files not in this fork"))
        elif present and not substantive:
            skip.append((short, sha, subj, "changelog-only footprint in this fork"))
        else:
            review.append((short, sha, subj, substantive))

    lines: list[str] = []
    lines.append(f"Upstream `{ref}` has **{len(behind)}** commit(s) this fork lacks: "
                 f"**{len(review)}** worth reviewing, **{len(skip)}** probably skippable.")
    lines.append("")
    lines.append("_Review only. Nothing was merged. Port methodology into native paths; never overwrite profile/ or restore a legacy runtime._")
    lines.append("")

    lines.append("### Worth reviewing")
    if review:
        lines.append("")
        lines.append("| Commit | Subject | Fork files it touches |")
        lines.append("|---|---|---|")
        for short, sha, subj, present in review:
            shown = ", ".join(f"`{p}`" for p in present[:4]) or "_(new/shared paths)_"
            if len(present) > 4:
                shown += f" +{len(present) - 4} more"
            lines.append(f"| {commit_cell(short, sha, slug)} | {subj} | {shown} |")
        # Read-only patch inspection lines - still information, not action. The
        # report stops here on purpose; a human runs (and verifies) these.
        lines.append("")
        lines.append("<details><summary>Inspect historical patches before porting native changes</summary>")
        lines.append("")
        lines.append("```bash")
        for short, sha, subj, _ in review:
            lines.append(f"git show {sha}  # {subj}")
        lines.append("```")
        lines.append("")
        lines.append("</details>")
    else:
        lines.append("")
        lines.append("_None._")
    lines.append("")

    lines.append("### Probably skip")
    if skip:
        lines.append("")
        lines.append("| Commit | Subject | Why |")
        lines.append("|---|---|---|")
        for short, sha, subj, why in skip:
            lines.append(f"| {commit_cell(short, sha, slug)} | {subj} | {why} |")
    else:
        lines.append("")
        lines.append("_None._")

    print("\n".join(lines))
    _print_crossref(ref)
    return 0


def _print_crossref(ref: str) -> None:
    print()
    print(
        "_For personalized-file version stamps (which methodology files changed), "
        f"run `python tools/check_upstream_updates.py --remote {ref.split('/')[0]}`._"
    )


if __name__ == "__main__":
    sys.exit(main())
