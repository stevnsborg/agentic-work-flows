#!/usr/bin/env python3
"""Rebuild .claude/skills and .claude/agents as relative symlinks.

Claude Code discovers project skills in .claude/skills/<name>/SKILL.md and
subagents in .claude/agents/<name>.md. The real files live in skills/ and
agents/; this script exposes them. Run it after sync_skills.py or after adding
a custom skill/agent.

Folders and files whose name starts with `_` (templates) are skipped.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills" / "manifest.json"
CLAUDE = ROOT / ".claude"


def skill_targets():
    """Yield (link name, target dir) for every vendored and custom skill."""
    manifest = json.loads(MANIFEST.read_text())
    for source in manifest["sources"]:
        base = ROOT / "skills" / "third-party" / source["repo"].replace("/", "__")
        for skill in source["skills"]:
            if skill.get("vendor", True):
                yield skill.get("alias", skill["name"]), base / skill["name"]
    for d in sorted((ROOT / "skills" / "custom").iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            yield d.name, d


def agent_targets():
    for f in sorted((ROOT / "agents" / "custom").glob("*.md")):
        if not f.name.startswith("_"):
            yield f.name, f


def rebuild(link_dir, targets):
    link_dir.mkdir(parents=True, exist_ok=True)
    for entry in link_dir.iterdir():
        if entry.is_symlink():
            entry.unlink()
    seen = {}
    for name, target in targets:
        if name in seen:
            sys.exit(f"error: name clash in {link_dir.name}: '{name}' -> {seen[name]} and {target}")
        if not target.exists():
            sys.exit(f"error: {target} missing (run scripts/sync_skills.py?)")
        seen[name] = target
        (link_dir / name).symlink_to(os.path.relpath(target, link_dir))
    print(f"{link_dir.relative_to(ROOT)}: {len(seen)} links")


def main():
    rebuild(CLAUDE / "skills", skill_targets())
    rebuild(CLAUDE / "agents", agent_targets())


if __name__ == "__main__":
    main()
