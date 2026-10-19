---
name: bookkeeping
description: Use when a Spanish autónomo wants to record an invoice, a receipt or an expense, log income, check whether an expense is deductible, see their income and expenses for a period, fix the ledger, or asks "add this invoice", "is this deductible", "how much did I earn this quarter", or drops invoice PDFs to be filed.
argument-hint: "[invoice file or description]"
---

# Bookkeeping

Keeps `books/ledger.csv` — the single source every other skill calculates from. A clean
ledger is what makes filing take 15 minutes instead of an afternoon.

## Files
- `books/ledger.csv` — format in `references/ledger-format.md`
- `books/profile.json` — `vat_is_cost`, `regime`
- `books/documents/<year>/` — PDFs of every invoice and receipt
- Script: `scripts/ledger.py` in this skill's folder (`init`, `add`, `list`, `summary`, `check`)
- References: `ledger-format.md`, `deductible-expenses.md`, `invoices.md`

On Claude.ai (no persistent disk), ask for the current `ledger.csv` first and give back the
updated file at the end of the conversation.

## Steps — recording documents

1. **Read each document** (PDF, photo, email text). Extract: date, issuer/recipient, invoice
   number, net amount, VAT, IRPF withholding, description.
2. **Classify it**: income (an invoice the user issued) or expense (one they received).
3. **For expenses, decide deductibility** with `references/deductible-expenses.md`. Set
   `deductible_pct` (100, a share for mixed use, or 0) and `category`. If unsure, ask one
   short question; if still unsure, record at 0 with a note.
4. **Check withholdings**: a Spanish freelancer's invoice with IRPF withheld →
   `withholding_kind professional` and ask for the payment date (`paid_date`); office rent with
   withholding → `rent`. These feed the 111/115.
5. **Add with the script** (one call per document):
   `python3 "<skill-dir>/scripts/ledger.py" add --books books --date ... --type ... --description ... --counterparty ... --country ... --net ... [--vat ...] [--withholding ... --withholding-kind ... --paid-date ...] [--deductible-pct ...] --category ... --invoice-no ...`
   The script refuses duplicates and inconsistent rows — read its message and fix the input.
6. **File the PDF** as `books/documents/<year>/<date>_<counterparty>_<invoice_no>.pdf` (Claude Code only).
7. **Confirm** in one table: what was added, the deductible amount, anything set aside as doubtful.

## Steps — checking income invoices the user issues
When the user shares an invoice they are about to send, check it against
`references/invoices.md`: consecutive number, both parties' tax IDs, the right legal mention
when no VAT is charged, no IRPF withholding for foreign clients. Point out exactly what to fix.

## Other requests
- "How much did I earn / spend?" → `ledger.py summary --books books --year Y [--quarter Q] [--cumulative]`
- "Is everything OK?" → `ledger.py check --books books`, then look for gaps: months with no
  social security fee, invoice numbers that skip, income without a client country.

## Rules
- Never invent a number. If a document is unreadable, ask for a better copy.
- Amounts are without VAT in `net`; VAT goes in `vat`.
- Do not edit `ledger.csv` by hand-writing CSV lines; use the script so validation runs.
  To correct a row, show the user the line, edit it, then run `check`.
- Do not create or send invoices on the user's behalf; review them only.
