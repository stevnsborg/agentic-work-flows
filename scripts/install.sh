#!/usr/bin/env bash
# Install this library into your Claude Code user settings so every project
# (CLI, desktop, IDE) gets its skills and agents.
#
#   ./scripts/install.sh            # install from GitHub (stays updatable)
#   ./scripts/install.sh --local    # install from this checkout (for testing edits)
set -euo pipefail

MARKETPLACE="stevnsborg/agentic-work-flows"
if [[ "${1:-}" == "--local" ]]; then
  MARKETPLACE="$(cd "$(dirname "$0")/.." && pwd)"
fi

claude plugin marketplace add "$MARKETPLACE"
claude plugin install awf@stevnsborg --scope user
claude plugin details awf@stevnsborg
