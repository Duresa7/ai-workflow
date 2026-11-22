# human-voice

Skills for prose that reads as its author, not as AI: newsletters, articles, and posts up to 5,000 words. Five skills share one script and one set of references.

| Skill | Job |
|---|---|
| [`human-voice`](skills/human-voice/SKILL.md) | Runs the loop: profile, write, audit, revise, validate. Holds the shared `references/` and `scripts/`. |
| [`voice-profile`](skills/voice-profile/SKILL.md) | Builds an author's voice profile (qualitative Markdown plus a numeric baseline) from samples of their own writing. |
| [`voice-write`](skills/voice-write/SKILL.md) | Drafts or rewrites in the author's voice from a brief and notes, without inventing specifics. |
| [`voice-audit`](skills/voice-audit/SKILL.md) | Reports the signals readers and AI detectors key on, quoting the lines, without rewriting. |
| [`voice-validate`](skills/voice-validate/SKILL.md) | Gives a cold-read PASS or FAIL with a ranked fix list. |

The bar is a skeptical reader who knows the author. The suite runs no commercial detector and promises no detector score.

## Where it stands

See [notes/status.md](notes/status.md).

## Research

[`research/raw/`](research/raw/) holds cited notes on GPTZero, Pangram, Turnitin, and other commercial detectors, compiled on 2026-10-13. They're meant to be distilled into the suite's missing reference files.

## Script

`skills/human-voice/scripts/stylometry.py` uses only the Python standard library:

```bash
python3 skills/human-voice/scripts/stylometry.py analyze draft.md --context newsletter
python3 skills/human-voice/scripts/stylometry.py profile a.md b.md c.md --out voice/me.stylometry.json --name me
python3 skills/human-voice/scripts/stylometry.py analyze draft.md --profile voice/me.stylometry.json --windows
python3 -I skills/human-voice/scripts/test_stylometry.py
```
