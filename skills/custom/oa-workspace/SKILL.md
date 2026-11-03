---
name: oa-workspace
description: Sets up and maintains the file-based memory for an owners' association (ejerforening / HOA) assistant - association profile, people, units, decision log, tasks, registers and session log. Use when starting a new association workspace, when recording a decision, contact, deadline or status change, when closing a session, or when the user asks "what do we know about X" for the association.
---

# Owners' association workspace

The workspace is a folder (ideally a private git repo) that holds everything the assistant needs to remember between sessions. The conversation is thrown away. The files stay.

## Layout

```
CLAUDE.md               # association profile + house style. Always loaded. Keep under ~150 lines.
TASKS.md                # open follow-ups, each with an owner and due date
context/
  people.md             # board, administrator, contractors, key contacts
  units.md              # unit register: unit id, owner(s), share/allocation key, notes
  decisions.md          # append-only decision log
  glossary.md           # terms, abbreviations, nicknames
  bylaws.md             # bylaws / house rules, or pointers to where they are
registers/
  work-orders.csv       # see oa-work-orders
finance/
  budget-<year>.csv     # see oa-finance
notes/                  # raw meeting notes and finished minutes, YYYY-MM-DD-<topic>.md
inbox/                  # drop zone for files the user hands over (PDFs, quotes, reports)
outbox/                 # drafts that aren't in Gmail/Drive yet
log/<YYYY-MM>.md        # one line per session or finished task
```

## Set up a new workspace

1. Copy [template/](template/) into the target folder (don't overwrite existing files).
2. Interview the user briefly and fill in `CLAUDE.md`: association name and address, number of units, board members and roles, administrator, financial year, default language and tone, email signature, where bylaws and accounts live. Ask at most five questions at a time, and leave `[[?]]` for anything they don't know yet.
3. If Gmail, Google Drive or Calendar tools are connected, ask whether to use them and record the answer (and any label or folder names) in `CLAUDE.md`.
4. Recommend keeping the workspace in a **private** repo or a local folder only. It holds owners' personal data.

## What goes where

| You learn... | Write it to | Format |
|---|---|---|
| A decision by the board or general meeting | `context/decisions.md` | `- YYYY-MM-DD · <body> · <decision> · ref: <minutes file or email>` |
| A commitment or follow-up | `TASKS.md` | `- [ ] <what> · owner: <who> · due: YYYY-MM-DD · ref: <source>` |
| A new contact or a changed role | `context/people.md` | one row in the right table |
| A new owner, sale or changed unit info | `context/units.md` | update the unit row; record the change date in notes |
| A work order or apartment change request | `registers/work-orders.csv` | see `oa-work-orders` |
| A recurring term, abbreviation or nickname | `context/glossary.md` | `term — meaning` |
| A house-style preference ("always sign as the board", "use 'du' not 'De'") | `CLAUDE.md` → House style | one bullet |

Rules:
- `decisions.md` is append-only. If a decision is changed, add a new line that refers to the old one.
- Close tasks by ticking them (`- [x]`) and adding `done: YYYY-MM-DD`. Move ticked tasks older than 60 days to `log/` when tidying.
- Don't copy whole emails or documents into `context/`. Store a one-line summary and a reference (message subject and date, Drive link, or `inbox/` path).
- Keep `CLAUDE.md` short. It is loaded every session. Detail goes in `context/`.

## Close a session or task

1. Make sure every decision, commitment and status change from this session has been written (table above).
2. Append one line to `log/<YYYY-MM>.md`: `- YYYY-MM-DD · <what was done> · files: <changed files>`.
3. If work is unfinished, add or update a task in `TASKS.md` with a one-sentence "where we left off".
4. If the workspace is a git repo, offer to commit with a short message. Don't push unless asked.

## Tidy (monthly, or when asked)

- Remove done tasks older than 60 days from `TASKS.md` (they are already in `log/`).
- Check `CLAUDE.md` is under ~150 lines. Move detail into `context/`.
- Run the work-order overview (`oa-work-orders`) and flag stale items.
- List files in `inbox/` that haven't been filed or summarised.
