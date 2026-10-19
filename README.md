# Spanish Autónomo Accountant

Turn Claude into the accountant of a self-employed person (**autónomo**) in Spain.
It keeps your books, tells you what is due and when, prepares every return box by box,
and walks you through filing it on the AEAT website. **You file; it prepares.**

Built for one goal first: **never pay a late surcharge again.**

## What it does

| Skill | Ask it… |
|---|---|
| `autonomo-setup` | "Set me up" — a short questionnaire, decides which returns you must file, organises the handover from your current accountant |
| `tax-calendar` | "What's due?" — next deadlines with a *prepare-by* date, and a calendar file (.ics) with alarms for Google / Apple / Outlook |
| `bookkeeping` | "Add these invoices" — records income and expenses, says what is deductible, checks your invoices |
| `quarterly-filing` | "Prepare my Q3" — modelo **130**, **111**, **115** (and guidance for 303/349), box by box, plus the filing steps |
| `annual-filing` | "What do I file in January?" / "Prepare my Renta" — 190/180/390, Renta figures, social security (RETA) bracket check |
| `set-aside` | "How much should I save this month?" — one number to move to a tax account |

All calculations run in small Python scripts (standard library only), tested against a
hand-calculated example (`examples/`). Claude never does tax arithmetic in its head.

## Who it is for
- Individual autónomo, **common tax territory** (not Basque Country, Navarre or the Canary Islands)
- Income tax by **direct assessment** (estimación directa, simplified or normal) — not módulos
- Typical freelancer: services, clients in Spain or abroad, maybe a subcontractor or office rent

## Install

### Option A — Claude Code (recommended: your books stay on your computer)
Works in the Claude desktop app (Code tab) or the terminal.

```
/plugin marketplace add iri2bouv/spanish-autonomo-accountant
/plugin install spanish-autonomo-accountant@spanish-autonomo-accountant
```

Then:
1. Create an empty folder, e.g. `My accounting`, and open it in Claude Code.
2. Say: **"Set me up as my Spanish accountant."**
3. Have these ready: your census certificate (*certificado de situación censal*, from the AEAT Sede), your last Renta, the last 130 you filed.

The setup creates a `books/` folder there with your profile, ledger and filings. Keep it backed up.

### Option B — Claude.ai (web or app, no installation)
1. Download the six zips from [`dist/`](dist/).
2. On claude.ai: **Settings → Capabilities**, turn on code execution, then upload each zip under **Skills**.
3. Create a **Project** called "My accounting" and paste the text from
   [`claude-ai/project-instructions.md`](claude-ai/project-instructions.md) into its instructions.
4. In the Project, say: **"Set me up as my Spanish accountant."**

Claude.ai has no permanent disk: after each session, download the updated `ledger.csv`,
`profile.json` and filings files it gives you and replace them in the Project files.

### Option C — manual
Copy the folders in `skills/` to `~/.claude/skills/`.

## Your data
Your profile, ledger, invoices and returns live only in your `books/` folder (or your Claude.ai
Project). Nothing in this repository contains personal data, and `.gitignore` blocks `books/`.

## Keeping it current
Tax rules and dates change. Every reference file says when it was last verified and against
which official source. Each December, regenerate next year's calendar once the AEAT
publishes its *Calendario del contribuyente*.

## Run the tests
```
python3 -m unittest discover -s tests -v
```

## Disclaimer
This is not a registered tax adviser (*gestor* / *asesor fiscal*) and not professional advice.
It prepares figures from what you record; you check them and you remain responsible for what
you file with the AEAT and the Social Security. For anything unusual — a letter from the AEAT,
an inspection, a change of legal form, significant foreign income outside your activity — ask
a professional.

MIT licence.
