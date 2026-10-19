#!/usr/bin/env python3
"""Vendor third-party skills listed in skills/manifest.json into skills/third-party/.

By default each source is fetched at the commit pinned in skills/skills.lock.json
(or the manifest `ref` if the source is not locked yet). Pass --update to move
to the latest commit on `ref` and rewrite the lock.

Usage:
    python3 scripts/sync_skills.py                     # sync everything at locked commits
    python3 scripts/sync_skills.py --update            # bump all sources to latest
    python3 scripts/sync_skills.py --source owner/repo # limit to one source
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills" / "manifest.json"
LOCK = ROOT / "skills" / "skills.lock.json"
THIRD_PARTY = ROOT / "skills" / "third-party"
IGNORE = shutil.ignore_patterns(".git", ".github", "__pycache__", ".DS_Store")


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch(repo, rev, dest):
    """Shallow-fetch `rev` (branch, tag or commit SHA) of a GitHub repo into dest."""
    run("git", "init", "-q", str(dest))
    run("git", "remote", "add", "origin", f"https://github.com/{repo}.git", cwd=dest)
    run("git", "fetch", "-q", "--depth", "1", "origin", rev, cwd=dest)
    run("git", "checkout", "-q", "FETCH_HEAD", cwd=dest)
    return run("git", "rev-parse", "HEAD", cwd=dest)


def source_dir(repo):
    return THIRD_PARTY / repo.replace("/", "__")


def copy_skill(checkout, skill, out):
    src = (checkout / skill["path"]).resolve()
    if not (src / "SKILL.md").is_file():
        sys.exit(f"error: {src.relative_to(checkout)} has no SKILL.md")
    if out.exists():
        shutil.rmtree(out)
    if "include" in skill:
        out.mkdir(parents=True)
        for item in skill["include"]:
            p = src / item
            if p.is_dir():
                shutil.copytree(p, out / item, ignore=IGNORE)
            elif p.is_file():
                shutil.copy2(p, out / item)
    else:
        shutil.copytree(src, out, ignore=IGNORE)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true", help="fetch latest commit on ref instead of the locked SHA")
    ap.add_argument("--source", help="only sync this owner/repo")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {"sources": {}}

    sources = manifest["sources"]
    if args.source:
        sources = [s for s in sources if s["repo"] == args.source]
        if not sources:
            sys.exit(f"error: {args.source} not in manifest")

    for source in sources:
        repo = source["repo"]
        locked = lock["sources"].get(repo, {})
        rev = source["ref"] if args.update or "commit" not in locked else locked["commit"]
        print(f"==> {repo} @ {rev}")

        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp) / "repo"
            sha = fetch(repo, rev, checkout)
            dest = source_dir(repo)

            # Drop skills that were removed from the manifest or marked vendor: false.
            wanted = {s["name"] for s in source["skills"] if s.get("vendor", True)}
            if dest.exists():
                for child in dest.iterdir():
                    if child.is_dir() and child.name not in wanted:
                        print(f"    - removing {child.name}")
                        shutil.rmtree(child)
            dest.mkdir(parents=True, exist_ok=True)

            for name in source.get("license_files", []):
                if (checkout / name).is_file():
                    shutil.copy2(checkout / name, dest / name)

            for skill in source["skills"]:
                if not skill.get("vendor", True):
                    print(f"    . {skill['name']} (not vendored)")
                    continue
                copy_skill(checkout, skill, dest / skill["name"])
                print(f"    + {skill['name']}")

        if locked.get("commit") != sha:
            lock["sources"][repo] = {"ref": source["ref"], "commit": sha, "synced": date.today().isoformat()}

    lock["sources"] = dict(sorted(lock["sources"].items()))
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")
    print(f"wrote {LOCK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
