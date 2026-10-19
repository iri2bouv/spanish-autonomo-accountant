#!/usr/bin/env python3
"""Income and expense ledger for a Spanish autónomo (one CSV file).

Usage:
  ledger.py init    --books DIR
  ledger.py add     --books DIR --date 2026-10-03 --type income --description "..." \
                    --counterparty "Client ApS" --country DK --net 1200 [--vat 0] \
                    [--withholding 0] [--withholding-kind none] [--deductible-pct 100] \
                    [--category services] [--invoice-no 2026-014] [--paid-date 2026-10-10] [--notes "..."]
  ledger.py list    --books DIR [--year 2026] [--quarter 4] [--type income|expense]
  ledger.py summary --books DIR --year 2026 [--quarter 4] [--cumulative]
  ledger.py check   --books DIR

Only the Python standard library is used. Amounts are euros with two decimals.
"""
import argparse
import csv
import json
import os
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

COLUMNS = [
    "date", "type", "description", "counterparty", "country", "net", "vat",
    "withholding", "withholding_kind", "deductible_pct", "category",
    "invoice_no", "paid_date", "notes",
]
TYPES = {"income", "expense"}
WITHHOLDING_KINDS = {"none", "professional", "employee", "rent", "other"}
CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value or "0")).quantize(CENT, rounding=ROUND_HALF_UP)


def ledger_path(books):
    return os.path.join(books, "ledger.csv")


