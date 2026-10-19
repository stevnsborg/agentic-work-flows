#!/usr/bin/env python3
"""Regenerate everything that exposes the library to Claude Code.

1. .claude/skills and .claude/agents: relative symlinks so Claude Code picks up
   every skill and agent when it runs inside this repo.
2. .claude-plugin/marketplace.json: makes this repo a plugin marketplace, so
   any project can install the whole library as the `awf` plugin.

The real files live in skills/ and agents/. Run this after sync_skills.py or
after adding a custom skill/agent.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills" / "manifest.json"
CLAUDE = ROOT / ".claude"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

MARKETPLACE_NAME = "stevnsborg"
PLUGIN_NAME = "awf"


def vendored_sources(manifest):
    for source in manifest["sources"]:
        skills = [s for s in source["skills"] if s.get("vendor", True)]
        if skills:
            yield ROOT / "skills" / "third-party" / source["repo"].replace("/", "__"), skills


def custom_skills():
    return sorted(d for d in (ROOT / "skills" / "custom").iterdir() if (d / "SKILL.md").is_file())


def agents():
    return sorted((ROOT / "agents").glob("*.md"))


def skill_targets(manifest):
    """Yield (link name, target dir) for every vendored and custom skill."""
    for base, skills in vendored_sources(manifest):
        for skill in skills:
            yield skill.get("alias", skill["name"]), base / skill["name"]
    for d in custom_skills():
        yield d.name, d


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


def rel(path):
    return "./" + path.relative_to(ROOT).as_posix() + ("/" if path.is_dir() else "")


def write_marketplace(manifest):
    # The plugin's source is the repo root, so list exactly which folders hold
    # skills; anything else at the root (templates, scripts) is never loaded.
    skill_dirs = [rel(base) for base, _ in vendored_sources(manifest)]
    if custom_skills():
        skill_dirs.append(rel(ROOT / "skills" / "custom"))
    plugin = {
        "name": PLUGIN_NAME,
        "displayName": "Agentic Work Flows",
        "source": "./",
        "description": "Vendored third-party skills (grill-me, caveman, humanizer, ...) plus custom skills and agents.",
        "license": "MIT (repo); vendored skills keep their upstream licenses",
        "skills": skill_dirs,
    }
    agent_files = [rel(f) for f in agents()]
    if agent_files:
        plugin["agents"] = agent_files
    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Mads Stevnsborg"},
        "description": "Skills, agents and agentic workflows library",
        "plugins": [plugin],
    }
    MARKETPLACE.parent.mkdir(exist_ok=True)
    MARKETPLACE.write_text(json.dumps(marketplace, indent=2) + "\n")
    print(f"{MARKETPLACE.relative_to(ROOT)}: {len(skill_dirs)} skill dirs, {len(agent_files)} agents")


def main():
    manifest = json.loads(MANIFEST.read_text())
    rebuild(CLAUDE / "skills", skill_targets(manifest))
    rebuild(CLAUDE / "agents", ((f.name, f) for f in agents()))
    write_marketplace(manifest)


if __name__ == "__main__":
    main()
