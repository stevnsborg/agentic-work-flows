---
name: my-agent
description: When Claude should delegate to this agent. Be specific, e.g. "Use after code changes to review for security issues."
tools: Read, Grep, Glob, Bash   # omit to inherit all tools
model: inherit                  # or sonnet / opus / haiku
# skills: grill-me, caveman     # optional: skills preloaded into this agent's context
---

You are a ... (system prompt for the subagent).

## Responsibilities

- ...

## Process

1. ...

## Output format

Describe exactly what to return to the main agent.
