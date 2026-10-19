# Agents

Subagent definitions for Claude Code. Each one is a Markdown file: YAML frontmatter (`name`, `description`, and optionally `tools`, `model`, `skills`) followed by the agent's system prompt.

```
agents/
  custom/        # agents authored here; linked into .claude/agents/
```

To add one:

```bash
cp agents/custom/_template.md agents/custom/<agent-name>.md
python3 scripts/link.py && python3 scripts/validate.py
```

To use these agents in another project, copy or symlink the file into that project's `.claude/agents/`, or into `~/.claude/agents/` to make it available everywhere.
