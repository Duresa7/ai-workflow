---
name: voice-validate
description: Independent PASS/FAIL gate on a finished draft, judged as a cold reader who knows the author, with a deterministic stylometry check against the author's profile. Use as the last step before publishing, when the user asks "is this ready" or "would this get called out", or when the human-voice pipeline needs a verdict.
---

# Voice validate

A cold read with a verdict. The validator is the reader who knows the author,
has seen a thousand AI drafts, and has not seen the brief, the audit, or the
writer's intentions. **Run it in a fresh context** with only the draft, the
profile, and (if provenance is to be checked) the material; a validator that
watched the draft being written passes things a stranger would not.

Shared files live in the sibling `human-voice` skill directory (resolve
`../human-voice` from this skill's real directory). The gate items reference
`references/signals.md`; read it before the cold read.

## Steps

1. **Cold read, whole piece, before any tool.** Then write down three things:
   the first sentence you doubted, the first place the voice slipped, and
   whether you would have guessed the author wrote it. These are evidence;
   keep them for the report.
2. **Measure:**
   ```bash
   python3 ../human-voice/scripts/stylometry.py analyze DRAFT --context <ctx> \
     --profile ./voice/<name>.stylometry.json --windows --format json > /tmp/validate.json
   python3 ../human-voice/scripts/stylometry.py analyze DRAFT --context <ctx> \
     --profile ./voice/<name>.stylometry.json --windows
   ```
   Without a profile, run without `--profile` and note in the report that
   gates G2 and G5 could not be applied.
3. **Apply the gates.** All must hold for PASS.

| Gate | Holds when |
|---|---|
| **G1 Reference** | No HIGH flag against the reference ranges, except one the author's own samples also show (cite the sample). |
| **G2 Profile** | No HIGH drift flag against the author's profile. |
| **G3 Call-outs** | Zero P0 lines (the `signals.md` "screenshot tells"): tier-A vocabulary, template phrases, contrast-negation reveals, summary or moral endings, interpretive -ing kickers, performed candor, bullet or header scaffolding in a prose voice, staccato drama. |
| **G4 Provenance** | No `[NEED: ...]` markers. When material is supplied: every number, name, date, and quote in the draft appears in it, and no opinion appears that the brief or profile does not record. |
| **G5 Voice** | At least three of the profile's signature moves are present, and none of its "never does" items occur. Vocabulary foreign to the author's samples: none from the AI lexicon. |
| **G6 Long form** (over 1,500 words) | The three windows differ in rhythm (no `window_similarity` flag); no two sections share a shape and an ending; no paragraph opener repeats within 500 words. |
| **G7 Length** | Within ten percent of the target, when a target was given. |

4. **Decide.** PASS only if every applicable gate holds. A MEDIUM flag never
   fails a gate on its own; it fails only when the cold read found the line it
   points to and the line is not the author's move.

## Report

```
VERDICT: PASS | FAIL
Cold read: <first doubted sentence, first voice slip, would-have-guessed>
Gates: G1 ok | G2 ok | G3 FAIL (2) | G4 ok | G5 ok | G6 n/a | G7 ok
Fix list (ranked, max 12):
  1. L<n>: "<quoted>"  gate G3  <signal>  <fix direction in under ten words>
  2. ...
Kept against a flag: L<n> "<quoted>" because <profile sample shows the same move>
Measurements: <one-screen script summary; window table for long pieces>
Scope: Independent cold read plus deterministic stylometry. No commercial
detector was run; this verdict predicts a reader, not a classifier score.
```

The fix list is the whole hand-off to the next revise pass, so each item
must be actionable from the line alone. Twelve items is the ceiling; if more
fail, list the twelve that a reader would hit first (opening, ending, then
P0s in reading order) and say how many remain.

## Completion criterion

A verdict, every gate marked ok / FAIL / n-a with a reason for each FAIL and
each n-a, a ranked fix list with quoted lines, and the scope line. The
validator produces no rewritten text.
