#!/usr/bin/env python3
"""Budget and cost tools for an owners' association. Standard library only.

Commands:
  variance  Budget vs actual per account, pro-rata for the part of the year
            elapsed, with full-year forecast and flags.
  allocate  Split an amount between units by their allocation key (share),
            rounded to 0.01 so the parts add up exactly to the total.

Budget CSV columns: account, category, kind (income|expense), budget, actual[, prior_year]
  - budget and prior_year are full-year amounts; actual is year-to-date.
  - amounts may be written 12500, 12500.50, 12.500,50 or 12,500.50.

Units file: a CSV, or the Markdown table in context/units.md, with columns
`unit` and `share` (other columns are ignored).

Examples:
  python3 oa_finance.py variance finance/budget-2026.csv --months 9
  python3 oa_finance.py variance finance/budget-2026.csv --months 9 --threshold 15 --decimal-comma
  python3 oa_finance.py allocate context/units.md --amount 250000
"""

import argparse
import csv
import io
import sys
from decimal import ROUND_DOWN, Decimal, InvalidOperation
from pathlib import Path

CENT = Decimal("0.01")


def money(value, where):
    raw = value
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
    try:
        return Decimal(value)
    except InvalidOperation:
        sys.exit(f"error: {where}: '{raw}' is not an amount")


def fmt(amount, decimal_comma=False, places=0):
    if amount is None:
        return ""
    s = f"{amount:,.{places}f}"
    if decimal_comma:
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def pct(part, whole):
    if not whole:
        return None
    return (part / abs(whole) * 100).quantize(Decimal("0.1"))


def read_budget(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        need = {"account", "category", "kind", "budget", "actual"}
        missing = need - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"error: {path} is missing columns: {', '.join(sorted(missing))}")
        rows = []
        for n, r in enumerate(reader, start=2):
            kind = (r["kind"] or "").strip().lower()
            if kind not in {"income", "expense"}:
                sys.exit(f"error: line {n}: kind must be income or expense, got '{r['kind']}'")
            rows.append({
                "account": (r["account"] or "").strip(),
                "category": (r["category"] or "").strip(),
                "kind": kind,
                "budget": money(r["budget"], f"line {n} budget") or Decimal(0),
                "actual": money(r["actual"], f"line {n} actual") or Decimal(0),
                "prior": money(r.get("prior_year"), f"line {n} prior_year"),
            })
    return rows


def variance(rows, months, year_months, threshold, dc):
    frac = Decimal(months) / Decimal(year_months)
    has_prior = any(r["prior"] is not None for r in rows)
    head = ["account", "category", "budget (year)", "budget to date", "actual to date",
            "variance", "var %", "forecast (year)"]
    if has_prior:
        head.append("prior year")
    head.append("flag")
    out = [f"# Budget vs actual — {months} of {year_months} months ({fmt(frac * 100, places=0)} % of year)\n\n",
           "Variance = actual − budget to date. For income, negative is unfavourable; for expenses, positive is unfavourable. "
           "Forecast is a straight-line projection; adjust for seasonal or one-off items.\n"]
    totals = {}
    for kind in ("income", "expense"):
        part = [r for r in rows if r["kind"] == kind]
        if not part:
            continue
        out.append(f"\n## {kind.capitalize()}\n\n")
        out.append("| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n")
        t = {"budget": Decimal(0), "todate": Decimal(0), "actual": Decimal(0), "forecast": Decimal(0), "prior": Decimal(0)}
        for r in part:
            todate = r["budget"] * frac
            var = r["actual"] - todate
            vp = pct(var, todate)
            forecast = r["actual"] / frac if frac else None
            unfavourable = var > 0 if kind == "expense" else var < 0
            flag = ""
            if vp is not None and abs(vp) >= threshold:
                flag = "⚠ over" if (kind == "expense" and var > 0) else ("⚠ under" if kind == "income" and var < 0 else "")
                if not unfavourable:
                    flag = "favourable"
            elif not todate and r["actual"]:
                flag = "⚠ unbudgeted"
            cells = [r["account"], r["category"], fmt(r["budget"], dc), fmt(todate, dc), fmt(r["actual"], dc),
                     fmt(var, dc), "" if vp is None else f"{fmt(vp, dc, 1)} %", fmt(forecast, dc)]
            if has_prior:
                cells.append(fmt(r["prior"], dc))
            cells.append(flag)
            out.append("| " + " | ".join(cells) + " |\n")
            t["budget"] += r["budget"]
            t["todate"] += todate
            t["actual"] += r["actual"]
            t["forecast"] += forecast or 0
            t["prior"] += r["prior"] or 0
        tv = t["actual"] - t["todate"]
        tp = pct(tv, t["todate"])
        cells = ["**Total**", "", fmt(t["budget"], dc), fmt(t["todate"], dc), fmt(t["actual"], dc),
                 fmt(tv, dc), "" if tp is None else f"{fmt(tp, dc, 1)} %", fmt(t["forecast"], dc)]
        if has_prior:
            cells.append(fmt(t["prior"], dc))
        cells.append("")
        out.append("| " + " | ".join(cells) + " |\n")
        totals[kind] = t
    inc = totals.get("income", {"budget": 0, "actual": 0, "forecast": 0, "todate": 0})
    exp = totals.get("expense", {"budget": 0, "actual": 0, "forecast": 0, "todate": 0})
    out.append("\n## Result (income − expenses)\n\n")
    out.append("| | budget (year) | budget to date | actual to date | forecast (year) |\n|---|---|---|---|---|\n")
    out.append(f"| Result | {fmt(inc['budget'] - exp['budget'], dc)} | {fmt(inc['todate'] - exp['todate'], dc)} | "
               f"{fmt(inc['actual'] - exp['actual'], dc)} | {fmt(inc['forecast'] - exp['forecast'], dc)} |\n")
    return "".join(out)


