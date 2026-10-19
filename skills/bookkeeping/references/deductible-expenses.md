# Deductible expenses — direct assessment (estimación directa)

Last verified: 2026-10-19. Main sources: Ley 35/2006 del IRPF art. 28–30, Reglamento IRPF
art. 30, AEAT "Manual práctico de Renta" (actividades económicas).

## The general test
An expense is deductible when it is (1) **linked to the activity**, (2) backed by a
**proper invoice** in the autónomo's name and NIF (a simple ticket is weak evidence),
(3) **recorded** in the books, and (4) dated in the period. When in doubt, record it with
`deductible_pct` 0 and a note, and ask.

## Usually deductible
| Expense | Rule |
|---|---|
| Social security fee (cuota RETA) | 100% |
| Software, subscriptions, hosting, domain | 100% if for the activity |
| Professional fees (asesor, lawyer), professional association | 100% |
| Coworking / office rent | 100% (rent of premises may require 19% withholding → 115) |
| Training linked to the activity | 100% |
| Bank fees of the business account | 100% |
| Health insurance for the autónomo, spouse and children under 25 | Up to **500 €/person/year** (1,500 € for a person with disability) |
| Home utilities when working from home (electricity, water, gas, internet) | **30% × (m² used for work / total m²)** — e.g. 20 m² of 80 m² → 7.5% |
| Home ownership costs (IBI, community fees, home insurance, depreciation) when the home is partly used | Proportion of m² used, if declared as used in the 036/037 |
| Meals while working, at a restaurant, paid **electronically** | Up to **26.67 €/day in Spain, 48.08 €/day abroad** (double when overnight). Paid by card, not cash |
| Travel and accommodation for work | With invoice and a clear business purpose |
| Phone / mobile | Business share only |
| Equipment (computer, furniture) | Depreciated over its useful life; new items ≤ 300 € each can be expensed at once, up to 25,000 €/year |
| VAT you paid, when your activity is VAT-exempt | Part of the expense (you cannot recover it) |

## Simplified regime extra
In **estimación directa simplificada**, add **5% of the positive net income** as
"provisiones y gastos de difícil justificación", **max 2,000 €/year**. The scripts do this
automatically when `profile.json` has `"regime": "simplified"`.

## Usually NOT deductible
- Personal expenses, clothing (unless uniforms/protective), gyms.
- Fines and penalties, late-filing surcharges.
- IRPF itself (130 payments) — it is a prepayment of tax, not an expense.
- Cars: generally not deductible for professionals unless used **exclusively** for the activity (hard to prove).
- Expenses without an invoice in the autónomo's name.

## When unsure
Explain the rule, record it as non-deductible with a note, and suggest checking the AEAT
"Informa" database or a one-off professional question. Never mark a doubtful expense
deductible just to lower the bill.
