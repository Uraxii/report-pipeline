# Root cause of a single occurrence

Frame the problem as the unwanted condition or action, never the system that
detected it. "The alert did not fire" is a finding about monitoring, not the
problem.

Build an explicit causal chain: from the immediate cause, keep asking why that
cause existed until you reach one with implications beyond this occurrence.
Never stop at a bare human-error label or physical condition; go on to a
management, design, or training explanation.

Select exactly one direct cause, exactly one root cause, and up to three
contributing causes, each described specifically to this occurrence, not by
category label. The single root-cause label is earned only after contributing
causes were searched for and each accepted cause was corroborated. Stopping at
the first uncorroborated cause is the single-cause fallacy.

Each accepted cause needs two independent pieces of corroborating evidence.
Only one exists: document the alternative causes considered and why each was
accepted or rejected.

One worksheet per cause: mark it direct, contributing, or root, describe how
it relates to the occurrence, and pair it with its own corrective action.
Word each action so somebody else can verify it, naming the cause it
addresses.

## Technique by job

- **Causal factor analysis.** Long chains with several facets.
- **Change analysis.** Obscure cause. Take a comparable case that did not
  fail, list every difference regardless of apparent relevance, and examine
  each for a role in the failure.
- **Barrier analysis.** A physical or procedural barrier failed. Determine
  whether it worked as designed, was maintained and inspected, could be
  evaded, and whether the failure was foreseeable, and why the unwanted energy
  was present. Check identical barriers elsewhere for the same flaw.
- **Programmatic review.** Recurring or systemic problems. Name the control
  that was less than adequate, then the management element that let it fail:
  policy, planning, resource allocation, or verification.
- **Human performance evaluation.** Personnel implicated. Evaluate detection,
  understanding, action selection, and execution against a documented
  failure-mode list. "Personnel error" alone is not a finding.

A task people perform is under investigation: reenact it step by step with
the person who performs it, an observer checking against the written
procedure and recording discrepancies. Never reconstruct it from memory or
documents alone.

The occurrence recurs: reopen the original finding instead of starting fresh,
determine why its corrective action failed, and analyze the new occurrence
against the fixed case.
