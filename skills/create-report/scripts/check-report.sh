#!/usr/bin/env bash
# Diffs a report's deviations block and format-elements note against its
# sibling scoreboard, <report-name>.checks.md. Design:
# .nikki-agents/deviations-mechanism-design.md.
# Run: bash <this-skill-directory>/scripts/check-report.sh <report.md>
set -euo pipefail

fail() {
	echo "FAIL: $1" >&2
	exit 1
}

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COLLISIONS="$SKILL_DIR/references/collisions.md"
CHECK_COUNT=23
# ponytail: exact contiguous match on normalized tokens, no fuzzy or
# paraphrase-evasion detection. Raise this if short quotes start
# false-flagging; add fuzzy matching only if paraphrase evasion shows up as
# a real case, not before.
VERBATIM_SPAN_WORDS=40

# ---- selftest fixtures -----------------------------------------------------
# Fixtures live here, not under skills/ or .nikki-agents/: the former trips
# the orphan check in scripts/verify-plugin.sh, the latter is gitignored and
# proves nothing to a downstream reviewer. This --selftest run is the
# rerunnable artifact.

scoreboard_rows() {
	# Prints 23 scoreboard rows, all "met" by default.
	# Args, any order: "SKIP=N" drops row N. "DUP=N" prints row N twice.
	# "N=<full row line>" replaces row N's line.
	local skip="" dup="" arg n line
	declare -A custom=()
	for arg in "$@"; do
		case "$arg" in
		SKIP=*) skip="${arg#SKIP=}" ;;
		DUP=*) dup="${arg#DUP=}" ;;
		*=*) custom["${arg%%=*}"]="${arg#*=}" ;;
		esac
	done
	for n in $(seq 1 "$CHECK_COUNT"); do
		[ "$n" = "$skip" ] && continue
		line="${custom[$n]:-}"
		[ -n "$line" ] || line=$(printf '| %d | met | | | |' "$n")
		printf '%s\n' "$line"
		[ "$n" = "$dup" ] && printf '%s\n' "$line"
	done
}

board() {
	# $1 = Format: value, rest = scoreboard_rows args.
	local fmt="$1"
	shift
	printf 'Format: %s\n\n' "$fmt"
	printf '| check | verdict | authoriser | quoted rule | reader loses |\n'
	printf '|---|---|---|---|---|\n'
	scoreboard_rows "$@"
}

clean_report() {
	cat <<'EOF'
The proposal saves money and time, so it is approved.

## Body

Detail.

## Sources

- Example Source, 2026.
EOF
}

span_words() {
	# Prints $1 distinct tokens ("span01 span02 ..."), for verbatim-span
	# fixtures. Distinct from clean_report's own words so a match can only
	# come from the fixture's own planted span.
	local n="$1" i out=""
	for i in $(seq 1 "$n"); do
		out="$out span$(printf '%02d' "$i")"
	done
	printf '%s' "${out# }"
}

report_with_span() {
	# $1 = text to place inside the body (not a heading), so check 2's
	# end-matter scan never sees it.
	cat <<EOF
The proposal saves money and time, so it is approved.

## Body

$1

## Sources

- Example Source, 2026.
EOF
}

report_with_attachment_span() {
	# $1 = text placed under an admissible ## Attachment: heading, the shape
	# round 5's case 5 used: a verbatim clause the operator asked for.
	cat <<EOF
The proposal saves money and time, so it is approved.

## Body

Detail.

## Sources

- Example Source, 2026.

## Attachment: source clause

$1
EOF
}

run_fixture() {
	# $1 name, $2 want_exit, $3 want_grep, $4 report content, $5 scoreboard
	# content ("" to omit the scoreboard file entirely, for the msg-1 case).
	local dir out status
	dir=$(mktemp -d)
	printf '%s\n' "$4" >"$dir/report.md"
	[ -z "$5" ] || printf '%s\n' "$5" >"$dir/report.checks.md"
	set +e
	out=$(bash "$0" "$dir/report.md" 2>&1)
	status=$?
	set -e
	rm -rf "$dir"
	if [ "$status" != "$2" ] || ! printf '%s' "$out" | grep -qF -- "$3"; then
		echo "SELFTEST FAIL: $1 (exit=$status want=$2): $out" >&2
		exit 1
	fi
	echo "PASS: $1 (exit=$status)"
}

