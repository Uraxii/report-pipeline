---
name: create-report
description: >-
  Drafts a standalone report for a reader who is not the operator and was
  not in the working session: a decision-maker, a client, or a reviewer who
  will read the report alone. Fires whenever the deliverable is a report,
  memo, position paper, background paper, or staff study that must carry its
  own conclusion, evidence, and stated uncertainty to that reader. Not for
  working notes the agent keeps for itself, and not for prose written back to
  the operator.
---

## Meta-rule

Operator instructions for this report outrank every rule in this skill.
Operator instruction differs from anything below -> instruction wins.
Following instruction against a rule here is a deviation, and the report
records it at step 8.

## Scope: this skill drafts, it does not analyze

Analysis is work already done. A step naming an analysis procedure (criteria
and decision matrix, evidence tests) names a standard the finished work must
meet and record, never a fresh task to run.

## The report contract

Every run meets all of these.

- The written-out question governs the report.
- The thesis and main conclusion appear in the first paragraph, with the
  primary supporting reasons grouped into categories, not a flat list.
- The first paragraph announces the order; the body follows it exactly.
- The body contains only what the first paragraph promises.
- Every container announces its point in its own label. The title states the
  conclusion, each subhead states its sub-conclusion, each paragraph opens by
  saying its point, and each graph is titled with its thesis.
- Say nothing that is not part of the answer to the question asked.
- Every claim carries specific support, every number is compared to another
  number, and every source is listed.
- Every major judgment states its likelihood on the ladder the report
  publishes, and states confidence in the judgment separately. Likelihood and
  confidence never share a sentence. A judgment that is not empirical carries
  no band; it states its premise as a premise and names where the premise
  comes from.
- Assumptions are marked as assumptions and never presented as information.
  Each critical assumption states what follows if it is wrong.
- Where a recommendation is asked for and the analysis compared options, at
  least two genuinely distinct options were compared against criteria set
  before the options were generated. Where the analysis instead states that no
  matrix applies and gives its reason, a defended single option, a screening
  that emptied the field, or a question of fact, this clause is met and the
  report owes no deviation entry. A single option handed over with no such
  reason is not a recommendation, because nothing was compared.
- Every major judgment names what would change it. A judgment with no stated
  falsifier is not finished. A judgment that is not empirical names instead
  what would have to change for it to stop holding.

The report prints the ladder it uses. Ladder table: references/style.md.

The contract is also the revision rule. Any revision leaves the first
paragraph's promise true: new material merges into the announced structure,
or the announcement changes with it.

## Gotchas

The exclusion list. Do not restate the problem; do not announce that the
research was completed; do not summarize background; do not define terms; do
not explain calculations; do not footnote your own conclusions, presentation
explanations, or summaries; and do not state an inference in the grammatical
form of a fact. Underlying information, assumptions, and judgments stay
visibly distinct. A named format may claim some of these: see "Pick the
format" below.

Four ways an agent-drafted report fails, each with its fix:

- Context bleed: session context or source text pasted into the report.
  Fix: draft only from the step 3 notes file.
- Agent narration: the report announces its own process. Fix: the exclusion
  list.
- Revision as append: new material bolted on the end. Fix: the revision rule.
- False confidence: an inference stated as a fact, or a conclusion with no
  stated likelihood or confidence. Fix: a ladder term, a separate confidence
  sentence, and the judgment labeled as a judgment.

## The eight steps

Load references/planning.md while working steps 1 to 5.

1. **Assignment.** Write out the specific question the report answers before
   anything else. Topic is the question; thesis is the answer. Yes-or-no
   asked means yes-or-no answered. "Look into X" is not an assignment. One
   controlling purpose governs, and every sentence serves it. Where the
   question came from someone else, get the problem statement approved before
   working on it, cast as who, what, when, why, and how. Run the key
   assumptions check here, against the answer the assignment already
   presumes, and again at step 8 against the draft. Each run: write down the
   current line; list every premise it needs, stated and unstated; challenge
   each (why must it be true, does it hold under all conditions); keep only
   the premises that must be true; for each, name the conditions or
   information under which it would fail. Record the output. A kept premise
   that can still fail is an assumption: mark it and state what follows if it
   is wrong.
2. **Audience.** Set two dials together: omit as much as possible (what the
   reader already knows) and be as technical as possible (what the reader can
   absorb). Default reader: intelligent, suspicious, busy. Address four roles,
   not one reader: primary receivers, secondary receivers, key decision
   makers, and gatekeepers.
3. **Notes.** Collect the facts the report will use in their own file beside
   the report, named `<report-name>.notes.md`. Transform each idea into your
   own words rather than copying text, and record each fact with its source.
   Check 22 fails when the file is not there.
4. **Thesis.** Form it from the notes, after them, never as a starting
   assumption. State it with its primary supporting reasons grouped into major
   categories.
5. **Plan.** Build a skeleton plan (the order of arguments), then a final plan
   that correlates every note with the point it supports. No prose yet. A note
   supporting no point gets cut here. Where the report recommends a course of
   action, load references/recommendation.md, which decides whether to draft
   or send the analysis back.
6. **Draft.** Apply the exclusion list. Load references/evidence.md when
   placing a number, a graph, a source, or a claim a suspicious reader will
   test. Load references/style.md when writing sentences, numbers, tables, or
   likelihood. Load references/sample-reports.md when a worked example would
   help apply the contract.
7. **Revise.** Three passes, in order, never all at once. Load
   references/style.md for the paragraph and sentence passes:
   - Big picture: does the draft answer the assignment at a fitting length,
     does anything not serve the answer, is anything missing.
   - Paragraphs: each makes one point and opens by saying it; transitions
     hold. Run the connective sweep.
   - Sentences and words: passive voice, unclear language, wordiness,
     grammar, spelling. Read the draft aloud, or have it read to you, and
     check the words a spell-checker passes but the sentence misuses
     (then/than, affect/effect).

   To slow a pass down, read one line at a time or read sentences backwards.
   Pause before you send: read the whole once more.
8. **Check.** Load references/checklist.md. In order: run the key assumptions
   check a second time (step 1), then the sensitivity test, and record both
   outputs. Score every check on `<report-name>.checks.md` beside the report.
   Then run `python3 <this-skill-directory>/scripts/check_report.py <report>
   <materials-dir>`, passing the folder the operator named, fix what it
   names, and run it again. A report sent while the checker fails is
   unfinished. The heavy challenge techniques (competing hypotheses, Team A
   and Team B, devil's advocacy, red team) run only when the operator asks for
   one by name, never as your default and never because a conclusion is
   uncomfortable; then load references/challenge-heavy.md.

## Pick the format from the function

Pick one shape from the function it serves. Hold it fixed for the whole
report. Load references/structure.md when choosing the shape, building the
skeleton plan, writing paragraphs, or writing a cover letter or executive
summary.

- Point paper: one-page bullet brief, quick reference or decision now.
- Talking paper: bullet talking points to carry into discussion or briefing.
- Bullet background paper: background in bullets, reader needs facts fast.
- Background paper: same background in prose, reader needs the reasoning.
- Position paper: argues one position, asks reader to adopt it.
- Staff study: full problem-to-recommendation report, five-part body.

Load references/skeletons.md whenever the report is a staff study or a
running estimate (a standing report updated as a situation moves), whoever
chose that shape.

Load references/collisions.md when two rules here appear to conflict, or
when the report uses a named paper format, whoever chose it.

## Reference files

Each loads at the step that names it above.
