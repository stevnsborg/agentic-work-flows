---
name: pre-pr-check
description: Runs a checklist before opening a pull request. Use when the user says they are ready to commit, push, or open a PR, or asks "is this ready". Verifies tests, generated files, leftovers and the commit message.
---

# Pre-PR check

## Steps

1. Run `git status` and `git diff` against the base branch. Flag unrelated or accidental changes.
2. Run the project's validation and test commands (see CLAUDE.md). Report failures with their output.
3. Search the diff for leftovers: debug prints, `TODO`/`FIXME` added by this change, commented-out code, secrets.
4. Confirm generated files are current if the project generates any.
5. Check the commit message or PR description says why the change exists, not only what changed.

## Output

A checklist with pass/fail per item, then one line: "Ready" or the list of blockers. Do not fix anything unless asked.
