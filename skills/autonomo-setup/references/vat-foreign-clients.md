# VAT (IVA) for services billed to clients abroad

Last verified: 2026-10-19. Sources: Ley 37/1992 del IVA (arts. 20, 69, 94), Reglamento
del IVA art. 79, AEAT instructions for modelos 303 and 349.

This decides whether forms **303, 390 and 349** apply. Work through it once, in the setup,
and write the answer into the profile. If the answer is not clear-cut, say so and
recommend confirming with the AEAT (free phone line / "Informa" database) or a one-off
consultation with an asesor — do not guess.

## Step 1 — Where is the service taxed? (place of supply, art. 69 LIVA)
- **Client is a business or professional (B2B) in another EU country** (has an EU VAT
  number, checkable in VIES): the service is taxed in the client's country. In Spain it
  is **not subject** ("no sujeta"). The invoice carries no Spanish VAT and the mention
  "Inversión del sujeto pasivo" / "Reverse charge".
- **Client is a private individual (B2C)**: as a general rule the service is taxed in
  **Spain** (where the provider is established). Some services have special rules.
- **Client outside the EU**: depends on the service type; many professional services
  to non-EU businesses are also not subject in Spain.

## Step 2 — If it is taxed in Spain, is it exempt? (art. 20 LIVA)
Certain activities are exempt by nature: healthcare by recognised professionals,
education, some cultural services, insurance, finance, etc. Exempt = no VAT charged,
but also **no right to recover** VAT on expenses → that VAT becomes a cost
(`vat_is_cost: true` in the profile).

## Step 3 — Which forms follow
| Situation | 303 / 390 | 349 | ROI/VIES registration |
|---|---|---|---|
| Only exempt activities (art. 20) registered as such in the 036 | Not filed | No | No |
| B2B services to EU clients, not subject in Spain, **subject and not exempt in the client's country** | Usually filed (not-subject sales in box 120) | **Yes** (key "S") | **Yes**, needed before invoicing |
| B2B services to EU clients that are exempt in the client's country too | Check with the AEAT | No (art. 79 RIVA only covers services subject and not exempt in the other State) | Check |
| Taxable services in Spain | Yes | No | No |

The 349 covers intra-EU services that are not located in Spain **and are subject and not
exempt in the other Member State** (art. 79 RIVA). If the profile says "VAT-exempt" but the
clients are EU businesses, ask: is the exemption a Spanish art. 20 exemption that would also
apply in the client's country? This is the single most important question to settle.

## Rules to apply
- Never charge Spanish VAT on an invoice until this has been settled.
- If ROI registration is required and missing, flag it as the first action (modelo 036).
- Record the conclusion, its reasoning and the date in `profile.md`.
