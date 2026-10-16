"""Regressions for safe literal text, usable Unicode and document page budgets."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader


SPEC = importlib.util.spec_from_file_location(
    "render_application", Path(__file__).resolve().parents[1] / "tools/render_application.py"
)
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


def fictional_cv():
    return {
        "person": {
            "name": "María Núñez - ejemplo ficticio",
            "email": "maria.nunez@example.com",
            "phone": "+54 11 5555 0100",
            "location": "Córdoba, Argentina",
            "links": ["https://example.com/maria"],
        },
        "headline": "Analista de datos - demostración ficticia",
        "summary": "Perfil ficticio para verificar la plantilla. Análisis, comunicación y atención al detalle.",
        "skills": ["Python y SQL", "Visualización y documentación"],
        "experience": [{
            "role": "Analista", "organization": "Empresa ficticia", "period": "marzo 2023 - abril 2025",
            "bullets": ["Preparó informes de gestión.", "Revisó la calidad de datos.", "Documentó consultas SQL."],
        }],
        "education": [{
            "degree": "Tecnicatura ficticia", "institution": "Instituto de ejemplo",
            "period": "2021 - 2023", "status": "Finalizado", "details": [],
        }],
        "languages": ["Español nativo (ejemplo ficticio)"],
    }


def fictional_cover():
    return {
        "person": fictional_cv()["person"],
        "date": "Córdoba, 15 de octubre de 2026",
        "company": "Empresa ficticia",
        "role": "Analista de datos (demostración)",
        "paragraphs": [
            "Esta carta utiliza datos ficticios para comprobar el diseño de una postulación en Argentina.",
            "El ejemplo demuestra texto en español, tildes y caracteres como ñ. No representa la experiencia de una persona real.",
            "Gracias por revisar esta demostración de la plantilla.",
        ],
    }


class RenderApplicationTests(unittest.TestCase):
    def test_cv_contacts_accents_ascii_dates_and_reading_order(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "cv.pdf"
            self.assertEqual(renderer.render_application(fictional_cv(), "cv", output), 1)
            reader = PdfReader(output)
            text = "\n".join(page.extract_text() for page in reader.pages)
            for expected in ("María Núñez", "Córdoba", "+54 11 5555 0100", "maria.nunez@example.com",
                             "marzo 2023 - abril 2025", "https://example.com/maria"):
                self.assertIn(expected, text)
            self.assertLess(text.index("Perfil profesional"), text.index("Experiencia laboral"))
            self.assertLess(text.index("Experiencia laboral"), text.index("Educación"))
            self.assertNotIn("\ufffd", text)

    def test_cover_letter_signature_and_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "letter.pdf"
            self.assertEqual(renderer.render_application(fictional_cover(), "cover", output), 1)
            text = PdfReader(output).pages[0].extract_text()
            self.assertIn("Al equipo de selección:", text)
            self.assertIn("Saludos cordiales,", text)
            self.assertEqual(text.count("María Núñez - ejemplo ficticio"), 2)

    def test_reportlab_markup_is_literal_and_does_not_fetch_assets(self):
        data = fictional_cv()
        payload = '<img src="https://example.com/private.png"/> & <b>literal</b>'
        data["skills"] = [payload]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "literal.pdf"
            renderer.render_application(data, "cv", output)
            self.assertIn(payload, PdfReader(output).pages[0].extract_text())

    def test_rejects_missing_or_wrong_minimum_data_and_private_fields(self):
        cases = [
            ({}, "cv"),
            ({**fictional_cv(), "person": {"name": "Ejemplo", "email": "incorrecto"}}, "cv"),
            ({**fictional_cv(), "dni": "12345678"}, "cv"),
            ({**fictional_cv(), "skills": "Python"}, "cv"),
            ({**fictional_cv(), "education": [], "experience": []}, "cv"),
            ({**fictional_cover(), "paragraphs": []}, "cover"),
            ({**fictional_cover(), "paragraphs": [123]}, "cover"),
        ]
        for data, kind in cases:
            with self.subTest(data=data, kind=kind), self.assertRaises(renderer.InputError):
                renderer.validate(data, kind)

    def test_rejects_unicode_dash_in_period(self):
        data = fictional_cv()
        data["experience"][0]["period"] = "2023\u20132025"
        with self.assertRaisesRegex(renderer.InputError, "guion ASCII"):
            renderer.validate(data, "cv")

    def test_overflow_does_not_replace_previous_pdf_or_drop_text(self):
        for kind, data in (("cv", fictional_cv()), ("cover", fictional_cover())):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                output = Path(folder) / "existing.pdf"
                output.write_bytes(b"previous result")
                if kind == "cv":
                    data["experience"] = [copy.deepcopy(data["experience"][0]) for _ in range(35)]
                else:
                    data["paragraphs"] = ["Texto ficticio de prueba para verificar el límite de página. " * 15] * 20
                with self.assertRaisesRegex(renderer.InputError, "máximo|no entra"):
                    renderer.render_application(data, kind, output)
                self.assertEqual(output.read_bytes(), b"previous result")

    def test_two_page_cv_is_accepted_without_padding(self):
        data = fictional_cv()
        data["experience"] = [copy.deepcopy(data["experience"][0]) for _ in range(7)]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "two.pdf"
            self.assertEqual(renderer.render_application(data, "cv", output), 2)

    def test_unknown_glyph_fails_instead_of_black_square(self):
        data = fictional_cv()
        data["summary"] = "Texto de ejemplo \U0001F680"
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(renderer.InputError, "carácter"):
            renderer.render_application(data, "cv", Path(folder) / "glyph.pdf")

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "duplicate.json"
            source.write_text('{"name": "uno", "name": "dos"}', encoding="utf-8")
            with self.assertRaisesRegex(renderer.InputError, "repetido"):
                renderer.load_input(source)


if __name__ == "__main__":
    unittest.main()
