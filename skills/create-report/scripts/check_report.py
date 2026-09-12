#!/usr/bin/env python3
"""Diffs a report's deviations block and format-elements note against its
sibling scoreboard, <report-name>.checks.md.

Design: .nikki-agents/deviations-mechanism-design.md.
Run: python3 <this-skill-directory>/scripts/check_report.py <report.md> <materials-dir>
Self-test: python3 scripts/check_report_selftest.py, in the report-pipeline repo.

Every verdict on the scoreboard is the writer's own; this script re-scores
none of them. It only checks that the scoreboard, the deviations block, the
end matter, the format-elements note and the report's own text agree with
each other.
"""
import difflib
import os
import re
import sys
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
    """A file the checks cannot read as text is named, the same as the
    verbatim scan names one it could not read: never a traceback."""
    try:
        with open(path, encoding="utf-8") as handle:
            yield from handle
    except (UnicodeDecodeError, OSError):
        fail(f"could not read {path} as text, so the checks cannot run: "
             "UTF-8 expected")


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
    if len(argv) == 1:
        fail(
            "materials directory not given, so check 22's verbatim scan cannot "
            "run: check_report.py <report.md> <materials-dir>, the folder the "
            "operator named"
        )
    if len(argv) != 2:
        fail("usage: check_report.py <report.md> <materials-dir>")
    check_report(argv[0], argv[1])


if __name__ == "__main__":
    main(sys.argv[1:])
