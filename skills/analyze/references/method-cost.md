# Cost, sensitivity, and value

## Cost sensitivity

Compute each cost element's percent share of the total, then test the
high-share elements as key drivers. Never pick by intuition.

Vary one input between its documented minimum and maximum, others at point
estimate, recompute the total, repeat. Rank inputs by how far each moves the
total. A factor is **sensitive** if a 10 to 50 percent change flips the
preferred option, **very sensitive** if under 10 percent does.

Trace every tested bound to a documented source: historical data, vendor
quote, or elicited expert bound. Never a subjective percentage. An expert
minimum and maximum with no historical backing: treat them as the 15th and
85th percentile and widen the tails.

## Cost range

Give each cost element a probability distribution, sum sampled elements over
many iterations, and report a cumulative distribution with the point estimate's
percentile marked.

Pick the shape by evidence: triangular for a three-point estimate with nothing
else known, lognormal for right skew with no upper bound, normal only for
symmetric variation, beta where analogous data show a biased tail, uniform only
where every value is equally likely.

Elements sharing a driver are correlated: assign a coefficient, 0.3 absent
better data.

Contingency is cost at the decision-maker's chosen confidence percentile minus
the point estimate, never a flat percentage. Down a work breakdown, allocate it
by each element's variance, not its cost, and make risk-adjusted children sum
to the risk-adjusted parent.

Nothing here runs a simulation. State that one is needed and what its output
must contain, and say plainly if it was not run.

## Benefit, cost, and discounting

- Normalize costs to one base year with a documented inflation index whose
  scope matches the item.
- Count incremental values only. Exclude sunk costs, already realized
  benefits, and pure transfers. Price inputs at opportunity cost, not budgeted
  outlay.
- Real rate with constant dollars, nominal rate with nominal dollars, never
  mixed.
- Discount every future benefit and cost, nonmonetized ones included. Produce a
  year-by-year table of cost, benefit, discount factor, and present value,
  summed. A stream accruing through the year takes a mid-year factor.
- Public investment and regulatory analysis: the published real rate.
  Cost-effectiveness and internal investment work: Treasury borrowing rates
  matched to the analysis term. Public expenditure: the published
  excess-burden multiplier. Look up each current value before use, never from
  memory.
- Net present value is discounted benefits minus discounted costs. Negative is
  a rejection signal. Recompute it at alternate discount rates and report the
  range.
- Benefits identical across options, or mandated by policy: switch to
  cost-effectiveness and report the lowest present-value life-cycle cost for
  that benefit level.
- Value not fully monetizable: still enumerate and quantify every benefit and
  cost type, and report a supplementary effectiveness measure, not prose.
- Name the sources of uncertainty and report a probability-weighted expected
  value or a full distribution, never a bare point estimate. Worst case
  reported beside expected value: state why and the direction of its bias.
- Every option carries a life-cycle cost estimate. Select principally on net
  present value, with a stated confidence range and a documented sensitivity
  analysis of cost and benefit against the key risks.