def read_units(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if path.endswith(".md"):
        lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("|")]
        lines = [ln for ln in lines if not set(ln.replace("|", "").strip()) <= set("-: ")]
        if not lines:
            sys.exit(f"error: no table found in {path}")
        buf = io.StringIO()
        csv.writer(buf).writerows([c.strip() for c in ln.strip("|").split("|")] for ln in lines)
        text = buf.getvalue()
    reader = csv.DictReader(io.StringIO(text))
    if not {"unit", "share"} <= set(reader.fieldnames or []):
        sys.exit(f"error: {path} needs 'unit' and 'share' columns")
    units = []
    for r in reader:
        if not (r["unit"] or "").strip():
            continue
        share = money(r["share"], f"unit {r['unit']} share")
        if share is None:
            sys.exit(f"error: unit {r['unit']} has no share")
        units.append((r["unit"].strip(), share))
    if not units:
        sys.exit(f"error: no units in {path}")
    return units


def allocate(units, amount, dc):
    total_share = sum(s for _, s in units)
    raw = [(u, s, amount * s / total_share) for u, s in units]
    floored = [(u, s, x.quantize(CENT, rounding=ROUND_DOWN), x) for u, s, x in raw]
    remainder = int(((amount - sum(f for _, _, f, _ in floored)) / CENT).to_integral_value())
    # Largest-remainder method: hand out the leftover cents to the biggest fractions.
    order = sorted(range(len(floored)), key=lambda i: floored[i][3] - floored[i][2], reverse=True)
    parts = [f for _, _, f, _ in floored]
    for i in order[:remainder]:
        parts[i] += CENT
    out = [f"# Allocation of {fmt(amount, dc, 2)} by share (total share {total_share.normalize()})\n\n",
           "| unit | share | % | amount |\n|---|---|---|---|\n"]
    for (u, s, _, _), p in zip(floored, parts):
        out.append(f"| {u} | {s.normalize()} | {fmt(s / total_share * 100, dc, 2)} % | {fmt(p, dc, 2)} |\n")
    out.append(f"| **Total** | {total_share.normalize()} | 100 % | {fmt(sum(parts), dc, 2)} |\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("variance")
    p.add_argument("budget_csv")
    p.add_argument("--months", type=int, required=True, help="months of the financial year covered by 'actual'")
    p.add_argument("--year-months", type=int, default=12)
    p.add_argument("--threshold", type=Decimal, default=Decimal(10), help="flag variances at or above this %% (default 10)")
    p.add_argument("--decimal-comma", action="store_true", help="format as 1.234,56")
    p = sub.add_parser("allocate")
    p.add_argument("units_file")
    p.add_argument("--amount", required=True)
    p.add_argument("--decimal-comma", action="store_true")
    args = ap.parse_args()

    if args.cmd == "variance":
        if not 0 < args.months <= args.year_months:
            sys.exit("error: --months must be between 1 and --year-months")
        print(variance(read_budget(args.budget_csv), args.months, args.year_months, args.threshold, args.decimal_comma))
    else:
        print(allocate(read_units(args.units_file), money(args.amount, "--amount"), args.decimal_comma))


if __name__ == "__main__":
    main()
