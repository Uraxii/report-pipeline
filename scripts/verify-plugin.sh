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

mkt_name=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['name'])")
[ "$mkt_name" != "Uraxii" ] ||
	fail ".claude-plugin/marketplace.json name is Uraxii, collides with the dotai marketplace"
[ "$mkt_name" = "$plugin_name" ] ||
	fail ".claude-plugin/marketplace.json name is '$mkt_name', want $plugin_name"

owner=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json')).get('owner', {}).get('name', ''))")
[ -n "$owner" ] ||
	fail ".claude-plugin/marketplace.json has no owner.name (Copilot rejects the manifest without it)"

source=$(python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['source'])")
[ "$source" = "./" ] ||
	fail ".claude-plugin/marketplace.json plugins[0].source is '$source', want './' (Copilot resolves it as a path)"

codex_name=$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['name'])")
[ "$codex_name" = "$plugin_name" ] ||
	fail ".codex-plugin/plugin.json name is '$codex_name', want $plugin_name"

codex_skills=$(python3 -c "import json; print(json.load(open('.codex-plugin/plugin.json'))['skills'])")
[ -d "${codex_skills#./}" ] ||
	fail ".codex-plugin/plugin.json skills path '$codex_skills' does not exist"

agents_url=$(python3 -c "import json; print(json.load(open('.agents/plugins/marketplace.json'))['plugins'][0]['source']['url'])")
[ "$agents_url" = "https://github.com/Uraxii/$plugin_name.git" ] ||
	fail ".agents/plugins/marketplace.json url is '$agents_url', want https://github.com/Uraxii/$plugin_name.git"

agents_ref=$(python3 -c "import json; print(json.load(open('.agents/plugins/marketplace.json'))['plugins'][0]['source']['ref'])")
[ "$agents_ref" = "main" ] ||
	fail ".agents/plugins/marketplace.json ref is '$agents_ref', want main"

for ref in $(grep -o 'Uraxii/[A-Za-z0-9_.-]*' README.md | sort -u); do
	[ "$ref" = "Uraxii/$plugin_name" ] ||
		fail "README.md installs from '$ref', want Uraxii/$plugin_name"
done

for ref in $(grep -oE '[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+' README.md | sort -u); do
	[ "$ref" = "$plugin_name@$plugin_name" ] ||
		fail "README.md installs '$ref', want $plugin_name@$plugin_name"
done

for skill_dir in skills/*/; do
	skill=$(basename "$skill_dir")
	skill_md="${skill_dir}SKILL.md"
	[ -f "$skill_md" ] || fail "missing $skill_md"
	grep -q "^name: $skill\$" "$skill_md" ||
		fail "$skill_md has no 'name: $skill' in its frontmatter"

	for ref in $(grep -rho 'references/[A-Za-z0-9_./-]*\.md' "$skill_dir" | sort -u); do
		[ -f "${skill_dir}${ref}" ] ||
			fail "$skill points at $ref, which does not exist (dangling)"
	done

	# Reverse check: every file in the skill besides SKILL.md must be named
	# by its references/... path in some .md file in the skill, or it ships
	# unreferenced.
	while IFS= read -r file; do
		rel=${file#"$skill_dir"}
		grep -rqF -- "$rel" "$skill_dir" ||
			fail "$file is not referenced by any file in $skill_dir (orphan)"
	done < <(find "$skill_dir" -type f ! -name SKILL.md)

	# Load-moment check: a reference named only in SKILL.md's trailing
	# "## Reference files" catalog never gets loaded at the step that needs
	# it. Require one mention in the body above that heading, or in a
	# sibling reference file. A file naming itself does not count.
	if [ -d "${skill_dir}references" ]; then
		grep -q '^## Reference files$' "$skill_md" ||
			fail "$skill_md has a references/ directory but no '## Reference files' heading, so the load-moment check cannot run"
		body=$(awk '/^## Reference files$/{exit} {print}' "$skill_md")
		unreached=
		for file in "${skill_dir}references"/*.md; do
			rel=references/$(basename "$file")
			grep -qF -- "$rel" <<<"$body" ||
				grep -rqF --exclude="$(basename "$file")" \
					-- "$rel" "${skill_dir}references" ||
				unreached="$unreached $rel"
		done
		[ -z "$unreached" ] ||
			fail "$skill names these only in its trailing reference list, so no step loads them:$unreached"

		# Prefix check: the load-moment check above matches on the
		# references/ prefix, so a pointer written as a bare basename
		# leaves the file it names reading as unreached. Only a file's
		# own title may name it bare.
		bare=
		for file in "${skill_dir}references"/*.md; do
			base=$(basename "$file")
			if grep -rqE "(^|[^/A-Za-z0-9_.-])${base%.md}\.md" \
				--exclude="$base" -- "$skill_dir"; then
				bare="$bare $base"
			fi
		done
		[ -z "$bare" ] ||
			fail "$skill points at these without the references/ prefix, so the load-moment check cannot see the pointer:$bare"
	fi
done

echo "OK: all checks passed"
