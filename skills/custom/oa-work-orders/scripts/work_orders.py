#!/usr/bin/env python3
"""Work-order and apartment-change register for an owners' association.

The register is a CSV file (default: registers/work-orders.csv) with the columns
listed in COLUMNS. Standard library only.

Commands:
  overview  Markdown status report: counts, needs-attention lists, costs.
  unit      Full history for one unit.
  validate  Check the register for bad statuses, dates, amounts and duplicate ids.
  next-id   Print the next free id (WO-<year>-<nnn>).

Examples:
  python3 work_orders.py overview registers/work-orders.csv
  python3 work_orders.py overview registers/work-orders.csv --today 2026-11-03 --stale-days 21
  python3 work_orders.py unit registers/work-orders.csv 3B
  python3 work_orders.py validate registers/work-orders.csv
  python3 work_orders.py next-id registers/work-orders.csv
"""

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation

COLUMNS = [
    "id", "type", "unit", "title", "requested_by", "received", "status", "priority",
    "contractor", "due", "est_cost", "actual_cost", "payer", "approval_ref",
    "last_update", "next_action", "notes",
]
TYPES = {"alteration", "repair", "maintenance", "common-area", "other"}
# Order matters: it is the lifecycle order used in reports.
STATUSES = [
    "received", "info-requested", "under-review", "quote-requested",
    "approved", "approved-with-conditions", "ordered", "in-progress",
    "completed", "inspected", "closed", "rejected", "cancelled",
]
CLOSED = {"closed", "rejected", "cancelled"}
AWAITING_BOARD = {"received", "under-review"}
WAITING_ON_OTHERS = {"info-requested", "quote-requested"}
PRIORITIES = {"", "low", "normal", "high", "urgent"}
PAYERS = {"", "owner", "association", "insurance", "shared"}
DATE_FIELDS = ("received", "due", "last_update")
MONEY_FIELDS = ("est_cost", "actual_cost")


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    return date.fromisoformat(value)


def parse_money(value):
    """Accept 12500, 12500.50, 12.500,50 and 12,500.50."""
    value = (value or "").strip().replace(" ", "").replace("kr.", "").replace("kr", "")
    if not value:
        return None
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")
    return Decimal(value)


def fmt_money(amount):
    if amount is None:
        return ""
    return f"{amount:,.0f}".replace(",", " ")


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"error: {path} is missing columns: {', '.join(missing)}")
        rows = []
        for n, raw in enumerate(reader, start=2):
            row = {k: (raw.get(k) or "").strip() for k in COLUMNS}
            row["_line"] = n
            rows.append(row)
    return rows


def problems(rows):
    out, seen = [], {}
    for r in rows:
        where = f"line {r['_line']} ({r['id'] or 'no id'})"
        if not r["id"]:
            out.append(f"{where}: missing id")
        elif r["id"] in seen:
            out.append(f"{where}: duplicate id, also on line {seen[r['id']]}")
        else:
            seen[r["id"]] = r["_line"]
        if r["type"] not in TYPES:
            out.append(f"{where}: type '{r['type']}' not in {sorted(TYPES)}")
        if r["status"] not in STATUSES:
            out.append(f"{where}: status '{r['status']}' not in {STATUSES}")
        if r["priority"] not in PRIORITIES:
            out.append(f"{where}: priority '{r['priority']}' not in {sorted(PRIORITIES - {''})}")
        if r["payer"] not in PAYERS:
            out.append(f"{where}: payer '{r['payer']}' not in {sorted(PAYERS - {''})}")
        if not r["title"]:
            out.append(f"{where}: missing title")
        for field in DATE_FIELDS:
            try:
                parse_date(r[field])
            except ValueError:
                out.append(f"{where}: {field} '{r[field]}' is not YYYY-MM-DD")
        for field in MONEY_FIELDS:
            try:
                parse_money(r[field])
            except InvalidOperation:
                out.append(f"{where}: {field} '{r[field]}' is not an amount")
        if r["type"] == "alteration" and r["status"] in {"approved", "approved-with-conditions", "rejected"} and not r["approval_ref"]:
            out.append(f"{where}: board decision recorded without approval_ref")
    return out


def clean(rows):
    """Parse dates and amounts; exit if the register has errors."""
    errs = problems(rows)
    if errs:
        sys.exit("register has errors, run `validate`:\n  " + "\n  ".join(errs))
    for r in rows:
        for field in DATE_FIELDS:
            r[field + "_d"] = parse_date(r[field])
        for field in MONEY_FIELDS:
            r[field + "_m"] = parse_money(r[field])
    return rows


def table(rows, cols, headers):
    if not rows:
        return "_none_\n"
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        lines.append("| " + " | ".join(str(c(r) if callable(c) else r[c]).replace("|", "/") for c in cols) + " |")
    return "\n".join(lines) + "\n"


def days_since(d, today):
    return (today - d).days if d else None


