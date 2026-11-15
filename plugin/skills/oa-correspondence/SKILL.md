---
name: oa-correspondence
description: Drafts emails, letters and replies for an owners' association board (ejerforening / HOA) - to owners, residents, the administrator, contractors, the municipality or insurers. Use for replies to owner enquiries, reminders, announcements, complaints and neighbour disputes, responses to apartment change requests, contractor requests for quotes, and follow-ups. Produces drafts only; never sends.
---

# Association correspondence

## Before drafting

1. **Who is it to, and in what role?** Owner, tenant, whole building, administrator, contractor, authority. Check `context/people.md` and `context/units.md` for names, units and history.
2. **What is the one thing the reader must do or know?** If you can't say it in one sentence, ask the user.
3. **What is already on file?** Look up related tasks, decisions and work orders. For a long thread, have `oa-reader` digest it first. Don't load the whole thread here.
4. **Does it rely on bylaws, house rules or a board decision?** Find the clause in `context/bylaws.md` or the decision in `context/decisions.md` and refer to it ("cf. bylaws §7.2", "board decision of 2026-09-12").

## Writing rules

- Language, tone and sign-off from `CLAUDE.md`. Match the language of the email you are replying to.
- Subject line: specific and searchable, with the unit or case where relevant. Example: `Lejl. 3 tv — godkendelse af badeværelsesrenovering` / `Unit 3B — bathroom renovation approved`.
- First sentence says the point. Background after, only as much as the reader needs.
- One request per paragraph. Put deadlines as dates ("by 15 November"), not "soon".
- Write as the board ("we") unless `CLAUDE.md` says otherwise. Don't commit the board to anything that isn't in `decisions.md` or confirmed by the user. Mark such statements `[[confirm with board?]]`.
- Short. Most owner emails are under 150 words. A whole-building announcement should fit on one screen.
- No legal threats, blame or sarcasm. In disputes, state facts, the rule and the next step.
- Don't name other owners in a message to an owner unless it is necessary and the user agrees (e.g. noise complaints: describe the issue, not who complained).
- Polish with `humanizer` before showing the draft.

Standard patterns for common situations: [patterns.md](patterns.md).

## Delivery

- **Gmail connected:** create a draft (reply in-thread when replying) and give the user the subject. Never send.
- **Otherwise:** save to `outbox/YYYY-MM-DD-<recipient>-<topic>.md` with To/Cc/Subject at the top, and also show it in chat.
- Several recipients with personal details (e.g. a reminder to each owner in arrears): one draft per recipient, never a shared To/Cc with exposed addresses. For whole-building mail, use Bcc or the association's distribution list.

## After drafting

- Add follow-ups to `TASKS.md` (for example "chase reply from contractor · due: +7 days").
- If the email tells someone about a decision or a work-order status, update the work-order register too.
- End with **Gaps** (placeholders to fill) and **Filed** (files updated).
