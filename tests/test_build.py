"""Leaderboard tests. All data is fake and built in temp files; nothing is committed."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "leaderboard"))
import build  # noqa: E402

RULES = build.load_rules(ROOT / "leaderboard" / "rules.json")
HEADER = "date,member,category,points,reason,awarded_by\n"


def run(csv_text):
    """Write csv_text to a temp file and return (exit_code, output_text, stderr_text)."""
    import contextlib
    import io
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "points.csv"
        out_path = Path(tmp) / "LEADERBOARD.md"
        csv_path.write_text(csv_text, encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = build.main(["--csv", str(csv_path), "--rules", str(ROOT / "leaderboard" / "rules.json"),
                               "--out", str(out_path)])
        out = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        return code, out, err.getvalue()


class ValidationTests(unittest.TestCase):
    def assertRejected(self, row, fragment):
        code, out, err = run(HEADER + row + "\n")
        self.assertEqual(code, 1, err)
        self.assertIn(fragment, err)
        self.assertEqual(out, "", "nothing may be written when validation fails")

    def test_self_award(self):
        self.assertRejected("2026-10-08,Ana B.,helping,2,Explained a proof to the group,Ana B.", "self-award")

    def test_unknown_category(self):
        self.assertRejected("2026-10-08,Ana B.,vibes,2,Good energy all session,Cy D.", "unknown category")

    def test_bad_points_for_category(self):
        self.assertRejected("2026-10-08,Ana B.,tool,4,Wrote a backtest script,Cy D.", "tool points must be")

    def test_puzzle_points_range(self):
        self.assertRejected("2026-10-08,Ana B.,puzzle_writeup,6,Excellent write-up of a hard one,Cy D.", "3 to 5")

    def test_full_name_rejected(self):
        self.assertRejected("2026-10-08,Ana Brown,helping,2,Explained a proof to the group,Cy D.", "first name and last initial")

    def test_email_rejected(self):
        self.assertRejected("2026-10-08,Ana B.,helping,2,Email ana@example.com for help,Cy D.", "'@'")

    def test_empty_reason(self):
        self.assertRejected("2026-10-08,Ana B.,helping,2,,Cy D.", "written reason")

    def test_bad_date(self):
        self.assertRejected("08/10/2026,Ana B.,helping,2,Explained a proof to the group,Cy D.", "YYYY-MM-DD")

    def test_non_integer_points(self):
        self.assertRejected("2026-10-08,Ana B.,helping,two,Explained a proof to the group,Cy D.", "whole number")

    def test_wrong_column_count(self):
        self.assertRejected("2026-10-08,Ana B.,helping,2,Explained a proof", "columns")

    def test_duplicate_award(self):
        row = "2026-10-08,Ana B.,helping,2,Explained a proof to the group,Cy D."
        code, _, err = run(HEADER + row + "\n" + row + "\n")
        self.assertEqual(code, 1)
        self.assertIn("duplicate", err)

    def test_wrong_header(self):
        code, _, err = run("date,name,category,points,reason,by\n")
        self.assertEqual(code, 1)
        self.assertIn("header", err)


class OutputTests(unittest.TestCase):
    def test_empty_file_renders_empty_state(self):
        code, out, _ = run(HEADER)
        self.assertEqual(code, 0)
        self.assertIn("No awards yet.", out)

    def test_ranking_with_ties(self):
        rows = (
            "2026-10-08,Ana B.,tournament,10,Won the chess tournament,Cy D.\n"
            "2026-10-08,Cy D.,tournament,7,Second in the chess tournament,Ana B.\n"
            "2026-10-08,Eli F.,tournament,7,Second in the chess tournament too,Ana B.\n"
            "2026-10-09,Gus H.,helping,2,Helped with the clocks,Ana B.\n"
        )
        code, out, _ = run(HEADER + rows)
        self.assertEqual(code, 0)
        overall = out.split("## Overall")[1].split("## By category")[0]
        self.assertIn("| 1 | Ana B. | 10 |", overall)
        self.assertIn("| 2 | Cy D. | 7 |", overall)
        self.assertIn("| 2 | Eli F. | 7 |", overall)
        self.assertIn("| 4 | Gus H. | 2 |", overall)

    def test_monthly_cap_clips_points(self):
        rows = (
            "2026-10-01,Ana B.,tournament,10,Won the first tournament,Cy D.\n"
            "2026-10-15,Ana B.,tournament,10,Won the second tournament,Cy D.\n"
            "2026-11-05,Ana B.,tournament,10,Won in November,Cy D.\n"
        )
        code, out, _ = run(HEADER + rows)
        self.assertEqual(code, 0)
        overall = out.split("## Overall")[1].split("## By category")[0]
        self.assertIn("| 1 | Ana B. | 25 |", overall)  # 10 + 5 (capped) + 10 (new month)
        self.assertIn("†", out)

    def test_latest_awards_limited_to_five_newest_first(self):
        rows = "".join(f"2026-10-{d:02d},Ana B.,attendance,1,Attended session {d},Cy D.\n" for d in range(1, 8))
        code, out, _ = run(HEADER + rows)
        self.assertEqual(code, 0)
        latest = out.split("## Latest awards")[1]
        self.assertEqual(latest.count("| 2026-10-"), 5)
        self.assertLess(latest.index("2026-10-07"), latest.index("2026-10-03"))
        self.assertNotIn("2026-10-02", latest)

    def test_pipe_in_reason_is_escaped(self):
        rows = "2026-10-08,Ana B.,helping,2,Explained a | b notation,Cy D.\n"
        code, out, _ = run(HEADER + rows)
        self.assertEqual(code, 0)
        self.assertIn("a \\| b", out)


class RealFileTests(unittest.TestCase):
    def test_committed_points_file_is_valid(self):
        rows, errors = build.load_rows(ROOT / "leaderboard" / "points.csv", RULES)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
