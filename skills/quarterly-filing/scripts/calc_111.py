#!/usr/bin/env python3
"""Modelo 111 (and 115) calculator: IRPF you withheld from others and must pay over.

Usage:
  calc_111.py --books DIR --year 2026 --quarter 3 [--save]

Reads expense rows of DIR/ledger.csv with a withholding. Timing follows the date
the payment was made (column paid_date, falling back to date), because the
obligation arises when you pay, not when the invoice is dated.

  withholding_kind = employee      -> 111 boxes 01-03 (work income)
  withholding_kind = professional  -> 111 boxes 07-09 (economic activities)
  withholding_kind = rent          -> modelo 115 (office/premises rent)

If a quarter has no withholdings at all, the 111 is NOT filed with empty boxes
(AEAT instructions); the script says so.
"""
import argparse
import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ZERO = Decimal("0")


def money(v):
    return Decimal(str(v or "0")).quantize(CENT, rounding=ROUND_HALF_UP)


def quarter_of(d):
    return (int(d[5:7]) - 1) // 3 + 1


def collect(rows, year, quarter):
    groups = {k: {"recipients": set(), "base": ZERO, "withheld": ZERO}
              for k in ("employee", "professional", "rent")}
    for r in rows:
        kind = r.get("withholding_kind") or "none"
        if r["type"] != "expense" or kind not in groups:
            continue
        d = r.get("paid_date") or r["date"]
        if int(d[:4]) != year or quarter_of(d) != quarter:
            continue
        g = groups[kind]
        g["recipients"].add((r.get("counterparty") or "").strip().lower() or f"row-{id(r)}")
        g["base"] += money(r["net"])
        g["withheld"] += money(r["withholding"])
    return groups


def boxes_111(groups):
    e, p = groups["employee"], groups["professional"]
    b = {
        "01": len(e["recipients"]), "02": e["base"], "03": e["withheld"],
        "07": len(p["recipients"]), "08": p["base"], "09": p["withheld"],
    }
    b["28"] = b["03"] + b["09"]
    b["29"] = ZERO  # only for a complementary return
    b["30"] = b["28"] - b["29"]
    return b


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--books", required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--quarter", type=int, required=True, choices=[1, 2, 3, 4])
    p.add_argument("--save", action="store_true")
    a = p.parse_args()

    ledger = os.path.join(a.books, "ledger.csv")
    if not os.path.exists(ledger):
        sys.exit(f"No ledger at {ledger}")
    with open(ledger, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    groups = collect(rows, a.year, a.quarter)
    b = boxes_111(groups)

    print(f"MODELO 111 — {a.year} Q{a.quarter} (withholdings on payments made this quarter)")
    if b["28"] == 0:
        print("  No withholdings this quarter. Do NOT file a 111 with all boxes empty "
              "(AEAT instructions). If you will never withhold again, update your census "
              "registration (modelo 036/037).")
    else:
        print(f"  [01] Employees (recipients)                 {b['01']:>12}")
        print(f"  [02] Employees: amounts paid                {b['02']:>12.2f}")
        print(f"  [03] Employees: IRPF withheld               {b['03']:>12.2f}")
        print(f"  [07] Professionals (recipients)             {b['07']:>12}")
        print(f"  [08] Professionals: amounts paid            {b['08']:>12.2f}")
        print(f"  [09] Professionals: IRPF withheld           {b['09']:>12.2f}")
        print(f"  [28] Total withheld                         {b['28']:>12.2f}")
        print(f"  [30] RESULT TO PAY                          {b['30']:>12.2f}")

    rent = groups["rent"]
    if rent["withheld"] > 0:
        print(f"\nMODELO 115 — {a.year} Q{a.quarter} (rent withholdings)")
        print(f"  [01] Landlords (recipients)                 {len(rent['recipients']):>12}")
        print(f"  [02] Rent paid (base)                       {rent['base']:>12.2f}")
        print(f"  [03] Withheld = RESULT TO PAY               {rent['withheld']:>12.2f}")

    if a.save:
        status = "draft" if b["28"] > 0 or rent["withheld"] > 0 else "not_required"
        os.makedirs(os.path.join(a.books, "filings"), exist_ok=True)
        out = os.path.join(a.books, "filings", f"{a.year}-Q{a.quarter}-111.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"form": "111", "year": a.year, "quarter": a.quarter,
                       "boxes": {k: (f"{v:.2f}" if isinstance(v, Decimal) else v) for k, v in b.items()},
                       "rent_115": {"recipients": len(rent["recipients"]), "base": f"{rent['base']:.2f}",
                                    "withheld": f"{rent['withheld']:.2f}"},
                       "status": status}, f, indent=2)
        print(f"\n  Saved {out} (status: {status})")


if __name__ == "__main__":
    main()
