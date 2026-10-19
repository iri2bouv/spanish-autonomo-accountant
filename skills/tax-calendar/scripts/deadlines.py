#!/usr/bin/env python3
"""Filing deadlines for a Spanish autónomo, with safe 'prepare by' dates.

Usage:
  deadlines.py --books DIR [--today 2026-10-19] [--days 60]
  deadlines.py --books DIR --year 2027 --ics calendar.ics

Reads the list of forms from DIR/profile.json ("forms": ["130", "111", ...]).
Supported: 130, 303, 349, 111, 115, 190, 180, 390, renta.

Rules (general AEAT calendar, common territory):
  - Quarterly Q1-Q3: 1-20 April / July / October.
  - Q4: 1-20 January (111, 115) or 1-30 January (130, 303, 349).
  - Annual: 190 and 180 by 31 January, 390 by 30 January, Renta by 30 June.
  - A deadline on a Saturday, Sunday or national holiday moves to the next working day.
  - Direct debit (domiciliación) closes earlier. This script uses a CONSERVATIVE
    cut-off of 5 calendar days before the original deadline. Check the official
    AEAT 'Calendario del contribuyente' of the year for the exact date.
  - 'prepare by' = direct-debit cut-off minus 7 days: the date to have the numbers ready.
"""
import argparse
import json
import os
import uuid
from datetime import date, datetime, timedelta

# National holidays that never move. Regional/local holidays are not included.
FIXED_HOLIDAYS = {(1, 1), (1, 6), (5, 1), (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)}

QUARTER_DUE = {1: (4, 20), 2: (7, 20), 3: (10, 20)}
Q4_DUE_DAY = {"130": 30, "303": 30, "349": 30, "111": 20, "115": 20}
NAMES = {
    "130": "Modelo 130 — IRPF payment on account",
    "303": "Modelo 303 — quarterly VAT return",
    "349": "Modelo 349 — EU operations summary",
    "111": "Modelo 111 — IRPF withheld from employees/professionals",
    "115": "Modelo 115 — IRPF withheld on rent",
    "190": "Modelo 190 — annual summary of the 111",
    "180": "Modelo 180 — annual summary of the 115",
    "390": "Modelo 390 — annual VAT summary",
    "renta": "Renta (modelo 100) — annual income tax return",
}


def next_working_day(d):
    while d.weekday() >= 5 or (d.month, d.day) in FIXED_HOLIDAYS:
        d += timedelta(days=1)
    return d


def obligations_for_tax_year(forms, y):
    items = []
    for f in forms:
        if f in Q4_DUE_DAY:
            for q, (m, d) in QUARTER_DUE.items():
                items.append((f, f"{y} Q{q}", date(y, m, d)))
            items.append((f, f"{y} Q4", date(y + 1, 1, Q4_DUE_DAY[f])))
        elif f in ("190", "180"):
            items.append((f, f"{y}", date(y + 1, 1, 31)))
        elif f == "390":
            items.append((f, f"{y}", date(y + 1, 1, 30)))
        elif f == "renta":
            items.append((f, f"{y}", date(y + 1, 6, 30)))
    out = []
    for f, period, original in items:
        deadline = next_working_day(original)
        has_payment = f not in ("190", "180", "390", "349")
        debit = original - timedelta(days=5) if has_payment else None
        prepare = (debit or deadline) - timedelta(days=7)
        out.append({"form": f, "name": NAMES[f], "period": period, "deadline": deadline,
                    "direct_debit_cutoff": debit, "prepare_by": prepare})
    return out


def all_obligations(forms, years):
    items = []
    for y in years:
        items.extend(obligations_for_tax_year(forms, y))
    return sorted(items, key=lambda i: (i["deadline"], i["form"]))


def ics(items):
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//spanish-autonomo-accountant//EN", "CALSCALE:GREGORIAN"]
    for i in items:
        for kind, day, alarms in (
            ("Prepare", i["prepare_by"], ["-P3D", "PT9H"]),
            ("DEADLINE", i["deadline"], ["-P2D"]),
        ):
            desc = f"{i['name']} for {i['period']}. Deadline {i['deadline'].isoformat()}."
            if i["direct_debit_cutoff"]:
                desc += f" Direct debit closes around {i['direct_debit_cutoff'].isoformat()} (check AEAT calendar)."
            lines += [
                "BEGIN:VEVENT", f"UID:{uuid.uuid4()}@spanish-autonomo-accountant", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}",
                f"SUMMARY:{kind}: {i['form'].upper()} {i['period']}", f"DESCRIPTION:{desc}",
            ]
            for trig in alarms:
                lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{kind}: {i['form'].upper()} {i['period']}",
                          f"TRIGGER:{trig}", "END:VALARM"]
            lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--books", help="folder with profile.json")
    p.add_argument("--forms", help="comma list, overrides profile, e.g. 130,111,190,renta")
    p.add_argument("--today", help="YYYY-MM-DD, default: today")
    p.add_argument("--days", type=int, default=60, help="look-ahead window")
    p.add_argument("--year", type=int, help="calendar year to export (all deadlines falling in it)")
    p.add_argument("--ics", help="write an .ics file to import into Google/Apple/Outlook calendar")
    a = p.parse_args()

    forms = []
    if a.forms:
        forms = [f.strip().lower() for f in a.forms.split(",") if f.strip()]
    elif a.books and os.path.exists(os.path.join(a.books, "profile.json")):
        with open(os.path.join(a.books, "profile.json"), encoding="utf-8") as f:
            forms = [str(x).lower() for x in json.load(f).get("forms", [])]
    if not forms:
        raise SystemExit("No forms: pass --forms or create profile.json with a 'forms' list.")
    unknown = [f for f in forms if f not in NAMES]
    if unknown:
        raise SystemExit(f"Unknown forms: {unknown}. Supported: {sorted(NAMES)}")

    today = date.fromisoformat(a.today) if a.today else date.today()
    if a.year:
        items = [i for i in all_obligations(forms, [a.year - 1, a.year]) if i["deadline"].year == a.year]
    else:
        items = [i for i in all_obligations(forms, [today.year - 1, today.year, today.year + 1])
                 if today <= i["deadline"] <= today + timedelta(days=a.days)]

    if a.ics:
        with open(a.ics, "w", encoding="utf-8", newline="") as f:
            f.write(ics(items))
        print(f"Wrote {len(items)} obligations ({len(items) * 2} events) to {a.ics}")

    if not items:
        print(f"Nothing due between {today} and {today + timedelta(days=a.days)}.")
    for i in items:
        days_left = (i["deadline"] - today).days
        debit = i["direct_debit_cutoff"].isoformat() if i["direct_debit_cutoff"] else "n/a (no payment)"
        flag = "  <-- PREPARE NOW" if i["prepare_by"] <= today <= i["deadline"] else ""
        print(f"{i['deadline'].isoformat()}  ({days_left:>3} days)  {i['form'].upper():<5} {i['period']:<8} "
              f"prepare by {i['prepare_by'].isoformat()} | direct debit until ~{debit}{flag}")


if __name__ == "__main__":
    main()
