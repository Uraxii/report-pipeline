# create-report

A skill that drafts a report for a reader who was not in the session: a
decision-maker, a client, or a reviewer reading alone. It covers planning,
structure, style, evidence, and a review checklist, and it never analyzes
data itself, only writes up analysis you give it.

Ships as an agent-skill plugin for Claude Code, GitHub Copilot CLI, and
Codex.

## Install

The repository is private, so every command below needs a GitHub login with
access to it.

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

Codex:

```
codex plugin marketplace add Uraxii/create-report
codex plugin add create-report@create-report
```

Codex reads `.agents/plugins/marketplace.json`, which pins the `main` branch.
You can also add the marketplace from the `/plugins` screen in the Codex TUI.
