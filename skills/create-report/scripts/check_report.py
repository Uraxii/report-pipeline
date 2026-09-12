#!/usr/bin/env python3
"""Diffs a report's deviations block and format-elements note against its
sibling scoreboard, <report-name>.checks.md.

Design: .nikki-agents/deviations-mechanism-design.md.
Run: python3 <this-skill-directory>/scripts/check_report.py <report.md> <materials-dir>
Self-test: python3 <this-skill-directory>/scripts/check_report.py --selftest

Every verdict on the scoreboard is the writer's own; this script re-scores
none of them. It only checks that the scoreboard, the deviations block, the
end matter, the format-elements note and the report's own text agree with
each other.
"""
import difflib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator, NamedTuple, NoReturn

SKILL_DIR = Path(__file__).resolve().parent.parent
# One path segment, not two: the plugin verifier's prefix check reads a bare
# basename as a pointer that no load step can follow.
COLLISIONS = SKILL_DIR / "references/collisions.md"
CHECK_COUNT = 23
# ponytail: difflib run-grouping over case- and whitespace-normalized tokens.
# Ceiling: it joins matched runs separated by insertions of up to
# RUN_GAP_WORDS, so padding a paste with "[sic]" no longer hides it, but a
# rewrite that changes more than that between runs still passes. Real
# paraphrase detection needs semantic matching, which this is not.
VERBATIM_SPAN_WORDS = 40
MIN_RUN_WORDS = 12
RUN_GAP_WORDS = 20
QUESTION_EXEMPT_MAX_WORDS = 80
UNREADABLE_NAMES_SHOWN = 5
SENTENCE_ENDS = (".", "!", "?")

VALID_VERDICTS = ("met", "not-met", "n-a")
ADMISSIBLE_END_MATTER = {"Sources", "Deviations", "Format elements", "Cover letter"}
END_MATTER_SCAN_START = {"Sources", "Deviations", "Format elements"}


class Row(NamedTuple):
    """One scoreboard row, keyed elsewhere by its check number as written."""

    verdict: str
    authoriser: str
    quoted: str
    loses: str


class Entry(NamedTuple):
    """One entry in the report's deviations block."""

    check: str  # "" for a `- Rule ...` entry, which cites no check number
    rest: str


class SpanScan(NamedTuple):
    """What the verbatim-span walk of the materials directory found."""

    compared_count: int
    unreadable_message: str
    span_file: str
    span_side: str
    span_opening: str


def fail(message: str) -> NoReturn:
    sys.exit(f"FAIL: {message}")


def lines_of(path: str | Path) -> Iterator[str]:
    with open(path, encoding="utf-8") as handle:
        yield from handle


# ---- scoreboard ------------------------------------------------------------


def parse_scoreboard(scoreboard: str) -> tuple[str, list[list[str]]]:
    """Reads the format line and every five-cell, digit-numbered table row."""
    fmt = ""
    rows: list[list[str]] = []
    for line in lines_of(scoreboard):
        match = re.match(r"^Format:\s*(.+?)\s*$", line)
        if match:
            fmt = match.group(1)
            continue
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5 or not cells[0].isdigit():
            continue
        rows.append(cells)
    return fmt, rows


def check_row_coverage(rows: list[list[str]], scoreboard: str) -> dict[str, Row]:
    """Every row carries a valid verdict, no check number repeats, and the
    table parsed to at least one row."""
    verdicts: dict[str, Row] = {}
    for number, verdict, authoriser, quoted, loses in rows:
        if verdict not in VALID_VERDICTS:
            fail(f"check {number} verdict is '{verdict}', want met|not-met|n-a")
        if number in verdicts:
            fail(f"scoreboard row for check {number} repeats")
        verdicts[number] = Row(verdict, authoriser, quoted, loses)
    # Zero rows parsed means the table itself didn't parse (e.g. rows missing
    # their leading/trailing pipe) — say that, not "no row for check 1", or the
    # writer goes hunting for a missing row instead of a malformed table.
    if not verdicts:
        fail(
            f"scoreboard has no parseable rows: {scoreboard}\n"
            "Expected a markdown table, one row per check, leading and trailing pipe on\n"
            "every row:\n"
            "| check | verdict | authoriser | quoted rule | reader loses |\n"
            "|---|---|---|---|---|\n"
            "| 1 | met |  |  |  |"
        )
    return verdicts


def check_every_check_scored(verdicts: dict[str, Row]) -> None:
    """Every check 1..CHECK_COUNT has a row."""
    for n in range(1, CHECK_COUNT + 1):
        if str(n) not in verdicts:
            fail(f"scoreboard has no row for check {n}")


# ---- deviations block ------------------------------------------------------


