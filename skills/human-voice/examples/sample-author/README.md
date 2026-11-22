# Example: sample author

A small synthetic author (three short newsletter issues written for this
example) with a brief and material for a long issue. Use it to see the
pipeline run end to end:

1. `voice-profile` on `samples/` produces `voice/sample-author.voice.md` and
   `voice/sample-author.stylometry.json` (the JSON is checked in already).
2. `voice-write` in `draft` mode with `brief.md` and `material.md` produces
   `drafts/issue-45.v1.md`.
3. `voice-audit` on the draft, `voice-write` in `revise` mode, then
   `voice-validate` for the verdict.

The samples are not a real person's writing; they exist so the example can be
redistributed.
