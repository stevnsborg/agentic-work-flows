---
name: feature-workflow
description: Runs the full feature loop from idea to reviewed change. Use when the user asks to build a feature end to end, or says "run the feature workflow". Chains grill-me, spec-planner, tdd and code-reviewer.
disable-model-invocation: true
---

# Feature workflow

Take a feature from rough idea to a reviewed change. Stop and ask at each gate; do not skip ahead.

## Steps

1. **Clarify.** Use the `grill-me` skill to pressure-test the idea until the scope is settled.
2. **Plan.** Delegate to the `spec-planner` agent. Show the user the plan and get approval.
3. **Build.** Use the `tdd` skill: write a failing test, make it pass, refactor. Work in the plan's order.
4. **Review.** Delegate to the `code-reviewer` agent. Fix every blocking finding, then re-review.
5. **Check.** Run the `pre-pr-check` skill.

## Output

A short summary: what was built, tests added, review result, and anything left open.
