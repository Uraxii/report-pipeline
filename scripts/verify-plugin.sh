#!/usr/bin/env bash
# Checks the four plugin manifests parse, carry the required fields, and
# point at paths that exist. Run with no arguments from anywhere in the repo.
set -euo pipefail
cd "$(dirname "$0")/.."

fail() {
	echo "FAIL: $1" >&2
	exit 1
}

for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json \
	.codex-plugin/plugin.json .agents/plugins/marketplace.json; do
	[ -f "$f" ] || fail "missing manifest: $f"
	python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" ||
		fail "invalid JSON: $f"
done

plugin_name=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['name'])")
[ "$plugin_name" = "create-report" ] ||
	fail ".claude-plugin/plugin.json name is '$plugin_name', want create-report"

mkt_name=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['name'])")
[ "$mkt_name" != "Uraxii" ] ||
	fail ".claude-plugin/marketplace.json name is Uraxii, collides with the dotai marketplace"
[ "$mkt_name" = "create-report" ] ||
	fail ".claude-plugin/marketplace.json name is '$mkt_name', want create-report"

owner=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json')).get('owner', {}).get('name', ''))")
[ -n "$owner" ] ||
	fail ".claude-plugin/marketplace.json has no owner.name (Copilot rejects the manifest without it)"

source=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['source'])")
[ "$source" = "./" ] ||
	fail ".claude-plugin/marketplace.json plugins[0].source is '$source', want './' (Copilot resolves it as a path)"

codex_name=$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['name'])")
[ "$codex_name" = "create-report" ] ||
	fail ".codex-plugin/plugin.json name is '$codex_name', want create-report"

codex_skills=$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['skills'])")
[ -d "${codex_skills#./}" ] ||
	fail ".codex-plugin/plugin.json skills path '$codex_skills' does not exist"

agents_url=$(python3 -c "import json; print(json.load(open('.agents/plugins/marketplace.json'))['plugins'][0]['source']['url'])")
[ "$agents_url" = "https://github.com/Uraxii/create-report.git" ] ||
	fail ".agents/plugins/marketplace.json url is '$agents_url'"

agents_ref=$(python3 -c "import json; print(json.load(open('.agents/plugins/marketplace.json'))['plugins'][0]['source']['ref'])")
[ "$agents_ref" = "main" ] ||
	fail ".agents/plugins/marketplace.json ref is '$agents_ref', want main"

skill_md=skills/create-report/SKILL.md
[ -f "$skill_md" ] || fail "missing $skill_md"
grep -q '^name: create-report$' "$skill_md" ||
	fail "$skill_md has no 'name: create-report' in its frontmatter"

skill_md=skills/analyze/SKILL.md
[ -f "$skill_md" ] || fail "missing $skill_md"
grep -q '^name: analyze$' "$skill_md" ||
	fail "$skill_md has no 'name: analyze' in its frontmatter"

for ref in $(grep -o 'references/[A-Za-z0-9_.-]*\.md' "$skill_md" | sort -u); do
	[ -f "skills/analyze/$ref" ] ||
		fail "$skill_md points at skills/analyze/$ref, which does not exist"
done

echo "OK: all checks passed"
