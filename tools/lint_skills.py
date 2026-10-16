#!/usr/bin/env python3
"""Validate native Agent Skills and workflow references, without runtime permissions.

Run from anywhere: python tools/lint_skills.py. Requires PyYAML.
Frontmatter capabilities describe skills; they never grant Codex permissions.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit("lint_skills.py requires PyYAML: python -m pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ".agents/skills/argentina-job-search/references/workflows"
SKILL_ALIASES = {"job-scraper": "scrape"}
FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
errors: list[str] = []


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_links(path: Path, text: str) -> None:
    """Markdown links resolve beside their source; root paths also work in skills."""
    for match in re.finditer(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
        target = match.group(1).strip().split(' "', 1)[0].strip("<>")
        if not target or target.startswith("#") or urlsplit(target).scheme:
            continue
        target = unquote(target.split("#", 1)[0])
        if not target or any(token in target for token in ("<", ">", "*", "{", "}")):
            continue
        if not any(candidate.exists() for candidate in (path.parent / target, ROOT / target)):
            errors.append(f"{rel(path)}: broken local link: {target}")


def check_skill(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{rel(path)}: missing YAML frontmatter (file must start with ---)")
        return None
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{rel(path)}: unterminated YAML frontmatter")
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: frontmatter did not parse to a mapping")
        return None
    unknown = set(data) - FRONTMATTER_KEYS
    if unknown:
        errors.append(f"{rel(path)}: unsupported native skill fields: {sorted(unknown)}; put custom fields inside metadata")
    for key in ("name", "description"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{rel(path)}: frontmatter missing required key '{key}'")
    name = data.get("name")
    expected = SKILL_ALIASES.get(path.parent.name, path.parent.name)
    if name and name not in {expected, path.parent.name}:
        errors.append(f"{rel(path)}: name must be '{expected}' (directory name or reviewed alias)")
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append(f"{rel(path)}: metadata must be a mapping")
    else:
        if "enabled" in metadata and not isinstance(metadata["enabled"], bool):
            errors.append(f"{rel(path)}: metadata.enabled must be a YAML boolean")
        if metadata.get("kind") == "workflow" and (path.parent / "cli").exists():
            errors.append(f"{rel(path)}: workflow skill cannot also be a portal CLI")
    allowed = data.get("allowed-tools", "")
    if isinstance(allowed, list):
        allowed = " ".join(str(item) for item in allowed)
    if not isinstance(allowed, str):
        errors.append(f"{rel(path)}: allowed-tools must be a string or list")
        allowed = ""
    for match in re.finditer(r"bun run ([^\s)]+)", allowed):
        target = match.group(1).rstrip("*")
        if not target or target.endswith("/"):
            continue
        if Path(target).is_absolute() or ".." in Path(target).parts:
            errors.append(f"{rel(path)}: CLI path must stay inside the repository: {target}")
            continue
        if "*" in target:
            if not any(p.is_file() for p in ROOT.glob(target)):
                errors.append(f"{rel(path)}: allowed-tools glob matches no files: {target}")
        elif not (ROOT / target).is_file():
            errors.append(f"{rel(path)}: allowed-tools references a missing file: {target}")
    check_links(path, text[end + 4:])
    return name if isinstance(name, str) else None


def check_workflow(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    first = next((line for line in text.splitlines() if line.strip()), "")
    if not first.startswith("# ") or not first[2:].strip():
        errors.append(f"{rel(path)}: workflow reference must start with a '# <title>' heading")
    if first.startswith("# /"):
        alias = first[3:].split()[0]
        if alias != path.stem:
            errors.append(f"{rel(path)}: workflow alias '{alias}' does not match filename")
    check_links(path, text)


def main() -> int:
    errors.clear()
    skills = sorted(ROOT.glob(".agents/skills/*/SKILL.md"))
    workflows = sorted((ROOT / WORKFLOWS).glob("*.md"))
    if not skills:
        errors.append("no SKILL.md files found under .agents/skills/ - native root is empty")
    if not workflows:
        errors.append(f"no workflow references found under {WORKFLOWS}/")
    names: set[str] = set()
    for skill in skills:
        name = check_skill(skill)
        if name and name in names:
            errors.append(f"{rel(skill)}: duplicate skill name: {name}")
        if name:
            names.add(name)
    for workflow in workflows:
        check_workflow(workflow)
    for legacy in (ROOT / ".claude", ROOT / "CLAUDE.md"):
        if legacy.exists():
            errors.append(f"{rel(legacy)}: legacy runtime path is unsupported; use native .agents/ and profile/")
    if errors:
        print(f"lint_skills: {len(errors)} failure(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"lint_skills: OK ({len(skills)} skills, {len(workflows)} workflow references)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