run_fixture_with_file() {
	# Same as run_fixture, plus one extra sibling file beside the report.
	# $1 name, $2 want_exit, $3 want_grep, $4 report content, $5 scoreboard
	# content, $6 sibling relpath (skip write if empty), $7 sibling content
	# ("BINARY" writes random bytes instead of text).
	local dir out status
	dir=$(mktemp -d)
	printf '%s\n' "$4" >"$dir/report.md"
	[ -z "$5" ] || printf '%s\n' "$5" >"$dir/report.checks.md"
	if [ -n "$6" ]; then
		mkdir -p "$dir/$(dirname "$6")"
		if [ "$7" = "BINARY" ]; then
			head -c 64 /dev/urandom >"$dir/$6"
		else
			printf '%s\n' "$7" >"$dir/$6"
		fi
	fi
	set +e
	out=$(bash "$0" "$dir/report.md" 2>&1)
	status=$?
	set -e
	rm -rf "$dir"
	if [ "$status" != "$2" ] || ! printf '%s' "$out" | grep -qF -- "$3"; then
		echo "SELFTEST FAIL: $1 (exit=$status want=$2): $out" >&2
		exit 1
	fi
	echo "PASS: $1 (exit=$status)"
}

fixture_clean() {
	run_fixture "clean report, nothing to flag" 0 \
		"no undeclared verbatim span found" \
		"$(clean_report)" "$(board "point paper")"
}

fixture_no_scoreboard() {
	run_fixture "no scoreboard beside the report" 1 \
		"no scoreboard beside the report:" \
		"$(clean_report)" ""
}

fixture_missing_row() {
	run_fixture "scoreboard missing a row" 1 \
		"scoreboard has no row for check 23" \
		"$(clean_report)" "$(board "point paper" "SKIP=23")"
}

fixture_duplicate_row() {
	run_fixture "scoreboard row repeats" 1 \
		"scoreboard row for check 1 repeats" \
		"$(clean_report)" "$(board "point paper" "DUP=1")"
}

fixture_bad_verdict() {
	run_fixture "scoreboard verdict not a valid token" 1 \
		"check 10 verdict is 'maybe', want met|not-met|n-a" \
		"$(clean_report)" \
		"$(board "point paper" "10=| 10 | maybe | | | |")"
}

fixture_case5_count() {
	# Case 5: seven not-met rows, zero deviation entries, block skipped
	# entirely. Message 4 must fire on this EMPTY-block shape, not only on
	# a merged entry (the defect that killed check 23's count test twice).
	local n rows=()
	for n in 1 3 5 7 9 11 13; do
		rows+=("$n=| $n | not-met | Op. | \"waived\" | reader loses it |")
	done
	run_fixture "case 5: seven not-met rows, no Deviations block" 1 \
		"7 checks not met, 0 deviation entries" \
		"$(clean_report)" "$(board "point paper" "${rows[@]}")"
}

fixture_missing_field() {
	local report
	report=$(clean_report)$'\n\n'"## Deviations"$'\n\n'
	report="${report}- Check 5. Operator instruction: \"skip it.\" Reader loses nothing."
	run_fixture "scoreboard not-met row missing a field" 1 \
		"check 5 is not-met with no authoriser field" \
		"$report" "$(board "point paper" "5=| 5 | not-met | | | |")"
}

fixture_missing_quoted_rule() {
	local report
	report=$(clean_report)$'\n\n'"## Deviations"$'\n\n'
	report="${report}- Check 5. Operator instruction: \"skip it.\" Reader loses nothing."
	run_fixture "scoreboard not-met row missing the quoted rule" 1 \
		"check 5 is not-met with no quoted rule field" \
		"$report" "$(board "point paper" "5=| 5 | not-met | Op. | | reader loses it |")"
}

