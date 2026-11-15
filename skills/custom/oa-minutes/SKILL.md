---
name: oa-minutes
description: Turns raw notes, transcripts, voice-memo text or email threads into meeting minutes, summaries and action lists for an owners' association (ejerforening / HOA) - board meetings, general meetings, site inspections and calls with contractors or the administrator. Use when the user says "take notes", "write the minutes", "referat", "summarise this meeting/thread/document", or pastes rough notes.
---

# Notes, minutes and summaries

## Live notetaking

When the user dictates or pastes notes during a meeting:
- Append to `notes/YYYY-MM-DD-<meeting>-raw.md`. Don't tidy yet; keep the user's words.
- Only answer if asked. If something is unclear (who will do it, by when), add `[[?]]` after it so it can be settled before the meeting ends.
- When the user says the meeting is over, list the `[[?]]` items and then write the minutes.

## Minutes

Save as `notes/YYYY-MM-DD-<meeting>.md`. Use the structure in [minutes-template.md](minutes-template.md).

Rules:
- **Decision minutes, not transcripts.** For each agenda item: short background (1-3 lines), what was decided, and who does what by when. Record discussion only when it explains a decision or when a member asks for their view to be recorded.
- **Decisions must be exact.** Write them as resolutions: "The board approved the bathroom renovation in unit 3B subject to the standard conditions." Include votes when the bylaws require it or the vote was not unanimous. For a general meeting, include vote counts and the majority required.
- **Attendance and quorum** at the top. For general meetings: owners present and by proxy, and whether the meeting was quorate under the bylaws (look up the clause).
- **Action items** as a table: what, owner, due date. Every action has an owner and a date; if not, mark `[[?]]`.
- Neutral wording. No characterisation of people ("angrily", "unreasonably").
- Personal data: mention arrears, disputes or private circumstances only as much as the decision requires; consider an internal annex instead of the minutes that go to all owners.
- Language from `CLAUDE.md` (minutes are usually in the association's main language).

General meeting minutes usually need the chair of the meeting (dirigent) to sign. Add the signature lines and leave them blank.

## After the minutes

1. Each decision → one line in `context/decisions.md`.
2. Each action item → `TASKS.md`.
3. Work-order changes (approved changes, ordered repairs) → `registers/work-orders.csv`.
4. Offer a draft cover email to the board (for comments) or to owners (for publication) via `oa-correspondence`.

## Summaries of threads and documents

For long material, ask `oa-reader` to digest it with a clear question, then shape the result for the user:

```
**Bottom line:** <one or two sentences>
**What's being asked of us:** <decisions/actions, with deadlines>
**Key facts:** <bullets with sources>
**Open points:** <bullets>
**Suggested next step:** <one line>
```

Keep summaries to what the user asked. Offer the detail rather than including it.
