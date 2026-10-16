# Onboarding del perfil en Codex

Workflow de Codex en lenguaje natural. Las opciones se extraen del pedido; las etiquetas de flujo no son comandos slash ni de consola. Rutas desde raíz; leer archivos personales opcionales solo si existen. Usar capacidades realmente disponibles y mantener las reglas de AGENTS.md.

Este workflow importa documentos o recoge información por conversación. Sus únicas escrituras son archivos personales bajo profile/ y, si se reciben materiales, documents/. No personaliza skills, metodología, plantillas, ejemplos públicos ni configuración técnica.

Antes de escribir, leé profile/candidate.md y los perfiles opcionales existentes. Si faltan, inicializá desde raíz con tools/bootstrap.py --profile-only; usa solo biblioteca estándar y no sobrescribe archivos. En Windows puede ejecutarse con el helper Python local. Leé 03 a 09 como metodología compartida, nunca como destino de datos personales.

Comprobá que profile/ y los materiales personales no estén rastreados ni preparados para publicación; la copia local debe conservarlos ignorados. No publicar ni hacer push durante onboarding. Si se detecta un archivo personal ya rastreado, explicá el problema concreto antes de agregar más datos.

Una actualización de sección se infiere de pedidos como «actualizá mis idiomas» o «cambiá mis preferencias de búsqueda» y no requiere repetir todo el onboarding. Preguntá solo lo que falte. Conversación en español y CV español predeterminado no acreditan un nivel laboral en ningún idioma. Una URL inaccesible o parcial de LinkedIn no acredita historia laboral.

## Step 0: Welcome & Choose Path

Then, before greeting the user, scan the `documents/` folder. Enumerá archivos con `documents/**/*` and count files per subfolder (`cv/`, `linkedin/`, `diplomas/`, `references/`, `projects/`, `applications/`).

Then welcome the user with a single message that lists three paths. The wording changes based on what was found.

**If `documents/` has files** in one or more subfolders, lead with Path A:

> **Welcome to the AI Job Search setup!**
>
> I'll help you build your professional profile so Codex can evaluate job postings, tailor CVs, write cover letters, and prepare you for interviews.
>
> I see files in your `documents/` folder: [list per subfolder, e.g. "2 in cv/, 1 in linkedin/, 3 in references/"]. Three ways to start:
>
> **Path A: Read my documents folder** (recommended for what you have) - I'll read everything in `documents/`, cross-reference for consistency, and build your profile from real source materials. Idempotent and safe to re-run as you add more documents.
>
> **Path B: Single CV import** - Paste or @-mention a single CV/resume here. I'll extract it and ask follow-up questions for what's missing.
>
> **Path C: Interview mode** - I'll walk you through structured questions section by section.
>
> Which would you like?

**If `documents/` is empty or missing**, surface Path A as a "do this if you have materials" option:

> **Welcome to the AI Job Search setup!**
>
> I'll help you build your professional profile so Codex can evaluate job postings, tailor CVs, write cover letters, and prepare you for interviews.
>
> Three ways to start:
>
> **Path A: Documents folder** (best signal if you have several materials) - Drop your CV / LinkedIn export / diplomas / reference letters / project summaries in the `documents/` folder, then say "go". I'll read everything and build your profile from it. See `documents/README.md` for the folder layout.
>
> **Path B: Single CV import** - Paste or @-mention a single CV/resume here. I'll extract it and ask follow-up questions for what's missing.
>
> **Path C: Interview mode** - I'll walk you through structured questions section by section. Good if you're starting from scratch.
>
> Which would you like?

Wait for the user's choice. If they pick A but the folder is still empty, tell them what to add (point at `documents/README.md`) and stop.

---

## Path A: Documents Folder

Reads structured documents in `documents/`, cross-references them for consistency, and merges extracted data into the personal profile files. Read-before-write and idempotent: changes already present will not be proposed again.

Follow these steps **exactly in order**.

### Step A1: Inventory

Enumerá archivos con `documents/**/*` to scan the full tree. Print:

