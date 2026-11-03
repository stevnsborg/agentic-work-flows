---
name: oa-finance
description: Budget, accounts and cost analysis for an owners' association (ejerforening / HOA) - budget vs actual, full-year forecast, draft budgets, common charges (fællesudgifter) and splitting costs between units by allocation key (fordelingstal), reserve fund and maintenance-plan funding, comparing contractor quotes, and reading the administrator's accounts. Use when the user asks about money, budget, accounts, charges, quotes or "can we afford X".
---

# Association finance

You support the treasurer and the board. You prepare figures and explain them. You don't approve payments, and the administrator's and auditor's figures override yours.

## Sources, in order of authority

1. Audited annual accounts and the administrator's statements (usually PDFs in `inbox/` or Drive). Use `oa-reader` to pull the figures out, with page references.
2. `finance/budget-<year>.csv`: the working budget-vs-actual sheet (columns below).
3. `registers/work-orders.csv` for committed and expected costs.
4. Quotes and invoices.

Every number you present must trace to one of these. If a figure is missing, write `[[amount?]]`. Don't estimate silently. When you do estimate (forecasts, scenarios), label it as an estimate and state the assumption.

## Budget sheet

`finance/budget-<year>.csv`, one row per account:

```
account,category,kind,budget,actual,prior_year
1010,Common charges,income,960000,720000,940000
2110,Insurance,expense,85000,85000,81000
```

- `kind` is `income` or `expense`. `budget` and `prior_year` are full-year; `actual` is year-to-date.
- Use the administrator's chart of accounts so updates are a copy job.
- When a new statement arrives: have `oa-reader` extract actuals per account, update the `actual` column, note the statement date in `log/`.

## Commands

`<skill-dir>` is this skill's folder (the base directory shown when the skill loads).

```bash
# budget vs actual, 9 months into the year, flag deviations of 10 % or more
python3 <skill-dir>/scripts/oa_finance.py variance finance/budget-2026.csv --months 9
# Danish number format, flag at 15 %
python3 <skill-dir>/scripts/oa_finance.py variance finance/budget-2026.csv --months 9 --threshold 15 --decimal-comma
# split 250,000 between units by the share column in context/units.md
python3 <skill-dir>/scripts/oa_finance.py allocate context/units.md --amount 250000
```

The variance report pro-rates the annual budget straight-line. Point out accounts where that is wrong (insurance paid once a year, seasonal heating, one-off projects) and comment on them, rather than taking the flag at face value.

## Typical jobs

- **Status for a board meeting:** run `variance`. Write 3–6 bullets: result to date vs budget, the biggest deviations with the reason if known, expected full-year result, cash/reserve position if known, and decisions the board must take. Put the table in an annex.
- **Draft next year's budget:** start from this year's forecast and the prior year. Adjust for known changes: contracts, insurance indexation, planned work from the maintenance plan and the work-order register, and reserve contributions. Show each change from this year with its reason. Calculate the effect on common charges per unit with `allocate` (on the change, and on the total).
- **Can we afford X?** Cost (with VAT), timing, funding options (reserve fund, operating surplus, one-off extra charge, loan) and the effect of each per unit. State what the bylaws say about who decides (board limit vs general meeting).
- **Compare quotes:** table with price excl./incl. VAT, scope differences, exclusions, timeline, warranty, payment terms. Point out where quotes aren't comparable. Don't pick a winner unless asked; then give the reason.
- **Cost of a work order:** update `est_cost`/`actual_cost` in the register, and say which budget account it lands on.

## Presentation

- Amounts in the house format from `CLAUDE.md`. Round to whole currency units in summaries.
- Lead with the conclusion, then the table.
- Charts only when they help (trend over several years, spend by category). Use the `dataviz` / `data:create-viz` skill if available.
- For spreadsheets the treasurer will keep editing, use the `xlsx` skill if installed, with formulas, not pasted values.
