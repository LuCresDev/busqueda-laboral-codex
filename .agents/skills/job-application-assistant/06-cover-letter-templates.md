---
framework_version: 2.1.0
---

# Cover Letter Templates and Tailoring Guide

Metodología compartida: no escribir datos personales en este archivo. La biografía proviene solo de profile/candidate.md; consultá los archivos personales opcionales profile/writing-style.md, profile/evaluation.md, profile/behavioral.md o profile/interview.md cuando corresponda. Los campos desconocidos siguen pendientes. El onboarding y el reset no modifican estas reglas.

<!-- BEGIN ACTIVE-TEMPLATE (managed by registro de plantillas - do not edit by hand) -->
> **Active template override: `argentina-simple`**
>
> A custom template is active. Where this block conflicts with the stock guidance below, this block wins. Truthful tailoring advice still applies.
>
> - **Template skeleton:** `templates/cover_letters/argentina-simple/template.json` - replace placeholders with confirmed facts instead of using the stock LaTeX class.
> - **Manifest:** `templates/cover_letters/argentina-simple/TEMPLATE.md` - read its JSON contract and style rules before drafting.
> - **Source extension:** `.json` (UTF-8 plain data).
> - **Compile command:** `python tools/render_application.py --kind cover --input <file>.json --output <file>.pdf`. Run from the repository root; `<file>` includes the output directory. There are no build intermediates. Never present an old PDF after a failed compile.
> - **Fonts:** Arial from Windows, fallback repository Lato, then system DejaVu Sans; embedded Unicode TrueType. No XeLaTeX required.
> - **Page limit:** exactly 1 page, including closing and printed name. Overflow is an explicit error; revise with the candidate and rerun.
> - **Output file:** `cover_letters/cover_<company>_<role>.json` and matching `.pdf`.
> - **Argentina defaults:** Spanish, date in Spanish, literal name and contacts, three concise paragraphs, professional tone. No private identifiers or unsupported claims. Use the actual application date; demo dates are examples only.
> - **Verification:** compile and visually inspect the page, then run `python tools/verify_pdf.py <file>.pdf --pages 1 --dump-text <file>.txt`. Check accents, contacts, company, role, date and all claims. Initial compile and visual inspection passed using explicitly fictional data before activation.
<!-- END ACTIVE-TEMPLATE -->

## Optional Legacy Template: cover.cls (only when explicitly active)

Cover letters use a custom LaTeX document class (`cover.cls`) with Lato/Raleway fonts.

**Output file:** `cover_letters/cover_<company>_<role>.tex`
**Compile with:** XeLaTeX (cover.cls requires fontspec)
**Font directory:** `cover_letters/OpenFonts/fonts/`

### Compile command

```bash
cd cover_letters && xelatex -interaction=nonstopmode cover_<company>_<role>.tex
```

Expected output: `Output written on cover_<company>_<role>.pdf (1 page, ...)`. Any page count other than 1 is a failure that must be fixed before presenting to the user.

## Compile-and-Inspect Loop (MANDATORY)

After writing the cover letter and before presenting to the user, always compile and visually inspect the PDF. Iterate until the layout is clean:

1. Run `xelatex -interaction=nonstopmode cover_<company>_<role>.tex`
2. Confirm page count is exactly 1 and compile succeeded
3. Read the PDF via the visor de PDF o imágenes disponible and visually check: signature fits at the bottom, no text cut off, bullet font matches body

### Known template pitfall: itemize inside `\lettercontent{}`

The `\lettercontent{}` macro appends `\\` to its argument. This breaks when the argument ends in `\end{itemize}` because `\\` has no line to break after the environment closes, producing `! LaTeX Error: There's no line here to end.` and no PDF output.

**Wrong (breaks compile):**
```latex
\lettercontent{Here is how my experience maps:
\begin{itemize}
    \item ...
\end{itemize}}
```

**Correct — close `\lettercontent{}` before the list and wrap the list in the matching Raleway-Medium font so typography stays consistent:**
```latex
\lettercontent{Here is how my experience maps:}

{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item ...
\end{itemize}\par}
\vspace{6pt}

\lettercontent{[next paragraph]}
```

The font wrapper is mandatory — if you just move `\begin{itemize}` outside `\lettercontent{}` without the `\fontspec` block, bullets render in the default body font (Lato) and visually mismatch the rest of the letter.

## Document Structure

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Cover Letter - [Company], [Role]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\documentclass[]{cover}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}

