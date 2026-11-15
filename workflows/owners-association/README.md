# Workflow: owners' association assistant

**Goal:** a standing secretary/administrator for the board of an owners' association (ejerforening / HOA). It drafts email, writes documents, takes notes and minutes, analyses the budget, and tracks work orders and apartment change requests. It remembers between sessions through files in a private workspace.

**Trigger:** run manually in the association workspace (`claude` there starts the agent automatically). Optional scheduled check-ins are below.

## Building blocks

| Kind | Name | Role |
|---|---|---|
| agent | `oa-secretary` | Main agent: rules, session routine, which skill for which job |
| agent | `oa-reader` | Read-only subagent that digests long threads, PDFs and accounts so the main context stays small |
| skill | `oa-workspace` | Workspace layout, memory rules, setup, session close, tidy |
| skill | `oa-correspondence` | Emails and letters (drafts only), with patterns for common cases |
| skill | `oa-minutes` | Live notes, minutes, decision and action extraction, summaries |
| skill | `oa-documents` | Notices of meeting, agendas, proposals, annual report, approval letters |
| skill | `oa-finance` | Budget vs actual, forecasts, draft budgets, cost allocation, quote comparison (`scripts/oa_finance.py`) |
| skill | `oa-work-orders` | CSV register for repairs and apartment changes, overview/overdue/stale reports (`scripts/work_orders.py`) |
| skill | `humanizer` | Final polish on any prose that goes to people |
| optional | `docx`, `pdf`, `xlsx` (Anthropic, install separately), Claude Docs | Final file formats |
| connectors | Gmail, Google Drive, Google Calendar | Read mail, create drafts, file documents, meeting dates |

## Set up (once)

1. **Make a private workspace.** A new private GitHub repo (e.g. `<you>/ejerforening`) or a local folder. It will hold owners' personal data, so never make it public.
2. **Install the plugin** where you'll run it:
   ```
   /plugin marketplace add stevnsborg/agentic-work-flows
   /plugin install awf@stevnsborg
   ```
3. **Open Claude Code in the empty workspace** and run:
   ```bash
   claude --agent awf:oa-secretary
   ```
   Then say: *"Set up this folder as our association workspace."* The agent uses `oa-workspace` to copy the template (including `.claude/settings.json`, which makes `oa-secretary` the default agent and enables the plugin for cloud sessions too) and interviews you to fill in `CLAUDE.md`.
4. **Load the basics** by dropping files into `inbox/` and asking the agent to file them:
   - bylaws and house rules → summary table in `context/bylaws.md`
   - owner list with allocation keys → `context/units.md`
   - board, administrator and contractors → `context/people.md`
   - this year's budget and the latest statement → `finance/budget-<year>.csv`
   - open cases → `registers/work-orders.csv`
5. **Connect Gmail / Drive / Calendar** (claude.ai Settings → Connectors) if you want mail drafts and Drive filing. Note the association's mail label and Drive folder in `CLAUDE.md`.

## Daily use

Start `claude` in the workspace. The agent reads `CLAUDE.md`, `TASKS.md` and the latest log, and gives you a three-line status. Then ask, for example:

- "Draft a reply to the Jensen email about the bathroom renovation."
- "Take notes, board meeting starting now." … "Meeting's over, write the minutes."
- "Prepare the notice for the general meeting on 22 April."
- "Here's the Q3 statement from the administrator (inbox/q3.pdf). How are we doing against budget?"
- "What's outstanding on work orders? Draft chasers for anything stale."
- "What alterations has unit 3B done? They're selling."

## How context is managed

| Layer | What | Loaded |
|---|---|---|
| `CLAUDE.md` | Association profile and house style (< ~150 lines) | Every session |
| `TASKS.md`, latest `log/` | Open follow-ups, last session | Session start |
| Skills | How to do each kind of job | Only when that job comes up |
| `context/*.md` | People, units, decisions, glossary, bylaws summary | When a task needs them |
| `registers/`, `finance/` CSVs | Work orders, budget | Through scripts that return summaries, never read whole |
| Originals (mail, PDFs, accounts) | Source material | Digested by `oa-reader` in its own context, which returns ~300 words with sources |

Habits that keep it working:
- **Write back immediately.** Decisions → `decisions.md`, follow-ups → `TASKS.md`, statuses → register. The next session only knows what's on file.
- **One topic per session.** Finish, let the agent log it, then `/clear` before the next topic. Use `/compact` if a long task fills up.
- **Long multi-session jobs** (general meeting prep, budget): keep a "where we left off" line on the task in `TASKS.md`, or use `/handoff`.
- **Monthly tidy:** "tidy the workspace" (prunes old tasks, checks `CLAUDE.md` length, lists unfiled inbox files, runs the work-order overview).

## Optional scheduled check-ins

With a cloud environment pointed at the workspace repo, schedule a weekly task (for example Monday 07:40) with the prompt:

> Run the work-order overview and check `TASKS.md` for items due in the next 7 days. If Gmail is connected, look for unanswered association email older than 3 days. Write a short status to `log/` and create Gmail drafts for any chasers. Don't send anything.

## Safety rules (built into the agent)

- Drafts only. Nothing is sent, shared or accepted without your explicit OK per item.
- No invented facts. Missing facts appear as `[[...]]` placeholders and are listed at the end.
- Bylaw and legal questions cite the clause and point to the administrator or a lawyer where needed.
- One owner's personal data never goes into messages to other owners.