def parse_deviation_entries(report: str) -> list[Entry]:
    """Reads the `- Check N.` / `- Rule ...` entries out of ## Deviations."""
    entries: list[Entry] = []
    in_block = False
    for line in lines_of(report):
        line = line.rstrip("\n")
        if re.match(r"^##\s+Deviations\s*$", line):
            in_block = True
            continue
        if in_block and re.match(r"^##\s", line):
            break
        if not in_block:
            continue
        match = re.match(r"^-\s+(?:Check\s+(\d+)|Rule\s+.+?)\.\s*(.*)$", line)
        if match:
            entries.append(Entry(match.group(1) or "", match.group(2)))
    return entries


def check_entry_count(
    verdicts: dict[str, Row], entries: list[Entry], report: str
) -> None:
    """Count test: not-met rows against deviation entries, zero counts included."""
    not_met = sum(
        1 for n in range(1, CHECK_COUNT + 1) if verdicts[str(n)].verdict == "not-met"
    )
    if not_met != len(entries):
        fail(f"{not_met} checks not met, {len(entries)} deviation entries in {report}")


def check_not_met_fields(verdicts: dict[str, Row]) -> None:
    """Field test: every not-met row carries its three deviation fields."""
    for n in range(1, CHECK_COUNT + 1):
        row = verdicts[str(n)]
        if row.verdict != "not-met":
            continue
        if not row.authoriser:
            fail(f"check {n} is not-met with no authoriser field")
        if not row.quoted:
            fail(f"check {n} is not-met with no quoted rule field")
        if not row.loses:
            fail(f"check {n} is not-met with no reader loses field")


def check_entries_are_scored_not_met(
    verdicts: dict[str, Row], entries: list[Entry]
) -> None:
    """Transcription test: each entry cites a check the scoreboard scores
    not-met. (A row that is not not-met has no quoted rule to transcribe, so
    check 23's "quoted rule does not appear in its entry" is this same test.)"""
    for entry in entries:
        if not entry.check:
            continue
        row = verdicts.get(entry.check)
        verdict = row.verdict if row else "missing"
        if verdict != "not-met":
            fail(
                f"deviations entry cites check {entry.check}, "
                f"scoreboard scores it {verdict}"
            )


# ---- end matter ------------------------------------------------------------


def is_attachment(heading: str) -> bool:
    return heading.startswith("Attachment: ") and len(heading) > len("Attachment: ")


def check_end_matter_types(report: str) -> None:
    """End-matter type test: every heading from the first end-of-body heading
    to EOF is one of the five admissible types. A cover letter sits before the
    body, so it never starts this scan (check 2)."""
    headings = []
    for line in lines_of(report):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(1))

    start = None
    for i, heading in enumerate(headings):
        if heading in END_MATTER_SCAN_START or is_attachment(heading):
            start = i
            break
    if start is None:
        return

    for heading in headings[start:]:
        if heading not in ADMISSIBLE_END_MATTER and not is_attachment(heading):
            fail(f"end-matter item '{heading}' is not an admissible type (check 2)")


# ---- format elements -------------------------------------------------------


def claimed_elements(fmt: str) -> list[str]:
    """The excluded elements references/collisions.md says this format claims."""
    in_table = False
    rows: list[list[str]] = []
    for line in lines_of(COLLISIONS):
        if line.strip() == "## Excluded elements each format claims":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("\n").strip("|").split("|")]
        if len(cells) == 2 and cells[0] not in ("format", "") and not cells[0].startswith("-"):
            rows.append(cells)

    wanted = fmt.strip().lower()
    for formats_cell, elements_cell in rows:
        for token in formats_cell.split(","):
            token = token.strip().lower()
            if wanted == token or wanted.startswith(token):
                if elements_cell.strip().lower() == "none":
                    return []
                return [e.strip().lower() for e in elements_cell.split(";")]
    return []


def named_elements(report: str) -> list[str]:
    """The elements the report's ## Format elements note names."""
    named: list[str] = []
    in_block = False
    for line in lines_of(report):
        line = line.rstrip("\n")
        if re.match(r"^##\s+Format elements\s*$", line):
            in_block = True
            continue
        if in_block and re.match(r"^##\s", line):
            break
        if not in_block or not line.strip():
            continue
        for part in line.split(","):
            part = part.strip().rstrip(".").lower()
            if part:
                named.append(part)
    return named


def check_format_elements(report: str, fmt: str) -> None:
    """Format-elements test: the note names every element the format claims."""
    claims = claimed_elements(fmt)
    if not claims:
        return
    named = named_elements(report)
    missing = [element for element in claims if element not in named]
    if missing:
        fail(
            f"format '{fmt}' claims {len(claims)} excluded elements, "
            f"format-elements note names {len(named)}: missing {', '.join(missing)}"
        )


