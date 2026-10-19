---
name: tax-calendar
description: Use when a Spanish autónomo asks what tax deadlines are coming, what is due now or this month, when the next 130/111/303/Renta is due, wants reminders or a calendar file (.ics) for Google/Apple/Outlook calendar, or says "am I late on anything", "what's next", "remind me of my tax dates".
---

# Tax calendar

The core job of this agent: **nothing gets paid late.** Shows what is due, when to prepare
it, and puts every date in the user's own calendar with alarms.

## Files
- `books/profile.json` — the `forms` list (which returns apply)
- `books/filings/` — which returns are already done (`"status": "filed"`)
- Script: `scripts/deadlines.py` in this skill's folder
- Reference: `references/calendar-rules.md`

## Steps — "what's due?"
1. Run `python3 "<skill-dir>/scripts/deadlines.py" --books books --days 60`
   (add `--today YYYY-MM-DD` only to simulate another date).
2. Cross-check against `books/filings/`: drop anything already filed for that period.
3. Answer in this shape — closest first, days counted from today:

```
Next deadline: 130 + 111 for Q3 — in 8 days (Tue 20 Oct)
  Direct debit closes in 3 days (Thu 15 Oct) → prepare today
After that: nothing until January (130 Q4 by 1 Feb, 111 Q4 by 20 Jan, 190 by 1 Feb)
```

4. If a "prepare by" date has passed, say it plainly and offer to start the
   `quarterly-filing` flow right now.
5. If a deadline has **already passed** without a filing, say so, explain the cost briefly
   (1% + 1% per month surcharge, no penalty if filed before the AEAT asks — see the
   quarterly-filing `late-filing.md`), and push to file today.

## Steps — "put it in my calendar"
1. Run `python3 "<skill-dir>/scripts/deadlines.py" --books books --year <year> --ics books/tax-calendar-<year>.ics`
   (the current year, and next year too from November on).
2. Explain the import in one line per app:
   - Google Calendar: Settings → Import & export → Import → choose the file.
   - Apple Calendar: double-click the file.
   - Outlook: File → Open & Export → Import/Export → iCalendar.
3. Each obligation creates two events: **"Prepare"** (alarm 3 days before, and on the day)
   and **"DEADLINE"** (alarm 2 days before).

## Rules
- Dates come from the script; never compute them mentally.
- The direct-debit cut-off the script gives is conservative. If the user needs the exact
  day, point them to the AEAT calendar of the year.
- At the start of December, remind the user to re-generate next year's calendar once the
  AEAT publishes it.
