#!/usr/bin/env python3
"""Initialize private profile/runtime files without replacing existing data.

Pure standard library; no package installation, network, model call or login.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILES = ("candidate.md", "behavioral.md", "writing-style.md", "evaluation.md", "interview.md")


class BootstrapError(ValueError):
    """A required public template or a safe destination is unavailable."""


def _private_target(root, relative):
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise BootstrapError(f"La ruta privada sale del proyecto: {relative}")
    return target


def _create_once(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Exclusive creation also protects against a concurrent initialization.
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except FileExistsError:
        return False
    return True


def detect_runtime(root=ROOT):
    """Discover paths on this machine; never persist somebody else's user path."""
    def executable(name):
        found = shutil.which(name)
        return str(Path(found).resolve()) if found else None
    result = {
        "schema_version": 1,
        "python": str(Path(sys.executable).resolve()),
        "bun": executable("bun"),
        "node": executable("node"),
        "codex": executable("codex"),
    }
    local_bun = Path(root) / ".runtime/bun/bun-windows-x64/bun.exe"
    if result["bun"] is None and local_bun.is_file():
        result["bun"] = str(local_bun.resolve())
    return result


def bootstrap(root=ROOT, *, profile_only=False, runtime_only=False):
    if profile_only and runtime_only:
        raise BootstrapError("Elegí solo --profile-only o --runtime-only.")
    root = Path(root).resolve()
    if not (root / "AGENTS.md").is_file():
        raise BootstrapError("No se encontró AGENTS.md; indicá la raíz del proyecto con --root.")
    result = {"created": [], "preserved": [], "missing_optional": []}
    if not runtime_only:
        templates = {name: root / "templates/profile" / name for name in PROFILE_FILES}
        for name, source in templates.items():
            if not source.is_file():
                raise BootstrapError(f"Falta el esqueleto público templates/profile/{name}.")
        for name, source in templates.items():
            relative = f"profile/{name}"
            target = _private_target(root, relative)
            created = _create_once(target, source.read_text(encoding="utf-8"))
            result["created" if created else "preserved"].append(relative)
    if not profile_only:
        relative = ".runtime/runtime.local.json"
        target = _private_target(root, relative)
        runtime = detect_runtime(root)
        created = _create_once(target, json.dumps(runtime, ensure_ascii=False, indent=2) + "\n")
        result["created" if created else "preserved"].append(relative)
        if created:
            result["missing_optional"] = [name for name in ("bun", "node", "codex") if not runtime[name]]
    return result


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Raíz del proyecto; por defecto la del script")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--profile-only", action="store_true", help="Crear solo los archivos privados de perfil que falten")
    mode.add_argument("--runtime-only", action="store_true", help="Crear solo runtime.local.json si falta")
    parser.add_argument("--json", action="store_true", help="Resultado estructurado, sin imprimir datos personales")
    args = parser.parse_args(argv)
    try:
        result = bootstrap(args.root, profile_only=args.profile_only, runtime_only=args.runtime_only)
    except (OSError, BootstrapError, UnicodeError) as exc:
        print(f"Error de inicialización: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for path in result["created"]:
            print(f"Creado: {path}")
        for path in result["preserved"]:
            print(f"Conservado sin cambios: {path}")
        if result["missing_optional"]:
            print("Herramientas opcionales no encontradas: " + ", ".join(result["missing_optional"]) + ".")
        print("No se instalaron paquetes ni se iniciaron sesiones. Ejecutá python tools/doctor.py para revisar el entorno.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
