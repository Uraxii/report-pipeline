# Evidence and judgment lines

## Fact notes

```
Fact                                  Source              Kind
Onboarding completion 14% in Q1       accounts_2026q1.csv fact
Pricing drove the churn               cs_lead_note.md     judgment
Renewal terms hold through FY27       renewal_terms.md    assumption
```

- Your own words, never copied source text.
- One source per fact, named specifically enough to reopen.
- Record what cuts against the emerging answer as you find it, not at the end.

## Source assessment

```
Source        What it is       Strengths       Weaknesses        Carries
accounts.csv  Billing export   Complete, dated No usage data     J1, J3
cs_lead.md    One lead's note  Close to users  Never opened the  J2
                                               billing export
```

- Attach each source's weakness to the judgments resting on it.
- Judge a source by whether it discriminates, not by whether it agrees.
  Evidence that fits the leading answer and the alternatives equally well
  drops out of the reasoning.
- Give a single anecdote little weight unless it is known to be typical.
  Prefer aggregate data.
- Neither fully accept nor fully reject a source of uncertain reliability.
  Carry the uncertainty into the combined judgment.

## Assumptions register

```
Assumption                    Why held             If wrong      Critical
Renewal price holds at list   Contract clause 4.2  Cost flips    yes
Headcount flat through FY26   Verbal, unconfirmed  Timeline slip yes
```

## Key assumptions check

Ask of every premise:

- Would it still hold if the situation changed in the ways it plausibly could?
- What evidence would show it is already false?
- Who would disagree with it, and on what basis?

A premise that survives both runs but could still fail goes in the assumptions
register, not the fact notes.

## Evidence-sensitivity test

Step 8. Name the few items of evidence the conclusion leans on hardest. Per
item, write what breaks if it is wrong and whether the recommendation
survives. If the recommendation does not survive the loss of one item, say so
plainly.

## Likelihood and confidence

```
Almost no chance   01 to 05 percent
Very unlikely      05 to 20 percent
Unlikely           20 to 45 percent
Roughly even       45 to 55 percent
Likely             55 to 80 percent
Very likely        80 to 95 percent
Almost certain     95 to 99 percent
```

Confidence is what the evidence behind the number is worth: quality, quantity,
how much of it discriminates. Cap confidence at low when the judgment rests on
a small body of evidence of undeterminable representativeness, however
consistent it looks.

No empty hedging. "It would appear costs may rise" fails. "Costs are likely,
55 to 80 percent, to rise" passes.

Do not claim calibration.

## Falsifiers

Every major judgment names an observable that would change it. "More
analysis" is not a falsifier. "Completion timestamps clustered at or after the
churn dates" is.
