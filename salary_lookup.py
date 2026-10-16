#!/usr/bin/env python3
"""
Consulta opcional de datos salariales aportados por el usuario

Looks up company salary data from a user-provided dataset.
Supports any salary data source — union statistics, Glassdoor exports,
manually collected benchmarks, etc.

This tool requires a data file (salary_data.json) that you create
from your own salary data. See tools/README_SALARY_TOOL.md for
instructions on the expected format and how to convert from Excel.

Usage:
    python salary_lookup.py "Company Name"
    python salary_lookup.py "Empresa Ficticia SRL" --city "Córdoba"
    python salary_lookup.py "Company Name" --json
    python salary_lookup.py --list-all
"""

import json
import sys
import re
import argparse
import unicodedata
import math
from datetime import date
from copy import deepcopy
from pathlib import Path

DATA_FILE = Path(__file__).parent / "salary_data.json"

# Compatibilidad de transliteración con datasets Unicode históricos.
SPELLING_VARIANTS = {
    "ø": "o", "æ": "ae", "å": "aa",
    "ö": "o", "ä": "ae", "ü": "u",
}

# Legal suffixes and noise to strip when matching company names
STRIP_PATTERNS = [
    r"\ba/s\b", r"\baps\b", r"\bi/s\b", r"\bp/s\b", r"\bk/s\b",
    r"\bivs\b", r"\bamba\b", r"\ba\.m\.b\.a\.?\b",
    r"\(vg\)", r"\(.*?\)",  # (VG) and other parentheticals
    r"\bgroup\b", r"\bholding\b",
    r",\s*.*$",  # everything after comma (sub-entities)
    r"(?:\s|^)(?:s\.?\s*a\.?\s*s\.?|s\.?\s*r\.?\s*l\.?|s\.?\s*a\.?)(?:\s*)$",
]

AMOUNT_CONTEXT = ("currency", "pay_basis", "period", "source", "as_of")
PERIOD_LABELS = {"month": "mensual", "year": "anual", "hour": "por hora", "week": "semanal", "day": "diario"}


def salary_context(category, metadata=None):
    """Keep absolute salary units/source with each value; never infer or convert."""
    metadata = metadata or {}
    return {key: category.get(key, metadata.get(key)) for key in AMOUNT_CONTEXT}


def results_with_context(results, metadata=None):
    """Preserve the legacy JSON array while making new amount rows self-contained."""
    results = deepcopy(results)
    for entry in results:
        for category in (entry.get("categories") or {}).values():
            if "amount" in category:
                category.update(salary_context(category, metadata))
    return results


def _fold_accents(text):
    # Retain historical Nordic transliteration choices (å -> aa, æ -> ae).
    text = unicodedata.normalize("NFC", text).casefold()
    return "".join(char if char in SPELLING_VARIANTS else "".join(
        part for part in unicodedata.normalize("NFKD", char) if not unicodedata.combining(part)
    ) for char in text)


def fail_data_error(message):
    """Exit with a user-facing salary data setup error."""
    print(f"Error: invalid salary_data.json: {message}", file=sys.stderr)
    print("", file=sys.stderr)
    print("See tools/README_SALARY_TOOL.md for the expected format.", file=sys.stderr)
    sys.exit(1)


