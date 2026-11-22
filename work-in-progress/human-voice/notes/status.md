# Status

As of 2026-11-22.

## Done

- All five `SKILL.md` files.
- `references/voice-profile-template.md` and `references/long-form-protocol.md`.
- `scripts/stylometry.py`, with 19 passing tests in `scripts/test_stylometry.py`.
- A worked example: `skills/human-voice/examples/sample-author/`, a synthetic author with three sample issues, a brief, notes, and a stylometry baseline.
- Raw research notes in `research/raw/`.

## Still to do

The skills point to three reference files that don't exist yet. Each should be distilled from `research/raw/`:

| File | Referenced by | Should cover |
|---|---|---|
| `skills/human-voice/references/signals.md` | `human-voice`, `voice-audit`, `voice-write`, `voice-validate` | What human readers and detectors key on, with sources. |
| `skills/human-voice/references/detectors.md` | `human-voice` | How GPTZero, Pangram, Turnitin, and the others work. |
| `skills/human-voice/references/detector-failures.md` | `human-voice` | Documented false positives, bias findings, and institutions dropping detectors, with citations. |

Once they exist, check every relative link in the five skills, then move the skills to `skills/` as described in [the work-in-progress README](../../README.md).