\rfoot{Page \thepage \hspace{0pt}}
\thispagestyle{empty}
\renewcommand{\headrulewidth}{0pt}
\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     TITLE NAME
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\namesection{}{\Huge{[YOUR_NAME]}}{  \href{mailto:[YOUR_EMAIL]}{[YOUR_EMAIL]} | [YOUR_PHONE] |  \urlstyle{same}\href{[YOUR_LINKEDIN_URL]}{LinkedIn}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     MAIN COVER LETTER CONTENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\currentdate{\today}
\lettercontent{Dear [Name/Team],}

\lettercontent{[Opening paragraph - role, connection to background, 2-3 sentences]}

\lettercontent{[Body paragraph - most relevant experience, introducing the bullet list]}

{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item {[Concrete achievement/skill 1]}
    \item {[Concrete achievement/skill 2]}
    \item {[Concrete achievement/skill 3]}
\end{itemize}\par}

\lettercontent{[Connection to company - why this role, why this company specifically]}

\lettercontent{[Personal fit paragraph - behavioral strengths, team contribution, 2-3 sentences]}

\lettercontent{I look forward to hearing from you.}

\begin{flushright}
% No trailing \\ inside \closing{} - cover.cls appends its own \\, and a
% doubled break triggers "! LaTeX Error: There's no line here to end."
\closing{Kind regards,}

\signature{[YOUR_NAME]}
\end{flushright}
\end{document}
```

## Key Commands Reference

| Command | Purpose |
|---------|---------|
| `\namesection{}{Name}{contact info}` | Header with name and contact |
| `\currentdate{date}` | Date field (use `\today` or explicit date) |
| `\lettercontent{text}` | Body paragraph (adds spacing after) |
| `\closing{text}` | Closing line |
| `\signature{name}` | Printed name below signature |

## Tailoring Guidelines

### Salutation
- If you know the hiring manager's name: "Dear [First Last],"
- If you know the team: "Dear [Company] hiring team,"
- Generic: "Dear [Company]," (avoid "To whom it may concern")

### Length - Hard 1-Page Limit
- Target: 1 page including signature block
- Maximum: **never exceed 1 page**
- **Word budget: 250-300 words** of body text (not counting LaTeX markup). This is the safe maximum. 350 words will overflow.
- **Always count**: opening paragraph + bullet list paragraph + closing paragraph = 3 blocks. Add a 4th only if the others are short.
- When adding company-specific content, trim other content to compensate rather than adding net length

### Line Spacing
- Add `\usepackage{setspace}` and `\setstretch{1.0}` if the letter is long and needs to fit on one page
- Use `\vspace{.5cm}` between major sections for readability (only if space permits)

### Bullet Lists
- Place `\begin{itemize}...\end{itemize}` **outside** a `\lettercontent{}` block (see "Known template pitfall" above), wrapped in the matching Raleway-Medium `\fontspec` so the bullet font matches the body
- 3-5 bullets is ideal
- Start each bullet with bold label or action verb
- Use `\textbf{Label:}` for category-style bullets
- A bullet whose text begins with a literal `[` must be braced: `\item {[text]}`. Unbraced, LaTeX parses `[text]` as `\item`'s optional label and renders it off the left page edge, missing from the PDF text layer entirely

### LaTeX Special Characters
Escape these wherever they appear in body text:
- Ampersand: `\&` (company names: Río \& Sur (empresa ficticia)) - unescaped, the compile fails loudly
- Percent: `\%` ("grew revenue 30\%") - unescaped, it does **not** fail: everything after the `%` on that line is silently eaten as a LaTeX comment
- Dollar: `\$`, hash: `\#`, underscore: `\_`
- Tilde: `\textasciitilde{}`, caret: `\textasciicircum{}`, backslash: `\textbackslash{}`

### Idioma acordado de la carta
- Mantener la estructura de la plantilla y usar el idioma acordado con el usuario para esa postulación; español predeterminado editable.
- Fecha legible y consistente con el idioma/documento acordado.
- Cierre profesional breve, por ejemplo «Saludos cordiales»; no aplicar fórmulas de otro mercado por defecto.

## Checklist Before Finalizing
- [ ] No em-dashes (use commas or periods instead)
- [ ] No cliches or empty filler
- [ ] Every claim backed by specific example
- [ ] Forward-looking framing: focuses on tasks you'll solve, not just past duties
- [ ] Motivation section references this specific company's mission/values
- [ ] Company name and role are correct throughout
- [ ] Date is current
- [ ] Fits on one page
- [ ] Language matches the job posting language
- [ ] Salutation is appropriate (named person if possible)
- [ ] Headline is engaging and specific, not generic

## Submission Guidelines (Best Practice)
- Submit only the documents the employer requests
- Export as PDF to preserve formatting
- Name files clearly: "[Your Name] CV" and "[Your Name] Cover Letter"
- Follow all employer instructions regarding anonymity or specific materials
