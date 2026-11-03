---
name: oa-documents
description: Generates formal documents for an owners' association (ejerforening / HOA) - notice of general meeting (indkaldelse), agendas, proposals, the board's annual report, house rules, approval letters for apartment alterations, contractor scopes, newsletters and notices for the stairwell. Use when the user asks for a document, notice, proposal, report, letter on letterhead, or a file to print, share, sign or attach.
---

# Association documents

## Process

1. **Identify the document type** (table below) and its source facts. Pull them from the workspace: `CLAUDE.md`, `context/bylaws.md`, `context/decisions.md`, the registers and `finance/`. Ask for anything missing, or leave `[[...]]`.
2. **Check formal requirements in the bylaws** before drafting anything that has legal effect (notices, proposals, resolutions): notice period, how notice must be given, required agenda items, proposal deadlines, majority rules. Cite the clause in a note to the user. If the bylaws aren't in the workspace, say so and list what must be checked.
3. **Draft in Markdown** in `outbox/YYYY-MM-DD-<doc>.md` using the structures below and in [document-types.md](document-types.md).
4. **Review pass:** every date, amount, unit and name matches the source. Dates are consistent (a notice sent on day X meets the notice period for meeting day Y). Polish prose with `humanizer`.
5. **Produce the final format the user wants:**
   - A shareable doc: use the `docs` skill / Claude Docs if available.
   - Word or PDF: use the `docx` or `pdf` skill if installed; otherwise give the Markdown and say which skill to install (`npx skills add anthropics/skills --skill docx`).
   - Google Doc in the association's Drive: use the Google Drive tools if connected, in the folder named in `CLAUDE.md`.
6. **File it:** link the final document in the relevant task, decision or work-order row, and log it.

## Document types

| Type | Key inputs | Watch out for |
|---|---|---|
| Notice of general meeting (indkaldelse) | date, place, agenda, proposals, accounts, budget | notice period and method under bylaws; mandatory agenda items; attach accounts/budget if required; proxy form |
| Agenda for board meeting | open tasks, pending requests, finance status | link supporting material; time per item |
| Proposal to the general meeting (forslag) | what, why, cost, financing, effect on common charges | exact wording to vote on; majority required |
| Board's annual report (bestyrelsens beretning) | decisions log, work orders closed, finance summary | factual, forward-looking section, thank-yous |
| Approval letter for apartment alteration | work-order row, board decision, conditions | standard conditions; owner's responsibility for costs and future maintenance |
| Contractor scope / tender | description, photos, standards, dates | quote basis must be comparable across bidders |
| House rules (husorden) revision | current rules, decisions | show changes clearly; adoption requires the correct body |
| Stairwell notice / newsletter | event, date, what residents must do | short, large type, date at top |
| Proxy form (fuldmagt) | meeting, unit, owner | as required by bylaws |

## Writing rules

- Formal documents use the association's main language and the formal names from `CLAUDE.md`.
- Put the key action and date at the top (what, when, where, what to do).
- Numbered sections, so the meeting can refer to "item 4.2".
- Money in the house format, with VAT status stated. Every figure traceable to `finance/` or a quote.
- Don't present a legal reading as settled. Write `[[check with administrator]]` where it matters.
