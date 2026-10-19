#!/usr/bin/env python3
"""Year-end figures: Renta (activity income), modelo 190 / 180 detail, 130 check.

Usage:
  annual_summary.py --books DIR --year 2026

Reads DIR/ledger.csv, DIR/profile.json and DIR/filings/<year>-Q<n>-130.json.
Prints what the Renta needs for the economic activity (income, expenses by
category, 5% hard-to-justify expenses in the simplified regime, net income),
the payments on account and withholdings to deduct, and one line per recipient
for the annual summaries of withholdings (190 for the 111, 180 for the 115).
"""
import argparse
import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
ZERO = Decimal("0")
KEY_190 = {"employee": "A (work income)", "professional": "G (professional activity)"}


def money(v):
    return Decimal(str(v or "0")).quantize(CENT, rounding=ROUND_HALF_UP)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--books", required=True)
    p.add_argument("--year", type=int, required=True)
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
    y = str(a.year)

    income = withheld_by_clients = ZERO
    by_cat = {}
    recipients = {}
    for r in rows:
        if r["date"][:4] == y:
            if r["type"] == "income":
                income += money(r["net"])
                withheld_by_clients += money(r["withholding"])
            else:
                base = money(r["net"]) + (money(r["vat"]) if vat_is_cost else ZERO)
                pct = Decimal(r.get("deductible_pct") or "100")
                cat = r.get("category") or "uncategorised"
                by_cat[cat] = by_cat.get(cat, ZERO) + (base * pct / 100).quantize(CENT, rounding=ROUND_HALF_UP)
        kind = r.get("withholding_kind") or "none"
        if r["type"] == "expense" and kind != "none" and (r.get("paid_date") or r["date"])[:4] == y:
            key = (kind, r.get("counterparty") or "(no name)")
            rec = recipients.setdefault(key, {"base": ZERO, "withheld": ZERO})
            rec["base"] += money(r["net"])
            rec["withheld"] += money(r["withholding"])

    expenses = sum(by_cat.values(), ZERO)
    difficult = ZERO
    if profile.get("regime", "simplified") == "simplified" and profile.get("difficult_expenses", True):
        if income - expenses > 0:
            difficult = min(((income - expenses) * Decimal("0.05")).quantize(CENT, rounding=ROUND_HALF_UP),
                            Decimal("2000.00"))
    net = income - expenses - difficult

    paid_130 = ZERO
    missing = []
    for q in range(1, 5):
        fp = os.path.join(a.books, "filings", f"{a.year}-Q{q}-130.json")
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                b = json.load(f)["boxes"]
            paid_130 += max(money(b["19"]), ZERO)
        else:
            missing.append(q)

    print(f"ANNUAL SUMMARY {a.year}\n")
    print("Renta — economic activity (estimación directa"
          f" {'simplificada' if profile.get('regime', 'simplified') == 'simplified' else 'normal'})")
    print(f"  Income                                {income:>12.2f}")
    for cat, amt in sorted(by_cat.items()):
        print(f"  - {cat:<35} {amt:>12.2f}")
    if difficult:
        print(f"  - 5% hard-to-justify expenses (cap 2,000) {difficult:>8.2f}")
    print(f"  NET ACTIVITY INCOME                   {net:>12.2f}")
    reta_paid = by_cat.get("social_security", ZERO)
    reta_base = ((net + reta_paid) * Decimal("0.93")).quantize(CENT, rounding=ROUND_HALF_UP)
    print("")
    print("Social security (RETA) check — computable income = (net + RETA fees paid) x 0.93")
    print(f"  RETA fees recorded as expense         {reta_paid:>12.2f}")
    print(f"  Computable income, year               {reta_base:>12.2f}")
    print(f"  Computable income, monthly average    {(reta_base / 12).quantize(CENT):>12.2f}"
          "  -> compare with the bracket (tramo) you declared")
    print("")
    print(f"  Payments on account (130) paid        {paid_130:>12.2f}")
    if missing:
        print(f"  WARNING: no saved 130 for Q{', Q'.join(map(str, missing))} — add the amounts from the filed PDFs.")
    print(f"  Withholdings suffered (from clients)  {withheld_by_clients:>12.2f}")
    print("  -> both are deducted in the Renta. The draft (Renta WEB) usually pre-fills them; check they match.")

    for form, kinds in (("190", ("employee", "professional")), ("180", ("rent",))):
        lines = [(k, n, v) for (k, n), v in sorted(recipients.items()) if k in kinds]
        if not lines:
            continue
        print(f"\nModelo {form} — one line per recipient (add each recipient's NIF in the form)")
        total_w = ZERO
        for k, n, v in lines:
            label = KEY_190.get(k, "rent") if form == "190" else "rent"
            print(f"  {n[:30]:<30} key {label:<26} paid {v['base']:>10.2f}  withheld {v['withheld']:>9.2f}")
            total_w += v["withheld"]
        print(f"  Total withheld {total_w:.2f} — must equal the sum of the four "
              f"{'111' if form == '190' else '115'} returns of {a.year}.")


if __name__ == "__main__":
    main()
