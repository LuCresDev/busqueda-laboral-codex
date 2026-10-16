# preparación de entrevista - Prepare for an Interview on a Tracked Application

Workflow de Codex en lenguaje natural. Las opciones se extraen del pedido; las etiquetas de flujo no son comandos slash ni de consola. Rutas desde raíz; leer archivos personales opcionales solo si existen. Usar capacidades realmente disponibles y mantener las reglas de AGENTS.md.

You are preparing the user for a real, scheduled interview on one of their applications. The frameworks for this already exist - `07-interview-prep.md` (STAR examples, tough questions, questions to ask, roleplay protocol) and the Company Research Checklist in `04-job-evaluation.md` - and the `seguimiento` archive records which stage the user is at and what earlier stages surfaced. This command wires them together into a stage-specific prep pack and an optional mock interview.

`preparación de postulación` optimizes what the company reads; `preparación de entrevista` optimizes what the company hears. The bridge between them is consistency: the interviewer has read the submitted CV and cover letter, so everything prepared here must match what those documents claim.

Follow these steps **in order**.

---

## Step 0: Parse Input

`datos del pedido` may contain a company name (optionally with a role), e.g. `preparación de entrevista acme`.

- **With an argument:** match against `job_search_tracker.csv` rows (case-insensitive on company, then role). One match → proceed. Several → list and ask. None → this application isn't tracked; suggest `seguimiento <company>` to register it first, or accept the posting and role details directly if the user wants to prep anyway.
- **Without an argument:** list tracker rows whose status suggests a live process — an open status per the **Tracker status vocabulary** in `seguimiento` (`interview`, `offer`, or recently `applied`; `drafted` is open but nothing was sent, so it never qualifies) — and ask which one. If the tracker is empty, ask for the company, role, and posting.

Prefer the real application's context when available. If the user requests generic practice, agree a target role and label the simulation hypothetical; do not invent a company, interview invitation, tracked application or candidate experience.

---

## Step 1: Load the Application Context

1. **The archive** (started by `preparación de postulación`, maintained by `seguimiento`): derive `<company>_<role>` by the **Subfolder naming** rule in `documents/README.md`, then use `documents/applications/<company>_<role>/`.
   - `job_posting.md` - the exact posting the user applied to
   - `cv_draft.<source-extension>` and `cover_letter.<source-extension>` with the submitted PDFs - what was actually submitted. Use `.json` for the active Argentina templates and accept legacy `.tex`; read the tracker/archive to resolve actual filenames, never assume the current template was used for an older application. **These are what the interviewer read**; every talking point must be consistent with their claims.
   - `outcome.md` - the stage reached so far and any recorded feedback from earlier stages. Feedback from stage N is the highest-value input for stage N+1 prep.
2. **Fallbacks** (the application may predate `seguimiento`): posting via lector web disponible on the tracker row's `source` URL, or ask the user to paste it; CV via `cv/main_<company>_<role>.*` and cover letter via `cover_letters/cover_<company>_<role>.*`, deriving `<company>_<role>` by the **Subfolder naming** rule in `documents/README.md`. **Never widen those globs to the company alone**: with two roles at one company it would prep you from the sibling role's documents. State plainly which context is missing rather than guessing - and suggest `seguimiento <company>` to build the archive for next time.
3. **Ask the user what this interview is** (skip anything `outcome.md` already records): stage, date, time zone, stated format/platform, agreed interview language, and interviewer names/titles when known. For a remote search, do not introduce onsite attendance unless the actual invitation requires it; flag any conflict with the user's confirmed preferences.
4. **Read the frameworks once** - do not re-read them in later steps:
   - `.agents/skills/job-application-assistant/07-interview-prep.md`
   - `profile/candidate.md`
   - `profile/behavioral.md` and `profile/interview.md` (optional; unknown if missing)
   - `.agents/skills/job-application-assistant/04-job-evaluation.md`

---

## Step 2: Research the Company (Interview-Focused)

**First, check the cache**: read `company_research/<normalized-company-name>.json` per the Company Research Cache section in `04-job-evaluation.md` (normalize the company name the same way). If it exists and is within the documented TTL, start from it instead of researching from scratch — `preparación de postulación` may already have populated it for this same application. The verification rule below still applies regardless of source.

If the cache is missing or stale, execute the Company Research Checklist that `04-job-evaluation.md` defines: company website (mission, values, recent news), review sites, LinkedIn (team size, recent hires), and media coverage (growth, restructuring, workplace issues). Afterward, write (or overwrite) the cache file with the fresh findings per the schema in `04-job-evaluation.md`, so a later `preparación de postulación` or `preparación de entrevista` run for the same company can reuse them.

Additions for interview purposes:

