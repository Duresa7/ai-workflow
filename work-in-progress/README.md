# Work in progress

Skills that aren't finished yet, together with everything gathered while building them. Nothing here is ready to install.

## Layout

One folder per project. A project can hold one skill or a suite of them.

```
work-in-progress/<project>/
  README.md        what the project is for and where it stands
  skills/<name>/   the skills being built, each with a SKILL.md
  notes/           working notes, decisions, open questions, to-do lists
  research/        source material, raw research notes, references
```

`notes/` and `research/` are optional. Keep them outside `skills/` so the finished skill ships without them.

## Rules

- `check.py` checks that each `SKILL.md` here has a `name:` matching its folder, and runs any `scripts/test_*.py`. It doesn't require these skills to be listed in [SOURCES.md](../SOURCES.md).
- If a project starts from a template, add its path to the template's **Customized as** cell in SOURCES.md anyway, so the origin isn't lost.

## Finishing a skill

1. Move `work-in-progress/<project>/skills/<name>/` to `skills/<name>/` (or into a profile).
2. List it in SOURCES.md, under **Your own skills** or in its template's **Customized as** cell.
3. Keep `notes/` and `research/` here, or delete the project folder once nothing in it is useful.

## Projects

| Project | Skills | Status |
|---|---|---|
| [`human-voice`](human-voice/README.md) | `human-voice`, `voice-profile`, `voice-write`, `voice-audit`, `voice-validate` | Three shared reference files are still unwritten. |