# ---- verbatim span ---------------------------------------------------------
# Round 5's case 5: a writer scored check 22 "met" on a report carrying 637
# words of pasted source text, and the count test above passed because the
# scoreboard and the (empty) deviations block agreed with each other. Neither
# reads the report. This test does. It walks the materials directory the
# operator named, not the output directory the writer chose, and compares the
# report and its notes file against every file under it for a 40-plus-word
# span (VERBATIM_SPAN_WORDS), whitespace and case normalized. A match is not
# itself a fail — a verbatim clause the operator asked for is a legal report —
# but it must be check 22 not-met with a recorded deviation, the same as any
# other barred fix. An ## Attachment: section gets no exemption: recording the
# deviation is the point even when the paste is the right call.


def read_tokens(path: str) -> list[str] | None:
    """None means the scan could not read this file at all. The caller reports
    those; it never treats them as carrying no source text."""
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (UnicodeDecodeError, OSError):
        return None
    return re.findall(r"\S+", text)


def ngrams(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + size]) for i in range(len(tokens) - size + 1)}


def matched_groups(
    source: list[str], target: list[str]
) -> list[tuple[int, int, int, int, int]]:
    # autojunk=False: SequenceMatcher's default drops any token appearing in
    # more than 1% of a long sequence, which throws away exactly the common
    # words a pasted clause is made of.
    blocks = [
        b
        for b in difflib.SequenceMatcher(
            None, source, target, autojunk=False
        ).get_matching_blocks()
        if b.size >= MIN_RUN_WORDS
    ]
    groups: list[tuple[int, int, int, int, int]] = []
    for b in blocks:
        if groups:
            src_start, src_end, tgt_start, tgt_end, total = groups[-1]
            if b.a - src_end <= RUN_GAP_WORDS and b.b - tgt_end <= RUN_GAP_WORDS:
                groups[-1] = (
                    src_start,
                    b.a + b.size,
                    tgt_start,
                    b.b + b.size,
                    total + b.size,
                )
                continue
        groups.append((b.a, b.a + b.size, b.b, b.b + b.size, b.size))
    return groups


def is_one_question(tokens: list[str], start: int, end: int) -> bool:
    """Check 22 bars session context, chat logs and raw source text. The
    operator's written-out question is none of the three, and the report
    contract requires the report to restate it, so a group that sits inside a
    single interrogative sentence on the source side is not a paste. Any
    sentence end strictly inside the group disqualifies it."""
    for i in range(start, len(tokens)):
        if tokens[i].endswith(SENTENCE_ENDS):
            return i >= end - 1 and tokens[i].endswith("?")
    return False


def scan_for_verbatim_span(report: str, materials: str) -> SpanScan:
    """Compares the report and any notes file against every file under the
    materials root, and returns the first long verbatim span found."""
    unreadable: list[str] = []
    compared_sides = []
    notes_path = report[:-len(".md")] + ".notes.md" if report.endswith(".md") else ""
    for label, path in (("the report", report), ("the report's notes file", notes_path)):
        path = os.path.abspath(path) if path else ""
        if not path or not os.path.isfile(path):
            continue
        tokens = read_tokens(path)
        if tokens is None:
            unreadable.append(os.path.relpath(path, materials))
            continue
        lowered = [w.lower() for w in tokens]
        compared_sides.append(
            (label, path, tokens, lowered, ngrams(lowered, MIN_RUN_WORDS))
        )

    skip = {os.path.abspath(report)}
    if report.endswith(".md"):
        skip.add(os.path.abspath(report[:-len(".md")] + ".checks.md"))

    candidates = []
    for root, dirs, files in os.walk(materials):
        dirs.sort()
        for fname in sorted(files):
            path = os.path.abspath(os.path.join(root, fname))
            if path not in skip:
                candidates.append(path)

    compared_count = 0
    hit: tuple[str, str, str] | None = None
    for path in candidates:
        tokens = read_tokens(path)
        if tokens is None:
            unreadable.append(os.path.relpath(path, materials))
            continue
        compared_count += 1
        if hit is not None:
            continue
        lowered = [w.lower() for w in tokens]
        if len(lowered) < MIN_RUN_WORDS:
            continue
        cand_grams = ngrams(lowered, MIN_RUN_WORDS)
        for label, side_path, side_tokens, side_lowered, side_grams in compared_sides:
            if side_path == path or cand_grams.isdisjoint(side_grams):
                continue
            for src_start, src_end, tgt_start, _, total in matched_groups(
                lowered, side_lowered
            ):
                if total < VERBATIM_SPAN_WORDS:
                    continue
                if total <= QUESTION_EXEMPT_MAX_WORDS and is_one_question(
                    lowered, src_start, src_end
                ):
                    continue
                hit = (
                    os.path.relpath(path, materials),
                    label,
                    " ".join(side_tokens[tgt_start:tgt_start + 12]),
                )
                break
            if hit is not None:
                break

    message = ""
    if unreadable:
        shown = ", ".join(unreadable[:UNREADABLE_NAMES_SHOWN])
        if len(unreadable) > UNREADABLE_NAMES_SHOWN:
            shown += ", and %d more" % (len(unreadable) - UNREADABLE_NAMES_SHOWN)
        message = (
            "could not read %d file%s under the materials root, so check 22's"
            " verbatim scan is incomplete: %s (extract its text beside it, or"
            " score check 22 not-met and record the deviation)"
            % (len(unreadable), "" if len(unreadable) == 1 else "s", shown)
        )
    if hit is None:
        return SpanScan(compared_count, message, "", "", "")
    return SpanScan(compared_count, message, hit[0], hit[1], hit[2])


