# Custom skills

Skills written for this repo. Each skill is a folder with a `SKILL.md`. That file has YAML frontmatter (`name`, `description`) followed by the instructions.

To add one:

```bash
cp -r templates/skill skills/custom/<skill-name>
# edit SKILL.md, set `name: <skill-name>`
python3 scripts/link.py && python3 scripts/validate.py
```

Every folder here with a `SKILL.md` ships in the `awf` plugin, so keep drafts out of this folder.
