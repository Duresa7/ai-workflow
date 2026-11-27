# AGENTS.md

This repository holds skills for AI coding agents. There is no CLAUDE.md. This file is the only agent instruction file.

## The skill folders

- `sources/<owner>/<skill>/` holds untouched upstream templates. **Never edit, rename, or delete anything inside template folders or locked files under `sources/`.** `check.py` compares every locked file with the hash in `sources/sources.lock.json` and fails on any change or stray file. Only `python sources.py add` writes templates there; `sources/<owner>/README.md` is the only local-only file allowed (trimmed upstream skill summaries).
- `skills/<name>/` holds the owner's own skills and customized versions meant for every project.
- `work-in-progress/<project>/` holds unfinished skills (`skills/<name>/`) with their `notes/` and `research/`. Put new skills, working notes, and research material here until the skill is finished; see `work-in-progress/README.md`.
- `profiles/<profile>/skills/<name>/` holds versions tweaked for one kind of work. `profiles/<profile>/profile.toml` lists the skills the profile uses unchanged.

## Customizing a template

1. Copy the whole folder: `cp -r sources/<owner>/<skill> skills/<name>` (or `profiles/<profile>/skills/<name>`).
2. If `<name>` differs from the template's, set `name:` in the copied `SKILL.md` to match the new folder.
3. Edit the copy.
4. In `SOURCES.md`, add the copy's path to that template's **Customized as** cell, in backticks, comma-separated if there are several.
5. Run `python check.py`.

A brand-new skill starts in `work-in-progress/<project>/skills/<name>/`. When it's finished, it moves to `skills/<name>/` and goes in the **Your own skills** table in `SOURCES.md`.

## Adding a template

Run `python sources.py add OWNER/REPO PATH [--ref REF]`, then add a row for it to `SOURCES.md` under its owner's heading, using the commit from the lock file. New owners also need their license: `python sources.py add OWNER/REPO LICENSE --kind license`.

## Checks

Run `python check.py` and `python -m unittest discover tests` before committing. Both must pass.

## Commits and pull requests

Never credit an AI model, AI assistant, or AI vendor as a co-author or contributor. Commit messages get no co-author trailer, and pull request descriptions get no AI attribution line.