def check_verbatim_span(scan: SpanScan, verdicts: dict[str, Row]) -> None:
    """A file the scan could not read is never a clean result: the report below
    would otherwise claim nothing was pasted out of material nobody compared.
    A span that is found must be check 22 not-met with a recorded deviation."""
    if scan.unreadable_message:
        fail(scan.unreadable_message)
    if not scan.span_file:
        return
    row = verdicts.get("22")
    verdict = row.verdict if row else "missing"
    if verdict != "not-met":
        fail(
            f"{scan.span_file} shares {VERBATIM_SPAN_WORDS}+ words verbatim with "
            f"{scan.span_side}, opening: \"{scan.span_opening}\" "
            f"(check 22 scored '{verdict}', want not-met with a deviation)"
        )


# ---- main ------------------------------------------------------------------


def check_report(report: str, materials_arg: str) -> None:
    if not os.path.isfile(report):
        fail(f"no report: {report}")
    if not os.path.isdir(materials_arg):
        fail(f"no materials directory: {materials_arg}")
    materials = os.path.abspath(materials_arg)
    report_dir = os.path.abspath(os.path.dirname(report))
    if report_dir != materials and not report_dir.startswith(materials + os.sep):
        fail(
            f"materials directory {materials} does not contain the report's own "
            f"directory {report_dir}, so the scan would miss the operator's files"
        )

    scoreboard = re.sub(r"\.md$", "", report) + ".checks.md"
    if not os.path.isfile(scoreboard):
        fail(f"no scoreboard beside the report: {scoreboard}")

    fmt, rows = parse_scoreboard(scoreboard)
    verdicts = check_row_coverage(rows, scoreboard)
    check_every_check_scored(verdicts)

    entries = parse_deviation_entries(report)
    check_entry_count(verdicts, entries, report)
    check_not_met_fields(verdicts)
    check_entries_are_scored_not_met(verdicts, entries)

    check_end_matter_types(report)
    check_format_elements(report, fmt)

    scan = scan_for_verbatim_span(report, materials)
    check_verbatim_span(scan, verdicts)

    print(
        "OK: scoreboard and deviations block agree, end matter is admissible, "
        "format elements are named, no undeclared verbatim span found (compared "
        f"the report and any notes file against {scan.compared_count} files under "
        f"{materials}). Every verdict on the scoreboard is the writer's own; "
        "this script re-scores none of them."
    )


def main(argv: list[str]) -> None:
    if argv[:1] == ["--selftest"]:
        selftest()
        return
    if len(argv) == 1:
        fail(
            "materials directory not given, so check 22's verbatim scan cannot "
            "run: check_report.py <report.md> <materials-dir>, the folder the "
            "operator named"
        )
    if len(argv) != 2:
        fail("usage: check_report.py <report.md> <materials-dir> | --selftest")
    check_report(argv[0], argv[1])


# ---- selftest fixtures -----------------------------------------------------
# Fixtures live here, not under skills/ or .nikki-agents/: the former trips
# the orphan check in scripts/verify_plugin.py, the latter is gitignored and
# proves nothing to a downstream reviewer. This --selftest run is the
# rerunnable artifact.

BINARY = "BINARY"


class Fixture(NamedTuple):
    """One materials tree, the run over it, and what that run must say."""

    name: str
    want_exit: int
    want_text: str
    report_rel: str
    files: tuple[tuple[str, str], ...]


def board(
    fmt: str,
    skip: int = 0,
    dup: int = 0,
    rows: dict[int, str] | None = None,
) -> str:
    """A scoreboard with CHECK_COUNT rows, all "met" by default. `skip` drops a
    row, `dup` prints one twice, `rows` replaces whole rows by check number."""
    lines = [
        f"Format: {fmt}",
        "",
        "| check | verdict | authoriser | quoted rule | reader loses |",
        "|---|---|---|---|---|",
    ]
    rows = rows or {}
    for n in range(1, CHECK_COUNT + 1):
        if n == skip:
            continue
        line = rows.get(n, f"| {n} | met | | | |")
        lines.append(line)
        if n == dup:
            lines.append(line)
    return "\n".join(lines)


