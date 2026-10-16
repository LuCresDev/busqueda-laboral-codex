#!/usr/bin/env python3
"""Build a public source ZIP without profile data, credentials or Git history."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PRIVATE_DIRS = {'.git', '.runtime', '.venv', 'venv', 'work', 'reports',
                'node_modules', '__pycache__', 'gmail_sync', 'company_research', '.claude'}
PRIVATE_FILES = {'CLAUDE.md', 'job_search_tracker.csv', 'salary_data.json', 'skills-lock.json', 'PUBLIC-MANIFEST.json'}
SOURCE_SUFFIXES = {'.py', '.md', '.json', '.yml', '.yaml', '.toml', '.txt', '.ps1', '.cmd', '.sh', '.ts', '.tex', '.cls', '.ttf', '.otf', '.gif', '.png', '.jpg', '.svg', '.woff', '.woff2'}
BINARY_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.ttf', '.otf', '.woff', '.woff2'}


def canonical_content(relative: str, data: bytes) -> bytes:
    """Mirror .gitattributes checkout EOLs without changing binary payloads.

    UTF-8 text uses LF, except .cmd files use CRLF. Non-UTF-8 data and
    NUL-containing payloads are kept byte-for-byte, like declared binaries.
    """
    suffix = PurePosixPath(relative).suffix.lower()
    if suffix in BINARY_SUFFIXES or b'\0' in data:
        return data
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return data
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if suffix == '.cmd':
        text = text.replace('\n', '\r\n')
    return text.encode('utf-8')


def public_path(relative: str) -> bool:
    path = PurePosixPath(relative.replace('\\', '/'))
    parts = path.parts
    if path.is_absolute() or '..' in parts or not parts:
        return False
    folded = tuple(part.casefold() for part in parts)
    if folded[0] == 'profile' or any(part in {p.casefold() for p in PRIVATE_DIRS} for part in folded) or path.name.casefold() in {p.casefold() for p in PRIVATE_FILES}:
        return False
    if path.name.casefold() == '.env' or path.name.casefold().startswith('.env.') or path.suffix.lower() in {'.pdf', '.ogg', '.mp3', '.wav', '.log', '.lock', '.pyc'}:
        return False
    if parts[0] == 'documents' and relative != 'documents/README.md' and path.name != '.gitkeep':
        return False
    if parts[0] == 'job_scraper' and path.name != '.gitkeep':
        return False
    if parts[0] == 'upskill' and path.name not in {'.gitkeep', 'README.md'}:
        return False
    if parts[0] == 'cv' and relative != 'cv/main_example.tex' and path.name != '.gitkeep':
        return False
    if parts[0] == 'cover_letters' and (path.name.startswith(('cover_', 'Cover_')) and relative != 'cover_letters/cover_example.tex'):
        return False
    if path.name in {'.gitignore', '.gitattributes', '.gitkeep', 'LICENSE', 'NOTICE', 'Makefile'}:
        return True
    return path.suffix.lower() in SOURCE_SUFFIXES


def source_files(root: Path) -> list[str]:
    # The Git index may contain a personal file from an older version. public_path
    # is an independent allowlist and therefore also filters tracked/forced files.
    result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=root, capture_output=True, check=True)
    paths = sorted(set(result.stdout.decode('utf-8').split('\0')) - {''})
    files = []
    for relative in paths:
        if not public_path(relative):
            continue
        file = root / relative
        if file.is_symlink():
            raise ValueError(f'No se exportan enlaces simbólicos: {relative}')
        if file.is_file():
            if not file.resolve().is_relative_to(root.resolve()):
                raise ValueError(f'Archivo fuera del repositorio: {relative}')
            files.append(relative)
    return files


def export(root: Path, output: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if output.is_relative_to(root):
        raise ValueError('El ZIP público debe quedar fuera del repositorio privado')
    files = source_files(root)
    for required in ('LICENSE', 'AGENTS.md', 'README.md', 'tools/bootstrap.py', 'templates/profile/candidate.md'):
        if required not in files:
            raise ValueError(f'Falta un archivo público obligatorio: {required}')
    manifest = {'format': 1, 'profile_included': False, 'git_history_included': False,
                'hash_basis': 'archive-entry-bytes',
                'line_endings': {'utf8_text': 'LF', 'cmd': 'CRLF', 'binary': 'unchanged'},
                'files': {}}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as handle:
            temporary = Path(handle.name)
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for relative in files:
                # Read each source once: hash and ZIP must use the same snapshot,
                # even if the working file changes while the export is running.
                content = canonical_content(relative, (root / relative).read_bytes())
                manifest['files'][relative] = hashlib.sha256(content).hexdigest()
                archive.writestr(relative, content)
            archive.writestr('PUBLIC-MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None or any(not public_path(name) for name in archive.namelist() if name != 'PUBLIC-MANIFEST.json'):
                raise ValueError('La validación del ZIP público falló')
        os.replace(temporary, output)
        return manifest
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        manifest = export(args.root, args.output)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'Exportación cancelada: {exc}', file=sys.stderr)
        return 1
    print(f'ZIP público: {args.output.resolve()} ({len(manifest["files"])} archivos; sin perfil ni historial Git)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
