# Comparing options and committing to one course

## Decision matrix

```
Criterion (weight):   Compliance(40) Cost(35) Restore(25)
Option A rank:        1 (40)         2 (70)   2 (50)
Option C rank:        2 (80)         1 (35)   1 (25)

Option A total:  5 unweighted, 160 weighted
Option C total:  4 unweighted, 140 weighted
```

Rank each option per criterion, lower rank preferred. Add ranks for the
unweighted total. Multiply each rank by its criterion's weight and add for the
weighted total. Say in the text where the judgment was subjective. Carry the
precision of the least precise input, and say so.

A high score on one criterion can offset a failing score on another above the
mandatory floor, and the total hides it.

## Weight re-run

Re-score under plausibly different weights: ones a reasonable person could
have argued for at step 5, never reverse-engineered to flip the answer. Move
the largest weight and the smallest, one at a time. Record whether the ranking
held.

```
Weight re-run
  Compliance 40 -> 30, Cost 35 -> 45:  ranking held, C ahead
  Compliance 40 -> 55, Cost 35 -> 25:  ranking flipped, A ahead
```

A flip under a defensible reweighting is a close call.

## Option-set check

Drop each non-winning option in turn and recompute. If the ranking of the
rest changes, that is rank reversal: disclose it in section 11. Section 8
carries this check.

## Breaking a tie

Level weighted totals: break on the criteria, not a fresh overall judgment. In
order:

1. The higher-weighted criterion where they differ.
2. The option that survives more alternative futures.
3. The option that consumes fewer constraints.

Label this ordering as a design decision where you use it.

## Committing

**Package.** An ill-structured problem may need several measures together or
in sequence. Name the package as one course, order its parts, and say which
comes first and what triggers the next. Independent parallel recommendations
are a menu.

**Close call.** Totals inside the noise, or the weight re-run flipped the
ranking: still name one, and in the same place:

- State that the margin is inside the noise.
- Name the observable that would break the tie. "Their Q4 incident
  postmortem, if it shows more than two Sev-1s" is one. "Further
  investigation" is not.
- Hand the runner-up over with what it would take to prefer it.

**Empty field.** Screening killed every option:

1. Record the screen each option failed.
2. Recommend the single change that would readmit an option, ordered as a
   course like a package.
3. Several changes would work: take the one cheapest to reach, with one line
   on why the others lose.
4. Section 8 says the matrix does not apply.

Never soften a screen to keep an option alive, and never hand over the empty
field with no course attached.

## Second-order pass

On the recommended course only. Per actor in the frame, name one concrete
change once the course is taken. Per constraint, say whether the course
consumes it.

## Section 11

Write the thesis now, after the comparison. The matrix-result paragraph names
the winner, the margin, the deciding criteria, and where judgment was
subjective. The losing options go over with their scores and why they lost.
Name surviving disagreement rather than smoothing it away, and include
everything in the fact notes that cuts against the recommendation.
