#!/usr/bin/env python3
"""Check the local Argentina workspace without network requests or CLI logins."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = {"reportlab": "reportlab", "pypdf": "pypdf", "yaml": "PyYAML"}
PROFILE_OPTIONAL = ("behavioral.md", "writing-style.md", "evaluation.md", "interview.md")


def dependency_status(python, package_directory=None):
    """Probe the selected interpreter, not an unrelated Python from the PATH."""
    if Path(python).resolve() == Path(sys.executable).resolve():
        result = {}
        original_path = list(sys.path)
        try:
            if package_directory:
                sys.path.insert(0, str(package_directory))
            for module, package in DEPENDENCIES.items():
                try:
                    imported = importlib.import_module(module)
                    result[package] = {
                        "available": True,
                        "version": str(getattr(imported, "__version__", getattr(imported, "Version", "instalado"))),
                    }
                except Exception as exc:
                    result[package] = {"available": False, "error": type(exc).__name__}
        finally:
            sys.path[:] = original_path
        return result
    # This is fixed local Python code, never code supplied by profile/config data.
    code = (
        "import importlib,json,sys\n"
        + (f"sys.path.insert(0,{str(package_directory)!r})\n" if package_directory else "")
        +
        f"dependencies={DEPENDENCIES!r}\n"
        "result={}\n"
        "for module,package in dependencies.items():\n"
        " try:\n"
        "  imported=importlib.import_module(module)\n"
        "  result[package]={'available':True,'version':str(getattr(imported,'__version__',getattr(imported,'Version','instalado')))}\n"
        " except Exception as exc:\n"
        "  result[package]={'available':False,'error':type(exc).__name__}\n"
        "print(json.dumps(result))\n"
    )
    completed = subprocess.run(
        [str(python), "-c", code], capture_output=True, text=True,
        encoding="utf-8", timeout=20, check=True,
    )
    return json.loads(completed.stdout)


def diagnose(root=ROOT):
    root = Path(root).resolve()
    checks = []

    def record(name, status, detail):
        checks.append({"name": name, "status": status, "detail": detail})

    def safe_path(relative):
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError("se requiere una ruta relativa dentro del proyecto")
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("la ruta sale del proyecto")
        return path

    def file_check(relative, *, required=True):
        try:
            present = safe_path(relative).is_file()
        except ValueError as exc:
            record(str(relative), "error", str(exc))
            return False
        if present:
            detail = "Presente"
        elif relative.startswith("profile/"):
            detail = "Falta; ejecutá python tools/bootstrap.py"
        else:
            detail = "Archivo faltante"
        record(relative, "ok" if present else "error" if required else "warning", detail)
        return present

    def json_file(relative):
        if not file_check(relative):
            return None
        try:
            value = json.loads(safe_path(relative).read_text(encoding="utf-8-sig"))
            if not isinstance(value, dict):
                raise ValueError("se esperaba un objeto JSON")
        except (OSError, UnicodeError, ValueError) as exc:
            record(relative + ":json", "error", f"JSON inválido: {exc}")
            return None
        record(relative + ":json", "ok", "JSON válido")
        return value

    for relative in (
        "AGENTS.md", ".agents/skills/argentina-job-search/SKILL.md",
        "tools/render_application.py", "templates/profile/candidate.md",
        ".agents/skills/job-application-assistant/05-cv-templates.md",
        ".agents/skills/job-application-assistant/06-cover-letter-templates.md",
    ):
        file_check(relative)
    config = json_file("config/argentina.json")
    if config is not None:
        expected = {"schema_version": 1, "locale": "es-AR", "country_code": "AR"}
        for key, value in expected.items():
            record(f"mercado.{key}", "ok" if config.get(key) == value else "error", f"Valor esperado: {value}")
        sources = config.get("profile_sources")
        allowed_sources = {"profile/candidate.md", *(f"profile/{name}" for name in PROFILE_OPTIONAL)}
        if (
            not isinstance(sources, list)
            or "profile/candidate.md" not in sources
            or not all(isinstance(item, str) and item in allowed_sources for item in sources)
            or len(set(sources)) != len(sources)
        ):
            record("mercado.profile_sources", "error", "Se requiere profile/candidate.md; solo se admiten sus cuatro complementos privados")
        else:
            record("mercado.profile_sources", "ok", "Una fuente privada de biografía")
        market = config.get("market")
        if not isinstance(market, dict) or not isinstance(market.get("portals_config"), str):
            record("mercado.portales", "error", "Falta market.portals_config")
        else:
            portals = json_file(market["portals_config"])
            if portals is not None:
                portal_list = portals.get("primary_portals")
                if not isinstance(portal_list, list):
                    record("mercado.portales", "error", "La configuración debe incluir una lista primary_portals")
                else:
                    record("mercado.portales", "ok", f"Catálogo válido: {len(portal_list)} fuentes guiadas")
        templates = config.get("templates")
        if not isinstance(templates, dict):
            record("plantillas", "error", "Falta el objeto templates")
        else:
            for kind in ("cv", "cover_letter"):
                relative = templates.get(kind)
                try:
                    source = safe_path(relative)
                    if not source.is_file():
                        raise ValueError("archivo faltante")
                    template = json.loads(source.read_text(encoding="utf-8-sig"))
                    if not isinstance(template, dict) or not isinstance(template.get("person"), dict):
                        raise ValueError("se esperaba una plantilla JSON con person")
                    if not (source.parent / "TEMPLATE.md").is_file():
                        raise ValueError("falta TEMPLATE.md")
                    record(f"plantilla.{kind}", "ok", relative)
                except (OSError, UnicodeError, ValueError, TypeError) as exc:
                    record(f"plantilla.{kind}", "error", str(exc))
        pdf = config.get("pdf")
        if not isinstance(pdf, dict):
            record("pdf", "error", "Falta el objeto pdf")
        else:
            for key, expected_value in (("cv_page_range", [1, 2]), ("cover_letter_pages", 1)):
                record(f"pdf.{key}", "ok" if pdf.get(key) == expected_value else "error", f"Valor esperado: {expected_value}")
            if isinstance(pdf.get("renderer"), str):
                file_check(pdf["renderer"])
            else:
                record("pdf.renderer", "error", "Falta la ruta del renderizador")
    if file_check("profile/candidate.md"):
        try:
            candidate = safe_path("profile/candidate.md").read_text(encoding="utf-8")
            if not candidate.strip():
                record("perfil.estado", "error", "El perfil está vacío; restaurá su estructura desde templates/profile sin perder datos")
            else:
                state = re.search(r"^## Estado\s*\n(.*?)(?=^## |\Z)", candidate, re.MULTILINE | re.DOTALL)
                if not state:
                    record("perfil.estado", "warning", "No hay sección Estado reconocible; revisá la incorporación con el usuario")
                elif re.search(r"pendiente|incomplet|sin confirmar", state.group(1), re.IGNORECASE) or "[YOUR_" in candidate:
                    record("perfil.estado", "warning", "Perfil incompleto; permite búsqueda amplia, no un CV factual ni ranking personal definitivo")
                else:
                    record("perfil.estado", "ok", "Perfil presente; requiere revisión humana de sus hechos")
        except (OSError, UnicodeError) as exc:
            record("perfil.estado", "error", f"No se pudo leer el perfil: {exc}")
    for name in PROFILE_OPTIONAL:
        file_check(f"profile/{name}", required=False)
    runtime_path = root / ".runtime/runtime.local.json"
    runtime = None
    python = sys.executable
    if runtime_path.is_file():
        runtime = json_file(".runtime/runtime.local.json")
        if runtime is not None:
            selected = runtime.get("python")
            if not isinstance(selected, str) or not Path(selected).is_absolute() or not Path(selected).is_file():
                record("runtime.python", "error", "La ruta Python configurada no es un archivo absoluto existente; revisá .runtime/runtime.local.json")
            else:
                python = selected
                record("runtime.python", "ok", f"Intérprete comprobado: {selected}")
    else:
        record("runtime", "warning", "Sin configuración local; se comprueba el Python actual. Inicializá con python tools/bootstrap.py --runtime-only")
    try:
        package_directory = root / ".runtime/python-packages"
        dependencies = dependency_status(python, package_directory=package_directory) if package_directory.is_dir() else dependency_status(python)
        for package in DEPENDENCIES.values():
            item = dependencies.get(package, {})
            available = item.get("available") is True
            detail = f"{item.get('version', 'instalada')} | Python: {python}" if available else "Falta o no se puede importar; ejecutá ese Python con -m pip install -r requirements.txt"
            record(f"dependencia.{package}", "ok" if available else "error", detail)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        record("dependencias", "error", f"No se pudo comprobar el Python seleccionado: {exc}")
    for name, fallback in (
        ("bun", "Se puede buscar por web; la CLI freehire requiere instalar Bun"),
        ("node", "Opcional para desarrollo y herramientas adicionales"),
        ("codex", "Opcional si se usa la app de Codex; no se inició ninguna sesión"),
    ):
        configured = runtime.get(name) if runtime else None
        detected = str(configured) if isinstance(configured, str) and Path(configured).is_file() else shutil.which(name)
        local_bun = root / ".runtime/bun/bun-windows-x64/bun.exe"
        if name == "bun" and not detected and local_bun.is_file():
            detected = str(local_bun.resolve())
        record(f"opcional.{name}", "ok" if detected else "warning", f"Disponible: {detected}" if detected else fallback)
    poppler = shutil.which("pdftotext")
    record("opcional.poppler", "ok" if poppler else "warning", f"Disponible: {poppler}" if poppler else "Sin medición automática de geometría; extraé texto con pypdf e inspeccioná visualmente el PDF")
    return {
        "ok": not any(check["status"] == "error" for check in checks),
        "checks": checks,
        "python": str(python),
    }


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = diagnose(args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        labels = {"ok": "OK", "warning": "AVISO", "error": "ERROR"}
        for check in result["checks"]:
            print(f"[{labels[check['status']]}] {check['name']}: {check['detail']}")
        print("Diagnóstico técnico aprobado; revisá los avisos y completá el perfil antes de postular." if result["ok"] else "Diagnóstico con errores. Corregí los puntos ERROR antes de generar documentos.")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
