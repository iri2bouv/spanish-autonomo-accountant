# Setup questionnaire

Ask in small rounds (max 3 questions per message). Skip anything already answered or
readable from a document the user shares (the census form 036/037, a past 130, an invoice).
The fastest route: ask for the **036/037** PDF ("Certificado de situación censal" from the
Sede) — it answers most of round 2.

## Round 1 — basics
1. Name and NIF/NIE (stored locally only, used to check invoices).
2. Where are you registered for tax: common territory, Basque Country / Navarre (foral), or Canary Islands?
   → Only **common territory** is supported. For the others, stop and say so.
3. Since when are you autónomo? (first 3 years: clients in Spain withhold 7% instead of 15%)

## Round 2 — activity and regime
4. What do you do, and under which IAE code / heading (epígrafe)?
5. Income tax regime: estimación directa **simplificada** (most freelancers), normal, or módulos?
   → Módulos (objective estimation) is not supported.
6. Do you charge VAT on your invoices? If not, what does the invoice say (exempt article, reverse charge)?

## Round 3 — clients and suppliers
7. Where are your clients (Spain / other EU countries / outside the EU)? Businesses or private individuals?
8. Do any clients withhold IRPF from your invoices? (only Spanish clients do)
9. Do you pay anyone with IRPF withholding — employees, Spanish freelancers, office rent?
   → yes: 111 (and 190); rent: 115 (and 180).

## Round 4 — money
10. Current monthly social security fee (cuota), and the bracket you declared if you know it.
11. Net activity income of last year (box "rendimiento neto" of the last Renta) — used for the 130 box 13 reduction.
12. Do you work from home? m² used for work / total m² (for utilities).

## Round 5 — the handover (if switching from an accountant)
13. Which returns of the current year has the accountant already filed? Ask for the PDFs.
14. Ask the accountant for: the income/expense books of the current year (libro de ingresos
    y gastos), copies of every return filed in the last 4 years, and the census form 036/037.
15. If the accountant holds a power of attorney (apoderamiento) or the user's certificate,
    the user can revoke it on the Sede ("Apoderamientos") once the handover is done.

## Deciding the forms list
| Situation | Add |
|---|---|
| Direct assessment and < 70% of income withheld | `130` |
| Pays employees or Spanish professionals with withholding | `111`, `190` |
| Pays office rent with withholding | `115`, `180` |
| VAT applies (see `vat-foreign-clients.md`) | `303`, `390` |
| Intra-EU B2B services subject and not exempt in the client's State | `349` |
| Always | `renta` |
