#!/usr/bin/env python3
"""Check the repository rules. Exits non-zero and lists every problem it finds.

    python check.py              offline checks
    python check.py --upstream   also confirm the lock file against GitHub

Rules:
- Every file under sources/ (except local sources/<owner>/README.md summaries)
  matches the blob hash recorded in sources/sources.lock.json, and every
  recorded file exists.
- Every skill folder in skills/, profiles/*/skills/, and
  work-in-progress/*/skills/ has a SKILL.md whose `name:` matches the folder.
- SOURCES.md has one row per skill template, with the commit from the lock
  file, and every skill in skills/ and profiles/ is traced in it. Work in
  progress doesn't need to be traced until it moves to skills/.
- Every profiles/*/profile.toml has a description, and its includes point at
  skill folders that exist.
- Skill test scripts (scripts/test_*.py inside skills/, profiles/, and
  work-in-progress/) pass.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import sources

ROOT = Path(__file__).resolve().parent
SOURCES_MD = "SOURCES.md"
EMPTY_CELL = {"", "-", "—"}


@dataclass
class TemplateRow:
    template: str
    commit: str
    customized_as: list[str]


def skill_name(skill_md: Path) -> str | None:
    """The `name:` value from SKILL.md front matter, or None."""
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        match = re.match(r"name:\s*(.+?)\s*$", line)
        if match:
            return match.group(1).strip("\"'")
    return None


def skill_folders(parent: Path) -> list[Path]:
    if not parent.is_dir():
        return []
    return sorted(
        path for path in parent.iterdir() if path.is_dir() and not path.name.startswith(".")
    )


def check_skill_folder(folder: Path, root: Path) -> list[str]:
    relative = folder.relative_to(root).as_posix()
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return [f"{relative}: missing SKILL.md"]
    name = skill_name(skill_md)
    if name != folder.name:
        return [f"{relative}/SKILL.md: name is {name!r}, expected {folder.name!r}"]
    return []


def check_sources(root: Path, lock: dict) -> list[str]:
    problems: list[str] = []
    base = root / "sources"
    expected: set[Path] = {base / "sources.lock.json"}
    for name, entry in lock["entries"].items():
        target = base / name
        for relative, sha in entry["files"].items():
            path = target / relative if relative else target
            expected.add(path)
            shown = path.relative_to(root).as_posix()
            if not path.is_file():
                problems.append(f"{shown}: recorded in the lock file but missing")
            elif sources.blob_sha(path.read_bytes()) != sha:
                problems.append(
                    f"{shown}: differs from {entry['repo']}@{entry['commit'][:7]}; "
                    "templates must stay untouched, so copy it into skills/ or a profile instead"
                )
    owners = {name.split("/", 1)[0] for name in lock["entries"]}
    allowed = expected | {base / owner / "README.md" for owner in owners}
    for path in sorted(base.rglob("*")):
        if path.is_file() and path not in allowed:
            problems.append(f"{path.relative_to(root).as_posix()}: not recorded in the lock file")
    for name, entry in lock["entries"].items():
        if entry["kind"] == "skill":
            problems += check_skill_folder(base / name, root)
    return problems


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _paths(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def parse_sources_md(text: str) -> tuple[list[TemplateRow], list[str]]:
    """Template rows and original-skill paths from SOURCES.md tables."""
    templates: list[TemplateRow] = []
    originals: list[str] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        first = _paths(cells[0])
        if not first:
            continue
        if first[0].startswith("sources/") and len(cells) == 5:
            commit = _paths(cells[3])
            customized = [] if cells[4] in EMPTY_CELL else _paths(cells[4])
            templates.append(TemplateRow(first[0], commit[0] if commit else "", customized))
        elif first[0].startswith(("skills/", "profiles/")):
            originals.append(first[0])
    return templates, originals


def check_sources_md(root: Path, lock: dict) -> list[str]:
    path = root / SOURCES_MD
    if not path.is_file():
        return [f"{SOURCES_MD}: missing"]
    templates, originals = parse_sources_md(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    skills = {
        f"sources/{name}": entry
        for name, entry in lock["entries"].items()
        if entry["kind"] == "skill"
    }
    seen: set[str] = set()
    for row in templates:
        entry = skills.get(row.template)
        if entry is None:
            problems.append(f"{SOURCES_MD}: {row.template} is not a skill template in the lock file")
            continue
        if row.template in seen:
            problems.append(f"{SOURCES_MD}: {row.template} is listed twice")
        seen.add(row.template)
        if not row.commit or not entry["commit"].startswith(row.commit):
            problems.append(
                f"{SOURCES_MD}: {row.template} commit is {row.commit!r}, "
                f"the lock file pins {entry['commit'][:7]}"
            )
        for target in row.customized_as:
            if not (root / target / "SKILL.md").is_file():
                problems.append(f"{SOURCES_MD}: {row.template} customized as {target}, which has no SKILL.md")
    for missing in sorted(set(skills) - seen):
        problems.append(f"{SOURCES_MD}: no row for {missing}")

    traced = set(originals) | {t for row in templates for t in row.customized_as}
    ours = [folder for folder in skill_folders(root / "skills")]
    for profile in skill_folders(root / "profiles"):
        ours += skill_folders(profile / "skills")
    for folder in ours:
        relative = folder.relative_to(root).as_posix()
        if relative not in traced:
            problems.append(
                f"{SOURCES_MD}: {relative} is not traced; list it as an original "
                "or in a template's 'Customized as' cell"
            )
    for original in originals:
        if not (root / original).is_dir():
            problems.append(f"{SOURCES_MD}: {original} is listed but does not exist")
    return problems


def check_profiles(root: Path) -> list[str]:
    problems: list[str] = []
    for profile in skill_folders(root / "profiles"):
        relative = profile.relative_to(root).as_posix()
        manifest = profile / "profile.toml"
        if not manifest.is_file():
            problems.append(f"{relative}: missing profile.toml")
            continue
        try:
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            problems.append(f"{relative}/profile.toml: {error}")
            continue
        if not isinstance(data.get("description"), str) or not data["description"].strip():
            problems.append(f"{relative}/profile.toml: needs a description")
        include = data.get("include", [])
        if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
            problems.append(f"{relative}/profile.toml: include must be a list of paths")
            continue
        for item in include:
            if not item.startswith(("skills/", "sources/")):
                problems.append(f"{relative}/profile.toml: {item} must be under skills/ or sources/")
            elif not (root / item / "SKILL.md").is_file():
                problems.append(f"{relative}/profile.toml: {item} is not a skill folder")
        for folder in skill_folders(profile / "skills"):
            problems += check_skill_folder(folder, root)
    return problems


def check_upstream(lock: dict) -> list[str]:
    problems: list[str] = []
    trees: dict[tuple[str, str], dict] = {}
    for name, entry in lock["entries"].items():
        key = (entry["repo"], entry["commit"])
        if key not in trees:
            trees[key] = sources.upstream_tree(*key)
        upstream = {
            relative: blob["sha"]
            for relative, blob in sources.files_under(trees[key], entry["path"]).items()
        }
        if upstream != entry["files"]:
            problems.append(
                f"sources/{name}: lock file does not match "
                f"{entry['repo']}@{entry['commit'][:7]}:{entry['path']}"
            )
    return problems


def run_skill_tests(root: Path) -> list[str]:
    problems: list[str] = []
    tests = [
        test
        for folder in ("skills", "profiles", "work-in-progress")
        for test in (root / folder).glob("**/scripts/test_*.py")
    ]
    for test in sorted(tests):
        completed = subprocess.run(
            [sys.executable, "-I", str(test)], capture_output=True, text=True
        )
        if completed.returncode != 0:
            tail = (completed.stdout + completed.stderr).strip().splitlines()[-5:]
            problems.append(f"{test.relative_to(root).as_posix()} failed:\n    " + "\n    ".join(tail))
    return problems


def run(root: Path, upstream: bool) -> list[str]:
    lock_path = root / "sources" / "sources.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.is_file() else {"entries": {}}
    problems = check_sources(root, lock)
    for folder in skill_folders(root / "skills"):
        problems += check_skill_folder(folder, root)
    for project in skill_folders(root / "work-in-progress"):
        for folder in skill_folders(project / "skills"):
            problems += check_skill_folder(folder, root)
    problems += check_sources_md(root, lock)
    problems += check_profiles(root)
    problems += run_skill_tests(root)
    if upstream:
        problems += check_upstream(lock)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the repository rules.")
    parser.add_argument("--upstream", action="store_true", help="also confirm the lock file against GitHub")
    args = parser.parse_args()
    problems = run(ROOT, args.upstream)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print(f"\n{len(problems)} problem(s).")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
