# Filing on the AEAT Sede electrónica (step by step)

The user files; the agent prepares the numbers. Interface labels are in Spanish.

## Before starting
- Identification: digital certificate (certificado electrónico), Cl@ve Móvil or DNIe.
- Have the draft open (box-by-box output from the calculation script).
- Have the IBAN of the account that will pay (it must be in the user's name for direct debit).

## Steps (130, 111, 115, 303 — same pattern)
1. Go to https://sede.agenciatributaria.gob.es → search the form number (e.g. "Modelo 130").
2. Open **"Presentar y consultar declaraciones"** → **"Presentación ejercicio <year>"**.
3. Identify with certificate or Cl@ve.
4. Choose the period ("1T", "2T", "3T", "4T") and fill the boxes exactly as in the draft.
5. Click **"Validar declaración"**: fix any warning before continuing.
6. Choose the payment method:
   - **"Domiciliación"** (direct debit): the bank charges it on the last day of the deadline.
     Only possible until the direct-debit cut-off (usually the 15th for a 20th deadline).
   - **"Ingreso"** with NRC: pay first through the bank / the Sede, then file with the NRC.
   - **"Negativa"** / **"Sin actividad"** when the result is zero or negative (130).
7. Click **"Firmar y enviar"** → download the PDF receipt ("justificante").
8. Save the PDF in `books/filings/` and mark the matching JSON as `"status": "filed"`.

## If the deadline has passed
File as soon as possible; see `late-filing.md`. Filing late on your own initiative costs
far less than waiting for the AEAT to send a request.
