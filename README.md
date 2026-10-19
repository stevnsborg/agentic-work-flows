# agentic-work-flows

This repo holds the skills, agents and workflows used across this account's projects. Third-party skills are vendored and pinned. Custom skills, agents and workflows live next to them.

## Layout

```
skills/
  manifest.json            # which third-party skills to vendor, and from where
  skills.lock.json         # pinned upstream commit per source (generated)
  third-party/<owner>__<repo>/<skill>/   # vendored copies; never edit by hand
  custom/<skill>/          # skills written here (start from custom/_template)
agents/
  custom/<agent>.md        # subagent definitions (start from custom/_template.md)
workflows/
  <workflow>/README.md     # multi-step processes combining skills + agents
.claude/
  skills/, agents/         # generated symlinks so Claude Code picks everything up in this repo
  settings.json
scripts/
  sync_skills.py           # vendor / update third-party skills
  link.py                  # rebuild .claude/ symlinks
  validate.py              # frontmatter + link checks (also run in CI)
```

## Installed skills

| Skill | Source | License | What it does |
|---|---|---|---|
| `grill-me` | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | Interviews you hard about a plan or design before you build it |
| `handoff` | mattpocock/skills | MIT | Writes a handoff doc so another session or agent can continue the work |
| `tdd` | mattpocock/skills | MIT | Red-green-refactor test-driven development loop |
| `to-spec` | mattpocock/skills | MIT | Turns a conversation into a written spec |
| `mp-code-review` | mattpocock/skills (`code-review`) | MIT | Two-axis review (standards + spec) of a diff |
| `diagnosing-bugs` | mattpocock/skills | MIT | Structured bug diagnosis loop |
| `caveman` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Apache-2.0 | Terse output mode that cuts tokens and keeps the technical facts |
| `caveman-commit` | JuliusBrussee/caveman | Apache-2.0 | Terse commit messages |
| `caveman-review` | JuliusBrussee/caveman | Apache-2.0 | Terse code review |
| `caveman-compress` | JuliusBrussee/caveman | Apache-2.0 | Compresses memory/prompt files such as CLAUDE.md |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer) | MIT | Removes signs of AI-generated writing from prose |
| `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 | Create, evaluate and improve skills |
| `mcp-builder` | anthropics/skills | Apache-2.0 | Guide for building MCP servers |

**Listed but not vendored:** Anthropic's `docx`, `pdf`, `pptx` and `xlsx` are proprietary ("all rights reserved"), so this repo can't redistribute them. They are recorded in `skills/manifest.json` with `"vendor": false`. Install them yourself with `npx skills add anthropics/skills --skill <name>`.

**Note on `mp-code-review`:** it is linked under a different name so it doesn't shadow Claude Code's built-in `/code-review`. Its upstream frontmatter still says `name: code-review`.

## Common tasks

```bash
# Update all third-party skills to the latest upstream commit
python3 scripts/sync_skills.py --update && python3 scripts/link.py && python3 scripts/validate.py

# Add a third-party skill: add an entry to skills/manifest.json, then
python3 scripts/sync_skills.py --source owner/repo && python3 scripts/link.py

# Add a custom skill / agent / workflow
cp -r skills/custom/_template skills/custom/<name>
cp agents/custom/_template.md agents/custom/<name>.md
cp -r workflows/_template workflows/<name>
python3 scripts/link.py && python3 scripts/validate.py
```

## Using these in another project

Inside this repo, Claude Code picks everything up through `.claude/`. To use the skills elsewhere:

- **Per user:** symlink a skill folder into `~/.claude/skills/`, for example
  `ln -s "$PWD/skills/third-party/mattpocock__skills/grill-me" ~/.claude/skills/grill-me`.
- **Per project:** copy the skill folder into that project's `.claude/skills/`.