fixture_missing_reader_loses() {
	local report
	report=$(clean_report)$'\n\n'"## Deviations"$'\n\n'
	report="${report}- Check 5. Operator instruction: \"skip it.\" Reader loses nothing."
	run_fixture "scoreboard not-met row missing reader-loses" 1 \
		"check 5 is not-met with no reader loses field" \
		"$report" "$(board "point paper" "5=| 5 | not-met | Op. | \"waived\" | |")"
}

fixture_stale_entry() {
	local report rows
	report=$(clean_report)$'\n\n'"## Deviations"$'\n\n'
	report="${report}- Check 5. Operator instruction: \"test.\" Reader loses nothing."
	rows="7=| 7 | not-met | Op. | \"waived\" | reader loses the estimate |"
	run_fixture "entry cites a check the scoreboard scores met" 1 \
		"deviations entry cites check 5, scoreboard scores it met" \
		"$report" "$(board "point paper" "$rows")"
}

fixture_bad_heading() {
	local report
	report=$(clean_report)$'\n\n'"## Notes"$'\n\n'"Should not be here."
	run_fixture "end-matter heading not one of the five types" 1 \
		"end-matter item 'Notes' is not an admissible type (check 2)" \
		"$report" "$(board "point paper")"
}

fixture_case8_format() {
	# Case 8: staff study claims four excluded elements, the note names one
	# and denies the rest.
	local report
	report=$(clean_report)$'\n\n'"## Format elements"$'\n\n'"Restate the problem."
	run_fixture "case 8: staff study names 1 of 4 claimed elements" 1 \
		"format 'staff study' claims 4 excluded elements, format-elements note names 1: missing define terms, summarize background, explain calculations" \
		"$report" "$(board "staff study")"
}

fixture_verbatim_span_met() {
	local span
	span="$(span_words "$VERBATIM_SPAN_WORDS")"
	run_fixture_with_file "verbatim span shared with sibling, check 22 scored met" 1 \
		"sibling.md shares ${VERBATIM_SPAN_WORDS}+ words verbatim with the report, opening: \"span01 span02" \
		"$(report_with_span "$span")" \
		"$(board "point paper")" \
		"sibling.md" "Source material.

$span

End of source."
}

fixture_verbatim_span_recorded() {
	local span report
	span="$(span_words "$VERBATIM_SPAN_WORDS")"
	report=$(report_with_span "$span")$'\n\n'"## Deviations"$'\n\n'
	report="${report}- Check 22. Operator instruction: \"reproduce clause 4.2 word for word.\" Reader loses the paraphrase."
	run_fixture_with_file "verbatim span shared, check 22 scored not-met and recorded" 0 \
		"no undeclared verbatim span found" \
		"$report" \
		"$(board "point paper" "22=| 22 | not-met | Operator | \"reproduce clause 4.2 word for word.\" | reader loses the paraphrase |")" \
		"sibling.md" "$span"
}

fixture_verbatim_span_under_threshold() {
	local span
	span="$(span_words $((VERBATIM_SPAN_WORDS - 1)))"
	run_fixture_with_file "verbatim span one word short of the threshold" 0 \
		"no undeclared verbatim span found" \
		"$(report_with_span "$span")" \
		"$(board "point paper")" \
		"sibling.md" "$span"
}

fixture_verbatim_span_case_whitespace() {
	local span sibling_span
	span="$(span_words "$VERBATIM_SPAN_WORDS")"
	sibling_span="$(printf '%s' "$span" | tr ' ' '\n' | tr '[:lower:]' '[:upper:]' | tr '\n' ' ')"
	run_fixture_with_file "verbatim span differs only in case and whitespace" 1 \
		"sibling.md shares ${VERBATIM_SPAN_WORDS}+ words verbatim" \
		"$(report_with_span "$span")" \
		"$(board "point paper")" \
		"sibling.md" "  $sibling_span

"
}

