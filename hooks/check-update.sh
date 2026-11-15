#!/usr/bin/env bash
# SessionStart hook: tell Claude when the stevnsborg marketplace is behind origin/main,
# so it can ask the user whether to pull and update the awf plugin.
# Silent (exit 0, no output) when up to date, offline, or the marketplace clone is missing.
set -u
MARKET="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/marketplaces/stevnsborg"
[ -d "$MARKET/.git" ] || exit 0

timeout 10 git -C "$MARKET" fetch --quiet origin main 2>/dev/null || exit 0
BEHIND=$(git -C "$MARKET" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
[ "${BEHIND:-0}" -gt 0 ] || exit 0

SUBJECTS=$(git -C "$MARKET" log --format='- %s' HEAD..origin/main | head -5 | sed 's/"/\\"/g' | tr '\n' ' ')
cat <<JSON
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"The awf plugin library (marketplace 'stevnsborg', repo stevnsborg/agentic-work-flows) is $BEHIND commit(s) behind origin/main. New changes: $SUBJECTS. At the start of your first reply, tell the user in one line and ask whether to pull and update now. Only if they say yes: run 'claude plugin marketplace update stevnsborg' and then 'claude plugin update awf@stevnsborg' with Bash (if the claude CLI is unavailable, tell them to run '/plugin marketplace update stevnsborg' and '/plugin update awf@stevnsborg'), then tell them to restart the session or run /reload-plugins. Do not update without their approval."}}
JSON
