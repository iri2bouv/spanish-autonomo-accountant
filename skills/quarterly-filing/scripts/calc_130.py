#!/usr/bin/env python3
"""Modelo 130 calculator (IRPF payment on account, direct assessment).

Follows the official AEAT box structure (section I + section III). Section II
(agriculture) is not supported and is left at zero.

Usage:
  calc_130.py --books DIR --year 2026 --quarter 3 [--save]
              [--prior-05 AMOUNT] [--prior-negative AMOUNT] [--housing-16 AMOUNT]

Reads DIR/ledger.csv and DIR/profile.json. Previous quarters of the same year are
read from DIR/filings/<year>-Q<n>-130.json (written by --save). If a previous
quarter was filed elsewhere (e.g. by a former accountant), pass --prior-05 (sum of
positive box 07 of earlier quarters, minus their box 16) and --prior-negative
(negative box 19 amounts not yet used) taken from the PDFs actually filed.
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


def reduction_box_13(prior_year_net):
    """Art. 110.3.c RIRPF: reduction by previous year's net activity income."""
    if prior_year_net is None:
        return ZERO
    n = Decimal(str(prior_year_net))
    if n <= 9000:
        return Decimal("100.00")
    if n <= 10000:
        return Decimal("75.00")
    if n <= 11000:
        return Decimal("50.00")
    if n <= 12000:
        return Decimal("25.00")
    return ZERO


