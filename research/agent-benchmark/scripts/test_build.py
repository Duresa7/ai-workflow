import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build


def run(**fields):
    row = dict(
        run=1,
        day="2026-11-26",
        task="T001",
        role="writer",
        model="Model A",
        harness="Harness",
        effort="medium",
        task_type="tests",
        tier=None,
        seat=None,
        round=None,
        evidence="live",
        outcome="completed",
        minutes=10.0,
        tokens=None,
        usage_limit_hits=0,
        measures={},
    )
    return row | fields


class BuildTest(unittest.TestCase):
    @unittest.skipUnless((build.HERE / "data").is_dir(), "no published data here")
    def test_published_tables_match_the_data(self):
        stale = [
            name
            for name, text in build.build(build.HERE).items()
            if (build.HERE / name).read_text(encoding="utf-8") != text
        ]
        self.assertEqual(stale, [])

    def test_rates_come_from_known_outcomes_only(self):
        rows = [
            run(measures={"landed": True, "rounds_to_pass": 1}),
            run(run=2, measures={"landed": True, "rounds_to_pass": 1}),
            run(
                run=3,
                task="T002",
                measures={
                    "landed": False,
                    "rounds_to_pass": 3,
                    "third_fail_stop": True,
                },
            ),
            run(run=4, task=None, measures={"landed": None, "rounds_to_pass": None}),
            run(
                role="reviewer",
                outcome="fail",
                measures={"blockers": 2, "false_blockers": 1},
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "data").mkdir()
            (folder / "data" / "runs.jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
            )
            (folder / "README.md").write_text(
                f"intro\n{build.START}\nold\n{build.END}\nend\n", encoding="utf-8"
            )
            files = build.build(folder)
        writers = files["tables/writers.md"]
        self.assertIn(
            "| Model A | medium | 4 † | 3 | 1/2 (50%) | 1/2 (50%) | 2.00 |", writers
        )
        self.assertIn("| 1 |", writers)
        self.assertIn("1/2", files["tables/reviewers.md"])
        self.assertTrue(files["README.md"].startswith("intro\n"))
        self.assertTrue(files["README.md"].endswith(build.END + "\nend\n"))
        self.assertNotIn("old", files["README.md"])


if __name__ == "__main__":
    unittest.main()
