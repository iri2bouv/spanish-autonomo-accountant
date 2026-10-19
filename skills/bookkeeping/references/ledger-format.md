# Ledger format — books/ledger.csv

One row per invoice issued (income) or expense paid. UTF-8 CSV with this header:

`date,type,description,counterparty,country,net,vat,withholding,withholding_kind,deductible_pct,category,invoice_no,paid_date,notes`

| Column | Rule |
|---|---|
| date | Invoice date, `YYYY-MM-DD`. Income and expenses are allocated to the quarter of this date |
| type | `income` or `expense` |
| description | Short, human-readable |
| counterparty | Client or supplier name, written the same way every time |
| country | ISO code (ES, DK, DE…). Drives VAT treatment and 349 checks |
| net | Taxable base, **without VAT**, two decimals |
| vat | VAT on the invoice (0 if none) |
| withholding | IRPF withheld. On income: withheld **by your client**. On expense: withheld **by you** from a supplier/employee/landlord |
| withholding_kind | `none`, `professional`, `employee`, `rent`, `other` |
| deductible_pct | 100 for fully business expenses; lower for mixed use (e.g. home utilities, phone) |
| category | e.g. services, software, office, home_utilities, phone_internet, social_security, insurance, training, professional_fees, subcontractors, travel, meals, equipment, bank_fees, other |
| invoice_no | Invoice number. Income invoice numbers must be consecutive |
| paid_date | Date actually paid. Needed for withholdings (111/115 follow payment date) |
| notes | Anything useful, e.g. "15% IRPF", "30% x 20 m2 / 80 m2" |

## Conventions
- The social security fee (cuota RETA) is recorded once a month or once a quarter as an
  expense, category `social_security`, vat 0. It is deductible.
- For a VAT-exempt activity, keep the VAT actually paid in `vat`: the scripts add it to the
  cost when `profile.json` has `"vat_is_cost": true`.
- Keep the PDF of every invoice/receipt in `books/documents/<year>/` named
  `<date>_<counterparty>_<invoice_no>.pdf`.
