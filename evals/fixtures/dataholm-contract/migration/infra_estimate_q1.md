# Migration estimate — analytics workload off Dataholm

Author: Priya, platform infra. Dated 2026-02-27.

Asked to size a move to a self-hosted stack. This is a first pass and I want
to be upfront that it is soft.

**Effort: somewhere between 9 and 26 engineer-weeks.** The spread is that wide
because of three things I could not resolve in the time I had:

1. I do not know how many of the 340 saved queries are actually in use. If it
   is the 40 or so I can see traffic on, this is the low end. If finance
   really does depend on the long tail, it is the high end.
2. The custom UDFs are the risk. There are 14. I looked at four. Two ported
   in an afternoon, one needs a rewrite, one I could not work out at all.
3. We have never done a migration of this shape here, so I have no internal
   benchmark to calibrate against. The 9-to-26 range is my judgement, not a
   model.

**Run cost after migration: $9,000 to $14,000 a month**, mostly compute. That
number I am more comfortable with, it is the same shape as the workloads we
already run, though it excludes the engineer time to keep it alive.

I would not treat the effort number as decision-grade without two more weeks
of query-usage analysis.
