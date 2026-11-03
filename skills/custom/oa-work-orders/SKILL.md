---
name: oa-work-orders
description: Tracks work orders, repairs, maintenance and apartment change requests (alterations / ombygning - kitchens, bathrooms, walls, floors, windows) for an owners' association (ejerforening / HOA) in a CSV register, and produces status overviews, overdue and stale lists, per-unit history and cost totals. Use when a request, quote, approval, start or completion comes in, or the user asks "what's the status", "what's outstanding", "what has unit X done".
---

# Work orders and apartment changes

The register is `registers/work-orders.csv` in the workspace: one row per case. It is the single source of truth for status. Emails and minutes point to it by `id`.

## Columns

| Column | Content |
|---|---|
| `id` | `WO-<year>-<nnn>`. Get the next one with `next-id`. |
| `type` | `alteration` (owner's change to their apartment), `repair`, `maintenance`, `common-area`, `other` |
| `unit` | unit id as in `context/units.md`; empty for common areas |
| `title` | short, searchable: "Bathroom renovation", "Leak in basement ceiling" |
| `requested_by` | owner name, board, administrator |
| `received` | YYYY-MM-DD |
| `status` | see lifecycle below |
| `priority` | `low`, `normal`, `high`, `urgent` (urgent = water, fire, safety, access) |
| `contractor` | company name |
| `due` | next deadline (decision, quote, completion, inspection) |
| `est_cost`, `actual_cost` | amounts incl. VAT, plain numbers |
| `payer` | `owner`, `association`, `insurance`, `shared` |
| `approval_ref` | board decision date or minutes file, e.g. `2026-09-12 board` |
| `last_update` | date of the last change to this row |
| `next_action` | the very next step and who does it: "Board: decide at 2026-11-10 meeting" |
| `notes` | short; references to emails/files, not their content |

## Lifecycle

```
alteration:  received → info-requested ⇄ under-review → approved | approved-with-conditions | rejected
             → in-progress → completed → inspected → closed
repair/maintenance/common-area:
             received → quote-requested → under-review → ordered → in-progress → completed → closed
any open status → cancelled
```

Every change of status: update `status`, `last_update` (today), `next_action`, `due`. Board decisions also need `approval_ref` and a line in `context/decisions.md`.

## Commands

The script is in this skill's `scripts/` folder. `<skill-dir>` is this skill's folder (the base directory shown when the skill loads). Run it from the workspace root:

```bash
python3 <skill-dir>/scripts/work_orders.py overview registers/work-orders.csv          # status report (Markdown)
python3 <skill-dir>/scripts/work_orders.py overview registers/work-orders.csv --stale-days 21
python3 <skill-dir>/scripts/work_orders.py unit registers/work-orders.csv 3B           # history for one unit
python3 <skill-dir>/scripts/work_orders.py validate registers/work-orders.csv          # check after editing
python3 <skill-dir>/scripts/work_orders.py next-id registers/work-orders.csv
```

Use the script output. Don't read the whole CSV into the conversation. To change a row, edit only that line.

## Typical jobs

- **New request comes in (email or form):** `next-id`, add the row (`received`, `info-requested` if documents are missing, otherwise `under-review`), add a task, then draft the acknowledgement with `oa-correspondence` (pattern "Acknowledge an apartment change request").
- **Before a board meeting:** run `overview` and put "Awaiting board decision" and "Overdue" on the agenda with `oa-documents`.
- **After a board meeting:** update each decided case from the minutes; draft approval or rejection letters.
- **Weekly check:** run `overview`. Report overdue, due within 14 days and stale items in a few lines, and propose a chase email for each stale case.
- **Owner sells the apartment:** run `unit` to list approved alterations and conditions for the sale information.
- **Cost check:** the overview shows association-paid estimates vs actuals and flags overruns above 10 %. For budget impact, hand over to `oa-finance`.

Always run `validate` after editing the register.
