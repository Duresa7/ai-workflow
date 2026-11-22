---
name: human-voice
description: End-to-end pipeline for publishing prose that reads as its author, not as AI, up to 5,000 words. Profiles the author's voice, writes or rewrites the piece, audits it for the signals readers and AI detectors key on, and validates it with an independent cold read. Use when the user wants a newsletter, article, or post written or rewritten "so it won't get called out as AI", or asks to run the full voice pipeline.
---

# Human voice

One loop, four skills, one bar: **a skeptical reader who knows the author
would accept this as theirs.** Detector scores are a diagnostic along the way,
never the goal, for reasons laid out in `references/detectors.md` and
`references/detector-failures.md`.

Layout (all paths relative to this skill directory):

| What | Where |
|---|---|
| Author baseline | `../voice-profile/SKILL.md` |
| Drafting and revising | `../voice-write/SKILL.md` |
| Detect-only audit | `../voice-audit/SKILL.md` |
| Independent cold-read gate | `../voice-validate/SKILL.md` |
| What readers and detectors key on | `references/signals.md` |
| How GPTZero, Pangram, Turnitin and others work | `references/detectors.md` |
| Cited failure cases (for writing about detectors) | `references/detector-failures.md` |
| Pieces over 1,500 words | `references/long-form-protocol.md` |
| Deterministic measurements | `scripts/stylometry.py` |

## Intake

Settle these before any drafting, asking the user only for what the request
and the working directory do not already answer:

1. **Author and profile.** Look for `./voice/<name>.voice.md`. None, but
   samples exist (or the user can paste 3+ pieces): run `voice-profile`.
   None and no samples: continue unprofiled and say so in the final report;
   the validator's bar is lower without a profile and the user should know.
2. **Format and length.** Newsletter issue, article, or post; target words.
3. **Mode.** New draft from a brief, or an existing draft to rewrite.
4. **Material.** Everything the piece may draw on. The writer may not invent
   specifics, so thin material means `[NEED]` markers in the draft, which is
   the correct outcome, not a failure.

## The loop

```
write ──> audit ──> revise ──> validate ──> (PASS) deliver
                        ^                      |
                        └───── (FAIL) ─────────┘   at most 3 rounds
```

1. **Write.** Follow `voice-write` in `draft` or `rewrite` mode. Output a
   draft file (`./drafts/<slug>.v1.md`) and Writer's notes.
2. **Audit.** Run `voice-audit` on the draft **in a fresh subagent** that
   receives the draft, the profile, and the brief, and nothing about how the
   draft was written. Anchoring on the writer's intentions is the main way an
   audit goes soft.
3. **Revise.** Follow `voice-write` in `revise` mode with the audit's findings
   as the scope. Output `v2`.
4. **Validate.** Run `voice-validate` on the revised draft in another fresh
   subagent, with the profile and the brief only. It returns PASS or FAIL with
   the exact lines that fail.
5. On FAIL, feed the validator's lines to another `revise` and validate again.
   Stop after three rounds either way; a piece that fails three cold reads has
   a material problem (thin specifics, wrong voice profile, a brief that
   demands claims the author never made), and the report says which.

Keep every version; the user may prefer an earlier one.

## Deliver

The final draft once, then a report under fifteen lines:

- **Verdict**: PASS or FAIL on the last cold read, with round count.
- **Open items**: `[NEED]` markers still in the text; lines kept against a
  flag because they are the author's move.
- **Measurements**: the final stylometry flags, each with its reason, and the
  per-window table for long pieces.
- **Voice**: the proportion of the author's own sentences preserved (rewrite
  mode), and the profile sections that were thin.
- **What this does and does not say**: the piece passed a deterministic
  stylometry check and an independent cold read against the author's profile.
  No commercial detector was run and no claim is made about any detector's
  score; see below.

## External detector scores as a metric

The user may run GPTZero, Pangram, Copyleaks, or Turnitin on the result,
because readers do. Treat a pasted result as one more noisy reader:

- Read the **sentence-level highlights**, not the headline percentage. A
  highlighted sentence is worth a second look with the audit checklist; the
  overall number is not actionable and the vendors themselves say so.
- Never iterate against a detector score. Rewriting a sentence until a
  classifier flips teaches the writer a new synthetic voice and does nothing
  for the human reader. If a sentence is the author's and passes the cold
  read, it stays.
- Human text gets flagged. `references/detector-failures.md` lists the
  measured false-positive rates and documented cases; cite them when a reader
  calls a piece out, and when writing about the tools.
- Pangram and the current GPTZero models are trained on paraphrased and
  "humanized" output. Mechanical rewriting is the one thing they are good at
  catching, which is a second reason this pipeline optimises for the reader.

## Completion criterion

A final draft at target length, a PASS from an independent validate (or a
FAIL with the material cause named), every `[NEED]` either resolved or listed,
and the report above delivered. The loop is done when the cold read passes,
not when the flags reach zero.
