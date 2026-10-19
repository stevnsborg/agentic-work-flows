# Custom skills

Skills written for this repo. Each skill is a folder with a `SKILL.md`. That file has YAML frontmatter (`name`, `description`) followed by the instructions.

To add one:

```bash
cp -r skills/custom/_template skills/custom/<skill-name>
# edit SKILL.md, set `name: <skill-name>`
python3 scripts/link.py && python3 scripts/validate.py
```

Folders whose name starts with `_` are templates. They are never linked into `.claude/`.
