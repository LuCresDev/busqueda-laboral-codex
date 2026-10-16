# Template: argentina-simple

- **Type:** Cover letter
- **Source extension:** .json
- **Engine/toolchain:** Python + ReportLab + pypdf
- **Page limit:** 1 page(s)
- **Fonts:** Arial (Windows system font), fallback Lato (bundled in `cover_letters/OpenFonts/fonts/lato/`), then DejaVu Sans (Linux system font). Embedded Unicode TrueType.
- **Class/packages:** reportlab, pypdf; no LaTeX required

## Compile command

Run from the repository root; `<file>` includes the output directory, without extension:

    python tools/render_application.py --kind cover --input <file>.json --output <file>.pdf

## Style rules

- A4, one column, Spanish (Argentina), simple and professional tone, one page including closing and name.
- Print name and contacts literally. No photo, DNI, CUIL, age, birth date or marital status.
- Date in Spanish, e.g. `Córdoba, 15 de octubre de 2026`; use the actual application date and confirmed candidate city, never the demo date as a default.
- Prefer three short paragraphs: specific motivation, relevant confirmed experience, closing. Roughly 180-300 words is a guide; actual page count is the enforced limit.
- Salutation and closing match the posting language. Do not claim availability, relocation, English fluency or work authorization unless confirmed.
- Submit a letter only when useful or requested by the employer. Compile, render to PNG and inspect before presenting it or sending anything.

## JSON contract

- Required: `person` object (`name`, valid `email`); `date`, `company`, `role` (nonempty text); `paragraphs` (nonempty list of nonempty plain text).
- Optional `person`: `phone`, `location`, `links` (list of literal URLs).
- Optional `recipient`: salutation; default `Al equipo de selección:`.
- Optional `closing`: default `Saludos cordiales,`. The renderer prints the exact `person.name` below it.
- `template.json` contains placeholders only; replace them with confirmed facts. Its placeholder email intentionally fails validation.
- Input is UTF-8 JSON data only. Unknown/duplicate keys, invalid values, missing glyphs and overflow fail explicitly. Markup is escaped and never executes; the renderer makes no network requests.

## Known pitfalls

- A second page is an error, never silently truncated. Previous output remains intact on failure; revise the text, then rerun.
- `python -m pip install reportlab pypdf` installs dependencies for the chosen Python. System Arial is preferred; repository Lato is portable fallback.
- Prototype PDFs in `reports/demo/` use explicitly fictional data and are not the candidate's documents. Initial compile and visual inspection verified before activation.