def load_profile(books):
    path = os.path.join(books, "profile.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_rows(books):
    path = ledger_path(books)
    if not os.path.exists(path):
        sys.exit(f"No ledger at {path}. Run: ledger.py init --books {books}")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def quarter_of(iso_date):
    return (int(iso_date[5:7]) - 1) // 3 + 1


def in_period(row, year, quarter=None, cumulative=False, field="date"):
    d = row.get(field) or row["date"]
    if int(d[:4]) != year:
        return False
    if quarter is None:
        return True
    q = quarter_of(d)
    return q <= quarter if cumulative else q == quarter


def deductible_amount(row, vat_is_cost):
    """Expense amount that reduces taxable profit (IRPF)."""
    base = money(row["net"])
    if vat_is_cost:
        # Input VAT you cannot recover (VAT-exempt activity) is part of the cost.
        base += money(row["vat"])
    pct = Decimal(row.get("deductible_pct") or "100")
    return (base * pct / 100).quantize(CENT, rounding=ROUND_HALF_UP)


def summarize(rows, profile, year, quarter=None, cumulative=False):
    vat_is_cost = bool(profile.get("vat_is_cost", False))
    out = {
        "income_net": Decimal("0"), "income_vat": Decimal("0"),
        "income_withheld_by_clients": Decimal("0"),
        "expenses_deductible": Decimal("0"), "expenses_vat": Decimal("0"),
        "withheld_from_others": {k: Decimal("0") for k in WITHHOLDING_KINDS - {"none"}},
        "expenses_by_category": {},
        "rows": 0,
    }
    for r in rows:
        if not in_period(r, year, quarter, cumulative):
            continue
        out["rows"] += 1
        if r["type"] == "income":
            out["income_net"] += money(r["net"])
            out["income_vat"] += money(r["vat"])
            out["income_withheld_by_clients"] += money(r["withholding"])
        else:
            amt = deductible_amount(r, vat_is_cost)
            out["expenses_deductible"] += amt
            out["expenses_vat"] += money(r["vat"])
            cat = r.get("category") or "uncategorised"
            out["expenses_by_category"][cat] = out["expenses_by_category"].get(cat, Decimal("0")) + amt
    # Withholdings she must pay over (111/115) follow the PAYMENT date.
    for r in rows:
        kind = r.get("withholding_kind") or "none"
        if r["type"] == "expense" and kind != "none" and in_period(r, year, quarter, cumulative, field="paid_date"):
            out["withheld_from_others"][kind] += money(r["withholding"])
    out["net_profit"] = out["income_net"] - out["expenses_deductible"]
    return out


def to_jsonable(obj):
    if isinstance(obj, Decimal):
        return f"{obj:.2f}"
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    return obj


def validate_row(row):
    errors = []
    try:
        date.fromisoformat(row["date"])
    except ValueError:
        errors.append(f"bad date {row['date']!r} (use YYYY-MM-DD)")
    if row.get("paid_date"):
        try:
            date.fromisoformat(row["paid_date"])
        except ValueError:
            errors.append(f"bad paid_date {row['paid_date']!r}")
    if row["type"] not in TYPES:
        errors.append(f"type must be income or expense, got {row['type']!r}")
    kind = row.get("withholding_kind") or "none"
    if kind not in WITHHOLDING_KINDS:
        errors.append(f"withholding_kind must be one of {sorted(WITHHOLDING_KINDS)}")
    for field in ("net", "vat", "withholding", "deductible_pct"):
        try:
            Decimal(str(row.get(field) or "0"))
        except Exception:
            errors.append(f"{field} is not a number: {row.get(field)!r}")
    if row["type"] == "income" and kind not in ("none", "professional"):
        errors.append("on income, withholding_kind is 'none' or 'professional' (withheld by your client)")
    if row["type"] == "expense" and money(row.get("withholding")) > 0 and kind == "none":
        errors.append("expense has a withholding but withholding_kind is 'none'")
    return errors


def cmd_init(a):
    os.makedirs(os.path.join(a.books, "filings"), exist_ok=True)
    os.makedirs(os.path.join(a.books, "documents"), exist_ok=True)
    path = ledger_path(a.books)
    if os.path.exists(path):
        print(f"Ledger already exists: {path}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(COLUMNS)
    print(f"Created {path}")


def cmd_add(a):
    row = {
        "date": a.date, "type": a.type, "description": a.description,
        "counterparty": a.counterparty or "", "country": (a.country or "ES").upper(),
        "net": f"{money(a.net):.2f}", "vat": f"{money(a.vat):.2f}",
        "withholding": f"{money(a.withholding):.2f}",
        "withholding_kind": a.withholding_kind, "deductible_pct": str(a.deductible_pct),
        "category": a.category or "", "invoice_no": a.invoice_no or "",
        "paid_date": a.paid_date or "", "notes": a.notes or "",
    }
    errors = validate_row(row)
    if errors:
        sys.exit("Not added:\n- " + "\n- ".join(errors))
    if not os.path.exists(ledger_path(a.books)):
        cmd_init(a)
    rows = read_rows(a.books)
    if row["invoice_no"] and any(
        r["invoice_no"] == row["invoice_no"] and r["type"] == row["type"]
        and r["counterparty"] == row["counterparty"] for r in rows
    ):
        sys.exit(f"Not added: {row['type']} invoice {row['invoice_no']} from/to {row['counterparty']} is already in the ledger.")
    with open(ledger_path(a.books), "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=COLUMNS).writerow(row)
    print(f"Added {row['type']} {row['date']} {row['net']} EUR — {row['description']}")


def cmd_list(a):
    rows = read_rows(a.books)
    for r in rows:
        if a.year and not in_period(r, a.year, a.quarter):
            continue
        if a.type and r["type"] != a.type:
            continue
        print(f"{r['date']}  {r['type']:<7} {r['net']:>10}  vat {r['vat']:>8}  wh {r['withholding']:>8}  "
              f"{r['counterparty'][:24]:<24} {r['description'][:40]}")


def cmd_summary(a):
    rows = read_rows(a.books)
    s = summarize(rows, load_profile(a.books), a.year, a.quarter, a.cumulative)
    print(json.dumps(to_jsonable(s), indent=2, ensure_ascii=False))


def cmd_check(a):
    rows = read_rows(a.books)
    problems = 0
    for i, r in enumerate(rows, start=2):
        for e in validate_row(r):
            problems += 1
            print(f"line {i}: {e}")
    if not problems:
        print(f"OK — {len(rows)} rows, no problems found.")
    sys.exit(1 if problems else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "add", "list", "summary", "check"):
        sp = sub.add_parser(name)
        sp.add_argument("--books", required=True, help="folder that holds ledger.csv and profile.json")
        if name == "add":
            sp.add_argument("--date", required=True, help="invoice date YYYY-MM-DD")
            sp.add_argument("--type", required=True, choices=sorted(TYPES))
            sp.add_argument("--description", required=True)
            sp.add_argument("--counterparty")
            sp.add_argument("--country", help="ISO code of the client/supplier, e.g. ES, DK")
            sp.add_argument("--net", required=True, help="taxable base, without VAT")
            sp.add_argument("--vat", default="0")
            sp.add_argument("--withholding", default="0", help="IRPF withheld (by client on income, by you on expense)")
            sp.add_argument("--withholding-kind", default="none", choices=sorted(WITHHOLDING_KINDS))
            sp.add_argument("--deductible-pct", default=100, type=int)
            sp.add_argument("--category")
            sp.add_argument("--invoice-no")
            sp.add_argument("--paid-date", help="date actually paid (drives 111/115 timing)")
            sp.add_argument("--notes")
        if name in ("list", "summary"):
            sp.add_argument("--year", type=int, required=(name == "summary"))
            sp.add_argument("--quarter", type=int, choices=[1, 2, 3, 4])
        if name == "list":
            sp.add_argument("--type", choices=sorted(TYPES))
        if name == "summary":
            sp.add_argument("--cumulative", action="store_true", help="from January to the end of --quarter")
    a = p.parse_args()
    {"init": cmd_init, "add": cmd_add, "list": cmd_list, "summary": cmd_summary, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
