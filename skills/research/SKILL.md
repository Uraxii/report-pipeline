---
name: research
description: >-
  Researches at three levels of rigor and names the level before any reading
  starts. Fires whenever a reply is about to cite a page from the web, which
  means storing the page and citing the stored copy instead of pasting a link.
  Fires when somebody wants one question looked up and answered from a few
  sources. Fires when material is being collected to feed analysis or a formal
  report, where the run hands over an audit trail a stranger can follow: one
  paraphrased fact per row, the document behind each one, what each document
  is weak at, and a log of everything opened including the dead ends. Not for
  weighing options, scoring them, or committing to a course, and not for
  writing the report.
---

## Name the mode before you open anything

Say which mode before the first search.

- **cite.** About to cite a web page in a reply.
- **lookup.** One question, a few sources, an answer. Load
  `references/lookup.md`.
- **full.** Material that feeds analysis or a formal report.

Pick by where the output ends up. Full whenever the run produces a file another
person or a later run opens. Lookup whenever the answer dies in this
conversation once the asker has read it. One page to put in front of somebody
is cite.

When documents disagree, or the answer needs somebody to weigh them, say so and
switch to full mode. Documents opened before escalating still get source-record
rows and consulted-log lines, shaped per `references/handover-tables.md`. Write
the collection plan after the fact, and say in the plan that you wrote it that
way.

In lookup and full, prefer the body that created or holds the data over anyone
reporting on it.

Hand lookup and full to a subagent when the asking thread has other work and
the harness offers one. Run cite inline. A delegated lookup returns the answer
plus the stored path of every document it cites.

## Meta-rule

Per-question operator instructions outrank every rule here. In full mode,
following an instruction against a rule here is a deviation, recorded in
contract item 8: load `references/deviation-block.md`. In cite and lookup,
state an override that drops the stored copy in the reply itself.

## Cite mode

1. Open the page and store it: the bytes, the retrieval path, the date, the
   licence terms.
2. Cite the stored copy: title, originator, date, and where the copy sits. A
   bare link is not a citation. Where the copy sits must be a path the reader
   can still open after this session ends, never a scratch path.
3. Take any quotation from the stored copy, never from memory and never from a
   summary of it.

No handover file, no collection plan, no check record.

## Full mode

### Words used in one sense only

- **Document.** The thing you opened and stored.
- **Originator.** The body or person that produced a document. A column, never
  a row.
- **Document id.** The short handle assigned when a document is first opened,
  written the same way in every table.
- **Judgment.** One of the three note kinds: fact, assumption, judgment.
  Nothing else here is called a judgment.

### The handover contract

Every full run hands over these eight, or names the ones that do not apply and
says why.

1. **The question.** The one question this collection answers, written before
   collecting, and the mode this run used. Where someone else set it, record
   their exact wording next to yours. A researchable question is specific,
   measurable, and free of a presumed answer, and it is settled with whoever
   asked before the work runs.
2. **The collection plan.** What evidence would answer the question, and what
   evidence would break it. Written before the first document is opened. Not
   what the answer hinges on: that needs an answer, and there is not one yet.
3. **Fact notes.** One row per fact.
4. **Source records.** One row per document. Provenance is columns here, not a
   second table.
5. **Contrary material.** What contradicts other material you collected, or
   contradicts what the plan expected to find. Each row cites the consulted-log
   line it came from.
6. **Consulted log.** Every document opened, dead ends included, one line each
   on what it yielded or why it did not. It has to let an experienced person
   who was not there work out what was done and what it produced.
7. **Gaps and the stop.** What was sought and refused, what could not be
   obtained, any claim you believe and cannot source, and which stopping
   condition ended the collection.
8. **Check record.** One row per check below, with its verdict. Never record a
   check you did not run: an unrun check is a verdict of not run. A check that
   stays failed carries a deviation block, and this item is where the block
   goes.

Hand it over as one Markdown file and name its path.

### The eight steps

Steps 3 to 7 run once per candidate document and repeat. Step 8 runs once.

Stop the loop when the next document would only add detail on what you hold,
or only add factors that change nothing. Keep going while it could still change
the value of a factor known to matter, or change which factors matter and how
they connect.

1. **Fix the question.** Narrow an area to one question you can answer. Do not
   write the answer down, even provisionally. Load
   `references/fixing-the-question.md`, in lookup mode too when the question
   does not fit in one sentence.
2. **Plan the collection.** Name what would answer the question and what would
   break it. Load `references/sources.md` to pick which document class could
   satisfy each requirement. Then decide what to go after first. Load
   `references/collection.md` and keep it open until the first document is
   stored.
3. **Find candidates.** Record where each candidate came from as you find it,
   not afterwards. Use `references/collection.md`.
4. **Open it and decide whether it is usable.** Skim before you take notes.
   Assign the document id here. Before writing the first table row, load
   `references/handover-tables.md`. A document you reject still gets a
   consulted-log line saying why. Cannot obtain it at all: load
   `references/refused.md`.
5. **Rate it.** Originator reliability and document credibility, separately,
   plus what it derives from, per `references/sources.md`.
6. **Take notes by transformation.** Understand the point, then write it in
   your own words. Quote only where the exact wording is itself the fact, and
   mark the quotation as one. Write facts, assumptions, and judgments as
   separately marked notes, never blended into a narrative.
7. **Store it** the way cite mode steps 1 and 3 do.
8. **Check and hand over.** Run the four checks, record the verdicts as
   contract item 8, and fix a fail rather than noting it. Only two things bar
   a fix: an operator instruction that overrides the check, or two rules here
   that collide with no wording satisfying both. A fail that is only tedious
   to clear is still a fail. Fix barred: load `references/deviation-block.md`.

### The four checks

1. **The join.** Every document id in the fact notes appears in the source
   records and in the consulted log. Fails when the same document is called
   three names.
2. **The licence.** No note carries a source's wording as its own, and no bytes
   are stored for a document whose terms forbid it.
3. **The stop.** Item 7 names the stopping condition that fired, plus every
   document sought and refused. An empty item 7 fails unless it states that
   nothing was refused and nothing was sought in vain.
4. **The marks.** Every note carries a kind mark, and the mark matches what the
   note says. A causal claim marked `fact` is a judgment.

## Gotchas

- **Judging while collecting.** No mode scores, ranks, weights, or states a
  likelihood. Cite and lookup state the answer the sources support, and
  escalate to full mode when a judgment is needed. Full mode also never
  chooses between anything, states a confidence level, or writes the answer.
- **Stacked evidence.** Go after the step 2 list of what would break the
  answer, not only what would support it.
- **Memory laundering.** Do not write a note you cannot trace to a stored
  document. Put an unsourced belief in item 7.
- **Copied wording.** Compare each paraphrase with its source open beside it.
- **Licence forbids keeping the bytes.** Do not quote or store them. Cite the
  document by title and section, say the text is not stored, and in full mode
  record the restriction in its row.
- **Circular reporting.** Two documents that both copied a third count as one.
  Fill `derives from` on every row.
- **The self-portrait.** An originator's own account of itself is not neutral.
  Discount it.
- **Confidence from volume.** End the loop by the stopping rule, not by the
  size of the pile.
- **The vivid case.** Record the aggregate next to a vivid single case, and
  say whether an anecdote is known to be typical.
- **The uncountable fact.** Do not drop a fact because it cannot be counted.
  Record it and say it resists measurement.

## Reference files

Each loads only at the mode or step above that names it.
