"""Run the agent benchmark's own tests (research/agent-benchmark/scripts/)."""

import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "research" / "agent-benchmark" / "scripts"


def load_tests(loader, tests, pattern):
    tests.addTests(loader.discover(str(SCRIPTS), pattern="test_*.py", top_level_dir=str(SCRIPTS)))
    return tests


if __name__ == "__main__":
    unittest.main()