fixture_no_sibling_files() {
	run_fixture "no other files beside the report" 0 \
		"no undeclared verbatim span found" \
		"$(clean_report)" "$(board "point paper")"
}

fixture_binary_sibling() {
	run_fixture_with_file "unreadable binary sibling file does not crash" 0 \
		"no undeclared verbatim span found" \
		"$(clean_report)" "$(board "point paper")" \
		"sibling.bin" "BINARY"
}

fixture_case5_verbatim() {
	# Round 5 case 5's own shape: every check scored met, zero deviations,
	# a sibling source file sharing a long span with the report's own
	# Attachment section. No exemption for the Attachment heading: this is
	# the shape the round found, and it must still fail.
	local span
	span="$(span_words "$VERBATIM_SPAN_WORDS")"
	run_fixture_with_file "case 5: all checks met, 0 deviations, sibling shares an attached verbatim span" 1 \
		"sibling.md shares ${VERBATIM_SPAN_WORDS}+ words verbatim with the report, opening: \"span01 span02" \
		"$(report_with_attachment_span "$span")" \
		"$(board "point paper")" \
		"sibling.md" "$span"
}

selftest() {
	fixture_clean
	fixture_no_scoreboard
	fixture_missing_row
	fixture_duplicate_row
	fixture_bad_verdict
	fixture_case5_count
	fixture_missing_field
	fixture_missing_quoted_rule
	fixture_missing_reader_loses
	fixture_stale_entry
	fixture_bad_heading
	fixture_case8_format
	fixture_verbatim_span_met
	fixture_verbatim_span_recorded
	fixture_verbatim_span_under_threshold
	fixture_verbatim_span_case_whitespace
	fixture_no_sibling_files
	fixture_binary_sibling
	fixture_case5_verbatim
	echo "OK: 19/19 selftest fixtures passed"
}

if [ "${1:-}" = "--selftest" ]; then
	selftest
	exit 0
fi

# ---- argument parse ---------------------------------------------------------

[ $# -eq 1 ] || fail "usage: check-report.sh <report.md> | --selftest"
report="$1"
[ -f "$report" ] || fail "no report: $report"

# ---- scoreboard guard --------------------------------------------------------

scoreboard="${report%.md}.checks.md"
[ -f "$scoreboard" ] || fail "no scoreboard beside the report: $scoreboard"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

python3 - "$scoreboard" >"$work/rows" <<'PYEOF'
import re, sys
fmt = ""
print_lines = []
for line in open(sys.argv[1], encoding="utf-8"):
	m = re.match(r'^Format:\s*(.+?)\s*$', line)
	if m:
		fmt = m.group(1)
		continue
	line = line.strip()
	if not line.startswith("|"):
		continue
	cells = [c.strip() for c in line.strip("|").split("|")]
	if len(cells) != 5 or not cells[0].isdigit():
		continue
	print_lines.append(cells)
# \x1f (unit separator): bash `read` treats tab as IFS whitespace and
# collapses an empty field between two tabs, silently shifting every field
# after it. \x1f is not IFS whitespace, so an empty cell stays its own field.
print("FORMAT\x1f" + fmt)
for c in print_lines:
	print("\x1f".join(c))
PYEOF

# ---- row-coverage loop: every check 1..N has exactly one valid-verdict row --

declare -A verdict=() authoriser=() quoted=() loses=()
fmt=""
while IFS=$'\x1f' read -r a b c d e; do
	if [ "$a" = "FORMAT" ]; then
		fmt="$b"
		continue
	fi
	case "$b" in
	met | not-met | n-a) : ;;
	*) fail "check $a verdict is '$b', want met|not-met|n-a" ;;
	esac
	[ -z "${verdict[$a]:-}" ] || fail "scoreboard row for check $a repeats"
	verdict[$a]="$b"
	authoriser[$a]="$c"
	quoted[$a]="$d"
	loses[$a]="$e"
done <"$work/rows"

for n in $(seq 1 "$CHECK_COUNT"); do
	[ -n "${verdict[$n]:-}" ] || fail "scoreboard has no row for check $n"
