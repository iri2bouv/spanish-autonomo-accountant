#!/usr/bin/env python3
"""How much to move to a separate 'taxes' account for a given month.

Usage:
  set_aside.py --books DIR --month 2026-10

Reads DIR/ledger.csv and DIR/profile.json:
  reta_monthly_fee   current monthly social security fee (cuota de autónomo)
  renta_buffer_pct   extra % of monthly profit kept for the annual Renta (default 5)

The 130 rate (20% of profit) is set by law. The Renta buffer is a prudence
heuristic, not a legal rate: the real annual tax depends on the full-year income,
personal allowances and the regional scale, and is settled in the Renta.
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--books", required=True)
    p.add_argument("--month", required=True, help="YYYY-MM")
    a = p.parse_args()

    ledger = os.path.join(a.books, "ledger.csv")
    if not os.path.exists(ledger):
        sys.exit(f"No ledger at {ledger}")
    with open(ledger, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    profile = {}
    pp = os.path.join(a.books, "profile.json")
    if os.path.exists(pp):
        with open(pp, encoding="utf-8") as f:
            profile = json.load(f)
    vat_is_cost = bool(profile.get("vat_is_cost", False))
    buffer_pct = Decimal(str(profile.get("renta_buffer_pct", 5)))
    reta = money(profile.get("reta_monthly_fee", 0))

    income = expenses = withheld_by_clients = withheld_from_others = vat_collected = ZERO
    for r in rows:
        if r["date"][:7] == a.month:
            if r["type"] == "income":
                income += money(r["net"])
                withheld_by_clients += money(r["withholding"])
                vat_collected += money(r["vat"])
            else:
                base = money(r["net"]) + (money(r["vat"]) if vat_is_cost else ZERO)
                pct = Decimal(r.get("deductible_pct") or "100")
                expenses += (base * pct / 100).quantize(CENT, rounding=ROUND_HALF_UP)
        if (r["type"] == "expense" and (r.get("withholding_kind") or "none") != "none"
                and (r.get("paid_date") or r["date"])[:7] == a.month):
            withheld_from_others += money(r["withholding"])

    profit = income - expenses
    irpf_130 = max((profit * Decimal("0.20")).quantize(CENT, rounding=ROUND_HALF_UP) - withheld_by_clients, ZERO)
    buffer = max((profit * buffer_pct / 100).quantize(CENT, rounding=ROUND_HALF_UP), ZERO)
    total = irpf_130 + buffer + withheld_from_others + (vat_collected if not vat_is_cost else ZERO)

    print(f"SET-ASIDE for {a.month}")
    print(f"  income (net)                         {income:>10.2f}")
    print(f"  deductible expenses                  {expenses:>10.2f}")
    print(f"  profit                               {profit:>10.2f}")
    print("")
    print(f"  for the 130 (20% of profit - withholdings)   {irpf_130:>10.2f}")
    print(f"  Renta buffer ({buffer_pct}% of profit, heuristic)   {buffer:>10.2f}")
    if withheld_from_others:
        print(f"  IRPF you withheld (111/115) — not your money {withheld_from_others:>10.2f}")
    if vat_collected and not vat_is_cost:
        print(f"  VAT collected (303) — not your money         {vat_collected:>10.2f}")
    print(f"  ---------------------------------------------------------")
    print(f"  MOVE TO THE TAX ACCOUNT                       {total:>10.2f}")
    if reta:
        print(f"\n  Plus: social security fee {reta:.2f} is direct-debited by the TGSS "
              "(last working day of the month) — keep it in the main account.")
    else:
        print("\n  Note: add 'reta_monthly_fee' to profile.json to include the social security fee.")


if __name__ == "__main__":
    main()
