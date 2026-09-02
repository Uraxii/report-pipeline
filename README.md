# report-pipeline

Three independent skills for a research-to-report pipeline: `research`
gathers material and its sources, `analyze` turns that material into a
framed decision, and `create-report` drafts the report for a reader who
was not in the session: a decision-maker, a client, or a reviewer reading
alone. Each skill covers its own step in full, and only its own step.

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
