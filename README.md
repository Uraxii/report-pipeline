# report-pipeline

Three independent skills for a research-to-report pipeline: `research`
gathers material and its sources, `analyze` turns that material into a
framed decision, and `create-report` drafts the report for a reader who
was not in the session: a decision-maker, a client, or a reviewer reading
alone. Each skill covers its own step in full, and only its own step.

Ships as an agent-skill plugin for Claude Code, GitHub Copilot CLI, and
Codex.

## Install

Claude Code:

```
/plugin marketplace add Uraxii/report-pipeline
/plugin install report-pipeline@report-pipeline
```

Copilot CLI:

```
copilot plugin marketplace add Uraxii/report-pipeline
copilot plugin install report-pipeline@report-pipeline
```

Codex:

```
codex plugin marketplace add Uraxii/report-pipeline
codex plugin add report-pipeline@report-pipeline
```

Codex reads `.agents/plugins/marketplace.json`, which pins the `main` branch.
You can also add the marketplace from the `/plugins` screen in the Codex TUI.
