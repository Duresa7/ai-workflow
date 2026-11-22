# Voice profile: {{author}}

Built {{date}} from {{n}} samples ({{words}} words). Pair with `{{author}}.stylometry.json`
(from `scripts/stylometry.py profile`), which holds the numeric baseline.

## Who is talking

One paragraph. Who this person is on the page: how they relate to the reader
(peer, guide, skeptic, friend), what they assume the reader already knows, what
they are usually trying to get the reader to do or feel.

## Signature moves (do these)

Concrete, quotable habits found in the samples, each with one verbatim example.
Aim for 6-12. Examples of the kind of thing that belongs here:

- Opens with a specific scene or a moment in time, not a thesis. ("I spent most
  of Tuesday trying to get a 2014 Thinkpad to boot off a USB stick.")
- Admits what they did not know or got wrong, in plain words.
- Addresses individual readers by name when replying to mail.
- Reports numbers as they were measured, with units, and says what they did
  not test.
- Lets a paragraph be one sentence when the point is small.
- Uses "which" clauses to tack a dry aside onto a factual sentence.

## Never does (the author's own absences)

Things the samples conspicuously lack. These are the first places an AI draft
will betray itself. Each with a note on what the author does instead.

- No headers in a piece under 1,500 words.
- No bullet lists in the body; lists happen in prose ("I have a list. It's not a
  short one.").
- No summarising last paragraph; ends on the last concrete thing or an ask.
- No "In this issue" / "Let's dive in" openers.
- Em dashes: {{never | rare, under N per 1,000 words | frequent}}.

## Vocabulary

- **Favourite words and phrases** (from the stylometry favourites list, trimmed
  to the ones that carry voice): ...
- **Register words**: the swears, slang, hedges, and intensifiers they actually
  use ("I swear", "eventually", "fine, actually").
- **Words they would never write**: pull from the AI lexicon anything absent
  from the samples (`vocabulary.ai_lexicon_used` in the JSON shows which ones
  they *do* use, so those are allowed).

## Rhythm (from the JSON, in words)

Sentence length mean {{x}} with CV {{y}}: say what that feels like ("long
sentences that run on with 'and' and 'which', broken by two- or three-word
sentences for emphasis"). Paragraphs: typical length, whether one-liners occur.
Contractions: {{rate}}, which reads as {{spoken | formal}}. First person: {{rate}}.
Questions: {{rate}}. Readability: Flesch {{z}}.

## Structure habits by format

- **Newsletter issue**: typical length, how it opens, whether it has sections,
  how it closes (ask, teaser, sign-off), how links are introduced.
- **Article / essay**: same questions.
- **Post (X/Threads/LinkedIn)**: line breaks, hooks, whether threads are used,
  emoji policy.

## Stance and limits

What the author is willing to say in their own name: strong opinions on X,
careful about Y, never claims Z. The writer skill must not give them opinions,
experiences, or facts the samples and the brief do not support.

## Sample passages (verbatim, 3-5)

Short passages (60-150 words) that are the most *them*. The writer skill reads
these before drafting and the validator compares against them.