done

# ---- count test: not-met rows vs deviation entries, zero counts included ----

python3 - "$report" >"$work/entries" <<'PYEOF'
import re, sys
in_block = False
for line in open(sys.argv[1], encoding="utf-8"):
	line = line.rstrip("\n")
	if re.match(r'^##\s+Deviations\s*$', line):
		in_block = True
		continue
	if in_block and re.match(r'^##\s', line):
		break
	if not in_block:
		continue
	m = re.match(r'^-\s+(?:Check\s+(\d+)|Rule\s+.+?)\.\s*(.*)$', line)
	if m:
		print((m.group(1) or "") + "\x1f" + m.group(2))
PYEOF

not_met_count=0
for n in $(seq 1 "$CHECK_COUNT"); do
	[ "${verdict[$n]}" = "not-met" ] && not_met_count=$((not_met_count + 1))
done
entry_count=$(wc -l <"$work/entries")
[ "$not_met_count" -eq "$entry_count" ] ||
	fail "$not_met_count checks not met, $entry_count deviation entries in $report"

# ---- field test: every not-met row carries its three deviation fields ------

for n in $(seq 1 "$CHECK_COUNT"); do
	[ "${verdict[$n]}" = "not-met" ] || continue
	[ -n "${authoriser[$n]}" ] || fail "check $n is not-met with no authoriser field"
	[ -n "${quoted[$n]}" ] || fail "check $n is not-met with no quoted rule field"
	[ -n "${loses[$n]}" ] || fail "check $n is not-met with no reader loses field"
done

# ---- transcription test: each entry cites a check the scoreboard scores ----
# not-met. (A row that is not not-met has no quoted rule to transcribe, so
# check 23's "quoted rule does not appear in its entry" is this same test.)

while IFS=$'\x1f' read -r n _rest; do
	[ -n "$n" ] || continue
	[ "${verdict[$n]:-}" = "not-met" ] ||
		fail "deviations entry cites check $n, scoreboard scores it ${verdict[$n]:-missing}"
done <"$work/entries"

# ---- end-matter type test: every heading from the first end-of-body -------
# heading to EOF is one of the five admissible types. A cover letter sits
# before the body, so it never starts this scan (check 2).

python3 - "$report" >"$work/heading" <<'PYEOF'
import re, sys
ADMISSIBLE = {"Sources", "Deviations", "Format elements", "Cover letter"}
SCAN_START = {"Sources", "Deviations", "Format elements"}


def is_attachment(h):
	return h.startswith("Attachment: ") and len(h) > len("Attachment: ")


headings = []
for line in open(sys.argv[1], encoding="utf-8"):
	m = re.match(r'^##\s+(.+?)\s*$', line)
	if m:
		headings.append(m.group(1))

start = None
for i, h in enumerate(headings):
	if h in SCAN_START or is_attachment(h):
		start = i
		break

if start is not None:
	for h in headings[start:]:
		if h not in ADMISSIBLE and not is_attachment(h):
			print(h)
			break
PYEOF

if [ -s "$work/heading" ]; then
	bad=$(head -n1 "$work/heading")
	fail "end-matter item '$bad' is not an admissible type (check 2)"
fi

# ---- format-elements test: the note names every element the format claims -

python3 - "$COLLISIONS" "$fmt" >"$work/claims" <<'PYEOF'
import sys
in_table = False
rows = []
for line in open(sys.argv[1], encoding="utf-8"):
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

wanted = sys.argv[2].strip().lower()
for formats_cell, elements_cell in rows:
	for token in formats_cell.split(","):
		token = token.strip().lower()
		if wanted == token or wanted.startswith(token):
			if elements_cell.strip().lower() != "none":
				for e in elements_cell.split(";"):
					print(e.strip().lower())
			sys.exit(0)
PYEOF

if [ -s "$work/claims" ]; then
	python3 - "$report" >"$work/note" <<'PYEOF'
