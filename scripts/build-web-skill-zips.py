#!/usr/bin/env python3
"""Build one upload-ready zip per skill for Claude's web app.

The web app has no marketplace install path: each skill must be
uploaded by hand as its own zip, with the skill's folder as the zip's
root entry (e.g. research.zip contains research/SKILL.md, not
skills/research/SKILL.md). See README.md for the upload steps.
"""
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DIST_DIR = REPO_ROOT / "dist"
JUNK_NAMES = {"__pycache__", ".DS_Store"}


def frontmatter_name(skill_md: Path) -> str:
    match = re.search(r"^name:\s*(\S+)\s*$", skill_md.read_text(), re.MULTILINE)
    if not match:
        sys.exit(f"{skill_md}: no `name:` field in frontmatter")
    return match.group(1)


def is_junk(path: Path) -> bool:
    return path.name in JUNK_NAMES or path.suffix == ".pyc"


def build_zip(skill_dir: Path) -> Path:
    name = frontmatter_name(skill_dir / "SKILL.md")
    if name != skill_dir.name:
        sys.exit(
            f"{skill_dir}: SKILL.md says name '{name}' but the folder "
            f"is '{skill_dir.name}' — the web app requires them to match"
        )
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"{name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir() or is_junk(path) or any(is_junk(p) for p in path.parents):
                continue
            zf.write(path, arcname=Path(name) / path.relative_to(skill_dir))
    return zip_path


def main() -> None:
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if (skill_dir / "SKILL.md").exists():
            zip_path = build_zip(skill_dir)
            print(
                f"Built {zip_path} — upload this one file for the "
                f"'{skill_dir.name}' skill in Claude's web app."
            )


if __name__ == "__main__":
    main()