def ytd_figures(rows, profile, year, quarter):
    vat_is_cost = bool(profile.get("vat_is_cost", False))
    income = expenses = withheld = ZERO
    for r in rows:
        d = r["date"]
        if int(d[:4]) != year or quarter_of(d) > quarter:
            continue
        if r["type"] == "income":
            income += money(r["net"])
            withheld += money(r["withholding"])
        else:
            base = money(r["net"]) + (money(r["vat"]) if vat_is_cost else ZERO)
            pct = Decimal(r.get("deductible_pct") or "100")
            expenses += (base * pct / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    difficult = ZERO
    if profile.get("regime", "simplified") == "simplified" and profile.get("difficult_expenses", True):
        positive = income - expenses
        if positive > 0:
            difficult = min((positive * Decimal("0.05")).quantize(CENT, rounding=ROUND_HALF_UP), Decimal("2000.00"))
    return income, expenses, difficult, withheld


def load_prior(books, year, quarter):
    """Returns (box05, pending_negative, missing_quarters)."""
    box05 = ZERO
    negatives = ZERO
    used = ZERO
    missing = []
    for q in range(1, quarter):
        path = os.path.join(books, "filings", f"{year}-Q{q}-130.json")
        if not os.path.exists(path):
            missing.append(q)
            continue
        with open(path, encoding="utf-8") as f:
            b = json.load(f)["boxes"]
        box05 += max(money(b["07"]), ZERO) - money(b["16"])
        if money(b["19"]) < 0:
            negatives += -money(b["19"])
        used += money(b["15"])
    return box05, max(negatives - used, ZERO), missing


def calculate(income, expenses, withheld, box05, pending_negative, box13, housing16=ZERO, quarter=1):
    b = {}
    b["01"] = income
    b["02"] = expenses
    b["03"] = b["01"] - b["02"]
    b["04"] = (b["03"] * Decimal("0.20")).quantize(CENT, rounding=ROUND_HALF_UP) if b["03"] > 0 else ZERO
    b["05"] = box05
    b["06"] = withheld
    b["07"] = b["04"] - b["05"] - b["06"]
    b["11"] = ZERO  # section II (agriculture) not supported
    b["12"] = max(b["07"] + b["11"], ZERO)
    b["13"] = box13
    b["14"] = b["12"] - b["13"]
    b["15"] = min(pending_negative, max(b["14"], ZERO))
    b["16"] = min(housing16, max(b["14"] - b["15"], ZERO), Decimal("660.14"))
    b["17"] = b["14"] - b["15"] - b["16"]
    b["18"] = ZERO  # only for a complementary return
    b["19"] = b["17"] - b["18"]
    if b["19"] > 0:
        outcome = "TO PAY"
    elif b["19"] < 0 and quarter < 4:
        outcome = "NEGATIVE — carry forward: deductible from later 130s of this same year"
    elif b["19"] < 0:
        outcome = "NEGATIVE (Q4) — tick 'Negativa'; nothing to pay, the excess is settled in the annual Renta"
    else:
        outcome = "ZERO — tick 'Negativa'; still must be filed"
    return b, outcome


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--books", required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--quarter", type=int, required=True, choices=[1, 2, 3, 4])
    p.add_argument("--prior-05", help="override box 05 (previous payments of this year)")
    p.add_argument("--prior-negative", help="override unused negative box 19 from earlier quarters")
    p.add_argument("--housing-16", default="0", help="box 16 housing deduction (only pre-2013 mortgages)")
    p.add_argument("--save", action="store_true", help="write filings/<year>-Q<n>-130.json")
    a = p.parse_args()

    ledger = os.path.join(a.books, "ledger.csv")
    if not os.path.exists(ledger):
        sys.exit(f"No ledger at {ledger}")
    with open(ledger, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    profile = {}
    if os.path.exists(os.path.join(a.books, "profile.json")):
        with open(os.path.join(a.books, "profile.json"), encoding="utf-8") as f:
            profile = json.load(f)

    income, expenses, difficult, withheld = ytd_figures(rows, profile, a.year, a.quarter)
    box05, pending, missing = load_prior(a.books, a.year, a.quarter)
    if a.prior_05 is not None:
        box05 = money(a.prior_05)
    if a.prior_negative is not None:
        pending = money(a.prior_negative)
    if missing and a.prior_05 is None:
        print(f"WARNING: no saved 130 for Q{', Q'.join(map(str, missing))} of {a.year}. "
              "Box 05 may be too low and you would overpay. Pass --prior-05 from the filed PDFs.\n")

    box13 = reduction_box_13(profile.get("prior_year_net_income"))
    boxes, outcome = calculate(income, expenses + difficult, withheld, box05, pending, box13,
                               money(a.housing_16), a.quarter)

    print(f"MODELO 130 — {a.year} Q{a.quarter} (cumulative 1 January to end of Q{a.quarter})")
    print(f"  income in ledger:                  {income:>12.2f}")
    print(f"  deductible expenses in ledger:     {expenses:>12.2f}")
    if difficult:
        print(f"  + 5% hard-to-justify expenses:     {difficult:>12.2f}  (simplified regime, capped 2,000/yr)")
    print("")
    labels = {
        "01": "Income (ingresos computables)", "02": "Deductible expenses (gastos fiscalmente deducibles)",
        "03": "Net income (01 - 02)", "04": "20% of 03 (if positive)",
        "05": "Payments from earlier quarters this year", "06": "Withholdings suffered (retenciones)",
        "07": "04 - 05 - 06", "12": "07 + 11, not below 0", "13": "Reduction art. 110.3.c (prior-year net)",
        "14": "12 - 13", "15": "Negative results of earlier quarters", "16": "Housing deduction",
        "17": "14 - 15 - 16", "18": "Complementary return: previously paid", "19": "RESULT (17 - 18)",
    }
    for k in ["01", "02", "03", "04", "05", "06", "07", "12", "13", "14", "15", "16", "17", "18", "19"]:
        print(f"  [{k}] {labels[k]:<52} {boxes[k]:>12.2f}")
    print(f"\n  Outcome: {outcome}")

    if a.save:
        os.makedirs(os.path.join(a.books, "filings"), exist_ok=True)
        out = os.path.join(a.books, "filings", f"{a.year}-Q{a.quarter}-130.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"form": "130", "year": a.year, "quarter": a.quarter,
                       "boxes": {k: f"{v:.2f}" for k, v in boxes.items()},
                       "outcome": outcome, "status": "draft"}, f, indent=2)
        print(f"\n  Saved {out} (status: draft — set to 'filed' once submitted)")


if __name__ == "__main__":
    main()
