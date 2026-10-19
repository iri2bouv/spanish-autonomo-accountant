---
name: annual-filing
description: Use when a Spanish autónomo asks about year-end or annual tax work — the Renta (modelo 100, income tax return), modelo 190 or 180 annual summaries, modelo 390, closing the year, or checking their social security (RETA) bracket against real income — or says "prepare my Renta", "do my annual return", "what do I file in January", "am I paying the right cuota".
argument-hint: "[year]"
---

# Annual filing

Closes the year: the January summaries (190/180/390), the Renta in spring, and the check of
the social security bracket. Same principle as the quarter: numbers from the scripts, the user
files.

## Files
- `books/ledger.csv`, `books/profile.json`, `books/filings/<year>-Q<n>-*.json`
- Script: `scripts/annual_summary.py` in this skill's folder
- Reference: `references/annual-obligations.md`
- For filing steps on the Sede and late filing, see the quarterly-filing skill references
  (`filing-on-sede.md`, `late-filing.md`).

## Steps

1. **Pick the year** (argument, or the last complete year).
2. **Make sure the year is closed**: all four 130s (and 111s if any) exist in
   `books/filings/` with `"status": "filed"`. If not, deal with the missing quarter first
   (quarterly-filing).
3. **Run** `python3 "<skill-dir>/scripts/annual_summary.py" --books books --year Y`.
4. **Then by season:**
   - **January** → 190 (if the 111 applies), 180 (if the 115 applies), 390 (if 303s were
     filed). Show the per-recipient lines from the script; ask for each recipient's NIF if
     missing; check the 190 total equals the sum of the 111s.
   - **April–June** → Renta. Walk through Renta WEB using the activity figures, check that
     the 130 payments and withholdings in the AEAT tax data match, and mention the 60/40
     split option if there is something to pay. The full Renta also has non-activity parts
     (bank interest, property, family situation, regional deductions): ask about them, and
     say clearly when something is outside this agent's scope.
   - **Any time after the year closes** → RETA check: compare the monthly computable income
     with the bracket the user declared. If they differ a lot, warn about the regularisation
     to come and suggest adjusting the bracket for the current year in Import@ss.
5. **Write down** what was filed in `books/filings/<year>-annual.md` (form, date, result, receipt file).

## Output format
Lead with the action and the date, then the figures:

```
2026 is closed. Two things left:
1. Modelo 190 — due Mon 1 Feb 2027 — 1 recipient, 150.00 withheld (matches the four 111s)
2. Renta 2026 — from April, by 30 June 2027
   Net activity income 680.20 · 130 already paid 1,276.04 → likely refund
RETA: computable 192.22/month vs declared bracket → expect a refund at regularisation
```

## Rules
- "Likely refund / likely to pay" are indications. The final Renta depends on the whole
  personal situation; say so.
- Never quote RETA bracket amounts or personal-allowance figures from memory; check the
  current official tables, or say you could not.
- Joint returns, property income, capital gains, foreign income other than the activity:
  flag them and recommend a professional review if they are significant.
