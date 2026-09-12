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

Claude web app:

The web app has no marketplace, so it cannot install this repo. Each
skill is a separate zip you upload by hand:

```
python3 scripts/build-web-skill-zips.py
```

This writes `dist/research.zip`, `dist/analyze.zip`, and
`dist/create-report.zip`. In the web app, go to Settings >
Capabilities > Skills and upload each zip one at a time.

`create-report` bundles a shell script, so its skill needs "Code
execution and file creation" turned on in Settings > Capabilities, or
the web app will not run it.
