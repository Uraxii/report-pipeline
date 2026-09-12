#!/usr/bin/env python3
"""Runs the report checker against 32 hand-built fixture trees and fails if any
one of them stops saying what it used to say.

Each fixture writes a small materials directory to a temporary folder, runs
skills/create-report/scripts/check_report.py over it as a subprocess, and
compares the exit code and a distinctive line of output against what that
fixture is meant to produce. Nothing here re-implements a check: the checker is
a black box called on the command line.

These fixtures used to live inside the checker itself, behind a --selftest
flag, which shipped roughly six hundred lines of test code to everyone who
downloaded the skill and told none of them it was there.

Run: python3 scripts/check_report_selftest.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple, NoReturn

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills/create-report/scripts"))

from check_report import CHECK_COUNT, SKILL_DIR, VERBATIM_SPAN_WORDS  # noqa: E402

CHECKER = SKILL_DIR / "scripts/check_report.py"

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
        report_fixture(
            "report is not UTF-8 text",
            1,
            "report.md as text, so the checks cannot run",
            BINARY,
            board("point paper"),
        ),
        report_fixture(
            "scoreboard is not UTF-8 text",
            1,
            "report.checks.md as text, so the checks cannot run",
            clean_report(),
            BINARY,
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
    """Runs the checker as a subprocess, stdout and stderr merged."""
    done = subprocess.run(
        [sys.executable, str(CHECKER), *args],
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
    selftest()
