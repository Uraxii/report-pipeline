# Criteria

## Screening criteria

Pass or fail, never a score. Five categories:

- **Feasible.** Fits within available resources.
- **Acceptable.** Worth the cost or the risk.
- **Suitable.** Solves the problem, and is legal and ethical.
- **Distinguishable.** Differs significantly from the other options.
- **Complete.** Contains the critical parts of solving the problem, start to
  finish.

Write each as a test against this problem's constraints list. "Feasible" is a
heading. "Fits inside the $340k FY26 infra line at C1" is a criterion.

Judge acceptable and suitable against guidance from the authorizing party, not
your own judgment. No such guidance issued:

1. Name the absence in the handover.
2. Write down the standard you actually used.
3. Mark it as your own.

List the objectives of the stakeholders the decision lands on, from the actor
table, beside the screening verdict. Never fold them into it.

## Evaluation criteria

Five parts, all required.

```
Short title:      Restore time
Definition:       Wall-clock hours to restore the full archive from cold
Unit of measure:  Hours
Benchmark:        4 hours, the RTO in the DR policy
Formula:          Under 4 an advantage, over 4 a disadvantage. Less is better.
```

- Benchmark: the value defining the desired state. Set it by reasoning,
  historical precedent, or a current example, never by averaging the options.
  A benchmark that honestly lands on one option's value: say why.
- Formula: how a change in value changes desirability, comparative ("less is
  better") or absolute ("in-region beats out-of-region").

## Direction and normalization, before any score

State per criterion whether it is minimized or maximized.

Normalize criteria in different units to one common scale before combining,
and name the scheme as your choice. Qualitative bands: define every band with
an explicit threshold before scoring anything.

```
Compliance posture
  High   (3)  Meets the DPA and the retention schedule with no exception
  Medium (2)  Meets the DPA, needs a documented retention exception
  Low    (1)  Requires a DPA amendment
```

## Mandatory criteria

Mark each hard requirement as mandatory. It gates inside the matrix as well as
at screening.

## Weights

Weights sum to 100 percent, one line of rationale each. An operator weighting
instruction given in words is quoted as the rationale's source, never silently
turned into a number.

```
Criterion            Weight  Rationale
Compliance posture   40%     Operator: compliance matters more than money
Monthly cost         35%     Bounded by C1, the FY26 infra line
Restore time         25%     DR policy sets an RTO but tolerates overrun
```

## Freeze

Record the freeze point in the handover.

The operator handed over options before criteria existed:

1. Derive the criteria from step 2's problem frame and constraints list, not
   from the option material.
2. Freeze.
3. Then look at the options.
4. Say in the handover that the options arrived first and what you did.
