---
name: voice-write
description: Draft or rewrite a newsletter issue, article, or social post in a specific author's voice, from their brief and notes, up to 5,000 words. Use when the user wants a piece written "in my voice", wants a draft rewritten so it reads as them, or asks to apply voice-audit findings to a draft.
---

# Voice write

Write prose a reader who knows the author would accept as theirs. The reader
is the test, and the reader is skeptical: they have seen a thousand AI drafts
and they notice the shape before they notice the words.

Shared files live in the sibling `human-voice` skill directory (resolve
`../human-voice` from this skill's real directory). Before drafting, read
`references/signals.md` (what readers and detectors key on) and, for anything
over 1,500 words, `references/long-form-protocol.md`.

## Inputs

- **Voice profile**: `./voice/<name>.voice.md` plus `<name>.stylometry.json`.
  If none exists and samples are available, run the `voice-profile` skill
  first. If neither exists, say so, write in a plain, unmarked register, and
  label the draft *unprofiled*; do not improvise a personality.
- **Brief**: the point of the piece, the audience, the format (newsletter,
  article, post), the target length, and the ask or close the author wants.
- **Material**: notes, numbers, links, quotes, earlier drafts, anything the
  piece may draw on. This is the only source of specifics.
- **Mode**: `draft` (new piece from brief and material), `rewrite` (an existing
  draft that should read as the author), or `revise` (apply a list of findings
  from voice-audit or voice-validate to a draft).

## Steps

1. **Load the ear.** Read the profile's sample passages aloud in your head,
   then the Signature moves and Never does lists. Keep the profile open; you
   will re-read it.
2. **Inventory the material.** List every specific it contains: numbers with
   units, names, dates, places, quotes, examples, the author's stated
   opinions. This list is the whole budget of specifics for the piece. Where
   the brief needs a specific that is not here, plan a `[NEED: ...]` marker.
3. **Plan beats.** For a post, one or two. For a 600-word issue, four to six.
   For long pieces follow `long-form-protocol.md` section 1, and keep its
   ledger from the first beat.
4. **Draft** beat by beat. Each beat does one thing in the author's shape for
   that thing. Targets:
   - Open on a specific (a moment, a number, a reader's question, an object),
     the way the profile's openings do.
   - The next paragraph begins with its own subject. Connectors belong inside
     sentences, if anywhere.
   - Say the author's opinion in the author's words where the brief or
     material records one. Where it does not, write the facts and leave the
     opinion out; a `[NEED: your take on X]` marker is better than a view they
     never held.
   - Sentence length follows the thought. Let a long sentence run when the
     thought runs; let a point stand alone when it is small.
   - End on the last concrete thing, the ask, or the next thing the author
     will do, as the profile's endings do.
5. **Assemble and read the whole piece once** before any tool runs. Fix
   repeats, symmetry between sections, and tense or person drift.
6. **Measure.**
   ```bash
   python3 ../human-voice/scripts/stylometry.py analyze DRAFT --profile ./voice/<name>.stylometry.json --context <newsletter|article|post> [--windows]
   ```
   Go to every evidence line behind a HIGH flag and rewrite that sentence from
   the material, not by paraphrase. A MEDIUM flag is a prompt to look; keep the
   line if it is the author's move. Run once more after fixing.
7. **Deliver**: the full draft once, then **Writer's notes** (under ten lines):
   open `[NEED]` markers, the beats where the material was thin, anything the
   profile and the brief disagreed on and which won, and the script's remaining
   flags with the reason each was kept.

### Rewrite mode

Read the existing draft first and mark the sentences that already sound like
the author. Those stay verbatim. Change only the spans that do not, and keep
the author's structure unless the brief asks for a new one. Report the
proportion of sentences left untouched.

### Revise mode

Take the findings list as the scope. Each finding gets one targeted change at
the quoted line, drawn from the material. Lines without a finding stay as
they were. Re-run the script, and report each finding as fixed, kept (with the
reason), or blocked (needs material from the author).

## The provenance test

For every sentence in the draft, one of these must be true: it restates
something in the material or brief; it is the author's recorded opinion; it
is structural connective tissue with no claim in it; or it is marked `[NEED]`.
A sentence that fails the test is deleted, however good it reads. The
specifics that make writing feel human are the ones that are *true*; a
fabricated one is worse than the vague line it replaced, and it is the first
thing a knowledgeable reader catches.

The same provenance rule covers the author's presence. First-person
experience, reactions, and admissions appear only where the material records
them. A draft that reaches for "I've seen this a hundred times" or "I'll be
honest" to sound human has installed a second fake voice on top of the first.

## Rhythm comes from content

The script measures sentence-length variation because human prose has it,
but the variation is a *consequence* of writing each thought at its own
length. Chopping sentences into fragments, stacking a punchy triplet, staging
an em dash for drama, or alternating long and short on a schedule all produce
a different recognisable fingerprint, the one readers now call "humanizer
voice". When a passage reads flat, the fix is in the beat: find the specific
that is missing, the aside the author would make, the point that deserves its
own line. Fix the content and the numbers follow.

## Formats

- **Newsletter issue**: opens the way the profile's issues open (a scene, a
  reader's mail, a correction, a date-stamp), carries the author's sign-off
  habits, introduces links in prose. Headings and bullets only if the profile
  uses them at this length.
- **Article**: a lede that is a specific, not a thesis; the argument carried
  in paragraphs; sections only where the profile uses them.
- **Post**: hook in the first line, the author's line-break habit, no
  hashtags or emoji unless the profile shows them, and no "thread" scaffolding
  unless asked. A post is too short for rhythm statistics; vocabulary and
  structure carry the whole signal.

## Completion criterion

The draft is at target length within ten percent, every sentence passes the
provenance test, the script shows no HIGH flag against the reference ranges or
the author's profile (or each remaining one is named in Writer's notes with
its reason), and the piece has been read once end to end after assembly.