import re, sys
in_block = False
for line in open(sys.argv[1], encoding="utf-8"):
	line = line.rstrip("\n")
	if re.match(r'^##\s+Format elements\s*$', line):
		in_block = True
		continue
	if in_block and re.match(r'^##\s', line):
		break
	if not in_block or not line.strip():
		continue
	for part in line.split(","):
		part = part.strip().rstrip(".").lower()
		if part:
			print(part)
PYEOF
	claimed_n=$(wc -l <"$work/claims")
	named_n=$(wc -l <"$work/note")
	missing=""
	while IFS= read -r elem; do
		grep -qxF -- "$elem" "$work/note" || missing="$missing, $elem"
	done <"$work/claims"
	missing="${missing#, }"
	[ -z "$missing" ] ||
		fail "format '$fmt' claims $claimed_n excluded elements, format-elements note names $named_n: missing $missing"
fi

# ---- verbatim-span test: no undeclared paste from a sibling file (check 22) -
# Round 5's case 5: a writer scored check 22 "met" on a report carrying 637
# words of pasted source text, and the count test above passed because the
# scoreboard and the (empty) deviations block agreed with each other. Neither
# reads the report. This test does: it scans every other file in the report's
# own directory, recursively, for a 40-plus-word span (VERBATIM_SPAN_WORDS)
# that also appears in the report, whitespace and case normalized. A match
# is not itself a fail — a verbatim clause the operator asked for is a legal
# report — but it must be check 22 not-met with a recorded deviation, the
# same as any other barred fix. An ## Attachment: section gets no exemption:
# recording the deviation is the point even when the paste is the right call.

python3 - "$report" "$VERBATIM_SPAN_WORDS" >"$work/span" <<'PYEOF'
import os, re, sys

report_path = sys.argv[1]
threshold = int(sys.argv[2])


def read_words(path):
	# None on anything unreadable as text (binary, permission-denied): a
	# sibling file the mechanism can't read carries no undeclared prose.
	try:
		with open(path, encoding="utf-8") as f:
			text = f.read()
	except (UnicodeDecodeError, OSError):
		return None
	return re.findall(r"\S+", text)


report_abs = os.path.abspath(report_path)
report_words = read_words(report_abs)
if not report_words or len(report_words) < threshold:
	sys.exit(0)

report_windows = {}
for i in range(len(report_words) - threshold + 1):
	key = tuple(w.lower() for w in report_words[i:i + threshold])
	report_windows.setdefault(key, i)

skip = {report_abs}
if report_path.endswith(".md"):
	base = report_path[:-len(".md")]
	skip.add(os.path.abspath(base + ".notes.md"))
	skip.add(os.path.abspath(base + ".checks.md"))

report_dir = os.path.dirname(report_abs) or "."
candidates = []
for root, dirs, files in os.walk(report_dir):
	dirs.sort()
	for fname in sorted(files):
		path = os.path.abspath(os.path.join(root, fname))
		if path not in skip:
			candidates.append(path)

for path in candidates:
	words = read_words(path)
	if not words or len(words) < threshold:
		continue
	for i in range(len(words) - threshold + 1):
		key = tuple(w.lower() for w in words[i:i + threshold])
		idx = report_windows.get(key)
		if idx is not None:
			opening = " ".join(report_words[idx:idx + 12])
			relpath = os.path.relpath(path, report_dir)
			print(relpath + "\x1f" + opening)
			sys.exit(0)
PYEOF

if [ -s "$work/span" ]; then
	IFS=$'\x1f' read -r span_file span_opening <"$work/span"
	[ "${verdict[22]:-}" = "not-met" ] ||
		fail "$span_file shares ${VERBATIM_SPAN_WORDS}+ words verbatim with the report, opening: \"$span_opening\" (check 22 scored '${verdict[22]:-missing}', want not-met with a deviation)"
fi

echo "OK: scoreboard and deviations block agree, end matter is admissible, format elements are named, no undeclared verbatim span found. Every verdict on the scoreboard is the writer's own; this script re-scores none of them."