```
## Documents Found

**cv/**: [list files, or "(empty)"]
**linkedin/**: [list files, or "(empty)"]
**diplomas/**: [list files, or "(empty)"]
**references/**: [list files, or "(empty)"]
**projects/**: [list files, or "(empty)"]
**applications/**: [list subfolders with their files, or "(empty)"]

I will read these and cross-reference before proposing any changes.
```

If every subfolder is empty, stop and tell the user to populate the folder. Point at `documents/README.md` for the layout.

### Step A2: Read Existing Personal Files

Leé profile/candidate.md y, si existen, profile/behavioral.md, profile/writing-style.md, profile/evaluation.md e profile/interview.md. Son los destinos personales de la importación. Consultá la metodología necesaria en los skills sin editarla. Conservá lo leído para evitar lecturas repetidas.

### Step A3: Parse Documents

Read each document found in Step A1. Process subfolders in this order: `cv/`, `linkedin/`, `diplomas/`, `references/`, `projects/`, `applications/`.

**`cv/` documents:** name, contact (email, phone, LinkedIn, GitHub), education (degree, institution, dates, thesis), work experience (title, company, dates, location, bullets), skills, languages (with any stated proficiency), publications, awards, profile/summary.

**`linkedin/` documents:** About/summary section (full text, used for behavioral inference), work experience, education, skills and endorsements, **Languages section** (language name + self-rated proficiency level, e.g. "Spanish - Native or bilingual proficiency" - a high-confidence structured source, feeds the Language Gate in `04-job-evaluation.md`), certifications, volunteer work, publications, recommendations received (full text). If multiple LinkedIn exports are present, use the most recently modified file.

**`diplomas/` documents:** official degree title and level, institution name (official spelling), graduation date, grade or distinction or GPA if visible.

**`references/` documents:** referee name, title, organization; full text of the letter (extract specific quotes); competency language used.

**`projects/` documents:** project name, summary/description, problem domain, tech stack (languages, frameworks, tools), key technical challenges and architectural decisions, measurable outcomes/metrics (e.g. users, performance, stars, impact).

**`applications/<company>_<role>/` subfolders:**
- `job_posting.md`: role title, company, required skills, experience level, sector, role type
- Carta realmente enviada (fuente JSON o legacy, y PDF): opening structure, body structure, bullet style, closing, recurring phrases
- CV realmente enviado (fuente JSON o legacy, y PDF): profile statement, section ordering, framing for this role type
- `outcome.md`: status (in_progress/hired/offer_declined/rejected/no_response/interview_only), interview stages, notes. Skip `in_progress` applications for calibration — they have no final signal yet.

After reading, proceed to Step A4 without intermediate output. The user sees a complete picture in Step A6.

### Step A4: Cross-Reference Check

Before mapping anything to skill files, check for inconsistencies:

- Date mismatches between CV / LinkedIn / diploma
- Title mismatches across documents for the same role
- Education mismatches (degree name, graduation date)
- Employer name variations

If inconsistencies are found, present them as a numbered list and wait for the user to resolve each one before continuing:

```
## Cross-Reference Issues Found

These need to be resolved before I continue. For each one, tell me which version is correct.

1. **Role title mismatch - [COMPANY]:**
   CV says: "[TITLE_A]"
   LinkedIn says: "[TITLE_B]"
   Which is correct?

2. ...
```

If no inconsistencies, state "No cross-reference issues found." and continue.

### Step A5: Build Change Sets

For each personal profile file, compare extracted document content against the current file content from Step A2. Build two buckets.

**Additive changes:** entirely new content not in the personal file in any form. Examples: a certification not in `profile/candidate.md`, a new independent project not in `profile/candidate.md`, a new endorsement skill, a referee not yet listed, a new behavioral quote from a reference letter, a new award.

**Conflicting changes:** content that touches something already in a personal file but disagrees. Examples: a different date range for an existing job, a different job title for the same role, a different graduation date than what is recorded.

**Inference rules** (apply when populating from inferred sources):

