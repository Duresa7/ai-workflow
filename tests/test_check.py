"""Tests for check.py against small throwaway repositories."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check  # noqa: E402
import sources  # noqa: E402

COMMIT = "a" * 40
SKILL = "---\nname: {name}\ndescription: test\n---\n\nBody.\n"


class Repo:
    """A minimal repository with one template and one own skill."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.write("skills/mine/SKILL.md", SKILL.format(name="mine"))
        template = SKILL.format(name="tdd").encode()
        self.write("sources/owner/tdd/SKILL.md", template.decode())
        self.lock = {
            "entries": {
                "owner/tdd": {
                    "kind": "skill",
                    "repo": "owner/skills",
                    "commit": COMMIT,
                    "path": "skills/tdd",
                    "files": {"SKILL.md": sources.blob_sha(template)},
                }
            }
        }
        self.save_lock()
        self.sources_md(customized="—")

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def save_lock(self) -> None:
        self.write("sources/sources.lock.json", json.dumps(self.lock))

    def sources_md(self, customized: str, commit: str = COMMIT[:7], extra: str = "") -> None:
        self.write(
            "SOURCES.md",
            "| Template | Upstream | License | Commit | Customized as |\n"
            "|---|---|---|---|---|\n"
            f"| [`sources/owner/tdd`](x) | [owner/skills](y) | MIT | `{commit}` | {customized} |\n\n"
            "| Skill | Origin |\n|---|---|\n"
            f"| [`skills/mine`](z) | Original |\n{extra}",
        )

    def problems(self) -> list[str]:
        return check.run(self.root, upstream=False)


class CheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assertProblem(self, fragment: str) -> None:
        problems = self.repo.problems()
        self.assertTrue(
            any(fragment in problem for problem in problems),
            f"expected a problem containing {fragment!r}, got {problems}",
        )

    def test_clean_repository_passes(self) -> None:
        self.assertEqual(self.repo.problems(), [])

    def test_edited_template_fails(self) -> None:
        self.repo.write("sources/owner/tdd/SKILL.md", SKILL.format(name="tdd") + "edit\n")
        self.assertProblem("templates must stay untouched")

    def test_unrecorded_file_in_sources_fails(self) -> None:
        self.repo.write("sources/owner/tdd/notes.md", "x")
        self.assertProblem("not recorded in the lock file")

    def test_owner_readme_in_sources_is_allowed(self) -> None:
        self.repo.write("sources/owner/README.md", "# owner\n")
        self.assertEqual(self.repo.problems(), [])

    def test_skill_readme_not_in_lock_fails(self) -> None:
        self.repo.write("sources/owner/tdd/README.md", "# tdd\n")
        self.assertProblem("not recorded in the lock file")

    def test_missing_template_file_fails(self) -> None:
        (self.repo.root / "sources/owner/tdd/SKILL.md").unlink()
        self.assertProblem("recorded in the lock file but missing")

    def test_skill_name_must_match_folder(self) -> None:
        self.repo.write("skills/mine/SKILL.md", SKILL.format(name="other"))
        self.assertProblem("expected 'mine'")

    def test_template_needs_a_row(self) -> None:
        self.repo.write("SOURCES.md", "| [`skills/mine`](z) | Original |\n")
        self.assertProblem("no row for sources/owner/tdd")

    def test_row_commit_must_match_lock(self) -> None:
        self.repo.sources_md(customized="—", commit="bbbbbbb")
        self.assertProblem("the lock file pins")

    def test_untraced_own_skill_fails(self) -> None:
        self.repo.write("skills/stray/SKILL.md", SKILL.format(name="stray"))
        self.assertProblem("skills/stray is not traced")

    def test_customized_copy_is_traced(self) -> None:
        self.repo.write("skills/tdd/SKILL.md", SKILL.format(name="tdd"))
        self.repo.sources_md(customized="`skills/tdd`")
        self.assertEqual(self.repo.problems(), [])

    def test_customized_as_must_exist(self) -> None:
        self.repo.sources_md(customized="`skills/tdd`")
        self.assertProblem("customized as skills/tdd, which has no SKILL.md")

    def test_profile_copy_must_be_traced(self) -> None:
        self.repo.write("profiles/gamedev/profile.toml", 'description = "Games"\ninclude = []\n')
        self.repo.write("profiles/gamedev/skills/tdd/SKILL.md", SKILL.format(name="tdd"))
        self.assertProblem("profiles/gamedev/skills/tdd is not traced")
        self.repo.sources_md(customized="`skills/tdd`, `profiles/gamedev/skills/tdd`")
        self.repo.write("skills/tdd/SKILL.md", SKILL.format(name="tdd"))
        self.assertEqual(self.repo.problems(), [])

    def test_profile_include_must_exist(self) -> None:
        self.repo.write(
            "profiles/gamedev/profile.toml",
            'description = "Games"\ninclude = ["sources/owner/tdd", "sources/owner/nope"]\n',
        )
        self.assertProblem("sources/owner/nope is not a skill folder")

    def test_profile_needs_description(self) -> None:
        self.repo.write("profiles/gamedev/profile.toml", "include = []\n")
        self.assertProblem("needs a description")

    def test_work_in_progress_needs_no_trace(self) -> None:
        self.repo.write("work-in-progress/idea/skills/idea/SKILL.md", SKILL.format(name="idea"))
        self.repo.write("work-in-progress/idea/notes/todo.md", "- finish it\n")
        self.assertEqual(self.repo.problems(), [])

    def test_work_in_progress_name_must_match_folder(self) -> None:
        self.repo.write("work-in-progress/idea/skills/idea/SKILL.md", SKILL.format(name="other"))
        self.assertProblem("expected 'idea'")

    def test_work_in_progress_tests_run(self) -> None:
        self.repo.write("work-in-progress/idea/skills/idea/SKILL.md", SKILL.format(name="idea"))
        self.repo.write("work-in-progress/idea/skills/idea/scripts/test_idea.py", "raise SystemExit(1)\n")
        self.assertProblem("test_idea.py failed")

    def test_failing_skill_test_fails(self) -> None:
        self.repo.write("skills/mine/scripts/test_mine.py", "raise SystemExit(1)\n")
        self.assertProblem("test_mine.py failed")


class BlobShaTests(unittest.TestCase):
    def test_matches_git_hash_object(self) -> None:
        # `printf 'hello\n' | git hash-object --stdin`
        self.assertEqual(sources.blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")


if __name__ == "__main__":
    unittest.main()
