"""Checks the scripts against the hand-calculated fictional case in examples/EXPECTED.md.

Run from the repo root:  python3 -m unittest discover -s tests -v
Standard library only.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
EXAMPLE = os.path.join(ROOT, "examples", "books")


def script(skill, name):
    return os.path.join(SKILLS, skill, "scripts", name)


def load(skill, name):
    spec = importlib.util.spec_from_file_location(name[:-3], script(skill, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(path, *args):
    res = subprocess.run([sys.executable, path, *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise AssertionError(f"{os.path.basename(path)} failed:\n{res.stdout}\n{res.stderr}")
    return res.stdout


class BooksTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.books = os.path.join(self.tmp, "books")
        shutil.copytree(EXAMPLE, self.books)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def saved(self, year, q, form="130"):
        with open(os.path.join(self.books, "filings", f"{year}-Q{q}-{form}.json")) as f:
            return json.load(f)["boxes"]


class Test130(BooksTestCase):
    def test_q1(self):
        run(script("quarterly-filing", "calc_130.py"), "--books", self.books, "--year", "2026", "--quarter", "1", "--save")
        b = self.saved(2026, 1)
        self.assertEqual(b["01"], "6000.00")
        self.assertEqual(b["02"], "2449.85")
        self.assertEqual(b["03"], "3550.15")
        self.assertEqual(b["04"], "710.03")
        self.assertEqual(b["19"], "710.03")

    def test_q2_uses_saved_q1(self):
        calc = script("quarterly-filing", "calc_130.py")
        run(calc, "--books", self.books, "--year", "2026", "--quarter", "1", "--save")
        run(calc, "--books", self.books, "--year", "2026", "--quarter", "2", "--save")
        b = self.saved(2026, 2)
        self.assertEqual(b["02"], "3619.80")
        self.assertEqual(b["04"], "1276.04")
        self.assertEqual(b["05"], "710.03")
        self.assertEqual(b["19"], "566.01")

    def test_q3_floors_at_zero(self):
        calc = script("quarterly-filing", "calc_130.py")
        for q in ("1", "2", "3"):
            out = run(calc, "--books", self.books, "--year", "2026", "--quarter", q, "--save")
        b = self.saved(2026, 3)
        self.assertEqual(b["05"], "1276.04")
        self.assertEqual(b["07"], "-1140.00")
        self.assertEqual(b["12"], "0.00")
        self.assertEqual(b["19"], "0.00")
        self.assertIn("Negativa", out)

    def test_missing_prior_quarter_warns(self):
        out = run(script("quarterly-filing", "calc_130.py"), "--books", self.books, "--year", "2026", "--quarter", "2")
        self.assertIn("WARNING", out)

    def test_box13_reduction_scale(self):
        m = load("quarterly-filing", "calc_130.py")
        self.assertEqual(m.reduction_box_13(9000), Decimal("100.00"))
        self.assertEqual(m.reduction_box_13(9000.01), Decimal("75.00"))
        self.assertEqual(m.reduction_box_13(11000), Decimal("50.00"))
        self.assertEqual(m.reduction_box_13(12000), Decimal("25.00"))
        self.assertEqual(m.reduction_box_13(12000.01), Decimal("0"))

    def test_negative_carry_forward(self):
        m = load("quarterly-filing", "calc_130.py")
        z = Decimal("0")
        # Nothing due, but a 100 reduction: result -100, carried to later quarters.
        b, outcome = m.calculate(z, z, z, z, z, Decimal("100.00"), quarter=1)
        self.assertEqual(b["19"], Decimal("-100.00"))
        self.assertIn("carry forward", outcome)
        # Next quarter owes 300; the pending 100 is used in box 15.
        b, _ = m.calculate(Decimal("1500.00"), z, z, z, Decimal("100.00"), Decimal("0"), quarter=2)
        self.assertEqual(b["04"], Decimal("300.00"))
        self.assertEqual(b["15"], Decimal("100.00"))
        self.assertEqual(b["19"], Decimal("200.00"))


class Test111(BooksTestCase):
    def test_q1(self):
        run(script("quarterly-filing", "calc_111.py"), "--books", self.books, "--year", "2026", "--quarter", "1", "--save")
        b = self.saved(2026, 1, "111")
        self.assertEqual(b["07"], 1)
        self.assertEqual(b["08"], "1000.00")
        self.assertEqual(b["09"], "150.00")
        self.assertEqual(b["30"], "150.00")

    def test_empty_quarter(self):
        out = run(script("quarterly-filing", "calc_111.py"), "--books", self.books, "--year", "2026", "--quarter", "2", "--save")
        self.assertIn("Do NOT file", out)
        with open(os.path.join(self.books, "filings", "2026-Q2-111.json")) as f:
            self.assertEqual(json.load(f)["status"], "not_required")


class TestLedger(BooksTestCase):
    def test_check_ok(self):
        out = run(script("bookkeeping", "ledger.py"), "check", "--books", self.books)
        self.assertIn("no problems", out)

    def test_add_and_duplicate(self):
        led = script("bookkeeping", "ledger.py")
        args = ["add", "--books", self.books, "--date", "2026-10-02", "--type", "income",
                "--description", "Project E", "--counterparty", "Nordic Client ApS", "--country", "DK",
                "--net", "800", "--invoice-no", "2026-005"]
        run(led, *args)
        res = subprocess.run([sys.executable, led, *args], capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("already in the ledger", res.stdout + res.stderr)

    def test_rejects_withholding_without_kind(self):
        res = subprocess.run([sys.executable, script("bookkeeping", "ledger.py"), "add", "--books", self.books,
                              "--date", "2026-10-02", "--type", "expense", "--description", "x",
                              "--net", "100", "--withholding", "15"], capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)

    def test_summary_matches_130(self):
        out = run(script("bookkeeping", "ledger.py"), "summary", "--books", self.books, "--year", "2026",
                  "--quarter", "1", "--cumulative")
        s = json.loads(out)
        self.assertEqual(s["income_net"], "6000.00")
        self.assertEqual(s["expenses_deductible"], "2263.00")
        self.assertEqual(s["withheld_from_others"]["professional"], "150.00")


class TestDeadlines(unittest.TestCase):
    def setUp(self):
        self.m = load("tax-calendar", "deadlines.py")

    def find(self, items, form, period):
        return next(i for i in items if i["form"] == form and i["period"] == period)

    def test_2026_dates(self):
        items = self.m.all_obligations(["130", "111", "190", "renta"], [2025, 2026])
        # Official 2026 calendar: 130 Q3 due 20 Oct 2026, direct debit until 15 Oct.
        q3 = self.find(items, "130", "2026 Q3")
        self.assertEqual(q3["deadline"], date(2026, 10, 20))
        self.assertEqual(q3["direct_debit_cutoff"], date(2026, 10, 15))
        # Q4 2025: 130 by 30 Jan 2026, 111 by 20 Jan 2026.
        self.assertEqual(self.find(items, "130", "2025 Q4")["deadline"], date(2026, 1, 30))
        self.assertEqual(self.find(items, "111", "2025 Q4")["deadline"], date(2026, 1, 20))
        # 190 for 2025: 31 Jan 2026 is a Saturday -> Monday 2 Feb 2026 (as published by AEAT).
        self.assertEqual(self.find(items, "190", "2025")["deadline"], date(2026, 2, 2))

    def test_weekend_shift(self):
        # 30 Jan 2027 is a Saturday -> Monday 1 Feb 2027.
        items = self.m.all_obligations(["130"], [2026])
        self.assertEqual(self.find(items, "130", "2026 Q4")["deadline"], date(2027, 2, 1))

    def test_ics_written(self):
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "cal.ics")
            run(script("tax-calendar", "deadlines.py"), "--forms", "130,111", "--year", "2027", "--ics", path)
            with open(path) as f:
                text = f.read()
            self.assertIn("BEGIN:VCALENDAR", text)
            self.assertIn("DEADLINE: 130 2026 Q4", text)
        finally:
            shutil.rmtree(tmp)


class TestAnnualAndSetAside(BooksTestCase):
    def test_annual(self):
        out = run(script("annual-filing", "annual_summary.py"), "--books", self.books, "--year", "2026")
        # 10,000 income - 9,284 expenses - 35.80 (5%) = 680.20
        self.assertIn("680.20", out)
        self.assertIn("Jordi Proof", out)
        # RETA: (680.20 + 1,800.00) x 0.93 = 2,306.59 ; / 12 = 192.22
        self.assertIn("2306.59", out)
        self.assertIn("192.22", out)

    def test_set_aside(self):
        out = run(script("set-aside", "set_aside.py"), "--books", self.books, "--month", "2026-04")
        # April: income 4,000, no expenses -> 20% = 800, buffer 5% = 200
        self.assertIn("800.00", out)
        self.assertIn("1000.00", out)


if __name__ == "__main__":
    unittest.main()
