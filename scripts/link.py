#!/usr/bin/env python3
"""Regenerate everything that exposes the library as a Claude Code plugin.

1. plugin/: a standard-layout copy of the library (skills/<name>/SKILL.md,
   agents/*.md, hooks/). Some loaders, such as the Claude desktop app, only
   find skills in this flat layout, so the plugin is served from here.
2. .claude-plugin/marketplace.json: makes this repo a plugin marketplace whose
   `awf` plugin lives in plugin/.

The real files live in skills/, agents/ and hooks/. plugin/ is generated and
never edited by hand. Run this after sync_skills.py or after adding or
changing a custom skill, agent or hook.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills" / "manifest.json"
PLUGIN = ROOT / "plugin"
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


def rel(path):
    return "./" + path.relative_to(ROOT).as_posix() + ("/" if path.is_dir() else "")


IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def skill_dirs(manifest):
    """(name, source dir) for every vendored and custom skill."""
    for base, skills in vendored_sources(manifest):
        for s in skills:
            yield s["name"], base / s["name"]
    for d in custom_skills():
        yield d.name, d


def build_plugin(manifest):
    """Copy skills, agents and hooks into plugin/ in the standard layout."""
    for sub in ("skills", "agents", "hooks"):
        shutil.rmtree(PLUGIN / sub, ignore_errors=True)
    seen = {}
    pairs = []
    for name, src in skill_dirs(manifest):
        if name in seen:
            sys.exit(f"error: skill name clash: '{name}' -> {seen[name]} and {src}")
        if not src.exists():
            sys.exit(f"error: {src} missing (run scripts/sync_skills.py?)")
        seen[name] = src
        shutil.copytree(src, PLUGIN / "skills" / name, ignore=IGNORE)
        pairs.append((src, PLUGIN / "skills" / name))
    (PLUGIN / "agents").mkdir(parents=True, exist_ok=True)
    for f in agents():
        shutil.copy2(f, PLUGIN / "agents" / f.name)
    if (ROOT / "hooks").is_dir():
        shutil.copytree(ROOT / "hooks", PLUGIN / "hooks", ignore=IGNORE)
        pairs.append((ROOT / "hooks", PLUGIN / "hooks"))
    note = ("# Generated plugin folder\n\n"
            "Built by `scripts/link.py` from `skills/`, `agents/` and `hooks/`. "
            "Do not edit; change the sources and re-run the script.\n")
    (PLUGIN / "README.md").write_text(note, encoding="utf-8")
    keep_exec_bits(pairs)
    print(f"plugin/: {len(seen)} skills, {len(agents())} agents")


def keep_exec_bits(pairs):
    """Windows copies lose the executable bit; restore it in the git index for files that had it."""
    for src, dest in pairs:
        try:
            out = subprocess.run(["git", "ls-files", "-s", "--", src.relative_to(ROOT).as_posix()], cwd=ROOT,
                                 capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return
        for line in out.splitlines():
            meta, path = line.split("\t", 1)
            target = dest / (ROOT / path).relative_to(src)
            if meta.split()[0] == "100755" and target.is_file():
                subprocess.run(["git", "update-index", "--add", "--chmod=+x", "--", target.relative_to(ROOT).as_posix()],
                               cwd=ROOT, check=False)


def write_marketplace():
    plugin = {
        "name": PLUGIN_NAME,
        "displayName": "Agentic Work Flows",
        "source": "./plugin",
        "description": "Vendored third-party skills (grill-me, caveman, humanizer, ...) plus custom skills and agents.",
        "license": "MIT (repo); vendored skills keep their upstream licenses",
    }
    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Mads Stevnsborg"},
        "description": "Skills, agents and agentic workflows library",
        "plugins": [plugin],
    }
    MARKETPLACE.parent.mkdir(exist_ok=True)
    MARKETPLACE.write_text(json.dumps(marketplace, indent=2) + "\n")
    print(f"{MARKETPLACE.relative_to(ROOT)}: plugin source ./plugin")


def main():
    manifest = json.loads(MANIFEST.read_text())
    build_plugin(manifest)
    write_marketplace()


if __name__ == "__main__":
    main()
