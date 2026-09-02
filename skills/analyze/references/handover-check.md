# handover-check.md: the step 9 gate

Run this against the assembled handover before you hand it over. This file is
process, not precept. Work it top to bottom.

The handover contract is stated once, in SKILL.md. This file re-applies it as a
gate. A contract nobody re-checks is a contract an agent skips without noticing,
and the handover looks complete either way.

Every check is pass or fail. A fail is a fix, not a note: go back to the step
the check names, produce the missing thing, and run the check again. Each
verdict goes into handover section 12; SKILL.md states what that section
holds.

## The checks

1. All twelve sections of the handover contract carry content. Count them
   against SKILL.md. A section that does not apply is named, with the reason
   it does not apply. Section 1 records who approved the problem statement, or
   records that approval was not sought. A handover with no section 12 fails
   here.
   Protects the contract. Failing it means the handover is missing a section
   the consumer needs, so write that section before handing over. Eleven
   sections and a silence is the failure this gate exists to catch.

2. The criteria set is marked frozen, the freeze is dated before the option set
   was written, and the frozen set has the same members now that it had at the
   freeze. Compare the two lists item by item.
   Protects the ordering that keeps criteria honest. Failing it means a
   criterion arrived after the options did, which is how a favourite gets
   rescued. Remove the late criterion and score the matrix again without it.

3. Every evaluation criterion carries all five parts, a weight, one line of
   rationale for that weight, a direction, and a normalization scheme. The
   weights sum to 100 percent.
   Protects a scoring anyone else can re-run. Failing it means the reader
   cannot reproduce a single cell. Complete the criterion; a weight with no
   rationale is a preference wearing a number.

4. Every option carries a pass or fail screening verdict with its reason,
   including the options that were dropped.
   Protects the record of what was ruled out. Failing it means a dropped option
   left no trace and the field looks smaller than it was. Write the verdict.

5. No option that failed a mandatory criterion was carried into the matrix with
   a low score. Each one was dropped, with the criterion it failed recorded.
   Protects the floor against compensability. Failing it means a disqualified
   option bought its way back on unrelated strengths. Drop it and rebuild the
   matrix.

6. Each surviving option was measured against every criterion's benchmark on
   its own, and section 7 shows that measurement before section 8 compares
   anything.
   Protects the measurement from the comparison. Failing it means the winner
   came out of a field rather than out of a benchmark, so redo the per-option
   analysis before you trust the matrix.

7. The matrix shows an unweighted total and a weighted total for every option.
   Both, per option.
   Protects the reader's ability to see what the weights did. Failing it means
   the weights are doing invisible work. Compute the missing total.

8. The weight re-run is recorded: the different weights used, the totals under
   them, and whether the ranking held.
   Protects against a ranking that only exists at one weighting. Failing it
   means nobody knows how fragile the result is. Run it and record the answer.

9. The option-set re-run is recorded: each non-winning option dropped in turn,
   the matrix recomputed, and whether the ranking of the remaining options
   changed. Any change is disclosed in section 11.
   Protects against rank reversal, which nothing else in this skill guards.
   Failing it means a ranking that a bookkeeping choice could flip went out
   undisclosed. Run it. "No reversal" is a claim only after you have looked.

10. Every major judgment carries three separate things: a likelihood band from
    the ladder printed at the head of section 9, a confidence stated in its own
    sentence, and a falsifier. Read each judgment line and find all three.
    Protects the reader from a number that hides how much it is worth. Failing
    it means an inference is dressed as a fact. A judgment missing any of the
    three is not finished; finish it or cut it.

11. Every assumption is marked as an assumption and states what follows if it
    is wrong. Critical assumptions are marked as critical.
    Protects the reader from inheriting a premise nobody flagged. Failing it
    means the analysis rests on something invisible, so write the consequence
    line before handing over.

12. The method log records both key-assumptions-check runs, the
    evidence-sensitivity output, and keeps two halves apart: escalation methods
    with the trigger that fired, challenge techniques with who named them.
    Protects the difference between what the question demanded and what the
    operator asked for. Failing it means an auto-routed method reads as
    operator-requested. Split the halves and add the missing output.

13. Where the authorizing party issued no guidance on what counts as acceptable
    or suitable, the handover names that absence, writes down the standard used
    instead, and marks that standard as your own. The affected stakeholders'
    objectives sit beside the screening verdict, never folded into it.
    Protects the reader from taking your standard for somebody else's. Failing
    it means a private judgment is passing as external guidance, which no
    reader can detect. Name the absence and label the standard.

14. The second-order pass ran on the recommended course: what changes for each
    actor listed in section 1, and which itemized constraints the course
    consumes. A restatement of the actor list with no stated change is a fail.
    Protects against a course whose cost lands on somebody who was never asked.
    Failing it means the recommendation is priced for the deciding organization
    alone. Name one concrete change per affected actor.

15. Exactly one course is recommended. Count the recommended courses; the answer
    is one. The losing options, the contrary evidence, and any surviving
    disagreement are handed over, not omitted. The thesis is one sentence, and
    section 11 states the matrix result in a paragraph a reader can follow
    without opening the matrix.
    Protects the decision-maker's job, which is to approve or disapprove.
    Failing it means the decision came back unmade. A sequenced package is one
    course only if it is named as one and its parts are ordered.

16. Each section is in the form its depth tier allows. At the cheap tier,
    sections 2, 3, 4, 6, 7, 8, 9 and 12 are tables or row sets, not
    paragraphs. Prose appears in section 1's environment and section 11's
    matrix result, and elsewhere only where a method escalated and its output
    fits no table.
    Protects the consumer from reading twelve essays for a decision worth a
    page. Failing it means the handover is padded, so convert the section to
    its table.

## What a fail looks like

One worked fail, so the shape is unmistakable. Check 10 against this judgment
line: "We have high confidence the vendor is very likely to miss the Q3 date."
One sentence, two axes, no falsifier. It fails on two counts. The fix is three
pieces: "The vendor misses the Q3 date: very likely, 80 to 95 percent." Then
"Confidence is low; the estimate rests on one unaudited status report." Then
"This changes if the vendor publishes a dated integration plan before June."
