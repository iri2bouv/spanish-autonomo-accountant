# Tax calendar rules — common territory

Last verified: 2026-10-19 against the AEAT "Calendario del contribuyente 2026".
Each December the AEAT publishes next year's calendar: re-check it then
(https://sede.agenciatributaria.gob.es → "Calendario del contribuyente").

| Form | Period | Filing window | Direct debit (domiciliación) closes |
|---|---|---|---|
| 130, 303, 349 | Q1 / Q2 / Q3 | 1–20 April / July / October | 15th |
| 130, 303, 349 | Q4 | 1–30 January | late January (27 Jan in 2026) — script uses 25th to be safe |
| 111, 115 | Q1 / Q2 / Q3 | 1–20 April / July / October | 15th |
| 111, 115 | Q4 | 1–20 January | 15 January |
| 190, 180 | year | 1–31 January | no payment |
| 390 | year | 1–30 January | no payment |
| Renta (100) | year | early April – 30 June | ~25 June |
| Social security (RETA) | month | charged by direct debit on the last working day of the month | automatic |

- When a deadline falls on a Saturday, Sunday or national holiday it moves to the next working day
  (e.g. the 190 for 2025 was due 2 February 2026).
- The script only knows national fixed holidays; regional holidays rarely matter for these dates.

## Why the "prepare by" date
Late payments come from starting too late, not from the deadline itself. The script sets
"prepare by" = direct-debit cut-off − 7 days. Having the numbers ready by then leaves time to
gather a missing invoice and still pay by direct debit, which removes the risk of forgetting
to pay on the last day.
