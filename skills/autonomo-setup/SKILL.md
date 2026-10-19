---
name: autonomo-setup
description: Use when a Spanish autónomo starts using this accountant for the first time, wants to set up their books, says "set me up", "I'm new here", "I'm leaving my accountant / gestor", "I want to do my own taxes in Spain", or when their situation changes (new clients abroad, hiring someone, changing regime, moving region).
---

# Autónomo setup

Builds the user's profile and books folder, decides which returns they must file, and
organises the handover from a former accountant. Everything else depends on this being right.

## Files created
```
books/
├── profile.json      # machine-readable, used by every script
├── profile.md        # human-readable: situation, decisions and why, open questions
├── ledger.csv        # created by the bookkeeping script
├── documents/        # invoice and receipt PDFs
└── filings/          # returns: drafts, filed, receipts
CLAUDE.md             # the accountant instructions (Claude Code only)
.gitignore            # keeps books/ out of any git repository
```
Templates: `assets/profile.template.json`, `assets/workspace-CLAUDE.md`.
References: `references/questionnaire.md`, `references/vat-foreign-clients.md`.

## Steps

1. **Explain in three lines** what will happen: a few questions (~15 min), then a folder
   with their books and a list of what they must file and when.
2. **Ask for documents first** — they answer most questions: the census certificate
   (036/037 or "certificado de situación censal"), last year's Renta, the last 130 filed,
   one recent invoice they issued.
3. **Run the questionnaire** in `references/questionnaire.md`, in small rounds, skipping what
   the documents answer.
4. **Stop if unsupported**: foral territory (Basque Country, Navarre), Canary Islands (IGIC),
   módulos, or a company (SL). Say so clearly; this agent covers individual autónomos in
   the common territory under direct assessment.
5. **Settle VAT** with `references/vat-foreign-clients.md`. Write the conclusion, the legal
   basis and any doubt in `profile.md`. If it is not clear-cut, list it as an open question
   to confirm with the AEAT — do not guess, it decides whether 303/349 apply.
6. **Decide the forms list** with the table at the end of the questionnaire.
7. **Create the files**:
   - `profile.json` from the template (`vat_is_cost: true` when VAT on expenses cannot be recovered);
   - `profile.md` with the situation, forms and why, open questions, setup date;
   - the books folder: `python3 "<bookkeeping-skill-dir>/scripts/ledger.py" init --books books`;
   - Claude Code only: copy `assets/workspace-CLAUDE.md` to `./CLAUDE.md`, and write a
     `.gitignore` containing `books/`.
8. **Handover** (if switching from an accountant):
   - record the returns already filed this year as `books/filings/<year>-Q<n>-130.json` with
     `"status": "filed"` and the boxes read from the PDFs (needed for the next 130);
   - add this year's past income and expenses to the ledger (bookkeeping skill), from the
     accountant's books or from the invoices;
   - give the user the request list for the accountant (questionnaire round 5).
9. **Finish with the calendar**: run the tax-calendar flow, offer the `.ics` file, and state
   the next deadline and its "prepare by" date.

## Output at the end
```
You're set up.
You file: 130 every quarter · 111 + 190 (you pay a freelancer with withholding) · Renta
You don't file: 303/390 (exempt activity) — open question: 349, see profile.md
Next: 130 + 111 for Q3, due Tue 20 Oct — prepare by Thu 8 Oct
```

## Rules
- Personal data (NIF, amounts) stays in `books/`. Never put it in the skill files or anywhere public.
- Do not change anything with the AEAT or the Social Security for the user; tell them what
  to do and where.
- Re-run this skill whenever the situation changes, and update `profile.md` with the date.