def clean_report() -> str:
    return (
        "The proposal saves money and time, so it is approved.\n"
        "\n"
        "## Body\n"
        "\n"
        "Detail.\n"
        "\n"
        "## Sources\n"
        "\n"
        "- Example Source, 2026."
    )


def span_words(n: int) -> str:
    """`n` distinct tokens ("span01 span02 ..."), for verbatim-span fixtures.
    Distinct from clean_report's own words so a match can only come from the
    fixture's own planted span."""
    return " ".join("span%02d" % i for i in range(1, n + 1))


def report_with_span(text: str) -> str:
    """`text` goes inside the body (not a heading), so check 2's end-matter
    scan never sees it."""
    return (
        "The proposal saves money and time, so it is approved.\n"
        "\n"
        "## Body\n"
        "\n"
        f"{text}\n"
        "\n"
        "## Sources\n"
        "\n"
        "- Example Source, 2026."
    )


def report_with_deviation(entry: str) -> str:
    return clean_report() + "\n\n## Deviations\n\n" + entry


def clause_text() -> str:
    """Real legal clause prose, not distinct tokens: the fixtures below have to
    survive the ordinary English a difflib scan sees in every file."""
    return (
        "Subject to the limitations set forth in this Section, each party shall\n"
        "indemnify, defend and hold harmless the other party and its affiliates,\n"
        "officers, directors, employees and agents from and against any and all\n"
        "claims, demands, losses, liabilities, damages, costs and expenses, including\n"
        "reasonable attorneys fees, arising out of or resulting from any breach of the\n"
        "representations and warranties made by the indemnifying party under this\n"
        "Agreement, provided that the indemnified party gives prompt written notice of\n"
        "such claim and permits the indemnifying party to control the defense and\n"
        "settlement thereof, and further provided that no settlement imposing any\n"
        "obligation upon the indemnified party shall be entered into without its prior\n"
        "written consent, which consent shall not be unreasonably withheld, delayed or\n"
        "conditioned by the indemnified party in any circumstance whatsoever."
    )


def operator_question() -> str:
    return (
        "Should Halden renew the master services agreement with Vantage on the "
        "current terms, or renegotiate the indemnity and liability provisions "
        "before the automatic renewal date of 31 March 2027, given the outage "
        "record of the past eighteen months and the pricing offered by the two "
        "alternative suppliers we approached in January?"
    )


def case5_report() -> str:
    """Round 5 case 5's recorded shape: a cover letter as front matter, the
    body, then the clause under an admissible ## Attachment: heading."""
    return (
        "## Cover letter\n"
        "\n"
        "For the general counsel, ahead of the 31 March renewal date.\n"
        "\n"
        "Halden should renegotiate before renewal, for reasons of cost and risk.\n"
        "\n"
        "## Body\n"
        "\n"
        "The indemnity provisions carry the exposure counsel asked about.\n"
        "\n"
        "## Sources\n"
        "\n"
        "- Vantage MSA, 2024.\n"
        "\n"
        "## Attachment: MSA clause 4.2 and referenced provisions\n"
        "\n"
        f"{clause_text()}"
    )


def sic_padded(text: str) -> str:
    """"[sic]" every 30 words breaks every contiguous window longer than 30 and
    leaves the reproduction word for word."""
    out = ""
    for i, word in enumerate(text.split(), start=1):
        out += f"{word} "
        if i % 30 == 0:
            out += "[sic] "
    return out


def checklist_example_table() -> str:
    """The header/separator/example row straight out of references/checklist.md
    (not hand-typed), to prove the doc's own example parses."""
    header = "| check | verdict | authoriser | quoted rule | reader loses |"
    checklist = SKILL_DIR / "references/checklist.md"
    lines = checklist.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if header in line:
            return "\n".join(lines[i:i + 3])
    return ""


def report_fixture(
    name: str,
    want_exit: int,
    want_text: str,
    report: str,
    scoreboard: str,
    extra: tuple[str, str] | None = None,
) -> Fixture:
    """A report at the materials root, its scoreboard beside it (omitted when
    `scoreboard` is empty), and at most one other sibling file."""
    files = [("report.md", report)]
    if scoreboard:
        files.append(("report.checks.md", scoreboard))
    if extra:
        files.append(extra)
    return Fixture(name, want_exit, want_text, "report.md", tuple(files))


