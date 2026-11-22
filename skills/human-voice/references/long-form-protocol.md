# Long-form protocol (1,500 to 5,000 words)

Why a separate protocol: the signals that get a long piece called out are
mostly *cross-section* problems a one-pass draft cannot see. Sections written
one after another in a single context drift toward the same opener, the same
paragraph length, the same three-beat rhythm, and the same closing move. The
piece reads fine paragraph by paragraph and reads machine-made as a whole.
Everything below exists to break that symmetry on purpose.

## 1. Plan with beats, not headings

Write the plan as a list of **beats** (one move each: a scene, a claim, an
example, a correction, an aside, a turn) rather than a list of headings. Record
for each beat:

- what the reader knows walking in and what this beat grounds for later beats;
- the **material** it draws on (which note, number, quote, or source);
- its intended **shape**: a story, an argument, a list in prose, a one-line
  paragraph, a quoted exchange, a table if the material is tabular.

Vary the shapes deliberately in the plan. If three consecutive beats are
"claim + two supporting points", change one into a scene or a question the
author is still sitting with. A 4,000-word piece typically has 12 to 20 beats.

Headings: only if the author's profile uses them at this length. Many
newsletter voices run 3,000 words with no headings at all.

## 2. Keep a ledger while drafting

Maintain a scratch ledger (a file, not memory) with four lists and update it
after every beat:

1. **Claims made**, in one line each, so later beats build on them rather than
   restate them.
2. **Specifics used**: every number, name, date, example, quote. Reuse means a
   reader notices; a second use must be a callback, not a repeat.
3. **Openers used**: the first three words of every paragraph. The same opener
   twice in 500 words is a tell. The same *kind* of opener (a rhetorical
   question, a "Here's", a time-stamp) more than twice in the piece is also a
   tell.
4. **Closers used**: how each section ended. Two sections ending on a
   one-sentence punch, or two ending on a lesson, is the pattern readers call
   "the AI mic drop".

## 3. Draft beat by beat, re-reading the previous beat first

Before writing beat N, re-read beat N-1 in full and the ledger. Write the beat
in the author's voice using the profile's signature moves and the sample
passages as the ear. Then record the beat in the ledger.

Rules that hold across the whole draft:

- **Specifics come from the brief, the notes, or the author.** Where the beat
  needs a specific the material does not supply, write `[NEED: what is
  missing]` in place and keep going. Never fill the hole with a plausible
  number or a generic example.
- **Rhythm comes from content.** A short sentence is short because its point is
  small, not because the last three were long. Never chop sentences to
  manufacture variation, and never run a staccato triplet for effect unless the
  profile shows the author doing that.
- **Paragraph length follows the beat.** A one-line paragraph for a small
  point; a 180-word paragraph for a story that needs it. The script's
  paragraph-length CV should land where the author's profile puts it, which for
  most human newsletter writers is above 0.4.
- **Transitions are content, not connectors.** The next paragraph starts with
  its own subject. "However", "Moreover", "Additionally", "That said" at the
  head of a paragraph are the single most reliable cross-section tell.
- **No section summaries, no piece summary.** The piece ends on the last
  concrete thing or on an ask, unless the profile shows the author summarising.

## 4. Assembly pass

Assemble the beats, then read the whole piece once, start to finish, before
running any tool. Fix, in this order:

1. **Repeats across sections**: the ledger will show them; the read confirms.
2. **Symmetry**: two sections with the same shape or the same ending.
3. **Drift in person or tense** between sections written at different times.
4. **Orphaned `[NEED: ...]` markers**: resolve from the material or raise them
   with the author. A draft with open markers is not finished.

Only then run `scripts/stylometry.py analyze --profile`. On a long piece the
rhythm and lexicon metrics are reliable (they are noisy under 300 words), so
treat a HIGH flag as real and go to the evidence lines.

## 5. Context limits and chunking

A 5,000-word draft plus the profile, the material, and the ledger fits one
context. The failure mode is not running out of room; it is the model
attending less to the profile as the draft grows. Counter it by re-reading the
profile's "Never does" list and one sample passage before every third beat.

If the material is very large (a long transcript, many notes), split the
material by beat in the plan and load only the beat's material while drafting
it. The ledger carries continuity.

## 6. Validation on long pieces

The validator reads the whole piece cold. On long pieces it additionally
samples three 300-word windows (beginning, middle, end) and compares their
metrics; a human writer's windows differ from each other, and a window whose
numbers match the others to the second decimal is itself a signal. The
validator reports which window, and which metric, if it finds this.
