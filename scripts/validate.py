#!/usr/bin/env python3
"""Sanity checks for the repo. Exits non-zero on any problem.

- every skill folder (third-party and custom) has a SKILL.md with `name` and `description` frontmatter
- every custom agent has `name` and `description` frontmatter
- every vendored skill in the manifest exists on disk and its source is in the lock file
- every symlink in .claude/skills and .claude/agents resolves
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def frontmatter_keys(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    return set(re.findall(r"^([A-Za-z_][\w-]*):", m.group(1), re.M))


def check_frontmatter(path, required=("name", "description")):
    keys = frontmatter_keys(path)
    rel = path.relative_to(ROOT)
    if keys is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return
    for k in required:
        if k not in keys:
            errors.append(f"{rel}: frontmatter missing '{k}'")


def main():
    manifest = json.loads((ROOT / "skills" / "manifest.json").read_text())
    lock_path = ROOT / "skills" / "skills.lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else {"sources": {}}

    for source in manifest["sources"]:
        base = ROOT / "skills" / "third-party" / source["repo"].replace("/", "__")
        vendored = [s for s in source["skills"] if s.get("vendor", True)]
        if vendored and source["repo"] not in lock["sources"]:
            errors.append(f"{source['repo']}: not in skills.lock.json (run scripts/sync_skills.py)")
        for skill in vendored:
            skill_md = base / skill["name"] / "SKILL.md"
            if not skill_md.is_file():
                errors.append(f"{skill_md.relative_to(ROOT)}: missing")
            else:
                check_frontmatter(skill_md)

    for d in (ROOT / "skills" / "custom").iterdir():
        if d.is_dir():
            if (d / "SKILL.md").is_file():
                check_frontmatter(d / "SKILL.md")
            else:
                errors.append(f"{d.relative_to(ROOT)}: missing SKILL.md")

    for f in (ROOT / "agents" / "custom").glob("*.md"):
        check_frontmatter(f)

    for link_dir in (ROOT / ".claude" / "skills", ROOT / ".claude" / "agents"):
        if link_dir.exists():
            for entry in link_dir.iterdir():
                if entry.is_symlink() and not entry.exists():
                    errors.append(f"{entry.relative_to(ROOT)}: broken symlink")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("ok")


if __name__ == "__main__":
    main()