def fixtures() -> list[Fixture]:
    span = span_words(VERBATIM_SPAN_WORDS)
    deviation_5 = '- Check 5. Operator instruction: "skip it." Reader loses nothing.'
    not_met_rows = {
        n: f'| {n} | not-met | Op. | "waived" | reader loses it |'
        for n in (1, 3, 5, 7, 9, 11, 13)
    }
    zero_parse_rows = "".join(
        f"{n} | met |  |  | \n" for n in range(1, CHECK_COUNT + 1)
    )
    return [
        report_fixture(
            "clean report, nothing to flag",
            0,
            "no undeclared verbatim span found",
            clean_report(),
            board("point paper"),
        ),
        report_fixture(
            "no scoreboard beside the report",
            1,
            "no scoreboard beside the report:",
            clean_report(),
            "",
        ),
        report_fixture(
            "scoreboard missing a row",
            1,
            "scoreboard has no row for check 23",
            clean_report(),
            board("point paper", skip=23),
        ),
        report_fixture(
            "scoreboard row repeats",
            1,
            "scoreboard row for check 1 repeats",
            clean_report(),
            board("point paper", dup=1),
        ),
        report_fixture(
            "scoreboard verdict not a valid token",
            1,
            "check 10 verdict is 'maybe', want met|not-met|n-a",
            clean_report(),
            board("point paper", rows={10: "| 10 | maybe | | | |"}),
        ),
        # All CHECK_COUNT rows present but missing the leading/trailing pipe (the
        # shape a literal reading of the checklist's old prose gave). None of them
        # parse; the message must say the table didn't parse, not blame check 1.
        report_fixture(
            "scoreboard rows without leading/trailing pipe parse to nothing",
            1,
            "scoreboard has no parseable rows",
            clean_report(),
            f"Format: point paper\n\n{zero_parse_rows}",
        ),
        # Checks 2-23 are still absent, so the run must reach the genuine
        # per-check message, not the zero-rows one.
        report_fixture(
            "scoreboard built from the checklist's own example row",
            1,
            "scoreboard has no row for check 2",
            clean_report(),
            f"Format: point paper\n\n{checklist_example_table()}",
        ),
        # Case 5: seven not-met rows, zero deviation entries, block skipped
        # entirely. Message 4 must fire on this EMPTY-block shape, not only on a
        # merged entry (the defect that killed check 23's count test twice).
        report_fixture(
            "case 5: seven not-met rows, no Deviations block",
            1,
            "7 checks not met, 0 deviation entries",
            clean_report(),
            board("point paper", rows=not_met_rows),
        ),
        report_fixture(
            "scoreboard not-met row missing a field",
            1,
            "check 5 is not-met with no authoriser field",
            report_with_deviation(deviation_5),
            board("point paper", rows={5: "| 5 | not-met | | | |"}),
        ),
        report_fixture(
            "scoreboard not-met row missing the quoted rule",
            1,
            "check 5 is not-met with no quoted rule field",
            report_with_deviation(deviation_5),
            board(
                "point paper",
                rows={5: "| 5 | not-met | Op. | | reader loses it |"},
            ),
        ),
        report_fixture(
            "scoreboard not-met row missing reader-loses",
            1,
            "check 5 is not-met with no reader loses field",
            report_with_deviation(deviation_5),
            board("point paper", rows={5: '| 5 | not-met | Op. | "waived" | |'}),
        ),
        report_fixture(
            "entry cites a check the scoreboard scores met",
            1,
            "deviations entry cites check 5, scoreboard scores it met",
            report_with_deviation(
                '- Check 5. Operator instruction: "test." Reader loses nothing.'
            ),
            board(
                "point paper",
                rows={7: '| 7 | not-met | Op. | "waived" | reader loses the estimate |'},
            ),
        ),
        report_fixture(
            "end-matter heading not one of the five types",
            1,
            "end-matter item 'Notes' is not an admissible type (check 2)",
            clean_report() + "\n\n## Notes\n\nShould not be here.",
            board("point paper"),
        ),
        # Case 8: staff study claims four excluded elements, the note names one
        # and denies the rest.
        report_fixture(
            "case 8: staff study names 1 of 4 claimed elements",
            1,
            "format 'staff study' claims 4 excluded elements, format-elements "
            "note names 1: missing define terms, summarize background, explain "
            "calculations",
            clean_report() + "\n\n## Format elements\n\nRestate the problem.",
            board("staff study"),
        ),
        report_fixture(
            "verbatim span shared with sibling, check 22 scored met",
            1,
            f'sibling.md shares {VERBATIM_SPAN_WORDS}+ words verbatim with the '
            f'report, opening: "span01 span02',
            report_with_span(span),
            board("point paper"),
            ("sibling.md", f"Source material.\n\n{span}\n\nEnd of source."),
        ),
        report_fixture(
            "verbatim span shared, check 22 scored not-met and recorded",
            0,
            "no undeclared verbatim span found",
            report_with_span(span)
            + "\n\n## Deviations\n\n"
            + '- Check 22. Operator instruction: "reproduce clause 4.2 word for '
            'word." Reader loses the paraphrase.',
            board(
                "point paper",
                rows={
                    22: '| 22 | not-met | Operator | "reproduce clause 4.2 word '
                    'for word." | reader loses the paraphrase |'
                },
            ),
            ("sibling.md", span),
        ),
        report_fixture(
            "verbatim span one word short of the threshold",
            0,
            "no undeclared verbatim span found",
            report_with_span(span_words(VERBATIM_SPAN_WORDS - 1)),
            board("point paper"),
            ("sibling.md", span_words(VERBATIM_SPAN_WORDS - 1)),
        ),
        report_fixture(
            "verbatim span differs only in case and whitespace",
            1,
            f"sibling.md shares {VERBATIM_SPAN_WORDS}+ words verbatim",
            report_with_span(span),
            board("point paper"),
            ("sibling.md", f"  {span.upper()}\n"),
        ),
        report_fixture(
            "no other files beside the report",
            0,
            "no undeclared verbatim span found",
            clean_report(),
            board("point paper"),
        ),
        report_fixture(
            "unreadable sibling file is named, not skipped",
            1,
            "could not read 1 file under the materials root",
            clean_report(),
            board("point paper"),
            ("sibling.bin", BINARY),
        ),
        # Round 5 case 5: report at the materials root beside its notes and
        # scoreboard, sources in correspondence/ and analysis/, every check scored
        # met, zero deviations, and the clause reproduced word for word under an
        # ## Attachment: heading. The Attachment heading buys no exemption:
        # recording the deviation is the point.
        Fixture(
            "case 5: all checks met, 0 deviations, attached clause copied from analysis/",
            1,
            f'shares {VERBATIM_SPAN_WORDS}+ words verbatim with the report, '
            f'opening: "Subject to the limitations',
            "halden-position-paper.md",
            (
                ("halden-position-paper.md", case5_report()),
                ("halden-position-paper.checks.md", board("position paper")),
                (
                    "halden-position-paper.notes.md",
                    "# Notes\n\n"
                    "- Renewal date 31 March 2027. Source: correspondence/notice_bundle.md\n"
                    "- Indemnity exposure. Source: analysis/position_note.md",
                ),
                (
                    "correspondence/notice_bundle.md",
                    "# Notice bundle\n\nVantage gave notice on 2 February 2026.",
                ),
                ("analysis/position_note.md", f"# Position note\n\n{clause_text()}"),
            ),
        ),
        # The paste never reaches the report: it sits in the notes file, copied
        # out of the operator's own material. The notes file used to be exempted
        # from this scan, which made it the safest place to hide one.
        Fixture(
            "clause pasted into the notes file only",
            1,
            f"msa.md shares {VERBATIM_SPAN_WORDS}+ words verbatim with the "
            f"report's notes file",
            "report.md",
            (
                ("report.md", clean_report()),
                ("report.checks.md", board("point paper")),
                ("report.notes.md", f"# Notes\n\n{clause_text()}"),
                ("msa.md", f"# Master agreement\n\n{clause_text()}"),
            ),
        ),
        # The route the old skip set left open in both directions: the clause
        # reaches the report through the notes file, and the material it came
        # from is no longer under the materials root to compare against.
        Fixture(
            "clause reaches the report through its own notes file",
            1,
            f"report.notes.md shares {VERBATIM_SPAN_WORDS}+ words verbatim with "
            f"the report",
            "report.md",
            (
                ("report.md", report_with_span(clause_text())),
                ("report.checks.md", board("point paper")),
                ("report.notes.md", f"# Notes\n\n{clause_text()}"),
            ),
        ),
        # The writer's output directory is one level below the operator's folder,
        # so scanning the report's own directory sees no source at all.
        Fixture(
            "report in out/, source one level up under the materials root",
            1,
            f"shares {VERBATIM_SPAN_WORDS}+ words verbatim with the report",
            "out/report.md",
            (
                ("out/report.md", report_with_span(clause_text())),
                ("out/report.checks.md", board("point paper")),
                ("msa.md", f"# Master agreement\n\n{clause_text()}"),
            ),
        ),
        Fixture(
            "source of the report's own text is unreadable",
            1,
            "could not read 1 file under the materials root, so check 22's "
            "verbatim scan is incomplete: msa.pdf",
            "report.md",
            (
                ("report.md", report_with_span(clause_text())),
                ("report.checks.md", board("point paper")),
                ("msa.pdf", BINARY),
            ),
        ),
        Fixture(
            "paste padded with [sic] every 30 words",
            1,
            f"msa.md shares {VERBATIM_SPAN_WORDS}+ words verbatim with the report",
            "report.md",
            (
                ("report.md", report_with_span(sic_padded(clause_text()))),
                ("report.checks.md", board("point paper")),
                ("msa.md", f"# Master agreement\n\n{clause_text()}"),
            ),
        ),
        # The report contract makes the written-out question govern the report,
        # so restating it verbatim is required, not a paste. Check 22 bars
        # session context, chat logs and raw source text; a question is none.
        Fixture(
            "report restates the operator's written-out question",
            0,
            "no undeclared verbatim span found",
            "report.md",
            (
                (
                    "report.md",
                    "Halden should renegotiate before renewal. The written-out "
                    f"question this report answers is: {operator_question()} The "
                    "reasons group into cost, risk and supplier readiness.\n"
                    "\n"
                    "## Body\n"
                    "\n"
                    "Uptime fell short of the promised level in six of the "
                    "eighteen months reviewed.\n"
                    "\n"
                    "## Sources\n"
                    "\n"
                    "- Vantage MSA, 2024.",
                ),
                ("report.checks.md", board("point paper")),
                (
                    "README.md",
                    f"# {operator_question()}\n\nOperator brief. Materials are in "
                    "this folder.",
                ),
            ),
        ),
        Fixture(
            "paraphrased report over a realistic materials tree",
            0,
            "no undeclared verbatim span found",
            "report.md",
            (
                (
                    "report.md",
                    "Halden should renegotiate before renewal.\n"
                    "\n"
                    "## Body\n"
                    "\n"
                    "Uptime fell short in six of eighteen months. Both alternative "
                    "bids undercut\nthe incumbent on unit price.\n"
                    "\n"
                    "## Sources\n"
                    "\n"
                    "- Vantage MSA, 2024.",
                ),
                ("report.checks.md", board("point paper")),
                (
                    "report.notes.md",
                    "# Notes\n\n"
                    "- Uptime shortfall, 6 of 18 months. Source: analysis/position_note.md\n"
                    "- Two bids undercut incumbent. Source: correspondence/notice_bundle.md",
                ),
                (
                    "correspondence/notice_bundle.md",
                    f"# Notice bundle\n\n{clause_text()}",
                ),
                ("analysis/position_note.md", f"# Position note\n\n{clause_text()}"),
            ),
        ),
    ]


