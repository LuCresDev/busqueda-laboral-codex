#!/usr/bin/env python3
"""Render validated, plain-text es-AR application JSON to an ATS-readable PDF.

No network, LaTeX, HTML, expression evaluation or user-supplied templates are used.
See templates/{cv,cover_letters}/argentina-*/TEMPLATE.md for the JSON contract.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from xml.sax.saxutils import escape

try:
    from pypdf import PdfReader
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        KeepTogether,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )
    from reportlab.platypus.doctemplate import LayoutError
except ImportError as exc:
    raise SystemExit(
        "Faltan dependencias PDF. Ejecutá: python -m pip install reportlab pypdf"
    ) from exc


ROOT = Path(__file__).resolve().parent.parent
MAX_INPUT_BYTES = 1_000_000
LIMITS = {"cv": 2, "cover": 1}


class InputError(ValueError):
    """The input cannot be rendered without changing or inventing its facts."""


def _object(value, where, allowed, required=()):
    if not isinstance(value, dict):
        raise InputError(f"{where}: se esperaba un objeto JSON.")
    unknown = set(value) - set(allowed)
    if unknown:
        raise InputError(f"{where}: campos no admitidos: {', '.join(sorted(unknown))}.")
    missing = set(required) - set(value)
    if missing:
        raise InputError(f"{where}: faltan campos: {', '.join(sorted(missing))}.")
    return value


def _text(value, where, max_length=6000):
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{where}: se esperaba texto no vacío.")
    if len(value) > max_length:
        raise InputError(f"{where}: supera {max_length} caracteres; revisá el contenido.")
    if any(unicodedata.category(char) == "Cc" and char not in "\n\r\t" for char in value):
        raise InputError(f"{where}: contiene caracteres de control no admitidos.")
    # Keep the submitted spelling and punctuation, including literal contacts.
    return value


def _strings(value, where, min_items=0, max_items=60):
    if not isinstance(value, list) or not min_items <= len(value) <= max_items:
        raise InputError(f"{where}: se esperaba una lista de {min_items} a {max_items} textos.")
    return [_text(item, f"{where}[{index}]") for index, item in enumerate(value)]


def _person(value):
    fields = {"name", "email", "phone", "location", "links"}
    _object(value, "person", fields, {"name", "email"})
    person = {key: _text(item, f"person.{key}", 500) for key, item in value.items() if key != "links"}
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", person["email"]):
        raise InputError("person.email: escribí una dirección de correo válida.")
    if "links" in value:
        person["links"] = _strings(value["links"], "person.links", max_items=5)
    return person


def _entries(value, where, required, optional):
    if not isinstance(value, list) or len(value) > 40:
        raise InputError(f"{where}: se esperaba una lista de hasta 40 entradas.")
    result = []
    for index, entry in enumerate(value):
        location = f"{where}[{index}]"
        _object(entry, location, set(required) | set(optional), required)
        normalized = {}
        for key, item in entry.items():
            normalized[key] = (
                _strings(item, f"{location}.{key}")
                if key in {"bullets", "details"}
                else _text(item, f"{location}.{key}", 2000)
            )
        if "period" in normalized and re.search(r"[\u2010-\u2015\u2212]", normalized["period"]):
            raise InputError(f"{location}.period: usá el guion ASCII (-) en las fechas.")
        result.append(normalized)
    return result


def validate(data, kind):
    """Return a validated copy. Unknown keys are errors, never silently dropped."""
    if kind not in LIMITS:
        raise InputError("El tipo debe ser cv o cover.")
    if kind == "cv":
        _object(data, "cv", {
            "person", "headline", "summary", "skills", "experience", "education",
            "languages", "certifications", "projects",
        }, {"person", "headline", "summary"})
    else:
        _object(data, "cover", {
            "person", "date", "company", "role", "recipient", "paragraphs", "closing",
        }, {"person", "date", "company", "role", "paragraphs"})
    result = {"person": _person(data["person"])}
    for key, value in data.items():
        if key == "person":
            continue
        if key == "experience":
            result[key] = _entries(value, key, {"role", "organization", "period", "bullets"}, {"location"})
        elif key == "education":
            result[key] = _entries(value, key, {"degree", "institution", "period"}, {"status", "details"})
        elif key == "projects":
            result[key] = _entries(value, key, {"name", "details"}, {"url"})
        elif key in {"skills", "languages", "certifications", "paragraphs"}:
            result[key] = _strings(value, key, min_items=1 if key == "paragraphs" else 0)
        else:
            result[key] = _text(value, key)
    if kind == "cv" and not any(result.get(key) for key in ("experience", "education", "projects")):
        raise InputError("El CV necesita al menos una experiencia, educación o proyecto confirmado.")
    return result


def _no_duplicate_keys(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise InputError(f"JSON: campo repetido: {key}.")
        data[key] = value
    return data


def load_input(path):
    source = Path(path)
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise InputError("El JSON supera 1 MB; usá solo el contenido de la candidatura.")
    try:
        return json.loads(source.read_text(encoding="utf-8-sig"), object_pairs_hook=_no_duplicate_keys)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise InputError(f"JSON UTF-8 inválido: {exc}") from exc


def _font_family():
    """Use embedded TrueType with a real Unicode mapping, or fail explicitly."""
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    lato = ROOT / "cover_letters/OpenFonts/fonts/lato"
    choices = [
        (windows / "arial.ttf", windows / "arialbd.ttf"),
        (lato / "Lato-Reg.ttf", lato / "Lato-Bol.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in choices:
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont("Application", str(regular)))
            pdfmetrics.registerFont(TTFont("Application-Bold", str(bold)))
            pdfmetrics.registerFontFamily("Application", normal="Application", bold="Application-Bold")
            return "Application"
    raise InputError("Falta una fuente Unicode: instalá Arial o restaurá las fuentes Lato del repositorio.")


def _check_glyphs(data, font_name):
    font = pdfmetrics.getFont(font_name)
    def visit(item):
        if isinstance(item, str):
            for char in item:
                if char.isspace():
                    continue
                if ord(char) not in font.face.charToGlyph:
                    raise InputError(f"La fuente no contiene el carácter {char!r} (U+{ord(char):04X}); revisalo.")
        elif isinstance(item, dict):
            for value in item.values():
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)
    visit(data)


def _styles(font):
    base = dict(fontName=font, fontSize=10.5, leading=14.5, textColor=colors.HexColor("#202a33"), alignment=TA_LEFT)
    return {
        "body": ParagraphStyle("Body", spaceAfter=6, **base),
        "name": ParagraphStyle("Name", fontName=f"{font}-Bold", fontSize=23, leading=28,
                               textColor=colors.HexColor("#183d56"), spaceAfter=6, keepWithNext=True),
        "headline": ParagraphStyle("Headline", fontName=f"{font}-Bold", fontSize=12, leading=16,
                                   spaceAfter=6, keepWithNext=True),
        "contact": ParagraphStyle("Contact", spaceAfter=3, **{**base, "fontSize": 9, "leading": 12}),
        "section": ParagraphStyle("Section", fontName=f"{font}-Bold", fontSize=11.5, leading=15,
                                  textColor=colors.HexColor("#183d56"), spaceBefore=11, spaceAfter=6,
                                  keepWithNext=True),
        "entry": ParagraphStyle("Entry", spaceAfter=2, keepWithNext=True, **{**base, "fontName": f"{font}-Bold"}),
        "meta": ParagraphStyle("Meta", spaceAfter=5, keepWithNext=True,
                               **{**base, "fontSize": 9, "leading": 12}),
        "bullet": ParagraphStyle("Bullet", leftIndent=11, firstLineIndent=-8, spaceAfter=4, **base),
    }


def _paragraph(text, style):
    # User text is never parsed as markup: <img>, <link>, entities, etc. stay literal.
    return Paragraph(escape(text).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>"), style)


def _header(person, styles, headline=None):
    story = [_paragraph(person["name"], styles["name"])]
    if headline:
        story.append(_paragraph(headline, styles["headline"]))
    contacts = [person[key] for key in ("email", "phone", "location") if person.get(key)]
    story.extend(_paragraph(value, styles["contact"]) for value in contacts)
    story.extend(_paragraph(link, styles["contact"]) for link in person.get("links", []))
    story.append(Spacer(1, 9))
    return story


def _cv_story(data, styles):
    story = _header(data["person"], styles, data["headline"])
    story.append(_paragraph("Perfil profesional", styles["section"]))
    story.append(_paragraph(data["summary"], styles["body"]))
    def strings_section(key, title):
        if data.get(key):
            story.append(_paragraph(title, styles["section"]))
            story.extend(_paragraph("- " + item, styles["bullet"]) for item in data[key])
    strings_section("skills", "Habilidades")
    if data.get("experience"):
        story.append(_paragraph("Experiencia laboral", styles["section"]))
        for entry in data["experience"]:
            heading = f"{entry['role']} | {entry['organization']}"
            meta = entry["period"] + (f" | {entry['location']}" if entry.get("location") else "")
            story.extend([_paragraph(heading, styles["entry"]), _paragraph(meta, styles["meta"])])
            story.extend(_paragraph("- " + item, styles["bullet"]) for item in entry["bullets"])
            story.append(Spacer(1, 4))
    if data.get("education"):
        story.append(_paragraph("Educación", styles["section"]))
        for entry in data["education"]:
            story.append(_paragraph(f"{entry['degree']} | {entry['institution']}", styles["entry"]))
            meta = entry["period"] + (f" | {entry['status']}" if entry.get("status") else "")
            story.append(_paragraph(meta, styles["meta"]))
            story.extend(_paragraph("- " + item, styles["bullet"]) for item in entry.get("details", []))
    if data.get("projects"):
        story.append(_paragraph("Proyectos", styles["section"]))
        for entry in data["projects"]:
            story.append(_paragraph(entry["name"], styles["entry"]))
            if entry.get("url"):
                story.append(_paragraph(entry["url"], styles["meta"]))
            story.extend(_paragraph("- " + item, styles["bullet"]) for item in entry["details"])
    strings_section("certifications", "Cursos y certificaciones")
    strings_section("languages", "Idiomas")
    return story


def _cover_story(data, styles):
    story = _header(data["person"], styles)
    for text in (data["date"], data["company"], "Postulación: " + data["role"]):
        story.append(_paragraph(text, styles["body"]))
    story.append(Spacer(1, 8))
    story.append(_paragraph(data.get("recipient", "Al equipo de selección:"), styles["body"]))
    story.extend(_paragraph(item, styles["body"]) for item in data["paragraphs"])
    story.append(Spacer(1, 8))
    story.append(KeepTogether([
        _paragraph(data.get("closing", "Saludos cordiales,"), styles["body"]),
        _paragraph(data["person"]["name"], styles["body"]),
    ]))
    return story


def render_application(data, kind, output):
    """Validate, build in memory, verify pages/text and replace output atomically."""
    data = validate(data, kind)
    output = Path(output)
    if output.suffix.lower() != ".pdf":
        raise InputError("La salida debe tener extensión .pdf.")
    font = _font_family()
    _check_glyphs(data, font)
    styles = _styles(font)
    stream = io.BytesIO()
    document = SimpleDocTemplate(
        stream, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title=f"{data['person']['name']} - {'CV' if kind == 'cv' else 'Carta de presentación'}",
        author=data["person"]["name"], pageCompression=1,
    )
    story = _cv_story(data, styles) if kind == "cv" else _cover_story(data, styles)
    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#536470"))
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()
    try:
        document.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    except LayoutError as exc:
        raise InputError("El contenido no entra en el diseño. Revisalo; no se recortó texto.") from exc
    pdf = stream.getvalue()
    reader = PdfReader(io.BytesIO(pdf))
    pages = len(reader.pages)
    if not 1 <= pages <= LIMITS[kind]:
        raise InputError(
            f"El documento tiene {pages} páginas; el máximo es {LIMITS[kind]}. "
            "Seleccioná y resumí contenido con el candidato. No se escribió ni recortó el PDF."
        )
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    folded = " ".join(text.split())
    for key in ("name", "email", "phone", "location"):
        if data["person"].get(key) and " ".join(data["person"][key].split()) not in folded:
            raise InputError(f"No se pudo verificar el contacto literal person.{key} en la capa de texto.")
    if "\ufffd" in text or re.search(r"\(cid:\d+\)", text):
        raise InputError("La capa de texto presenta errores de codificación; no se guardó el PDF.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".application-", suffix=".pdf", dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(pdf)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return pages


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Generá un CV o carta PDF en español (Argentina), sin LaTeX.")
    parser.add_argument("--kind", required=True, choices=LIMITS)
    parser.add_argument("--input", required=True, type=Path, help="JSON UTF-8 con datos confirmados")
    parser.add_argument("--output", required=True, type=Path, help="Archivo PDF de destino")
    arguments = parser.parse_args(argv)
    try:
        if arguments.input.resolve() == arguments.output.resolve():
            raise InputError("La entrada y la salida deben ser archivos distintos.")
        pages = render_application(load_input(arguments.input), arguments.kind, arguments.output)
    except (InputError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"PDF generado: {arguments.output} ({pages} página(s)). Revisá el PDF antes de postularte.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
