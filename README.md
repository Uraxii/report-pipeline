# create-report

A skill that drafts a report for a reader who was not in the session: a
decision-maker, a client, or a reviewer reading alone. It covers planning,
structure, style, evidence, and a review checklist, and it never analyzes
data itself, only writes up analysis you give it.

Ships as an agent-skill plugin for Claude Code, GitHub Copilot CLI, and
Codex.

## Install

Claude Code:

```
/plugin marketplace add Uraxii/create-report
/plugin install create-report@create-report
```

Copilot CLI:

```
copilot plugin marketplace add Uraxii/create-report
copilot plugin install create-report@create-report
```

Codex: `/plugins`, add this repo as a marketplace (it carries
`.agents/plugins/marketplace.json`), install `create-report`.
