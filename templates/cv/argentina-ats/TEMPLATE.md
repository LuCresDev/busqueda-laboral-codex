# Template: argentina-ats

- **Type:** CV
- **Source extension:** .json
- **Engine/toolchain:** Python + ReportLab + pypdf
- **Page limit:** 2 page(s) maximum; 1 page is valid and must not be padded
- **Fonts:** Arial (Windows system font), fallback Lato (bundled in `cover_letters/OpenFonts/fonts/lato/`), then DejaVu Sans (Linux system font). All embedded as Unicode TrueType; missing glyphs fail explicitly.
- **Class/packages:** reportlab, pypdf; no LaTeX required

## Compile command

Run from the repository root; `<file>` includes the output directory, without extension:

    python tools/render_application.py --kind cv --input <file>.json --output <file>.pdf

## Style rules

- A4, one column, readable 10.5 pt body, selectable text, headings in Spanish, restrained navy accent.
- One or two pages according to real experience. Never invent content, fill space or shrink the type to meet a page target.
- Name, email, phone, city/province and URLs are printed literally; no contact icons or hidden links.
- No photo, DNI, CUIL, birth date, age, full street address or marital status by default. Unknown JSON fields fail so facts are never silently ignored.
- Use reverse chronological experience and ASCII hyphens in periods, e.g. `marzo 2023 - actualidad`. Do not invent missing dates.
- State `En curso, finalización estimada ...` explicitly in `education[].status` when applicable.
- Only include truthful skills, metrics, degrees, courses and language levels confirmed in the candidate profile. No automatic claims or translations of proper names.
- After compilation, render every page to PNG and inspect it. Also run `python tools/verify_pdf.py <file>.pdf --ascii-dates` and check the extracted contact details and job keywords. A readable text layer does not guarantee acceptance by every ATS.

## JSON contract

JSON is UTF-8, data only; HTML and ReportLab tags are displayed as literal text. The renderer performs no network requests and executes no code from the input. Duplicate keys, unknown keys, missing minimum data, unsupported glyphs and layout overflow are errors. Content is never silently truncated. Output is replaced only after successful validation.

- Required: `person` with nonempty `name` and valid `email`; `headline`; `summary`; and at least one entry in `experience`, `education` or `projects`.
- Optional `person`: `phone`, `location`, `links` (list of literal URLs). Remove unknown optional values; do not leave placeholders.
- `skills`, `languages`, `certifications`: lists of plain text, optional.
- `experience`: list of objects requiring `role`, `organization`, `period`, `bullets` (list of text); optional `location`.
- `education`: list of objects requiring `degree`, `institution`, `period`; optional `status`, `details` (list of text).
- `projects`: list of objects requiring `name`, `details` (list of text); optional `url` printed literally.
- Omit empty optional sections. Keep at least one real entry for a candidate without work experience, such as education or a real project.
- `template.json` is a structural skeleton, never a factual source. Replace all placeholders with confirmed facts before rendering. Its placeholder email intentionally fails validation.

## Known pitfalls

- The stock final-page whitespace threshold does not require padding a short CV; inspect readability and page breaks without inventing content.
- Maximum two pages is enforced with pypdf. Overflow leaves an existing output untouched and returns a nonzero exit code; revise content with the candidate, then rerun.
- Fonts with no glyph for a supplied character cause an explicit error. Spanish accents and ñ are covered by the supplied font choices. Do not hide that error by switching to a non-Unicode PDF font.
- ReportLab and pypdf must be installed in the Python interpreter used by the command: `python -m pip install reportlab pypdf`.
- Prototype PDFs in `reports/demo/` use explicitly fictional data and are not the candidate's CV. Initial compile and visual inspection verified before activation.
