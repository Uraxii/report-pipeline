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

# The anchor lives in .git/config, inside the checkout, so it catches an
# unsynchronised rename, not a hostile edit (remote and manifests changed
# together still pass).
if ! origin_url=$(git remote get-url origin 2>&1); then
	fail "cannot resolve repo name from git remote origin: $origin_url"
fi
repo_name=${origin_url%/}
repo_name=${repo_name%.git}
repo_name=${repo_name##*/}
[ -n "$repo_name" ] ||
	fail "cannot resolve repo name from git remote origin '$origin_url'"
[ "$repo_name" = "$plugin_name" ] ||
	fail ".claude-plugin/plugin.json name is '$plugin_name', want '$repo_name' (repo name via git remote origin, the external anchor)"

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

[ -f README.md ] || fail "missing README.md"

# Match the command form (`plugin marketplace add Uraxii/<name>`), not a
# bare 'Uraxii/<name>' token, so a profile link or prose mention can't
# either false-trip this or hide a missing install section.
marketplace_refs=$(grep -oE 'plugin marketplace add Uraxii/[A-Za-z0-9_.-]+' README.md |
	sed -E 's/^plugin marketplace add //' | sort -u || true)
[ -n "$marketplace_refs" ] ||
	fail "README.md has no 'plugin marketplace add Uraxii/<repo>' line (install section missing?)"
for ref in $marketplace_refs; do
	[ "$ref" = "Uraxii/$plugin_name" ] ||
		fail "README.md installs from '$ref', want Uraxii/$plugin_name"
done

# Match the command form (`plugin install <name>@<name>` / `plugin add
# <name>@<name>`), not a bare '<name>@<name>' string, so a pinned dependency
# version or an email address in prose can't false-trip this.
install_refs=$(grep -oE 'plugin (install|add) [A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+' README.md |
	awk '{print $NF}' | sort -u || true)
[ -n "$install_refs" ] ||
	fail "README.md has no 'plugin install/add <name>@<name>' command (install section missing?)"
for ref in $install_refs; do
	[ "$ref" = "$plugin_name@$plugin_name" ] ||
		fail "README.md installs '$ref', want $plugin_name@$plugin_name"
done

for skill_dir in skills/*/; do
	skill=$(basename "$skill_dir")
	skill_md="${skill_dir}SKILL.md"
	[ -f "$skill_md" ] || fail "missing $skill_md"
	grep -q "^name: $skill\$" "$skill_md" ||
		fail "$skill_md has no 'name: $skill' in its frontmatter"

	while IFS= read -r src; do
		for ref in $(grep -o 'references/[A-Za-z0-9_./-]*\.md' "$src" |
			sort -u); do
			[ -f "${skill_dir}${ref}" ] ||
				fail "$src points at $ref, which does not exist (dangling)"
		done
	done < <(find "$skill_dir" -type f -name '*.md')

	# Reverse check: every file in the skill besides SKILL.md must be named
	# by its references/... path in some OTHER .md file in the skill, or it
	# ships unreferenced. A file naming its own path does not count.
	while IFS= read -r file; do
		rel=${file#"$skill_dir"}
		grep -rqF --exclude="$(basename "$file")" -- "$rel" "$skill_dir" ||
			fail "$file is not referenced by any file in $skill_dir (orphan)"
	done < <(find "$skill_dir" -type f ! -name SKILL.md)

	# Load-moment check: a reference named only in SKILL.md's trailing
	# "## Reference files" catalog never gets loaded at the step that needs
	# it. Every reference file must be reachable from SKILL.md's body by
	# following pointers. Reachability is transitive, so a pair of files
	# that cite only each other stays unreached and fails.
	if [ -d "${skill_dir}references" ]; then
		grep -q '^## Reference files$' "$skill_md" ||
			fail "$skill_md has a references/ directory but no '## Reference files' heading, so the load-moment check cannot run"
		body=$(awk '/^## Reference files$/{exit} {print}' "$skill_md")
		reached=" "
		for file in "${skill_dir}references"/*.md; do
			rel=references/$(basename "$file")
			grep -qF -- "$rel" <<<"$body" && reached="$reached$rel "
		done
		# Fixed point: add any file a reached file names, until the
		# set stops growing. A file never seeds itself, so a
		# self-naming file gains nothing from naming itself.
		growing=1
		while [ "$growing" = 1 ]; do
			growing=0
			for file in "${skill_dir}references"/*.md; do
				rel=references/$(basename "$file")
				case "$reached" in *" $rel "*) continue ;; esac
				for src in $reached; do
					grep -qF -- "$rel" "${skill_dir}${src}" ||
						continue
					reached="$reached$rel "
					growing=1
					break
				done
			done
		done
		unreached=
		for file in "${skill_dir}references"/*.md; do
			rel=references/$(basename "$file")
			case "$reached" in *" $rel "*) continue ;; esac
			unreached="$unreached $rel"
		done
		[ -z "$unreached" ] ||
			fail "$skill does not reach these from SKILL.md's body by following pointers, so no step loads them:$unreached"

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
