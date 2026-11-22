---
name: voice-audit
description: Detect-only audit of a draft for the signals that make readers and AI detectors call prose AI-written, plus drift from the author's voice profile. Use when the user asks whether a piece reads as AI, wants it scanned or flagged without rewriting, or when the human-voice pipeline needs findings for a revise pass.
---

# Voice audit

Read the draft the way the hostile reader does, then measure it, then say
exactly which lines would get screenshotted and why. **Detect only.** The
audit never rewrites; its product is a findings list another pass can act on.

Shared files live in the sibling `human-voice` skill directory (resolve
`../human-voice` from this skill's real directory). Read
`references/signals.md` in full before the first pass; it is the checklist
and it carries the sources behind each item.

## Inputs

- The draft (file path or pasted text; write pasted text to a temp file so
  the script can run).
- Optional: `./voice/<name>.voice.md` and `<name>.stylometry.json`.
- Optional: the brief and material, which enable the provenance checks.
- Context: `newsletter`, `article`, `post`, or `essay`.

## Steps

1. **Cold read first, whole piece, no tools.** Write one line: what a
   skeptical reader would say about this piece after reading it once
   ("reads like a LinkedIn post about leadership", "sounds like the author
   until the last section", "fine"). Keep that line; it heads the report.
2. **Measure:**
   ```bash
   python3 ../human-voice/scripts/stylometry.py analyze DRAFT --context <ctx> \
     [--profile ./voice/<name>.stylometry.json] [--windows] --with-avoid-ai-writing
   ```
   Read the flags *and* the evidence lines. A flag without an evidence line
   you can quote is not a finding.
3. **Shape pass.** Headers, bullets, bold, paragraph lengths, section
   symmetry, how sections end, how the piece ends, opener repetition across
   paragraphs. Compare to the profile's Structure habits when present.
4. **Sentence pass.** Walk every paragraph against the sentence-level items in
   `signals.md`: vocabulary, template phrases, contrast negation, triplets,
   interpretive -ing kickers, transition openers, hedge stacks, puffery,
   performed candor, rhetorical question-and-answer, colon reveals. Quote
   each hit with its line number.
5. **Substance pass.** The portability test on each paragraph (could it move
   unchanged into a piece on another subject?), presence of specifics
   (numbers with units, names, dates, mechanisms), presence of the author's
   stance, and provenance of every specific when material was supplied.
6. **Voice pass** (profile present). Which signature moves appear; which
   "never does" items the draft does; AI-lexicon words foreign to the author's
   samples (the script lists them); rhythm and readability drift the script
   flagged.
7. **Rank.** Severity is about the reader, not the tool:
   - **P0 call-out**: a line a reader would screenshot on its own (tier-A
     vocabulary, a template phrase, a contrast-negation reveal, a summary
     ending, an -ing kicker, bullet-point body in a prose voice).
   - **P1 pattern**: a tell that needs two or three instances to register
     (transition openers, triplets, uniform paragraphs, nominalised prose,
     hedge stacks, missing specifics).
   - **P2 drift**: measurable distance from the author's own baseline or from
     the reference ranges, with no single quotable line.

## Report

Return, in this order, and nothing else:

1. **Cold read**: the one line from step 1.
2. **Call-outs (P0)**: each as `L<n>: "<quoted text>"` followed by the signal
   name from `signals.md` and the *direction* of the fix in under ten words
   ("replace with the number from the notes", "end on the previous
   sentence"). Direction, not a rewrite.
3. **Patterns (P1)**: signal name, count, two or three quoted instances, fix
   direction.
4. **Drift (P2)**: the script's flags with value, bound or author baseline,
   and one line on what it means for this piece.
5. **Keep verbatim**: three to six lines that are the most the author and
   must survive revision untouched. A revise pass with no keep-list over-edits.
6. **Measurements**: the script's one-screen summary (word count, rhythm,
   lexicon, structure, windows if run) and whether the avoid-ai-writing
   detector ran.
7. **Scope**: "Detect-only. Deterministic script ran / did not run. No
   commercial detector was consulted; nothing here predicts their scores."

## Completion criterion

Every P0 and P1 item carries a quoted line and a line number, every script
flag is either explained or listed under Drift, the keep-list is present, and
the report contains no rewritten text.
