# Correspondence patterns

Each pattern is a structure, not a script. Fill it with facts from the workspace and write it in the house style. `[[...]]` marks a fact to look up or ask for.

## Reply to an owner's question

1. Direct answer (yes / no / it depends on X).
2. The rule or decision behind it, with reference.
3. What happens next and who does it.
4. Contact point if they have more questions.

## Acknowledge an apartment change request

1. Thank them; confirm what was received (date, what they want to do, which unit).
2. What the board needs before deciding: drawings, description, contractor, wet-room certification, engineer's statement for walls, building permit if required. Only list what is missing.
3. Expected decision date (next board meeting [[date]]).
4. Reminder: work must not start before written approval.
→ Create or update the row in `registers/work-orders.csv` (status `info-requested` or `under-review`).

## Approve / approve with conditions / reject a change request

1. Decision in the first sentence, with board decision date.
2. Conditions as a numbered list (e.g. authorised contractor, wet-room standard, working hours, noise, protection of stairwell, waste handling, owner pays all costs and future maintenance of the change, notify board at start and completion, inspection).
3. For a rejection: the reason and the rule it rests on, and whether a revised request can be submitted.
4. Contact for questions.
→ Update the register (`approved`, `approved-with-conditions` or `rejected`, `approval_ref`), log the decision.

## Reminder (house rules: noise, waste, bikes, stairwell, pets)

1. Neutral description of the issue, not of a person.
2. The house rule (quote it briefly).
3. What we ask for, from when.
4. Thank them. No threats in a first reminder.
Second reminder: refer to the first one by date and state the next step under the bylaws [[confirm with board]].

## Payment reminder (arrears)

Usually the administrator's job. If the board sends one: one recipient per message, factual, amount and due date from the administrator's statement, how to pay, who to contact if there is a problem. Never Cc other owners.

## Request for quote (contractor)

1. Who we are, address, access contact.
2. Scope: what, where, quantities, standards, photos attached.
3. Dates: site visit options, quote deadline, desired execution period.
4. What the quote must include (fixed price or estimate, VAT, timeline, warranty, insurance).
5. Reply-to address.
→ Register row with status `quote-requested`, follow-up task on the quote deadline.

## Order / confirm work (contractor)

Reference to their quote (number, date, amount), scope, start date, access arrangements, contact on site, invoicing address (often the administrator), and how to report completion.

## Announcement to all residents

Subject with the date of the event. First line: what happens, when, and what residents must do (move cars, give access, expect water off between 9 and 12). Then the reason, the contact, and a thank-you. One screen, max.

## Neighbour complaint between owners

Acknowledge receipt and that the board takes it seriously. State what the board can and cannot do under the bylaws/house rules. Next step. Don't share the complainant's identity without their consent. Flag to the user if the matter may need the administrator or legal advice.

## Message to the administrator

Short and businesslike: case reference, what we need, by when, attachments. One topic per email so threads stay searchable.
