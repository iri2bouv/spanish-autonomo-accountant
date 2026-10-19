---
name: quarterly-filing
description: Use when a Spanish autónomo asks to prepare, calculate or file their quarterly tax returns — modelo 130 (IRPF payment on account), modelo 111 or 115 (withholdings), and when relevant 303 or 349 — or asks "what do I owe this quarter", "do my taxes for Q3", "prepare my 130", or how to submit a return on the AEAT Sede.
argument-hint: "[year] [quarter]"
---

# Quarterly filing

Prepares the quarter's returns box by box from the ledger, then guides the user through
submitting them on the AEAT Sede. **The user submits; you never claim something was filed
until they confirm it.**

## Files
- `books/profile.json` and `books/profile.md` — which forms apply (created by `autonomo-setup`)
- `books/ledger.csv` — income and expenses (kept by `bookkeeping`)
- `books/filings/<year>-Q<n>-<form>.json` — drafts and filed returns
- Scripts live in this skill's `scripts/` folder. Run them with the full path of this
  skill's base directory, e.g. `python3 "<skill-dir>/scripts/calc_130.py" ...`
- References in `references/`: `modelo-130.md`, `modelo-111.md`, `vat-foreign-clients.md`,
  `filing-on-sede.md`, `late-filing.md`

On Claude.ai (no persistent disk), ask the user to upload `ledger.csv`, `profile.json` and
earlier filings JSON at the start, and hand back updated files to download at the end.

## Steps

1. **Pick the period.** Use the arguments if given; otherwise the quarter that just ended
   (in January: Q4 of the previous year). Say which period you are preparing.
2. **Read the profile.** If `books/profile.json` is missing, stop and run the
   `autonomo-setup` flow first. Note the `forms` list.
3. **Check the ledger is complete.** Run `ledger.py check` (bookkeeping skill) if available,
   then list the quarter's rows. Ask once: "Are all invoices you issued and all expenses
   you paid this quarter in here?" Missing items are added through `bookkeeping` before
   calculating.
4. **Check earlier quarters.** For Q2–Q4 the 130 needs earlier 130s of the same year. If a
   `filings/<year>-Q<n>-130.json` is missing (e.g. a former accountant filed it), ask for
   the filed PDF and read boxes 07, 16 and 19 from it, then pass `--prior-05` and
   `--prior-negative`. Never skip this: a missing box 05 makes the user pay twice.
5. **Calculate — always with the scripts, never by hand:**
   - `python3 "<skill-dir>/scripts/calc_130.py" --books books --year Y --quarter Q`
   - `python3 "<skill-dir>/scripts/calc_111.py" --books books --year Y --quarter Q` (if 111 or 115 in forms)
   - 303 / 349: only if the profile says so. There is no script; read
     `references/vat-foreign-clients.md` and prepare the boxes from `ledger.py summary`.
6. **Sanity-check the output** before showing it: box 01 equals the ledger's year-to-date
   income; box 05 equals earlier positive 07s; nothing is negative where it can't be.
   If something looks off, say what and why — do not smooth it over.
7. **Present the draft** (format below), then save with `--save`.
8. **Guide the submission** with `references/filing-on-sede.md`. Recommend direct debit
   (domiciliación) when the cut-off has not passed: it removes the risk of paying late.
9. **After the user confirms submission**: set `"status": "filed"` in the JSON, store the
   PDF receipt in `books/filings/`, and tell them the next deadline (tax-calendar).

## Output format

```
Q3 2026 — ready to file

MODELO 130  (deadline 20 Oct · direct debit until ~15 Oct)
  [01] Income ......................... 10,000.00
  [02] Expenses ........................ 9,319.80
  ...
  [19] RESULT .............................. 0.00  → file as "Negativa"

MODELO 111  — no withholdings this quarter: nothing to file.

Next: open the Sede → Modelo 130 → "Presentación ejercicio 2026" (steps below)
```

Keep amounts with two decimals and the official box numbers so the user can copy them.

## Rules
- Use only script output for numbers. If a script fails, fix the input, don't estimate.
- If the deadline has already passed, say so plainly, explain the surcharge from
  `references/late-filing.md`, and push to file today.
- Do not file anything on the user's behalf and do not ask for their certificate or Cl@ve.
- If the situation is outside what the scripts cover (agriculture, objective estimation /
  módulos, a company), say so and recommend a professional.
- This is not professional tax advice; the user remains responsible for what is filed.