def collect_validation_issues(data):
    """Return (errors, warnings) for the salary data shape.

    errors   -> hard problems that make lookups crash or emit wrong output
                (these cause validate_data() to exit(1)).
    warnings -> usability concerns that still work (e.g. duplicate company
                names); --validate reports them but exits 0.
    """
    errors = []
    warnings = []

    if not isinstance(data, dict):
        errors.append("top-level JSON value must be an object")
        return errors, warnings

    metadata = data.get("metadata", {})
    if metadata is not None and not isinstance(metadata, dict):
        errors.append("'metadata' must be an object when provided")

    companies = data.get("companies")
    if not isinstance(companies, list):
        errors.append("'companies' must be a list")
        return errors, warnings

    seen_companies = {}
    for index, entry in enumerate(companies, start=1):
        if not isinstance(entry, dict):
            errors.append(f"companies[{index}] must be an object")
            continue

        company = entry.get("company")
        if not isinstance(company, str) or not company.strip():
            errors.append(f"companies[{index}].company must be a non-empty string")
        else:
            key = company.lower()
            if key in seen_companies:
                warnings.append(
                    f"Duplicate company name '{company}' "
                    f"(companies[{seen_companies[key]}] and companies[{index}])"
                )
            else:
                seen_companies[key] = index

        city = entry.get("city")
        if city is not None and not isinstance(city, str):
            errors.append(f"companies[{index}].city must be a string when provided")

        categories = entry.get("categories", {})
        if categories is not None and not isinstance(categories, dict):
            errors.append(f"companies[{index}].categories must be an object when provided")
        elif categories:
            for cat_label, cat_data in categories.items():
                if not isinstance(cat_data, dict):
                    errors.append(
                        f"companies[{index}].categories.{cat_label} must be an object "
                        f"with 'count' and/or 'index' (got {type(cat_data).__name__})"
                    )
                    continue
                count = cat_data.get("count")
                if count is not None and not isinstance(count, (int, float)):
                    errors.append(
                        f"companies[{index}].categories.{cat_label}.count must be a "
                        f"number (got {type(count).__name__})"
                    )
                index_val = cat_data.get("index")
                if index_val is not None and not isinstance(index_val, (int, float, str)):
                    errors.append(
                        f"companies[{index}].categories.{cat_label}.index must be a "
                        f"number or string (got {type(index_val).__name__})"
                    )
                if "amount" in cat_data:
                    where = f"companies[{index}].categories.{cat_label}"
                    amount = cat_data["amount"]
                    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
                        errors.append(f"{where}.amount must be a finite non-negative number")
                    if index_val is not None:
                        errors.append(f"{where}: amount and index are different metrics; use separate categories")
                    context = salary_context(cat_data, metadata if isinstance(metadata, dict) else {})
                    if not isinstance(context["currency"], str) or not re.fullmatch(r"[A-Z]{3}", context["currency"]):
                        errors.append(f"{where}.currency must be an explicit three-letter code such as ARS or USD")
                    if not isinstance(context["pay_basis"], str) or context["pay_basis"] not in {"gross", "net"}:
                        errors.append(f"{where}.pay_basis must be gross or net (bruto/neto)")
                    if not isinstance(context["period"], str) or context["period"] not in PERIOD_LABELS:
                        errors.append(f"{where}.period must be month, year, hour, week or day")
                    if not isinstance(context["source"], str) or not context["source"].strip():
                        errors.append(f"{where}.source must name the supplied source")
                    try:
                        if not isinstance(context["as_of"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", context["as_of"]):
                            raise ValueError("date required")
                        date.fromisoformat(context["as_of"])
                    except ValueError:
                        errors.append(f"{where}.as_of must be a real date YYYY-MM-DD")

    return errors, warnings


def validate_data(data):
    """Validate the salary data shape before lookups use it.

    Preserves historical behavior: exits(1) on the first hard error with the
    same user-facing message, and returns data unchanged when valid.
    """
    errors, _ = collect_validation_issues(data)
    if errors:
        fail_data_error(errors[0])
    return data


def read_raw_data():
    """Load and JSON-parse salary_data.json; exit with a helpful message if missing/invalid."""
    if not DATA_FILE.exists():
        print("Error: salary_data.json not found.", file=sys.stderr)
        print("", file=sys.stderr)
        print("This tool requires a salary data file.", file=sys.stderr)
        print("See tools/README_SALARY_TOOL.md for setup instructions.", file=sys.stderr)
        print("", file=sys.stderr)
        print("If you don't have salary data, the salary lookup", file=sys.stderr)
        print("step will be skipped during /apply.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        fail_data_error(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    return data


def load_data():
    """Load, parse, and validate salary_data.json for lookups."""
    return validate_data(read_raw_data())


def normalize(s):
    """Normalize string for robust fuzzy matching."""
    s = _fold_accents(s).strip()
    for pat in STRIP_PATTERNS:
        s = re.sub(pat, "", s)
    s = "".join(char for char in s if char.isalnum())
    return s.strip()


def anglicize(s):
    """Convert Danish/Nordic characters to anglicized equivalents."""
    s = _fold_accents(s)
    for danish, english in SPELLING_VARIANTS.items():
        s = s.replace(danish, english)
    return s


def extract_core_words(s):
    """Extract meaningful words from a company name, ignoring noise."""
    s = _fold_accents(s)
    for pat in STRIP_PATTERNS:
        s = re.sub(pat, "", s)
    words = re.findall(r"[^\W_]+", s)
    return [w for w in words if len(w) > 1]


def match_score_optimized(q_norm, q_ang, q_words_set, q_words_ang_set, query, entry_name):
    """Compute a match score between 0 and 100 using precalculated query values."""
    n_norm = normalize(entry_name)

    if not q_norm or not n_norm:
        return 0

    if q_norm == n_norm:
        return 100

    if q_norm in n_norm:
        ratio = len(q_norm) / len(n_norm)
        if len(q_norm) <= 4 and ratio < 0.5:
            n_words = set(extract_core_words(entry_name))
            if not q_words_set & n_words:
                pass
            else:
                return 80 + int(ratio * 10)
        else:
            return 80 + int(ratio * 10)
    if n_norm in q_norm:
        ratio = len(n_norm) / len(q_norm)
        if len(n_norm) <= 4 and ratio < 0.5:
            pass
        else:
            return 80 + int(ratio * 10)

    n_ang = anglicize(n_norm)
    if q_ang == n_ang:
        return 85
    if q_ang in n_ang or n_ang in q_ang:
        shorter = min(len(q_ang), len(n_ang))
        longer = max(len(q_ang), len(n_ang))
        if shorter <= 4 and shorter / longer < 0.5:
            n_words_ang = {anglicize(w) for w in extract_core_words(entry_name)}
            if q_words_ang_set & n_words_ang:
                return 75
        else:
            return 75

    n_words = set(extract_core_words(entry_name))
    if not q_words_set or not n_words:
        return 0

    overlap = q_words_set & n_words
    if not overlap:
        n_words_ang = {anglicize(w) for w in n_words}
        overlap = q_words_ang_set & n_words_ang

    if overlap:
        if len(q_words_set) == 1:
            q_word = list(q_words_set)[0]
            if q_word in n_words or anglicize(q_word) in {anglicize(w) for w in n_words}:
                return 70
            else:
                return 0

        coverage = len(overlap) / len(q_words_set)
        return int(30 + coverage * 40)

    return 0


def match_score(query, entry_name):
    """Compute a match score between 0 and 100 for ranking results."""
    q_norm = normalize(query)
    q_ang = anglicize(q_norm)
    q_words = extract_core_words(query)
    q_words_set = set(q_words)
    q_words_ang_set = {anglicize(w) for w in q_words}
    return match_score_optimized(q_norm, q_ang, q_words_set, q_words_ang_set, query, entry_name)


def search_company(data, query, city=None):
    """Search for a company by name. Returns matching entries sorted by relevance."""
    companies = data.get("companies", [])
    scored = []

    # Pre-calculate query representations once to avoid redundant computations inside the loop
    q_norm = normalize(query)
    q_ang = anglicize(q_norm)
    q_words = extract_core_words(query)
    q_words_set = set(q_words)
    q_words_ang_set = {anglicize(w) for w in q_words}

    for entry in companies:
        if city:
            city_lower = city.lower()
            entry_city = (entry.get("city") or "").lower()
            if city_lower not in entry_city and anglicize(city_lower) not in anglicize(entry_city):
                continue

        score = match_score_optimized(q_norm, q_ang, q_words_set, q_words_ang_set, query, entry["company"])
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: (-x[0], x[1]["company"]))

    min_score = 30
    return [entry for score, entry in scored if score >= min_score]


def format_entry(entry, metadata):
    """Format a single company entry for display."""
    # `metadata` and `entry["categories"]` may be an explicit null: --validate
    # treats a null the same as an omitted key ("...must be an object when
    # provided"), but dict.get(key, default) only substitutes the default for an
    # absent key, so a null reached `.get()`/`[]` here and crashed the lookup.
    metadata = metadata or {}
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  {entry['company']}")
    if entry.get("city"):
        lines.append(f"  Location: {entry['city']}")
    lines.append(f"{'='*60}")

    # Get category data (everything except company/city fields).
    categories = entry.get("categories") or {}
    if not categories:
        # Fallback: treat any numeric fields as categories
        skip_keys = {"company", "city", "categories"}
        for key, value in entry.items():
            if key not in skip_keys and isinstance(value, dict):
                categories[key] = value

    if categories:
        amounts = {label: values for label, values in categories.items() if "amount" in values}
        for label, values in amounts.items():
            context = salary_context(values, metadata)
            basis = {"gross": "bruto", "net": "neto"}.get(context["pay_basis"], "base pendiente")
            period = PERIOD_LABELS.get(context["period"], "período pendiente")
            lines.append(f"  {label.replace('_', ' ').title()}: {values['amount']:,.2f} {context['currency'] or 'moneda pendiente'} {basis}, {period}")
            lines.append(f"    Fuente: {context['source'] or 'pendiente'} | Fecha del dato: {context['as_of'] or 'pendiente'}")
        categories = {label: values for label, values in categories.items() if "amount" not in values}
        if not categories:
            lines.append("  Solo datos aportados; sin conversión de moneda, actualización automática ni referencia de mercado.")
            return "\n".join(lines)
        index_label = metadata.get("index_label", "Index")
        baseline = metadata.get("index_baseline", 100)

        lines.append(f"  {'Category':<22} {'Count':>6} {index_label:>8}  {'vs Baseline':>10}")
        lines.append(f"  {'-'*50}")

        suppressed = False  # did any row render its index as N/A*?
        for label, data in categories.items():
            display_label = label.replace("_", " ").title()
            count = data.get("count")
            index = data.get("index")
            if count is not None or index is not None:
                count_str = str(count) if count is not None else "-"
                if isinstance(index, (int, float)):
                    index_str = f"{index:.1f}"
                    if baseline == 0:
                        diff_str = ""
                    else:
                        diff_pct = ((index - baseline) / baseline) * 100
                        sign = "+" if diff_pct >= 0 else ""
                        diff_str = f"{sign}{diff_pct:.1f}%"
                elif index is not None:
                    index_str = str(index)
                    diff_str = ""
                elif "index" in data:
                    index_str = "N/A*"
                    diff_str = ""
                    suppressed = True
                else:
                    index_str = "-"
                    diff_str = ""
                lines.append(f"  {display_label:<22} {count_str:>6} {index_str:>8}  {diff_str:>10}")

        # The footnote explains the N/A* marker; printing it under a table with
        # no such row asserts a privacy suppression that did not happen.
        lines.append("")
        if suppressed:
            lines.append("  * N/A = Too few employees to publish (privacy)")
        if metadata.get("baseline_description"):
            lines.append(f"  {metadata['baseline_description']}")
        else:
            lines.append(f"  {index_label} {baseline} = baseline")
    else:
        # Simple format: just show all non-standard fields
        skip_keys = {"company", "city", "categories"}
        for key, value in entry.items():
            if key not in skip_keys:
                display_key = key.replace("_", " ").title()
                lines.append(f"  {display_key}: {value}")

    return "\n".join(lines)


def print_validation_report(errors, warnings):
    """Print an actionable validation report. Returns the process exit code."""
    if not errors and not warnings:
        print("OK - no issues found.")
        return 0
    print(f"Found {len(errors) + len(warnings)} issue(s):")
    if errors:
        print("  Errors:")
        for i, msg in enumerate(errors, start=1):
            print(f"    [{i}] {msg}")
    if warnings:
        print("  Warnings:")
        for i, msg in enumerate(warnings, start=1):
            print(f"    [{i}] {msg}")
    if errors:
        print("")
        print("Fix the errors above, then re-run. See tools/README_SALARY_TOOL.md "
              "for the expected format.")
        return 1
    return 0


def _force_utf8_output() -> None:
    """Write UTF-8 whatever the host's default encoding is.

    A piped stdout on Windows defaults to the ANSI code page (cp1252 on most
    Western installs), so printing a company, title or file name outside it
    raised UnicodeEncodeError before the workflow saw any output.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)  # absent on a StringIO under test
        if reconfigure:
            reconfigure(encoding="utf-8")


def main():
    _force_utf8_output()
    parser = argparse.ArgumentParser(description="Consulta salarial sobre tu propio dataset; sin cotizaciones ni estimaciones de mercado")
    parser.add_argument("company", nargs="?", help="Empresa que querés buscar")
    parser.add_argument("--city", help="Filtrar por ciudad")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list-all", action="store_true", help="List all companies")
    parser.add_argument("--validate", action="store_true",
                        help="Validate salary_data.json and print a report, then exit")
    args = parser.parse_args()

    if args.validate:
        data = read_raw_data()
        errors, warnings = collect_validation_issues(data)
        print(f"Validating {DATA_FILE.name} ...")
        print("")
        sys.exit(print_validation_report(errors, warnings))

    data = load_data()
    metadata = data.get("metadata", {})
    companies = data.get("companies", [])

    if args.list_all:
        for entry in companies:
            city = entry.get("city", "")
            city_str = f" ({city})" if city else ""
            print(f"{entry['company']}{city_str}")
        return

    if not args.company:
        parser.print_help()
        sys.exit(1)

    results = search_company(data, args.company, args.city)

    if not results:
        print(f"No se encontraron datos para '{args.company}'")
        if args.city:
            print(f"  (filtro de ciudad: {args.city})")
        print("\nProbá un nombre más corto. Las empresas del dataset")
        print("pueden contener tildes o formas legales como SA, SRL o SAS.")
        sys.exit(1)

    if args.json:
        print(json.dumps(results_with_context(results, metadata), ensure_ascii=False, indent=2))
    else:
        print(f"\nCoincidencias en los datos aportados para '{args.company}': {len(results)}")
        for entry in results:
            print(format_entry(entry, metadata))
        print()


if __name__ == "__main__":
    main()
