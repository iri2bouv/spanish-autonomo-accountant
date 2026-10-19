# Annual obligations

Last verified: 2026-10-19. Sources: AEAT Calendario del contribuyente 2026, AEAT
instructions for modelos 190 / 390, Manual práctico de Renta.

## January (for the year just ended)
| Form | Who | Deadline | Notes |
|---|---|---|---|
| 190 | Anyone who filed a 111 during the year | 31 January | One line per recipient: NIF, name, key (A = employee, G = professional activity), amount paid, IRPF withheld. Total = sum of the four 111s |
| 180 | Anyone who filed a 115 | 31 January | One line per landlord |
| 390 | Only if 303s are filed | 30 January | Annual VAT summary |
| 347 | Operations > 3,005.06 € with one Spanish counterparty, not already reported elsewhere | February | Rarely relevant for foreign-clients-only freelancers; check if you have big Spanish suppliers |

## Renta (modelo 100) — April to 30 June
1. In April the AEAT opens **Renta WEB** with a draft (borrador) and tax data (datos fiscales).
2. The economic activity section is **not** pre-filled correctly for autónomos: enter
   income and expenses by category from `annual_summary.py`, with the regime
   (estimación directa simplificada) and the IAE code of the activity.
3. Check the **130 payments** and **withholdings** in the tax data match the summary.
   The Renta deducts them from the final tax.
4. Result to pay can be split: 60% when filing and 40% by 5 November, with no interest,
   as long as the return is filed on time. Useful when cash is tight.
5. Direct debit for the Renta closes around 25 June.

## Social security (RETA) regularisation
Since 2023 the contribution depends on real net income. The user picks a bracket (tramo)
from forecast income and can change it up to six times a year through Import@ss. After
the Renta, the TGSS receives the real income from the AEAT and **regularises**: refund if
too much was paid, an extra charge if too little.
- Computable income = (net activity income + RETA fees paid) × 0.93 (0.97 for company directors).
- Divide by the months registered to get the monthly figure, and compare with the declared bracket.
- The bracket table changes every year: check the current one on seg-social.es / Import@ss
  before advising a change. Do not quote bracket amounts from memory.