def run_checker(args: list[str]) -> tuple[int, str]:
    """Runs this script as a subprocess, stdout and stderr merged."""
    done = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return done.returncode, done.stdout.rstrip("\n")


def write_tree(root: Path, files: tuple[tuple[str, str], ...]) -> None:
    for rel, content in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if content == BINARY:
            path.write_bytes(os.urandom(64))
        else:
            path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")


def selftest_fail(name: str, status: int, want: int, out: str) -> NoReturn:
    sys.exit(f"SELFTEST FAIL: {name} (exit={status} want={want}): {out}")


def run_fixture_tree(fixture: Fixture) -> None:
    """Builds the materials tree in a temp dir, runs the checker over it with
    that dir as the materials root, and asserts exit status and output."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_tree(root, fixture.files)
        status, out = run_checker([str(root / fixture.report_rel), str(root)])
    if status != fixture.want_exit or fixture.want_text not in out:
        selftest_fail(fixture.name, status, fixture.want_exit, out)
    print(f"PASS: {fixture.name} (exit={status})")


def fixture_no_materials_dir_given() -> None:
    """The one-argument call the whole repo used to make. It must name the
    missing argument and must not print the clean line."""
    name = "no materials directory given"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_tree(
            root,
            (("report.md", clean_report()), ("report.checks.md", board("point paper"))),
        )
        status, out = run_checker([str(root / "report.md")])
    if (
        status != 1
        or "materials directory not given" not in out
        or "no undeclared verbatim span found" in out
    ):
        sys.exit(f"SELFTEST FAIL: {name} (exit={status}): {out}")
    print(f"PASS: {name} (exit={status})")


def fixture_materials_dir_beside_the_report() -> None:
    name = "materials directory does not contain the report"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "elsewhere").mkdir()
        write_tree(
            root,
            (
                ("out/report.md", clean_report()),
                ("out/report.checks.md", board("point paper")),
            ),
        )
        status, out = run_checker([str(root / "out" / "report.md"), str(root / "elsewhere")])
    if status != 1 or "does not contain the report's own directory" not in out:
        sys.exit(
            f"SELFTEST FAIL: materials directory beside the report "
            f"(exit={status}): {out}"
        )
    print(f"PASS: {name} (exit={status})")


def selftest() -> None:
    tree_fixtures = fixtures()
    for fixture in tree_fixtures:
        run_fixture_tree(fixture)
    bespoke = (fixture_no_materials_dir_given, fixture_materials_dir_beside_the_report)
    for run in bespoke:
        run()
    total = len(tree_fixtures) + len(bespoke)
    print(f"OK: {total}/{total} selftest fixtures passed")


if __name__ == "__main__":
    main(sys.argv[1:])