def overview(rows, today, stale_days):
    rows = clean(rows)
    open_rows = [r for r in rows if r["status"] not in CLOSED]
    out = [f"# Work orders — overview {today.isoformat()}\n"]

    counts = Counter(r["status"] for r in rows)
    by_type = Counter(r["type"] for r in open_rows)
    out.append(f"**Open:** {len(open_rows)} of {len(rows)} · by type: "
               + (", ".join(f"{t} {n}" for t, n in sorted(by_type.items())) or "none") + "\n")
    out.append("**By status:** " + ", ".join(f"{s} {counts[s]}" for s in STATUSES if counts[s]) + "\n")

    def age(r):
        n = days_since(r["last_update_d"] or r["received_d"], today)
        return "" if n is None else f"{n} d"

    overdue = sorted((r for r in open_rows if r["due_d"] and r["due_d"] < today), key=lambda r: r["due_d"])
    out.append("\n## Overdue\n")
    out.append(table(overdue, ["id", "unit", "title", "status", "due", "next_action"],
                     ["id", "unit", "title", "status", "due", "next action"]))

    soon = sorted((r for r in open_rows if r["due_d"] and 0 <= (r["due_d"] - today).days <= 14),
                  key=lambda r: r["due_d"])
    out.append("\n## Due in the next 14 days\n")
    out.append(table(soon, ["id", "unit", "title", "status", "due", "next_action"],
                     ["id", "unit", "title", "status", "due", "next action"]))

    board = sorted((r for r in open_rows if r["status"] in AWAITING_BOARD), key=lambda r: r["received"])
    out.append("\n## Awaiting board decision\n")
    out.append(table(board, ["id", "type", "unit", "title", "received", age],
                     ["id", "type", "unit", "title", "received", "age"]))

    waiting = [r for r in open_rows if r["status"] in WAITING_ON_OTHERS]
    out.append("\n## Waiting on owner / contractor\n")
    out.append(table(waiting, ["id", "unit", "title", "status", "requested_by", "contractor", age],
                     ["id", "unit", "title", "status", "owner", "contractor", "since update"]))

    stale = sorted(
        (r for r in open_rows
         if (days_since(r["last_update_d"] or r["received_d"], today) or 0) > stale_days),
        key=lambda r: r["last_update_d"] or r["received_d"])
    out.append(f"\n## Stale (no update for more than {stale_days} days)\n")
    out.append(table(stale, ["id", "unit", "title", "status", "last_update", age],
                     ["id", "unit", "title", "status", "last update", "age"]))

    missing_next = [r for r in open_rows if not r["next_action"]]
    out.append("\n## Open items without a next action\n")
    out.append(table(missing_next, ["id", "unit", "title", "status"], ["id", "unit", "title", "status"]))

    out.append("\n## Costs (association-paid and shared items)\n")
    totals = defaultdict(lambda: [Decimal(0), Decimal(0)])
    for r in rows:
        if r["payer"] in {"association", "shared"} and r["status"] not in {"rejected", "cancelled"}:
            key = "open" if r["status"] not in CLOSED else "closed"
            totals[key][0] += r["est_cost_m"] or 0
            totals[key][1] += r["actual_cost_m"] or 0
    out.append(table(
        [{"k": k, "e": fmt_money(v[0]), "a": fmt_money(v[1])} for k, v in sorted(totals.items())],
        ["k", "e", "a"], ["", "estimated", "actual"]))
    over = [r for r in rows if r["est_cost_m"] and r["actual_cost_m"] and r["actual_cost_m"] > r["est_cost_m"] * Decimal("1.1")]
    if over:
        out.append("\n**Actual more than 10 % over estimate:**\n")
        out.append(table(over, ["id", "title", lambda r: fmt_money(r["est_cost_m"]), lambda r: fmt_money(r["actual_cost_m"])],
                         ["id", "title", "estimated", "actual"]))
    return "".join(out)


def unit_history(rows, unit):
    rows = clean(rows)
    mine = sorted((r for r in rows if r["unit"].lower() == unit.lower()), key=lambda r: r["received"])
    label = mine[0]["unit"] if mine else unit
    out = [f"# Unit {label} — work orders and alterations\n\n"]
    out.append(table(mine, ["id", "type", "title", "received", "status", "approval_ref", "next_action"],
                     ["id", "type", "title", "received", "status", "approval", "next action"]))
    return "".join(out)


def next_id(rows, year):
    pat = re.compile(rf"^WO-{year}-(\d+)$")
    nums = [int(m.group(1)) for r in rows if (m := pat.match(r["id"]))]
    return f"WO-{year}-{max(nums, default=0) + 1:03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("overview")
    p.add_argument("register")
    p.add_argument("--today", type=date.fromisoformat, default=date.today())
    p.add_argument("--stale-days", type=int, default=14)
    p = sub.add_parser("unit")
    p.add_argument("register")
    p.add_argument("unit")
    p = sub.add_parser("validate")
    p.add_argument("register")
    p = sub.add_parser("next-id")
    p.add_argument("register")
    p.add_argument("--year", type=int, default=date.today().year)
    args = ap.parse_args()

    rows = load(args.register)
    if args.cmd == "overview":
        print(overview(rows, args.today, args.stale_days))
    elif args.cmd == "unit":
        print(unit_history(rows, args.unit))
    elif args.cmd == "validate":
        errs = problems(rows)
        print("\n".join(errs) if errs else f"ok: {len(rows)} rows")
        sys.exit(1 if errs else 0)
    elif args.cmd == "next-id":
        print(next_id(rows, args.year))


if __name__ == "__main__":
    main()
