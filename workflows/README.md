# Workflows

Agentic workflows are repeatable, multi-step processes that combine skills and agents to get a job done. Examples: "spec → tickets → TDD implementation → review", or "draft → humanize → caveman-compress".

Each workflow gets its own folder:

```
workflows/
  <workflow-name>/
    README.md      # goal, trigger, steps, which skills/agents it uses
    prompt.md      # optional: the kickoff prompt / slash-command body
    *.yml          # optional: CI / scheduled automation that runs it
```

Start from the template:

```bash
cp -r templates/workflow workflows/<workflow-name>
```

Claude Code workflow scripts (`.js` files) placed directly in this folder ship in the `awf` plugin.
