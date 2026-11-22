---
name: voice-profile
description: Build an author's voice profile from samples of their own writing, so drafts can be written and checked against how they actually write. Use when the user wants a voice profile, style fingerprint, or "learn how I write", or before voice-write runs for an author with no profile on disk.
---

# Voice profile

Produce two files that describe how one author writes: a qualitative profile a
writer can imitate, and a numeric baseline a validator can measure drift
against. Everything downstream (voice-write, voice-audit, voice-validate) is
only as good as this profile, so the bar is **a reader who knows the author
would recognise them from the profile alone**.

Shared files live in the sibling `human-voice` skill directory (resolve
`../human-voice` from this skill's real directory): the script is
`scripts/stylometry.py`, the template is `references/voice-profile-template.md`.

## Inputs

- **Samples.** 3 to 8 pieces the author wrote themselves, without AI, in the
  format they publish (newsletter issues, articles, posts). 300+ words each for
  prose; for posts, collect 20+ posts into one file separated by blank lines.
  Fewer than 3 samples: build the profile anyway, label it *thin*, and say
  which sections are guesses.
- **Name** for the author and an **output directory** (default `./voice/`).
- Optional: a note from the author on what they think their voice is. Use it
  as a hypothesis to check against the samples, never as the profile itself.

If no samples are supplied, ask for them. A profile written from the author's
self-description alone is fiction.

## Steps

1. **Read every sample end to end** before measuring anything. Note, with
   line references, each place you thought "only this person would write
   that". Those become the signature moves.
2. **Run the numeric baseline:**
   ```bash
   python3 ../human-voice/scripts/stylometry.py profile SAMPLE1 SAMPLE2 ... \
     --out ./voice/<name>.stylometry.json --name "<name>"
   ```
   Then run `analyze` on each sample individually and read the reports. Any
   sample that flags HIGH against the reference ranges is either not the
   author's unaided writing or a deliberate house style; ask which, and drop it
   from the profile if the answer is the former.
3. **Fill the template** at `references/voice-profile-template.md` into
   `./voice/<name>.voice.md`. Every claim in "Signature moves" and "Never does"
   carries a verbatim example or a count from the JSON. A move you cannot quote
   from a sample is not a move; cut it.
4. **Translate the numbers into prose** in the Rhythm section. The writer
   skill reads words, not JSON; "runs long, then snaps short" is usable,
   "CV 0.64" is not.
5. **Pick 3 to 5 sample passages** that are the most characteristic, 60 to 150
   words each, verbatim. Prefer passages that show the moves and absences at
   once (an opening, a correction, an ending).
6. **Check the profile against a held-out sample** if one exists: read the
   sample, then the profile, and list anything the sample does that the
   profile does not predict. Fold it in.

## Completion criterion

Both files exist, every signature move and absence has a quoted example, the
Rhythm section reads as prose, and the sample passages are verbatim. Report
the paths, the sample count and total words, and which sections are thin.

## Boundaries

A profile records what the author does. It does not invent opinions, stories,
or facts for them, and it does not describe a voice they would like to have.
When the author's self-description and the samples disagree, the samples win
and the disagreement goes in the Stance section as a note.
