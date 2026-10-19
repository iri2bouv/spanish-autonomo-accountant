# Modelo 130 — IRPF payment on account (direct assessment)

Last verified: 2026-10-19 against the official AEAT instructions:
https://sede.agenciatributaria.gob.es/Sede/impuestos-tasas/impuesto-sobre-renta-personas-fisicas/modelo-130-irpf______esionales-estimacion-directa-fraccionado_/instrucciones.html

## Who files it
Every autónomo in direct assessment (normal or simplified), every quarter, **unless**
at least 70% of the previous year's activity income had IRPF withheld by clients
(for a new activity: 70% of the current quarter's income). Clients outside Spain do
not withhold Spanish IRPF, so someone billing foreign clients almost always files it.

## How it works
It is **cumulative**: every quarter you declare income and expenses from 1 January to
the end of the quarter, take 20% of the profit, and subtract what you already paid
earlier in the year and the withholdings you suffered.

## Boxes (section I and section III)
| Box | Meaning |
|---|---|
| 01 | Income, 1 Jan to end of quarter (without VAT) |
| 02 | Deductible expenses, same period (in simplified regime includes the 5% hard-to-justify expenses, max 2,000/yr) |
| 03 | 01 − 02 (may be negative) |
| 04 | 20% of 03 if positive, else 0 |
| 05 | Sum of positive box 07 of earlier quarters of the same year, minus their box 16 |
| 06 | IRPF withheld by clients, 1 Jan to end of quarter |
| 07 | 04 − 05 − 06 (may be negative) |
| 12 | 07 + 11, not below 0 (11 = agriculture, normally 0) |
| 13 | Reduction by previous year's net activity income (art. 110.3.c RIRPF): ≤9,000 → 100; ≤10,000 → 75; ≤11,000 → 50; ≤12,000 → 25; above → 0. No activity last year counts as 0 → 100 |
| 14 | 12 − 13 (may be negative) |
| 15 | Negative box 19 results of earlier quarters of the same year not yet used, capped at positive 14 |
| 16 | Housing-loan deduction (only loans for a main home bought before 2013), max 660.14 per quarter |
| 17 | 14 − 15 − 16 |
| 18 | Only in a complementary return: amount paid by the earlier return |
| 19 | 17 − 18 = **result** |

## Result
- Positive → pay it.
- Negative in Q1–Q3 → nothing to pay; carry it to box 15 of later quarters (same year only).
- Zero, or negative in Q4 → file anyway and tick **"Negativa"**. A 130 is filed every quarter even when nothing is owed.

## Common mistakes
- Using only the quarter's figures instead of year-to-date.
- Forgetting box 05 (paying twice for the same profit).
- Including VAT in box 01.
- For a VAT-exempt activity: forgetting that VAT paid on expenses cannot be recovered, so it is part of the deductible expense.