- **`profile/candidate.md` (`## Proyectos independientes`):** Source is `projects/` documents. Extract structured project entries formatted as `- **[PROJECT_NAME]**: [DESCRIPTION with tech stack and measurable outcome]`. Ground all claims in the document text.
- **`profile/behavioral.md`:** Source is LinkedIn About + recommendation letters. Extract recurring themes, adjectives, phrases about how the candidate works. Add only to the "Fortalezas confirmadas", "Forma de trabajo y entorno preferido", or "Evaluaciones y fuentes" sections (the shipped file's `##` headings). Do not overwrite existing scored assessments. Always label inferred additions: *[Inferred from LinkedIn About / Reference letter - review before relying on this]*
- **`profile/writing-style.md`:** Source is actual submitted cover-letter sources (.json or legacy .tex) and their PDFs. Extract recurring patterns. Add as observations under "## Referencias aportadas por el usuario". Do not modify existing rules. Only add if 2+ cover letters show a genuine pattern.
- **`profile/evaluation.md`:** Source is `job_posting.md` + `outcome.md` pairs. If an application reached interview or offer: note role type and sector as a confirmed strong-fit signal. If 2+ applications repeat a no-response or rejection pattern: note it. Add findings under "## Calibración con resultados reales". Do not modify the existing scoring framework.
- **`profile/writing-style.md — CV`:** Source is actual submitted CV sources (.json or legacy .tex) and their PDFs. Extract any profile statement that does not already appear in templates. Label with: *[Used for: <company>_<role>]*. **Ground before extracting:** archived drafts are tailored outputs, not source documents - verify every factual claim in an extracted statement (titles, employers, metrics, technologies) against `profile/candidate.md` and drop or correct any claim the profile does not support, keeping only the framing. A tailored draft that drifted must never become a template future applications start from.
- **`profile/writing-style.md — cartas`:** Source is actual submitted cover-letter sources (.json or legacy .tex) and their PDFs. Extract opening patterns, bullet structures, closing formulations. Add only what is structurally distinct from existing templates.
- **`profile/interview.md`:** Source is CV bullets, LinkedIn descriptions, reference letter quotes. Identify achievements not yet covered by an existing STAR example. Do NOT draft full STAR examples. Add stubs under "## Experiencias candidatas para STAR":

```markdown
### [Achievement title]
**Source:** [CV / LinkedIn / Reference letter - role/company]
**What happened:** [one sentence]
**Why it matters:** [interview question types this could answer]
**S/T/A/R stub:**
- Situation:
- Task:
- Action:
- Result:
```

### Step A6: Present and Confirm Changes

Present the full change set before writing anything.

**Additive changes** (single grouped list, organized by target file):

```
## Proposed Additive Changes

### profile/candidate.md
- [ ] New certification: [title], [issuer], [date] - extracted from LinkedIn
- [ ] New independent project: [PROJECT_NAME] - [description, tech stack, key outcome]
- [ ] New reference: [name, title, company]
  Quote: "[relevant quote]"

### profile/behavioral.md
- [ ] New behavioral observation [labeled as inference]: "[phrase]"

[and so on per file]
```

Then ask:

> **Apply all additive changes?** These add new content without touching anything already in the files.
> Reply **yes** to apply all, or list the numbers you want to skip.

Wait for the response. Apply only the confirmed items.

**Conflicting changes** (one at a time):

```
## Conflict 1 of [N]: Job title - [COMPANY]

**Current in profile/candidate.md:**
[TITLE_A] - [COMPANY] ([START]-[END])

**Proposed (from LinkedIn export):**
[TITLE_B] - [COMPANY] ([START]-[END])

Options:
  [keep] Keep the existing text
  [replace] Replace with the version from the document
  [manual] I'll edit this myself - skip for now
```

Wait for the user's choice on each conflict. If no conflicts, state "No conflicting changes found." and skip this section.

### Step A7: Write Confirmed Changes and Fill Gaps

Apply the confirmed changes with the herramienta de edición de archivos. Make targeted edits only. Do not rewrite entire files. State which changes were applied per file. If a file has no confirmed changes, state "No changes made to [filename]."

Documents cover skills, experience, education, references, and behavioral signal. They do not cover everything `preparación de postulación` and `búsqueda de empleos` need. After the writes, ask follow-up questions for gaps:

- Career goals and target role types
- What excites the user in their next role
- Deal-breakers and must-haves
- Languages you work in professionally, with proficiency levels (only if not already extracted from `cv/` or `linkedin/` above) - this feeds the Language Gate in `04-job-evaluation.md`, so ask directly rather than skipping it
- Salary expectations (optional): amount, ARS/USD if stated, period, gross/net and arrangement; no automatic conversion.
- Commute or location constraints (if not visible from CV)
- Job search configuration (use the questions from Path C Section 9 below)

Then proceed to Step 3 to finish the personal profile files only. Shared skills and templates remain unchanged.

---

## Path B: Single CV Import

If the user provides a single CV/resume:

1. Read the document thoroughly.
2. Extract all structured information: name, contact, education, experience, skills, languages, publications, awards.
3. Present a summary of what was extracted.
4. Ask follow-up questions for gaps (behavioral profile, career goals, deal-breakers, languages and proficiency levels if not already extracted, salary expectations, references).
5. Proceed to Step 3 (file generation).

---

## Path C: Interview Mode

Walk through each section conversationally. Ask questions naturally, not as a form. Let the user answer in their own words and you'll structure the data.

### Section 1: Identity & Contact
Ask about:
- Full name
- Location (city, country)
- Phone, email, LinkedIn, GitHub
- What languages they work in professionally, and roughly what level in each (native, fluent, conversational, a CEFR letter like B2 - whatever's natural for them to describe, doesn't need to be precise). Worth explaining why: a posting requiring a language they don't list at all gets auto-excluded later by the Language Gate, while one asking for a higher level in a language they do list gets flagged for their own judgment instead of silently passed or rejected - so it's worth being honest here rather than optimistic.
- Current employment status
- Relevant availability/time-zone constraints; commute only if the accepted modality requires it. Do not collect family details as a default.

### Section 2: Education
For each degree:
- Level (PhD, MSc, BSc, etc.), field, institution, years
- Thesis topic (if applicable)
- Key coursework or topics

Also ask about certifications (online courses, professional certs).

### Section 3: Professional Experience
For each role (most recent first):
- Job title, company, dates, location
- Key responsibilities (3-5 bullets)
- Key achievements or projects
- Technologies/tools used

Also ask about independent projects, freelance work, or side projects.

### Section 4: Technical Skills
- Programming languages + proficiency level
- ML/AI frameworks and tools
- Domain expertise
- Software tools and platforms
- Any other technical skills

### Section 5: Publications & Awards (optional)
- Peer-reviewed papers, conference presentations
- Hackathons, competitions, awards
- Skip if not applicable

### Section 6: Behavioral Profile (optional)
If they have a formal assessment (PI, DISC, Myers-Briggs, StrengthsFinder):
- Ask them to describe or share the results

If not, ask behavioral questions:
- "What work environments do you thrive in?"
- "What drains your energy at work?"
- "How do you prefer to work in teams?"
- "How do you make decisions, quickly or deliberately?"
- "What's your communication style?"
- Synthesize answers into a behavioral profile

### Section 7: Career Goals & Preferences
- Target roles and industries
- What excites you in work
- Deal-breakers and must-haves
- Salary expectations (optional): amount, currency, period, gross/net and arrangement.
- What environments to avoid
- Commute/location constraints

### Section 8: References (optional)
For each reference:
- Name, title, company, email, phone
- Relationship to the user

### Section 9: Job Search Configuration
This section generates the search queries that power `búsqueda de empleos`. Use the information from Sections 1, 4, and 7 to build targeted queries.

Ask about:
- **Role titles to search for:** Job titles for the same underlying work vary a lot across companies and markets - a "Data Scientist" role at one employer may be called "Insights Analyst" or "Data Consultant" at another. Ask about the function first: "What kind of work do you actually want to be doing day-to-day?" Then translate that into concrete search terms: "Given that, what job titles should I search for? For example: Desarrollador Backend, Desarrollador Frontend, Ingeniero de Software." Collect 3-8 specific titles, but keep the underlying function in mind - it feeds the category naming in `search-queries.md` and the Experience Match dimension in `04-job-evaluation.md`.
- **Key skills as search terms:** "Which of your skills are most likely to appear in job postings?" Pick 3-5 that are distinctive and searchable.
- **Target companies (optional):** "Are there specific companies you'd like to monitor for openings?"
- **Geographic scope:** "Which cities or regions should I search in? How far are you willing to commute?" Use this to define the location filter tiers (ideal, acceptable, borderline, too far).
- **Portales:** revisar config/portales-argentina.json y references/portales.md del skill de entrada. Mantener deshabilitados los portales CLI que lo estén; no habilitar LinkedIn ni mercados ajenos como parte del onboarding. El catálogo y las preferencias técnicas no se personalizan aquí.
- **Idioma del CV:** español predeterminado editable. Registrar la preferencia documental en profile/candidate.md; preguntar idiomas laborales y niveles por separado. No inferir inglés o español nativo.

**Important:** Also suggest role types the user may not have considered, based on their skill profile. For example:
- If they have strong Python + domain expertise: "Have you considered roles like 'Technical Consultant' or 'Solutions Engineer' in your domain?"
- If they have ML + a specific industry: "Companies in adjacent industries also hire for these skills. Should I include searches for [adjacent sector]?"
- If they have project management experience alongside technical skills: "Would you also want to search for 'Technical Project Manager' or 'Team Lead' roles?"

This proactive suggestion step helps users discover career paths they might not have considered.

---

## Step 3: Write Personal Files Only

Aplicá solo hechos confirmados, sin sustituir desconocidos por ejemplos. Reutilizá los archivos existentes y realizá cambios dirigidos; no dupliques filas o proyectos al repetir una importación.

1. profile/candidate.md: única biografía, contacto, trayectoria, estudios, proyectos, habilidades e idiomas con niveles. Registrar procedencia y fecha de cada importación; separar hecho de inferencia. Las preferencias actuales de roles, modalidad, lugar, disponibilidad, expectativas y lenguaje documental se guardan aquí sin copiar la biografía a otro archivo.
2. profile/behavioral.md, opcional: assessment real o preferencias declaradas. Observaciones inferidas se marcan como inferencias pendientes de revisión; no inventar puntajes.
3. profile/writing-style.md, opcional: patrones personales respaldados por al menos dos cartas previas, frases/encuadres para CV y cartas y referencias de procedencia. Una frase adaptada no demuestra hechos; volver a contrastarlos con candidate.md al usarla.
4. profile/evaluation.md, opcional: prioridades, fortalezas/dificultades para evaluar y calibración desde resultados reales. Mantener pesos y gates compartidos de 04; no interpretar un rechazo aislado como falta de habilidad.
5. profile/interview.md, opcional: STAR confirmados y stubs con fuente y huecos explícitos. No completar resultados o responsabilidades inventados.

Generá consultas desde las preferencias del perfil siguiendo .agents/skills/job-scraper/search-queries.md, sin editar esa estrategia pública. Se pueden conservar consultas personales en profile/evaluation.md si aportan valor. No escribir datos en los archivos 03–09, template.json, cv/main_example.tex ni ejemplos de cartas.

Los caminos A, B y C convergen aquí. Si Path A ya aplicó una modificación confirmada, no escribirla otra vez. La ausencia de un dato opcional no bloquea lo demás; un dato imprescindible para un CV final queda pendiente y se informa.

## Step 4: Confirm & Next Steps

Presentá cambios por archivo, fuentes usadas, conflictos resueltos y datos pendientes. No declares perfil completo si faltan trayectoria, tecnologías, idiomas o contacto necesario. Los datos quedan locales bajo profile/ y documents/, ignorados por Git; no se incluyen en la exportación pública.

Ofrecé las acciones pertinentes en lenguaje natural: buscar opciones, evaluar un aviso, preparar materiales o completar STAR. No generar un CV con contactos ficticios ni pedir que use un comando slash. Una búsqueda amplia puede avanzar con criterios confirmados aunque el ajuste personal definitivo siga pendiente.

## Design Principles

- Importación idempotente: leer antes de escribir, combinar sin duplicar, aclarar contradicciones.
- No confundir el idioma de un aviso o de la conversación con idiomas laborales.
- Leer y transcribir documentos/audio solo mediante capacidades disponibles; pedir texto/CV cuando una fuente no pueda inspeccionarse.
- Las preferencias personales no alteran automáticamente reglas compartidas, portales o plantillas.
- Lo que el usuario confirme en conversación llega al perfil en el mismo trabajo; no queda solo en un borrador.