- **Interviewer angle:** if interviewer names are known (from Step 1 or the tracker's `contact_person`), look up their public professional profile. A hiring manager probes team fit and motivation; a senior engineer probes technical depth; HR probes the CV timeline. Note the likely angle per interviewer - do not speculate beyond public information.
- **Conversation hooks:** 2-3 recent, verifiable company specifics (a product launch, a stated strategic priority) the user can reference naturally in answers and in the "why this company" moment.

**Verify before using:** every company claim that will appear in the prep pack must be independently confirmed via lector web disponible/búsqueda web disponible - same rule the repo applies to cover-letter claims. An unverified "fact" delivered confidently in an interview is worse than no fact. On a 403, retry with browser headers per `.agents/skills/job-application-assistant/09-web-research.md` rather than dropping to search snippets; a snippet is a lead, not a source.

---

## Step 3: Build the Prep Pack

Assemble a stage-appropriate prep document with these sections:

### 1. Likely questions
Derive from four sources, in priority order:
1. **Recorded feedback from earlier stages** (`outcome.md`) - anything flagged, doubted, or left unresolved will come back
2. **The fit evaluation's gaps** - the requirements where the profile is weakest are the likeliest probes. For each, prepare an honest bridge answer per `07`'s "You don't have [X]" pattern: acknowledge, connect adjacent experience, show the learning path. **Never prepare an answer that invents experience.**
3. **The posting's stated requirements** - competency by competency
4. **The stage type** - phone screens get motivation and timeline questions; technical rounds get the posting's stack; final rounds get values, salary, and "any reservations" questions

### 2. STAR answer mapping
Match the confirmed personal STAR examples in `profile/interview.md` to the likely questions using their "Use for" tags. Then:
- For likely questions **no existing STAR example covers**, draft a new STAR answer grounded strictly in facts from `profile/candidate.md` - profile facts arranged into S/T/A/R, not embellished. Include these drafts in the prep pack; offer to append them to `profile/interview.md` only if the user explicitly approves.
- If `onboarding` left incomplete STAR stubs relevant to this role, surface them: the user should fill in the details before the interview.

### 3. Consistency brief
A short list of the specific claims the submitted CV and cover letter make (achievements, numbers, skills emphasized) that the interviewer is most likely to probe. The rule stated plainly: **no claim in the room that isn't on the paper, and every claim on the paper must be defensible in depth.**

### 4. Tough questions, customized
The relevant entries from `07`'s tough-question list with per-application answers - "Why this company specifically?" must use the verified hooks from Step 2, never a generic line.

### 5. Questions to ask
Pick 4-6 from `07`'s categories, customized to the research and the stage: role and team questions at screens, tech and growth questions at technical rounds, culture and leadership questions by the final round (that is the last chance to detect a deal-breaker). Cut any question the research already answers publicly - asking it signals you didn't look.

### 6. Logistics
The phone/video tips from `07` when the format calls for them, plus date and interviewer names as a header.

Save the pack in the archive folder derived in Step 1 as `interview_prep_<stage>.md` (create the folder if this application predates `seguimiento`). The folder is gitignored, so the pack stays personal; one file per stage, so earlier packs remain as history. Present the pack in chat as well - the file is the artifact, the conversation is the delivery.

---

## Step 4: Offer a Mock Interview

Ask if the user wants to practice. If yes, run the roleplay **in this conversation** following the Roleplay Guidelines in `07-interview-prep.md` exactly: warm-up first, then role-specific technical questions, 1-2 behavioral questions tied to the posting's competencies, and one tough question or curveball. After each answer, give brief feedback - what worked, what to sharpen, and which STAR example from the pack would have served better.

Calibrate feedback against `profile/behavioral.md`: coach toward the user's natural register, not a generic ideal - the same voice-consistency rule the `preparación de postulación` reviewer applies to cover letters.

---

## Step 5: Close the Loop

End with:

> Good luck. After the interview, run `seguimiento <company>` to log the stage and any feedback - it sharpens the prep for the next round, and once the process resolves it feeds your fit-framework calibration via `onboarding`.

If Step 3 drafted new STAR answers the user approved for keeps, remind them those were appended to `profile/interview.md` (or offer again if they deferred).

---

## Important Rules

1. **Consistency with the submitted documents.** The interviewer read the archived CV and cover letter; prep must never contradict them or coach claims beyond them.
2. **Honesty on gaps.** Weak matches get bridge answers (acknowledge → adjacent experience → learning path), never invented experience. Same rule as everywhere else in this repo.
3. **Verified research only.** Company specifics go in the pack only after independent confirmation. Interviewer notes stick to public professional information.
4. **Stage-appropriate prep.** A phone screen pack and a final-round pack are different documents; recorded feedback from earlier stages takes priority over generic question lists.
5. **Write the prep pack to the application archive; personal updates stay under profile/.** The prep pack lands in the archive folder derived in Step 1; framework files are not edited; personal STAR examples belong only to `profile/interview.md` on explicit request.

   **The exception is `profile/candidate.md`.** Interview prep is where new facts surface most often: the user recalls a metric, corrects a scope, or fills in a STAR stub. When that happens, write the fact into the profile, as well as putting it in the prep pack. A fact recorded only in prep material reads as unsupported to a later drafting session and gets stripped from CVs as a fabrication. Prep files are not a substitute for the profile.
