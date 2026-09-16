# Step 8 checks

## Fail, gap, or deviation

A fail is a fix. Two things are not:

- An input the analysis never produced is a gap: say so and send it back at
  step 5. It is not a deviation.
- A fix that is barred is a recorded deviation. Barred means an operator
  instruction overrides the check, or two rules in this skill collide with no
  way to satisfy both by any rewriting. Nothing else is barred.

Record deviations under `## Deviations`, in one block. Every check that stays
failed gets its own entry, never one merged entry. One line per entry, opening
`- Check N.`, or `- Rule <name>.` for a rule outside the numbered list. Three
fields per entry, all required:

- The check not met, by its number, or a rule outside the list by its name.
  Never a file:line in the report.
- The rule that authorises it, quoted: the operator's instruction in the
  operator's own words, or both colliding rules and the side you took. A rule
  named but not quoted is not an authoriser.
- What the reader loses by it.

An entry missing a field is an unrecorded fail.

## The scoreboard

A sibling file, `<report-name>.checks.md`, beside the report. Score every
check here first; the deviations block transcribes this file's `not-met`
rows, never a fresh judgment made at write time.

One line, `Format: <the paper format chosen>`, then a markdown table, one row
per numbered check, every row opening and closing with `|`. Copy this shape,
do not paraphrase it:

| check | verdict | authoriser | quoted rule | reader loses |
|---|---|---|---|---|
| 1 | met |  |  |  |

Verdict is one of `met`, `not-met`, `n-a`. A `met` or `n-a` row leaves
`authoriser`, `quoted rule`, and `reader loses` blank. A `not-met` row fills
all three.

## The numbered checks

1. The first paragraph answers the written-out question, with the reasons
   grouped into categories, not a flat list.
2. The first paragraph announces the order; the body follows it exactly, with
   nothing beyond what the paragraph promised. A section bolted on the end
   fails this. Whatever sits outside the announced body is end matter, and
   every end-matter item is one of these five types, under the heading named
   here. The list is closed; the count is not: zero, one, or several items of
   a type all pass.
   - The source list. `## Sources`.
   - The deviations block. `## Deviations`.
   - The format-elements note check 5 requires when a named format claims an
     excluded element. `## Format elements`.
   - The cover letter an external report carries (check 11).
     `## Cover letter`.
   - A verbatim-clause attachment: source text reproduced word for word,
     tabbed so the reader finds one item. `## Attachment: <name>`.
   An item under any other heading fails this check. A cover letter sits
   before the body: it is front matter.
3. The title states the conclusion, and the subheads, read alone, carry the
   argument; each subhead states a sub-conclusion, not a topic.
4. The conclusion is not buried past the first paragraph.
5. Exclusion scan against the exclusion list, including the ban on stating an
   inference in the grammatical form of a fact. Where the report uses a format
   whose skeleton requires an excluded element, whoever chose that format,
   that element passes this check, and the report names every excluded
   element the format claimed, by their names on the exclusion list. All of
   them: the excluded-elements table fixes which elements each format claims,
   and the note names every element on that format's row. Announcing the
   format's parts is not naming them. The naming goes in the
   `## Format elements` end-matter item, never in the notes file and never
   folded into the body.
6. Every number is compared to another number, and every figure carries its
   context. The reader never has to wonder good-or-bad. A number the report
   derives names the numbers it came from and their sources. A number that
   appears in no source and in no named derivation does not appear in the
   report. Naming the inputs is not explaining the calculation.
7. No vague evaluative terms: "significant," "appear," and their kin.
8. Every graph has a thesis, stated in its title, with labels complete.
9. Sources are precise, varied in kind, weighed for credibility, and listed
   at the end.
10. Competing claims are each addressed individually.
11. External report: the cover letter is present, purpose first, with the
    expected response explicit.
12. Connective sweep done; read-aloud pass done; spell-checker blind spots
    checked; pause before send.
13. Every major judgment carries a likelihood term from one declared ladder.
    No sentence mixes ladders, and no sentence pairs confidence with
    likelihood. A judgment that is not empirical carries no band: a value
    commitment, a legal disqualification, or a policy rule states its premise
    as a premise and names where the premise comes from. A band on a value
    claim fails this check.
14. No weasels: scan for "serious possibility," any modified "possible,"
    "may well," and bare "reportedly."
15. Assumptions are marked as assumptions, and each states what follows if it
    is wrong.
16. Where options were compared: the criteria, the weights with their
    rationale, and both matrix totals are present, and the result is
    summarized in the body.
17. The recommendation commits to one course, and the decision-maker's job is
    to approve or disapprove, nothing more. Where no option passed screening,
    the report says so and names what would have to change for one to pass,
    rather than recommending a screened-out option.
18. The key assumptions check ran twice, at the start of the work and again
    before finalizing, and both outputs are recorded. The sensitivity test ran
    and its output is recorded: for each critical item of evidence, what
    breaks if that item is wrong. Any single point of failure it found is
    named in the report.
19. The edit ran in three passes, in order: big picture, then paragraphs,
    then sentences and words.
20. Contrary information and the losing options are acknowledged, not omitted.
    A source's position is stated as the source stated it. Do not add a
    qualifier the source did not use, and do not drop the sentence that closes
    the option.
21. Every major judgment names its falsifier, the condition or the information
    that would change it. A judgment with no stated falsifier is not finished.
    A judgment that is not empirical names instead what would have to change
    for it to stop holding: the premise, the policy, or the finding it rests
    on. A falsifier that restates the reasoning is not a falsifier.
22. No session context, chat log, or raw source text is pasted into the
    report; every fact appears as transformed notes with its source recorded.
    The step 3 notes exist as their own file beside the report, named
    `<report-name>.notes.md`, and every fact in the report traces to a line in
    it that names the source. No notes file is a fail. The remedy is
    returning to step 3 and writing the notes from the sources; a notes file
    written by copying facts back out of the finished report still fails.
    A criterion, a weight, or a matrix cell traces to a notes line whose source
    is the analysis handover. One that traces to no such line was manufactured
    while drafting, and it fails this check. The remedy is the send-back in
    step 5, never a line added to the notes to cover it.
    A 40-plus-word span from the operator's materials that also appears in the
    report or its notes file, whitespace and case normalized, fails unless
    this check is scored `not-met` with the deviation recorded. A clause that
    reaches the report by way of the notes is still pasted, and `[sic]` does
    not hide it. A file the checker cannot read, a PDF among them, fails the
    run: extract its text beside it and run again. An operator instruction can
    authorise the paste; it cannot excuse recording it, and an
    `## Attachment:` section gets no exemption.
23. Every check this report does not meet appears in the deviations block as
    its own entry, with its authorising rule quoted and what the reader loses.
    Score every check on the scoreboard first, then transcribe. The checker
    fails when the not-met rows and the entries differ in count, or when a
    row's quoted rule does not appear in its entry. An entry with no quoted
    authoriser fails this check. This check does not apply to itself. Where
    every other check passes, leave the deviations block out: an absent block
    is what a clean report looks like, not a fail.

## Sensitivity test

Run right after the second key assumptions check.

1. Name the few critical items of evidence the conclusion leans on hardest.
2. For each, write one line: "if X is wrong, Y breaks".
3. If the whole conclusion breaks on one item, that item is a single point of
   failure: say so in the report, and treat that item's own reliability as
   load-bearing.
