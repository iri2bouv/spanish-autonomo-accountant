---
name: set-aside
description: Use when a Spanish autónomo asks how much money to put aside for taxes, how much of an invoice is really theirs, whether they can afford something, or wants a monthly "tax savings" figure — e.g. "how much should I save this month", "how much of this 2,000 is mine", "set aside for Hacienda".
argument-hint: "[YYYY-MM]"
---

# Set-aside

Late payments often come from the money not being there on the day. This skill turns each
month's ledger into one number: **what to move to a separate tax account**.

## Files
- `books/ledger.csv`, `books/profile.json` (`reta_monthly_fee`, `renta_buffer_pct`, `vat_is_cost`)
- Script: `scripts/set_aside.py` in this skill's folder

## Steps
1. Month = argument, or the month just ended (or the current month if asked mid-month).
2. Make sure the month's invoices and expenses are in the ledger (bookkeeping skill).
3. Run `python3 "<skill-dir>/scripts/set_aside.py" --books books --month YYYY-MM`.
4. Answer with the single amount first, then the breakdown:

```
Move 1,000.00 to your tax account for April.
  800.00  for the 130 (20% of April profit)
  200.00  buffer for the annual Renta (5%, adjustable)
Social security 300.00 is charged automatically on 30 April — keep it in your main account.
```

5. For "how much of this invoice is mine?": profit share ≈ invoice − 20% for the 130 −
   buffer − any VAT collected. Show the arithmetic with the script's rates.

## Tips to offer once (not every time)
- Open a second account used only for taxes; move the amount the day the client pays.
- Set the 130 and 111 to direct debit (domiciliación) when filing: the money leaves on the
  last day automatically.

## Rules
- The 20% is the legal 130 rate on profit. The buffer is a prudence choice, not a tax rate;
  the user can change `renta_buffer_pct` in `profile.json`. After the first Renta, suggest
  adjusting it based on what they actually paid or got back.
- Never present the set-aside as the final tax bill.
