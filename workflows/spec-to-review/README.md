# Workflow: spec-to-review

**Goal:** take a feature from rough idea to a reviewed, PR-ready change.

**Trigger:** manually, by running `/awf:feature-workflow` (or `/feature-workflow` inside this repo).

## Building blocks

| Kind  | Name | Role in this workflow |
|-------|------|-----------------------|
| skill | feature-workflow | Orchestrates the steps below |
| skill | grill-me | Pressure-test the idea before planning |
| agent | spec-planner | Explore the code and produce the plan |
| skill | tdd | Implement in red-green-refactor steps |
| agent | code-reviewer | Review the diff for defects |
| skill | pre-pr-check | Final checklist before the PR |

## Steps

1. Clarify scope with `grill-me`.
2. Plan with `spec-planner`; the user approves.
3. Implement with `tdd`.
4. Review with `code-reviewer`; fix blockers.
5. Run `pre-pr-check`.

## Inputs / outputs

- **Inputs:** a feature idea.
- **Outputs:** tested code, a review result, and a ready/blocked verdict.
