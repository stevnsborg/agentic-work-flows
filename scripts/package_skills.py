#!/usr/bin/env python3
"""Package skills as ZIP files for upload to claude.ai (Customize > Skills).

Each ZIP holds one top-level folder named after the skill, as claude.ai
requires:  <name>.zip -> <name>/SKILL.md, scripts/, ...
Vendored skills also get their upstream LICENSE copied in if they lack one.

Usage:
    python3 scripts/package_skills.py                  # every vendored + custom skill
    python3 scripts/package_skills.py grill-me caveman # only these
    python3 scripts/package_skills.py --out some/dir   # default: dist/claude-ai
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills" / "manifest.json"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKIP = {"__pycache__", ".DS_Store", ".git"}
# Fixed timestamp so re-packaging unchanged skills gives identical ZIPs.
EPOCH = (1980, 1, 1, 0, 0, 0)


def all_skills():
    """Yield (name, skill dir, license files to add) for every packageable skill."""
    manifest = json.loads(MANIFEST.read_text())
    for source in manifest["sources"]:
        base = ROOT / "skills" / "third-party" / source["repo"].replace("/", "__")
        licenses = [base / f for f in source.get("license_files", []) if (base / f).is_file()]
        for skill in source["skills"]:
            if skill.get("vendor", True):
                yield skill["name"], base / skill["name"], licenses
    for d in sorted((ROOT / "skills" / "custom").iterdir()):
        if (d / "SKILL.md").is_file():
            yield d.name, d, []


def frontmatter(skill_md):
    """Return {'name': ..., 'description': ...} from SKILL.md, handling YAML block scalars."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", skill_md.read_text(encoding="utf-8"), re.S)
    if not m:
        return {}
    fields, key = {}, None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            fields[key] = "" if value in (">", "|", ">-", "|-") else value.strip("\"'")
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def check(name, skill_dir):
    fm = frontmatter(skill_dir / "SKILL.md")
    problems = []
    if fm.get("name") != name:
        problems.append(f"frontmatter name '{fm.get('name')}' must equal folder name '{name}'")
    if not NAME_RE.match(name) or len(name) > 64:
        problems.append("name must be lowercase letters, digits and hyphens, max 64 chars")
    desc = fm.get("description", "")
    if not desc:
        problems.append("missing description")
    elif len(desc) > 1024:
        problems.append(f"description is {len(desc)} chars (max 1024)")
    return problems


def write_zip(name, skill_dir, licenses, out_dir):
    out = out_dir / f"{name}.zip"
    files = sorted(p for p in skill_dir.rglob("*") if p.is_file() and not SKIP & set(p.parts))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        def add(path, arcname):
            info = zipfile.ZipInfo(f"{name}/{arcname}", EPOCH)
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, path.read_bytes())

        for p in files:
            add(p, p.relative_to(skill_dir).as_posix())
        for lic in licenses:
            if not (skill_dir / lic.name).exists():
                add(lic, lic.name)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skills", nargs="*", help="skill names to package (default: all)")
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "claude-ai")
    args = ap.parse_args()

    skills = list(all_skills())
    if args.skills:
        known = {s[0] for s in skills}
        unknown = set(args.skills) - known
        if unknown:
            sys.exit(f"error: unknown skill(s): {', '.join(sorted(unknown))}")
        skills = [s for s in skills if s[0] in args.skills]

    failed = False
    for name, skill_dir, _ in skills:
        for problem in check(name, skill_dir):
            print(f"error: {name}: {problem}")
            failed = True
    if failed:
        sys.exit(1)

    args.out.mkdir(parents=True, exist_ok=True)
    for name, skill_dir, licenses in skills:
        out = write_zip(name, skill_dir, licenses, args.out)
        print(f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}  ({out.stat().st_size // 1024} KB)")
    print(f"\nUpload at https://claude.ai/customize/skills (one ZIP per skill), then turn each skill on.")


if __name__ == "__main__":
    main()
