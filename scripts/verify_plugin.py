#!/usr/bin/env python3
"""Check the plugin manifests, marketplace listings, README install
lines, and every skill's SKILL.md are internally consistent.

Checks: the four JSON manifests parse and carry their required fields;
the plugin name matches the git remote's repo name; the marketplace
and codex manifests point at real names, owners, and paths; the
.agents manifest's url and ref are right; the README's install
commands match the plugin name; and per skill, the frontmatter name
matches the folder, every references/*.md pointer resolves, no file
ships unreferenced, and every references/*.md file is reachable from
SKILL.md's body by following pointers.

Port of the former scripts/verify-plugin.sh. Run with no arguments
from anywhere in the repo.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NoReturn

REPO_ROOT = Path(__file__).resolve().parent.parent
GITHUB_OWNER = "Uraxii"

PLUGIN_JSON = Path(".claude-plugin/plugin.json")
MARKETPLACE_JSON = Path(".claude-plugin/marketplace.json")
CODEX_JSON = Path(".codex-plugin/plugin.json")
AGENTS_JSON = Path(".agents/plugins/marketplace.json")
README = Path("README.md")
# Same junk list as scripts/build-web-skill-zips.py, duplicated because that
# file's hyphenated name cannot be imported.
JUNK_NAMES = {"__pycache__", ".DS_Store"}

REFERENCE_LINK_RE = re.compile(r"references/[A-Za-z0-9_./-]*\.md")
MARKETPLACE_ADD_RE = re.compile(
    rf"plugin\s+marketplace\s+add\s+({GITHUB_OWNER}/[A-Za-z0-9_.-]+)"
)
PLUGIN_INSTALL_RE = re.compile(
    r"plugin\s+(?:install|add)\s+([A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+)"
)


def fail(message: str) -> NoReturn:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def key_path(keys: tuple[str | int, ...]) -> str:
    """('plugins', 0, 'source') -> 'plugins[0].source'."""
    written = ""
    for key in keys:
        if isinstance(key, int):
            written += f"[{key}]"
        else:
            written += f".{key}" if written else key
    return written


def manifest_field(manifest: Path, data: Any, *keys: str | int) -> Any:
    """One field out of a parsed manifest. A missing key or index names the
    manifest and the key path that is missing instead of raising."""
    found = data
    for depth, key in enumerate(keys, start=1):
        try:
            found = found[key]
        except (KeyError, IndexError, TypeError):
            fail(f"{manifest} has no {key_path(keys[:depth])}")
    return found


def is_junk(path: Path) -> bool:
    return path.name in JUNK_NAMES or path.suffix == ".pyc"


def skill_files(skill_dir: Path, pattern: str = "*") -> list[Path]:
    """Every file the skill ships, build junk (__pycache__, *.pyc, .DS_Store)
    left out: it is not shipped, so it is not an orphan either."""
    return sorted(
        p
        for p in skill_dir.rglob(pattern)
        if p.is_file() and not is_junk(p) and not any(is_junk(q) for q in p.parents)
    )


def load_json(manifest: Path) -> Any:
    path = REPO_ROOT / manifest
    if not path.is_file():
        fail(f"missing manifest: {manifest}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        fail(f"invalid JSON: {manifest}")


def load_manifests() -> dict[Path, Any]:
    manifests = [PLUGIN_JSON, MARKETPLACE_JSON, CODEX_JSON, AGENTS_JSON]
    return {manifest: load_json(manifest) for manifest in manifests}


def repo_name_from_git() -> str:
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    origin_url = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        fail(f"cannot resolve repo name from git remote origin: {origin_url}")

    name = origin_url
    while name.endswith(".git") or name.endswith("/"):
        name = name[:-4] if name.endswith(".git") else name[:-1]
    name = name.rsplit("/", 1)[-1]
    if not name:
        fail(f"cannot resolve repo name from git remote origin '{origin_url}'")
    return name


def check_plugin_name_matches_repo(plugin_name: str) -> None:
    repo_name = repo_name_from_git()
    if repo_name != plugin_name:
        fail(
            f"{PLUGIN_JSON} name is '{plugin_name}', want '{repo_name}' "
            "(repo name via git remote origin, the external anchor)"
        )


def check_marketplace(marketplace: dict, plugin_name: str) -> None:
    mkt_name = manifest_field(MARKETPLACE_JSON, marketplace, "name")
    if mkt_name == GITHUB_OWNER:
        fail(
            f"{MARKETPLACE_JSON} name is {GITHUB_OWNER}, collides with "
            "the dotai marketplace"
        )
    if mkt_name != plugin_name:
        fail(f"{MARKETPLACE_JSON} name is '{mkt_name}', want {plugin_name}")

    owner = marketplace.get("owner", {}).get("name", "")
    if not owner:
        fail(
            f"{MARKETPLACE_JSON} has no owner.name (Copilot rejects the "
            "manifest without it)"
        )

    source = manifest_field(
        MARKETPLACE_JSON, marketplace, "plugins", 0, "source"
    )
    if source != "./":
        fail(
            f"{MARKETPLACE_JSON} plugins[0].source is '{source}', want "
            "'./' (Copilot resolves it as a path)"
        )


def check_codex(codex: dict, plugin_name: str) -> None:
    codex_name = manifest_field(CODEX_JSON, codex, "name")
    if codex_name != plugin_name:
        fail(f"{CODEX_JSON} name is '{codex_name}', want {plugin_name}")

    codex_skills = manifest_field(CODEX_JSON, codex, "skills")
    skills_path = codex_skills[2:] if codex_skills.startswith("./") else codex_skills
    if not (REPO_ROOT / skills_path).is_dir():
        fail(f"{CODEX_JSON} skills path '{codex_skills}' does not exist")


def check_agents(agents: dict, plugin_name: str) -> None:
    url = manifest_field(AGENTS_JSON, agents, "plugins", 0, "source", "url")
    expected_url = f"https://github.com/{GITHUB_OWNER}/{plugin_name}.git"
    if url != expected_url:
        fail(f"{AGENTS_JSON} url is '{url}', want {expected_url}")

    ref = manifest_field(AGENTS_JSON, agents, "plugins", 0, "source", "ref")
    if ref != "main":
        fail(f"{AGENTS_JSON} ref is '{ref}', want main")


def check_readme_exists() -> Path:
    path = REPO_ROOT / README
    if not path.is_file():
        fail("missing README.md")
    if not os.access(path, os.R_OK):
        fail("cannot read README.md")
    return path


def check_readme_install_lines(readme_path: Path, plugin_name: str) -> None:
    text = readme_path.read_text()

    marketplace_refs = sorted(set(MARKETPLACE_ADD_RE.findall(text)))
    if not marketplace_refs:
        fail(
            f"{README} has no 'plugin marketplace add {GITHUB_OWNER}/<repo>' "
            "line (install section missing?)"
        )
    expected_marketplace_ref = f"{GITHUB_OWNER}/{plugin_name}"
    for ref in marketplace_refs:
        if ref != expected_marketplace_ref:
            fail(
                f"{README} installs from '{ref}', want "
                f"{expected_marketplace_ref}"
            )

    install_refs = sorted(set(PLUGIN_INSTALL_RE.findall(text)))
    if not install_refs:
        fail(
            f"{README} has no 'plugin install/add <name>@<name>' command "
            "(install section missing?)"
        )
    expected_install_ref = f"{plugin_name}@{plugin_name}"
    for ref in install_refs:
        if ref != expected_install_ref:
            fail(f"{README} installs '{ref}', want {expected_install_ref}")


def check_skill_frontmatter(skill_dir: Path, skill: str) -> Path:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        fail(f"missing {relpath(skill_md)}")
    lines = skill_md.read_text().splitlines()
    if f"name: {skill}" not in lines:
        fail(f"{relpath(skill_md)} has no 'name: {skill}' in its frontmatter")
    return skill_md


def check_dangling_references(skill_dir: Path) -> None:
    for md_file in skill_files(skill_dir, "*.md"):
        text = md_file.read_text()
        for ref in sorted(set(REFERENCE_LINK_RE.findall(text))):
            if not (skill_dir / ref).is_file():
                fail(
                    f"{relpath(md_file)} points at {ref}, which does not "
                    "exist (dangling)"
                )


def check_orphan_files(skill_dir: Path) -> None:
    all_files = skill_files(skill_dir)
    for file in sorted(all_files):
        if file.name == "SKILL.md":
            continue
        rel = file.relative_to(skill_dir).as_posix().encode()
        referenced = any(
            rel in other.read_bytes()
            for other in all_files
            if other.name != file.name
        )
        if not referenced:
            fail(
                f"{relpath(file)} is not referenced by any file in "
                f"{relpath(skill_dir)} (orphan)"
            )


def find_heading_body(skill_md: Path) -> str:
    """Text of SKILL.md before its '## Reference files' heading."""
    lines = skill_md.read_text().splitlines()
    try:
        heading_idx = lines.index("## Reference files")
    except ValueError:
        fail(
            f"{relpath(skill_md)} has a references/ directory but no "
            "'## Reference files' heading, so the load-moment check "
            "cannot run"
        )
    return "\n".join(lines[:heading_idx])


def reachable_references(
    body: str, skill_dir: Path, reference_files: list[Path]
) -> set[str]:
    """Fixed point: start from refs named in body, add any ref a
    reached file names, until the set stops growing."""
    reached = {
        f"references/{f.name}" for f in reference_files
        if f"references/{f.name}" in body
    }
    growing = True
    while growing:
        growing = False
        for f in reference_files:
            rel = f"references/{f.name}"
            if rel in reached:
                continue
            for src in list(reached):
                if rel in (skill_dir / src).read_text():
                    reached.add(rel)
                    growing = True
                    break
    return reached


def bare_references(skill_dir: Path, reference_files: list[Path]) -> list[str]:
    """references/*.md files also named elsewhere without the
    references/ prefix, which the reachability check cannot see."""
    bare = []
    for f in reference_files:
        pattern = re.compile(
            rf"(?:^|[^/A-Za-z0-9_.-]){re.escape(f.stem)}\.md", re.MULTILINE
        )
        for other in skill_files(skill_dir):
            if other.name != f.name and pattern.search(other.read_text()):
                bare.append(f.name)
                break
    return bare


def check_load_moment(skill_dir: Path, skill: str, skill_md: Path) -> None:
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return

    body = find_heading_body(skill_md)
    reference_files = sorted(references_dir.glob("*.md"))
    reached = reachable_references(body, skill_dir, reference_files)

    unreached = [
        f"references/{f.name}" for f in reference_files
        if f"references/{f.name}" not in reached
    ]
    if unreached:
        fail(
            f"{skill} does not reach these from SKILL.md's body by "
            f"following pointers, so no step loads them: {' '.join(unreached)}"
        )

    bare = bare_references(skill_dir, reference_files)
    if bare:
        fail(
            f"{skill} points at these without the references/ prefix, so "
            f"the load-moment check cannot see the pointer: {' '.join(bare)}"
        )


def check_skill(skill_dir: Path) -> None:
    skill = skill_dir.name
    skill_md = check_skill_frontmatter(skill_dir, skill)
    check_dangling_references(skill_dir)
    check_orphan_files(skill_dir)
    check_load_moment(skill_dir, skill, skill_md)


def main() -> None:
    manifests = load_manifests()
    plugin_name = manifest_field(PLUGIN_JSON, manifests[PLUGIN_JSON], "name")

    check_plugin_name_matches_repo(plugin_name)
    check_marketplace(manifests[MARKETPLACE_JSON], plugin_name)
    check_codex(manifests[CODEX_JSON], plugin_name)
    check_agents(manifests[AGENTS_JSON], plugin_name)

    readme_path = check_readme_exists()
    check_readme_install_lines(readme_path, plugin_name)

    skills_dir = REPO_ROOT / "skills"
    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        check_skill(skill_dir)

    print("OK: all checks passed")


if __name__ == "__main__":
    main()
