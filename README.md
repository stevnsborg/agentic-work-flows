# agentic-work-flows

This repo holds the skills, agents and workflows used across this account's projects. Third-party skills are vendored and pinned. Custom skills, agents and workflows live next to them.

## Use it with Claude Code

The repo is a Claude Code **plugin marketplace** called `stevnsborg`. It publishes the whole library as one plugin, `awf`. Once you install it, Claude sees every skill and agent in every project. It picks a skill automatically when your request matches the skill's description, and you can also call one directly, for example `/awf:grill-me`.

**On your machine (CLI, desktop app, IDE):** run this once, inside Claude Code:

```
/plugin marketplace add stevnsborg/agentic-work-flows
/plugin install awf@stevnsborg
```

You can also run `./scripts/install.sh` from a clone of this repo. Run `/plugin marketplace update stevnsborg` to pull new skills later. If the repo is private, your local git needs access to it.

**In a project, including cloud sessions on claude.ai/code:** cloud sessions don't read your personal settings. Merge [`templates/project-settings.json`](templates/project-settings.json) into that repo's `.claude/settings.json`. Anyone who opens the project, including cloud sessions, is then prompted to install the marketplace with the plugin enabled.

**Inside this repo:** nothing to install. The `.claude/skills` symlinks load everything without the `awf:` prefix.

## Layout

```
.claude-plugin/
  marketplace.json         # generated: publishes the library as the `awf` plugin
skills/
  manifest.json            # which third-party skills to vendor, and from where
  skills.lock.json         # pinned upstream commit per source (generated)
  third-party/<owner>__<repo>/<skill>/   # vendored copies; never edit by hand
  custom/<skill>/          # skills written here
agents/
  <agent>.md               # subagent definitions
workflows/
  <workflow>/README.md     # multi-step processes combining skills + agents
templates/                 # starters for skills, agents, workflows, project settings
.claude/
  skills/, agents/         # generated symlinks so Claude Code picks everything up in this repo
  settings.json
scripts/
  sync_skills.py           # vendor / update third-party skills
  link.py                  # rebuild .claude/ symlinks and the marketplace file
  validate.py              # frontmatter + link checks (also run in CI)
  install.sh               # install the plugin into your user settings
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

**Note on `code-review`:** inside this repo it is linked as `mp-code-review` so it doesn't shadow Claude Code's built-in `/code-review`. In the plugin it is namespaced as `awf:code-review`, so there's no clash.

## Common tasks

```bash
# Update all third-party skills to the latest upstream commit
python3 scripts/sync_skills.py --update && python3 scripts/link.py && python3 scripts/validate.py

# Add a third-party skill: add an entry to skills/manifest.json, then
python3 scripts/sync_skills.py --source owner/repo && python3 scripts/link.py

# Add a custom skill / agent / workflow
cp -r templates/skill skills/custom/<name>
cp templates/agent.md agents/<name>.md
cp -r templates/workflow workflows/<name>
python3 scripts/link.py && python3 scripts/validate.py
```

Push to `main`, then run `/plugin marketplace update stevnsborg` wherever the plugin is installed to pick up the changes.
