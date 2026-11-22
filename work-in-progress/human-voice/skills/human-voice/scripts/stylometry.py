#!/usr/bin/env python3
"""Deterministic stylometry for prose: the measurable half of "does this read as AI?"

Three subcommands:

  analyze  FILE [--profile voice.json] [--format text|json] [--context newsletter|article|post]
           Compute metrics, flag outliers against reference ranges (and against the
           author's own profile when given), and list evidence lines.

  profile  SAMPLE... --out voice.json [--name "Author"]
           Build an author baseline from 3+ samples of their own writing.

  compare  FILE --profile voice.json
           Only the drift-from-profile part of analyze.

Pure standard library. Markdown aware: code blocks, URLs, front matter, HTML
comments, and tables are excluded from the prose before measuring.

Exit codes: 0 = no high-severity flags, 1 = at least one high-severity flag,
2 = usage or I/O error. Exit 1 is a prompt to look, never a verdict.

Reference ranges come from the literature summarised in
../references/signals.md (burstiness, sentence-length CV, lexical diversity,
nominalisation and participial-clause rates). They describe typical published
human prose in English; a specific author can sit outside them and still be
human, which is exactly why `profile` exists.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
from collections import Counter

# --------------------------------------------------------------------------
# Reference ranges (typical published English prose). Each entry:
#   key: (low, high, direction, severity, note)
# direction: 'low' = flag when value is below low; 'high' = flag when above high;
#            'both' = flag outside [low, high]. A None bound is unbounded.
# Calibrated against: Reinhart et al. 2025 (PNAS), Muñoz-Ortiz et al. 2023,
# Herbold et al. 2023, Kobak et al. 2024/2025, GPTZero's burstiness definition,
# and the avoid-ai-writing stylometric rules. See references/signals.md.
# --------------------------------------------------------------------------
REFERENCE = {
    "sentence_len_cv":        (0.45, None, "low",  "high", "Sentence lengths are too uniform. Human prose usually has CV >= 0.45; LLM prose clusters near 0.30-0.40."),
    "burstiness":             (-0.35, None, "low", "medium", "Low burstiness (sigma-mu)/(sigma+mu). Human prose is rarely below -0.35; near -0.5 reads as metronomic."),
    "uniform_sentence_share": (None, 0.55, "high", "medium", "More than 55% of sentences sit within 25% of the mean length."),
    "paragraph_len_cv":       (0.35, None, "low", "medium", "Paragraph lengths are too even. Human paragraphs vary (CV >= 0.35)."),
    "mattr_100":              (0.70, None, "low", "medium", "Low lexical diversity (MATTR window 100). Human published prose typically 0.72-0.85."),
    "mtld":                   (60.0, None, "low", "low", "Low MTLD; repetitive vocabulary."),
    "ai_lexicon_per_1k":      (None, 4.0, "high", "high", "AI-associated vocabulary density per 1,000 words. Human baseline is roughly 0-2; above 4 gets noticed."),
    "ai_phrase_per_1k":       (None, 2.0, "high", "high", "AI-associated phrase/template density per 1,000 words."),
    "structural_tells_per_1k": (None, 2.5, "high", "high", "Structural tells (contrast negation, colon reveals, tricolons, staccato runs, -ing kicker clauses) per 1,000 words."),
    "transition_opener_share": (None, 0.12, "high", "medium", "Share of sentences opening with a discourse transition (However, Moreover, Additionally, Furthermore...)."),
    "nominalization_per_1k":  (None, 45.0, "high", "medium", "Nominalisations (-tion/-ment/-ness/-ity) per 1,000 words. Reinhart et al. 2025: LLMs over-use these."),
    "participial_clause_per_1k": (None, 6.0, "high", "medium", "Present-participial clauses (', verb-ing ...') per 1,000 words. A strong LLM marker in Reinhart et al. 2025."),
    "em_dash_per_1k":         (None, 3.0, "high", "low", "Em dashes per 1,000 words. Not evidence of authorship, but readers now treat clusters as a tell."),
    "contraction_per_1k":     (3.0, None, "low", "low", "Few contractions. Fine for formal prose; in a newsletter or post, their absence reads as stiff."),
    "first_person_per_1k":    (None, None, "both", "low", "First-person density. Context dependent; compared against the profile when available."),
    "opener_repeat_share":    (None, 0.18, "high", "medium", "Share of sentences that start with the single most common opener word."),
    "staccato_runs":          (None, 1, "high", "medium", "Runs of 3+ consecutive sentences under 6 words (manufactured punchiness)."),
    "bold_mid_sentence":      (None, 2, "high", "low", "Bold spans inside sentences (count)."),
    "header_per_500w":        (None, 2.0, "high", "low", "Headers per 500 words. Over-structured prose."),
    "bullet_share":           (None, 0.35, "high", "low", "Share of non-empty lines that are bullets."),
    "emoji_count":            (None, 0, "high", "low", "Emoji present in body prose."),
    "flesch_reading_ease":    (None, None, "both", "low", "Readability. Compared against the profile when available."),
    "sentence_final_ing_kicker": (None, 1.5, "high", "medium", "Sentences ending in an interpretive -ing clause ('..., highlighting the importance of X') per 1,000 words."),
}

# Rate metrics only flag when the underlying count is also at least this large,
# so one colon in a 400-word piece cannot trip a high-severity flag.
MIN_COUNT = {
    "ai_lexicon_per_1k": ("ai_lexicon_count", 3),
    "ai_phrase_per_1k": ("ai_phrase_count", 2),
    "structural_tells_per_1k": ("structural_tells_count", 3),
    "participial_clause_per_1k": ("participial_clause_count", 3),
    "sentence_final_ing_kicker": ("ing_kicker_count", 2),
    "em_dash_per_1k": ("em_dash_count", 3),
    "nominalization_per_1k": ("nominalization_count", 8),
}

# Metrics compared against an author profile (z-score on the author's own spread).
PROFILE_KEYS = [
    "sentence_len_mean", "sentence_len_cv", "burstiness", "paragraph_len_mean", "paragraph_len_cv",
    "mattr_100", "contraction_per_1k", "first_person_per_1k", "second_person_per_1k",
    "em_dash_per_1k", "semicolon_per_1k", "question_per_1k", "exclamation_per_1k", "paren_per_1k",
    "flesch_reading_ease", "avg_syllables_per_word", "nominalization_per_1k", "participial_clause_per_1k",
    "transition_opener_share", "short_sentence_share", "long_sentence_share", "ai_lexicon_per_1k",
]

# --------------------------------------------------------------------------
# Lexicon. Words and phrases that readers and vocabulary studies associate with
# LLM prose. Tier A fires on a single use; tier B fires on density (2+ uses or
# >= 1 per 500 words). Keep this list in sync with references/signals.md.
# --------------------------------------------------------------------------
LEXICON_A = """
delve delves delving delved tapestry tapestries testament multifaceted
underscore underscores underscoring underscored unwavering ever-evolving
groundbreaking game-changer game-changing paradigm realm realms beacon
synergy synergies seamless seamlessly meticulous meticulously intricate intricacies
pivotal paramount plethora myriad transformative elevate elevates elevating
embark embarking harness harnessing unlock unlocking unleash unleashing
supercharge supercharged holistic holistically nuanced vibrant bustling
captivating enchanting enduring resonate resonates resonating
foster fosters fostering leverage leverages leveraging utilize utilizes utilizing
streamline streamlined streamlining robust cutting-edge state-of-the-art
navigate navigating landscape landscapes trailblazer trailblazing
showcase showcases showcasing spearhead spearheaded
""".split()

LEXICON_B = """
crucial crucially vital essential key comprehensive dynamic innovative
empower empowering empowers insights actionable impactful
journey journeys ensure ensuring enhance enhancing enhanced
significant significantly notably remarkable remarkably
ultimately additionally moreover furthermore
""".split()

PHRASES = [
    r"\bin today'?s (?:fast-paced|rapidly (?:evolving|changing)|digital|modern|ever-changing)\b",
    r"\bin the (?:rapidly )?(?:evolving|ever-changing|dynamic) (?:world|landscape|realm) of\b",
    r"\bit(?:'s| is) (?:important|worth|crucial|essential) to (?:note|remember|understand|recognize|mention)\b",
    r"\bit(?:'s| is) worth noting\b",
    r"\ba testament to\b",
    r"\bplays? a (?:crucial|vital|pivotal|key|significant|important) role\b",
    r"\bin the realm of\b",
    r"\bat the end of the day\b",
    r"\bin conclusion\b",
    r"\bin summary\b",
    r"\bto sum up\b",
    r"\bthe key takeaway\b",
    r"\bkey takeaways?\b",
    r"\bthat being said\b",
    r"\bwith that (?:being )?said\b",
    r"\bit goes without saying\b",
    r"\bneedless to say\b",
    r"\blet'?s (?:dive|delve|jump|explore|unpack|break)\b",
    r"\b(?:dive|delve) (?:deep(?:er)? )?into\b",
    r"\bnavigat(?:e|ing) the (?:complexities|challenges|nuances|landscape)\b",
    r"\bwhether you(?:'re| are) a\b",
    r"\blook no further\b",
    r"\bin an era (?:of|where)\b",
    r"\bin a world where\b",
    r"\bnow more than ever\b",
    r"\bthe stakes (?:have never been|are) higher\b",
    r"\bhere'?s the thing\b",
    r"\bhere'?s (?:what|why|how) (?:that|this|it) (?:means|matters|works)\b",
    r"\bthe (?:truth|reality|fact) is\b",
    r"\blet'?s be (?:honest|real|clear)\b",
    r"\bI(?:'ll| will) be honest\b",
    r"\bto be honest\b",
    r"\breal talk\b",
    r"\bserves? as (?:a|an)\b",
    r"\bstands? as (?:a|an)\b",
    r"\bact(?:s|ing)? as (?:a|an) (?:beacon|catalyst|cornerstone|bridge)\b",
    r"\bunlock(?:s|ing)? (?:the|your|its) (?:full )?potential\b",
    r"\ba (?:deep|profound|new) (?:dive|understanding|appreciation)\b",
    r"\b(?:rich|vibrant) (?:tapestry|history|culture)\b",
    r"\bfrom .{3,40} to .{3,40}, (?:and )?everything in between\b",
    r"\bnot (?:just|only|merely|simply) (?:about )?\w[^.;:!?]{0,60}?,? (?:but|it'?s|it is) (?:also )?(?:about )?\b",
    r"\bisn'?t (?:just|only|merely|simply|about)\b[^.;:!?]{0,80}?(?:;|,|—|-)\s*it'?s\b",
    r"\bit(?:'s| is) not (?:just |only |merely |simply |about )?[^.;:!?]{0,80}?(?:;|,|—|-)\s*it(?:'s| is)\b",
    r"\bthe (?:question|problem|issue|point) (?:isn'?t|is not|here isn'?t)\b[^.;:!?]{0,80}?(?:;|,|—|-)\s*it'?s\b",
    r"\bfirst(?:ly)?,? .{10,200}? second(?:ly)?,? .{10,200}? (?:third|finally|lastly)\b",
    r"\bin other words\b",
    r"\bas (?:we|you) can see\b",
    r"\bthis (?:is|was) (?:a )?(?:game[- ]changer|huge|big)\b",
    r"\bthis changes everything\b",
    r"\bbuckle up\b",
    r"\bstay tuned\b",
    r"\bI hope this helps\b",
    r"\bgreat question\b",
    r"\bas an AI\b",
    r"\bas of my last (?:update|training)\b",
    r"\bexperts (?:agree|believe|say|suggest)\b",
    r"\bstudies (?:show|suggest|have shown)\b",
    r"\bmany (?:people |experts )?(?:argue|believe|say)\b",
    r"\bwidely (?:regarded|considered|recognized) as\b",
    r"\bmark(?:s|ed|ing)? a (?:pivotal|significant|turning|crucial|new) (?:moment|point|chapter|era)\b",
    r"\bsolidif(?:y|ies|ied|ying) (?:its|their|his|her) (?:position|place|status)\b",
    r"\bstands? out as\b",
    r"\bbreath of fresh air\b",
    r"\bthe (?:best|worst|craziest|wildest|interesting) part\??:\s*[a-z]",
    r"\bplot twist:",
    r"\bthink about it:",
    r"\bwhat if I told you\b",
    r"\bthe part (?:most people|everyone|nobody) (?:miss|skip|get wrong|tell)",
    r"\bwhat (?:most people|everyone|nobody) (?:miss|get wrong|tell you|talk about)",
]

TRANSITION_OPENERS = {
    "however", "moreover", "furthermore", "additionally", "consequently", "therefore", "thus",
    "nevertheless", "nonetheless", "ultimately", "overall", "importantly", "notably", "indeed",
    "similarly", "likewise", "conversely", "accordingly", "subsequently", "hence", "firstly",
    "secondly", "thirdly", "finally", "lastly", "essentially", "fundamentally", "crucially",
    "interestingly", "significantly", "remarkably", "undoubtedly", "arguably",
}

FIRST_PERSON = {"i", "i'm", "i've", "i'd", "i'll", "me", "my", "mine", "myself", "we", "we're", "we've", "we'd", "we'll", "us", "our", "ours"}
SECOND_PERSON = {"you", "you're", "you've", "you'd", "you'll", "your", "yours", "yourself"}

NOMINAL_SUFFIX = re.compile(r"\b\w{4,}(?:tion|sion|ment|ness|ity|ance|ence|ancy|ency)s?\b", re.I)
PARTICIPIAL_CLAUSE = re.compile(r"[,;]\s+(?:(?:thus|thereby|while|also|further|effectively|ultimately|potentially)\s+)?\w+ing\b")
SENTENCE_FINAL_ING = re.compile(r",\s+(?:highlighting|underscoring|showcasing|reflecting|demonstrating|signaling|signalling|emphasizing|emphasising|illustrating|suggesting|indicating|reinforcing|solidifying|cementing|marking|paving|ensuring|fostering|enabling|allowing|making|leaving)\b[^.!?]*[.!?]\s*$")
TRICOLON = re.compile(r"\b(\w+(?:\s\w+)?),\s(\w+(?:\s\w+)?),\s(?:and|or)\s(\w+(?:\s\w+)?)\b")
COLON_REVEAL = re.compile(r"(?:^|[.!?]\s+)(?:[A-Z][^.!?:]{2,40}):\s+[a-z][^.!?]{3,}")
RHETORICAL_Q_ANSWER = re.compile(r"\?\s+(?:Yes|No|Not really|Absolutely|Exactly|Simple|Nope|Yep|Turns out|It depends|Because)\b")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF]")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
ABBREV = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "e.g", "i.e", "fig", "inc", "ltd", "co", "u.s", "u.k", "a.m", "p.m", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"}


# --------------------------------------------------------------------------
# Text preparation
# --------------------------------------------------------------------------

def strip_markdown(text: str) -> tuple[str, dict]:
    """Return prose-only text and markdown structure counts."""
    info = {"headers": 0, "bullets": 0, "bold_spans": 0, "bold_mid_sentence": 0, "code_blocks": 0, "links": 0, "lines_nonempty": 0}
    # Front matter
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    # HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # Fenced code
    info["code_blocks"] = len(re.findall(r"```", text)) // 2
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", "CODE", text)
    # Tables
    text = re.sub(r"^\|.*\|\s*$", "", text, flags=re.M)
    # Links and images: keep link text
    info["links"] = len(re.findall(r"\[[^\]]*\]\([^)]+\)", text))
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", "URL", text)
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            lines.append("")
            continue
        info["lines_nonempty"] += 1
        if re.match(r"^#{1,6}\s", s):
            info["headers"] += 1
            continue  # headers are not prose for rhythm purposes
        if re.match(r"^(?:[-*+]|\d+[.)])\s", s):
            info["bullets"] += 1
            s = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", s)
        if re.match(r"^>\s?", s):
            s = re.sub(r"^>\s?", "", s)
        lines.append(s)
    text = "\n".join(lines)
    # Bold / italics
    bolds = re.findall(r"\*\*([^*\n]+)\*\*|__([^_\n]+)__", text)
    info["bold_spans"] = len(bolds)
    for m in re.finditer(r"\*\*[^*\n]+\*\*|__[^_\n]+__", text):
        before = text[max(0, m.start() - 2):m.start()]
        after = text[m.end():m.end() + 1]
        starts_line = m.start() == 0 or text[m.start() - 1] == "\n"
        ends_sentence = after in (":", "\n", "") or after in ".!?"
        if not (starts_line and ends_sentence):
            info["bold_mid_sentence"] += 1
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_\n]+)__", r"\1", text)
    text = re.sub(r"(?<!\w)[*_]([^*_\n]+)[*_](?!\w)", r"\1", text)
    return text, info


def paragraphs_of(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text)]
    return [p for p in paras if p and len(WORD.findall(p)) >= 3]


SENTENCE_BOUNDARY = re.compile(r"[.!?][\"'”’)\]]*\s+(?=[\"'“‘(\[]?[A-Z0-9])")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    pieces, start = [], 0
    for m in SENTENCE_BOUNDARY.finditer(text):
        pieces.append(text[start:m.end()].strip())
        start = m.end()
    pieces.append(text[start:].strip())
    out, buf = [], []
    for t in pieces:
        if not t:
            continue
        if buf:
            prev = buf[-1]
            core = prev.rstrip("\"'”’)]").rstrip(".!?")
            last_word = re.findall(r"[\w.]+$", core)
            lw = last_word[0].lower() if last_word else ""
            if lw in ABBREV or re.fullmatch(r"[A-Za-z]", lw) or re.fullmatch(r"\d+", lw):
                buf[-1] = prev + " " + t
                continue
        buf.append(t)
    for s in buf:
        if len(WORD.findall(s)) >= 1:
            out.append(s)
    return out


def syllables(word: str) -> int:
    w = word.lower().strip("'’-")
    if not w:
        return 0
    w = re.sub(r"e$", "", w) if len(w) > 3 and not w.endswith(("le", "ee", "ye", "oe")) else w
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def mattr(words: list[str], window: int = 100) -> float:
    if len(words) < window:
        return len(set(words)) / len(words) if words else 0.0
    ttrs = []
    counts = Counter(words[:window])
    ttrs.append(len(counts) / window)
    for i in range(window, len(words)):
        out_w, in_w = words[i - window], words[i]
        counts[out_w] -= 1
        if counts[out_w] == 0:
            del counts[out_w]
        counts[in_w] += 1
        ttrs.append(len(counts) / window)
    return sum(ttrs) / len(ttrs)


def mtld(words: list[str], threshold: float = 0.72) -> float:
    def run(seq):
        factors, types, tokens = 0.0, set(), 0
        for w in seq:
            tokens += 1
            types.add(w)
            if len(types) / tokens <= threshold:
                factors += 1
                types, tokens = set(), 0
        if tokens:
            ttr = len(types) / tokens
            factors += (1 - ttr) / (1 - threshold) if ttr > threshold else 1
        return len(seq) / factors if factors else float(len(seq))
    if len(words) < 50:
        return 0.0
    return (run(words) + run(list(reversed(words)))) / 2


def cv(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = statistics.mean(values)
    return statistics.pstdev(values) / m if m else 0.0


def burstiness(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m, s = statistics.mean(values), statistics.pstdev(values)
    return (s - m) / (s + m) if (s + m) else 0.0


def per_1k(count: float, words: int) -> float:
    return 1000.0 * count / words if words else 0.0


def find_lines(raw: str, pattern: re.Pattern, limit: int = 8) -> list[dict]:
    hits = []
    for i, line in enumerate(raw.split("\n"), 1):
        for m in pattern.finditer(line):
            hits.append({"line": i, "match": m.group(0)[:80], "context": line.strip()[:160]})
            if len(hits) >= limit:
                return hits
    return hits


def analyze_text(raw_text: str, context: str = "newsletter") -> dict:
    prose, md = strip_markdown(raw_text)
    paras = paragraphs_of(prose)
    sentences = []
    for p in paras:
        sentences.extend(split_sentences(p))
    words_raw = WORD.findall(prose)
    words = [w.lower() for w in words_raw]
    n_words = len(words)
    n_sent = len(sentences)
    sent_lens = [len(WORD.findall(s)) for s in sentences]
    para_lens = [len(WORD.findall(p)) for p in paras]
    m = {}
    m["word_count"] = n_words
    m["sentence_count"] = n_sent
    m["paragraph_count"] = len(paras)
    m["sentence_len_mean"] = statistics.mean(sent_lens) if sent_lens else 0.0
    m["sentence_len_sd"] = statistics.pstdev(sent_lens) if len(sent_lens) > 1 else 0.0
    m["sentence_len_cv"] = cv(sent_lens)
    m["burstiness"] = burstiness(sent_lens)
    m["sentence_len_min"] = min(sent_lens) if sent_lens else 0
    m["sentence_len_max"] = max(sent_lens) if sent_lens else 0
    m["short_sentence_share"] = (sum(1 for x in sent_lens if x < 8) / n_sent) if n_sent else 0.0
    m["long_sentence_share"] = (sum(1 for x in sent_lens if x > 30) / n_sent) if n_sent else 0.0
    if sent_lens:
        mu = m["sentence_len_mean"]
        m["uniform_sentence_share"] = sum(1 for x in sent_lens if abs(x - mu) <= 0.25 * mu) / n_sent
    else:
        m["uniform_sentence_share"] = 0.0
    m["paragraph_len_mean"] = statistics.mean(para_lens) if para_lens else 0.0
    m["paragraph_len_cv"] = cv(para_lens)
    m["sentences_per_paragraph"] = (n_sent / len(paras)) if paras else 0.0
    m["mattr_100"] = mattr(words, 100)
    m["mtld"] = mtld(words) if n_words >= 200 else None
    m["hapax_share"] = (sum(1 for _, c in Counter(words).items() if c == 1) / n_words) if n_words else 0.0
    m["avg_syllables_per_word"] = (sum(syllables(w) for w in words_raw) / n_words) if n_words else 0.0
    m["avg_word_length"] = (sum(len(w) for w in words_raw) / n_words) if n_words else 0.0
    if n_sent and n_words:
        m["flesch_reading_ease"] = 206.835 - 1.015 * (n_words / n_sent) - 84.6 * m["avg_syllables_per_word"]
    else:
        m["flesch_reading_ease"] = 0.0
    # Punctuation per 1k words
    m["em_dash_count"] = len(re.findall(r"—|(?<!-)--(?!-)", prose))
    m["em_dash_per_1k"] = per_1k(m["em_dash_count"], n_words)
    m["en_dash_per_1k"] = per_1k(prose.count("–"), n_words)
    m["semicolon_per_1k"] = per_1k(prose.count(";"), n_words)
    m["colon_per_1k"] = per_1k(len(re.findall(r":(?!\d)", prose)), n_words)
    m["question_per_1k"] = per_1k(prose.count("?"), n_words)
    m["exclamation_per_1k"] = per_1k(prose.count("!"), n_words)
    m["paren_per_1k"] = per_1k(prose.count("("), n_words)
    m["ellipsis_per_1k"] = per_1k(len(re.findall(r"\.\.\.|…", prose)), n_words)
    m["curly_quote_share"] = (len(re.findall(r"[“”‘’]", prose)) / max(1, len(re.findall(r"[\"'“”‘’]", prose))))
    # Voice markers
    m["contraction_per_1k"] = per_1k(len(re.findall(r"\b\w+(?:'|’)(?:t|s|re|ve|ll|d|m)\b", prose)), n_words)
    m["first_person_per_1k"] = per_1k(sum(1 for w in words if w.replace("’", "'") in FIRST_PERSON), n_words)
    m["second_person_per_1k"] = per_1k(sum(1 for w in words if w.replace("’", "'") in SECOND_PERSON), n_words)
    m["numeral_per_1k"] = per_1k(len(re.findall(r"\b\d[\d,.%]*\b", prose)), n_words)
    m["proper_noun_share"] = (sum(1 for i, w in enumerate(words_raw) if w[0].isupper() and i > 0 and not words_raw[i - 1].endswith((".", "!", "?"))) / n_words) if n_words else 0.0
    # Grammar-style markers (Reinhart et al. 2025)
    m["nominalization_count"] = len(NOMINAL_SUFFIX.findall(prose))
    m["nominalization_per_1k"] = per_1k(m["nominalization_count"], n_words)
    m["participial_clause_count"] = len(PARTICIPIAL_CLAUSE.findall(prose))
    m["participial_clause_per_1k"] = per_1k(m["participial_clause_count"], n_words)
    kicker_hits = [s for s in sentences if SENTENCE_FINAL_ING.search(s)]
    m["ing_kicker_count"] = len(kicker_hits)
    m["sentence_final_ing_kicker"] = per_1k(len(kicker_hits), n_words)
    # Openers
    openers = [WORD.findall(s)[0].lower() for s in sentences if WORD.findall(s)]
    oc = Counter(openers)
    m["opener_repeat_share"] = (oc.most_common(1)[0][1] / n_sent) if n_sent else 0.0
    m["opener_top"] = oc.most_common(5)
    m["transition_opener_share"] = (sum(1 for o in openers if o in TRANSITION_OPENERS) / n_sent) if n_sent else 0.0
    m["opener_types_share"] = (len(oc) / n_sent) if n_sent else 0.0
    # Staccato runs
    runs, run = 0, 0
    for x in sent_lens:
        if x < 6:
            run += 1
            if run == 3:
                runs += 1
        else:
            run = 0
    m["staccato_runs"] = runs
    # Lexicon
    lex_a = [w for w in words if w in LEXICON_A]
    lex_b_counts = Counter(w for w in words if w in LEXICON_B)
    # Tier B words are ordinary English; they count only when they pile up.
    lex_b_fired = {w: c for w, c in lex_b_counts.items() if c >= 2}
    m["ai_lexicon_hits"] = Counter(lex_a).most_common()
    m["ai_lexicon_b_hits"] = sorted(lex_b_fired.items(), key=lambda x: -x[1])
    m["ai_lexicon_count"] = len(lex_a) + sum(lex_b_fired.values())
    m["ai_lexicon_per_1k"] = per_1k(m["ai_lexicon_count"], n_words)
    phrase_hits = []
    for pat in PHRASES:
        rx = re.compile(pat, re.I)
        for h in find_lines(prose, rx, limit=4):
            h["pattern"] = pat
            phrase_hits.append(h)
    m["ai_phrase_hits"] = phrase_hits
    m["ai_phrase_count"] = len(phrase_hits)
    m["ai_phrase_per_1k"] = per_1k(len(phrase_hits), n_words)
    # Structural tells
    structural = []
    for label, rx in (("colon-reveal", COLON_REVEAL), ("tricolon", TRICOLON), ("rhetorical-q-answer", RHETORICAL_Q_ANSWER)):
        for h in find_lines(prose, rx, limit=6):
            h["tell"] = label
            structural.append(h)
    raw_lines = prose.split("\n")
    for s in kicker_hits[:6]:
        tail = s[-40:]
        line_no = next((i for i, l in enumerate(raw_lines, 1) if tail in l), None)
        structural.append({"tell": "ing-kicker", "match": s[-80:], "context": s[:160], "line": line_no})
    contrast = [h for h in phrase_hits if "it'?s" in h["pattern"] or "isn'?t" in h["pattern"] or "not (?:just" in h["pattern"]]
    for h in contrast:
        structural.append({"tell": "contrast-negation", "match": h["match"], "context": h["context"], "line": h.get("line")})
    m["structural_tells"] = structural
    m["structural_tells_count"] = len(structural) + m["staccato_runs"]
    m["structural_tells_per_1k"] = per_1k(m["structural_tells_count"], n_words)
    # Markdown structure
    m["headers"] = md["headers"]
    m["header_per_500w"] = (500.0 * md["headers"] / n_words) if n_words else 0.0
    m["bullets"] = md["bullets"]
    m["bullet_share"] = (md["bullets"] / md["lines_nonempty"]) if md["lines_nonempty"] else 0.0
    m["bold_spans"] = md["bold_spans"]
    m["bold_mid_sentence"] = md["bold_mid_sentence"]
    m["emoji_count"] = len(EMOJI.findall(prose))
    m["sentence_lengths"] = sent_lens
    m["context"] = context
    return m


# --------------------------------------------------------------------------
# Flagging
# --------------------------------------------------------------------------

CONTEXT_ADJUST = {
    # posts are short: rhythm stats are unreliable, lexicon still counts
    "post": {"skip": {"paragraph_len_cv", "mattr_100", "mtld", "header_per_500w", "bullet_share", "staccato_runs", "uniform_sentence_share"}},
    "article": {"skip": {"contraction_per_1k"}},
    "newsletter": {"skip": set()},
    "essay": {"skip": {"contraction_per_1k"}},
}


def flag_reference(m: dict) -> list[dict]:
    flags = []
    skip = CONTEXT_ADJUST.get(m.get("context", "newsletter"), {}).get("skip", set())
    if m["word_count"] < 120:
        skip = skip | {"sentence_len_cv", "burstiness", "paragraph_len_cv", "mattr_100", "mtld", "uniform_sentence_share", "opener_repeat_share"}
    for key, (lo, hi, direction, sev, note) in REFERENCE.items():
        if key in skip or key not in m or m[key] is None:
            continue
        v = m[key]
        if key in MIN_COUNT:
            count_key, min_n = MIN_COUNT[key]
            if m.get(count_key, 0) < min_n:
                continue
        bad = False
        if direction in ("low", "both") and lo is not None and v < lo:
            bad = True
        if direction in ("high", "both") and hi is not None and v > hi:
            bad = True
        if bad:
            flags.append({"metric": key, "value": round(v, 3) if isinstance(v, float) else v, "bound": [lo, hi], "severity": sev, "note": note})
    return flags


def metric_floor(key: str) -> float:
    """Smallest spread worth treating as real, so a zero-variance baseline cannot produce absurd z-scores."""
    if key.endswith("_per_1k"):
        return 2.0
    if key.endswith("_share"):
        return 0.04
    if key.endswith("_cv") or key == "burstiness":
        return 0.06
    if key in ("mattr_100",):
        return 0.02
    if key in ("flesch_reading_ease",):
        return 5.0
    if key in ("avg_syllables_per_word",):
        return 0.05
    if key.endswith("_mean"):
        return 2.0
    return 0.1


def flag_profile(m: dict, profile: dict) -> list[dict]:
    flags = []
    stats = profile.get("metrics", {})
    for key in PROFILE_KEYS:
        if key not in m or key not in stats or m[key] is None:
            continue
        mu, sd = stats[key]["mean"], stats[key]["sd"]
        v = m[key]
        floor = max(sd, abs(mu) * 0.15, metric_floor(key))
        z = (v - mu) / floor
        if abs(z) >= 2.0:
            sev = "high" if abs(z) >= 3 else "medium"
            direction = "above" if z > 0 else "below"
            flags.append({"metric": key, "value": round(v, 3), "author_mean": round(mu, 3), "author_sd": round(sd, 3), "z": round(z, 2), "severity": sev, "note": f"{key} is {direction} the author's usual range (z={z:.1f})."})
    # vocabulary drift: words the draft uses that the author never uses in samples, from the AI lexicon
    author_vocab = set(profile.get("vocabulary", {}).get("all_words", []))
    if author_vocab:
        foreign = [w for w, _ in m.get("ai_lexicon_hits", []) if w not in author_vocab]
        if foreign:
            flags.append({"metric": "vocabulary_foreign_to_author", "value": foreign[:12], "severity": "high", "note": "AI-lexicon words that never appear in the author's samples."})
    return flags


# --------------------------------------------------------------------------
# Windows: compare beginning / middle / end of a long piece. A human writer's
# windows differ from each other; windows that match to the second decimal are
# themselves a signal (see references/long-form-protocol.md, section 6).
# --------------------------------------------------------------------------

WINDOW_KEYS = ["sentence_len_mean", "sentence_len_cv", "mattr_100", "contraction_per_1k", "first_person_per_1k", "nominalization_per_1k", "flesch_reading_ease"]


def window_report(raw_text: str, n_windows: int = 3, context: str = "newsletter") -> dict | None:
    prose, _ = strip_markdown(raw_text)
    paras = paragraphs_of(prose)
    if sum(len(WORD.findall(p)) for p in paras) < 250 * n_windows:
        return None
    target = sum(len(WORD.findall(p)) for p in paras) / n_windows
    windows, cur, cur_n = [], [], 0
    for p in paras:
        cur.append(p)
        cur_n += len(WORD.findall(p))
        if cur_n >= target and len(windows) < n_windows - 1:
            windows.append("\n\n".join(cur))
            cur, cur_n = [], 0
    if cur:
        windows.append("\n\n".join(cur))
    rows = []
    for i, w in enumerate(windows, 1):
        m = analyze_text(w, context)
        rows.append({"window": i, "words": m["word_count"], **{k: m[k] for k in WINDOW_KEYS}})
    flags = []
    means = [r["sentence_len_mean"] for r in rows]
    cvs = [r["sentence_len_cv"] for r in rows]
    if max(means) - min(means) < 1.0 and max(cvs) - min(cvs) < 0.05:
        flags.append({"metric": "window_similarity", "severity": "medium", "note": "Beginning, middle and end have near-identical sentence rhythm (mean within 1 word, CV within 0.05). Human long-form drifts; this does not."})
    return {"rows": rows, "flags": flags}


# --------------------------------------------------------------------------
# Optional: avoid-ai-writing deterministic detector, if installed
# --------------------------------------------------------------------------

def run_avoid_ai_writing(path: str) -> dict | None:
    candidates = [
        os.environ.get("AVOID_AI_WRITING_CLI", ""),
        os.path.expanduser("~/.agents/skills/avoid-ai-writing/bin/avoid-ai-writing.js"),
        os.path.expanduser("~/.claude/skills/avoid-ai-writing/bin/avoid-ai-writing.js"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            try:
                out = subprocess.run(["node", c, "--source-mode", "rendered-markdown", "--", path], capture_output=True, text=True, timeout=60)
                if out.returncode == 0:
                    data = json.loads(out.stdout)
                    return {"score": data.get("score"), "label": data.get("label"), "issues": data.get("issues", [])[:40], "cli": c}
            except Exception as e:  # noqa: BLE001
                return {"error": str(e), "cli": c}
    return None


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def fmt(v):
    if isinstance(v, float):
        return f"{v:.3f}" if abs(v) < 10 else f"{v:.1f}"
    return str(v)


def text_report(m: dict, ref_flags: list[dict], prof_flags: list[dict], ext: dict | None, profile_name: str | None) -> str:
    lines = []
    lines.append(f"STYLOMETRY REPORT  ({m['word_count']} words, {m['sentence_count']} sentences, {m['paragraph_count']} paragraphs, context={m['context']})")
    lines.append("")
    lines.append("Rhythm")
    lines.append(f"  sentence length mean/sd/cv   {fmt(m['sentence_len_mean'])} / {fmt(m['sentence_len_sd'])} / {fmt(m['sentence_len_cv'])}   (min {m['sentence_len_min']}, max {m['sentence_len_max']})")
    lines.append(f"  burstiness                   {fmt(m['burstiness'])}      uniform-share {fmt(m['uniform_sentence_share'])}   short<8 {fmt(m['short_sentence_share'])}   long>30 {fmt(m['long_sentence_share'])}")
    lines.append(f"  paragraph words mean/cv      {fmt(m['paragraph_len_mean'])} / {fmt(m['paragraph_len_cv'])}   sentences/para {fmt(m['sentences_per_paragraph'])}")
    lines.append(f"  staccato runs                {m['staccato_runs']}")
    lines.append("Vocabulary")
    lines.append(f"  MATTR(100) / MTLD / hapax    {fmt(m['mattr_100'])} / {fmt(m['mtld']) if m['mtld'] is not None else 'n/a (<200w)'} / {fmt(m['hapax_share'])}")
    lines.append(f"  syllables/word, Flesch       {fmt(m['avg_syllables_per_word'])}, {fmt(m['flesch_reading_ease'])}")
    lines.append(f"  AI lexicon per 1k            {fmt(m['ai_lexicon_per_1k'])}   hits: {', '.join(f'{w}x{c}' for w, c in m['ai_lexicon_hits'][:10]) or 'none'}")
    if m["ai_lexicon_b_hits"]:
        lines.append(f"  AI lexicon (density tier)    {', '.join(f'{w}x{c}' for w, c in m['ai_lexicon_b_hits'][:10])}")
    lines.append(f"  AI phrases per 1k            {fmt(m['ai_phrase_per_1k'])}")
    lines.append("Grammar and structure")
    lines.append(f"  nominalizations /1k          {fmt(m['nominalization_per_1k'])}     participial clauses /1k {fmt(m['participial_clause_per_1k'])}     -ing kickers /1k {fmt(m['sentence_final_ing_kicker'])}")
    lines.append(f"  transition openers share     {fmt(m['transition_opener_share'])}     top opener share {fmt(m['opener_repeat_share'])}  {m['opener_top'][:3]}")
    lines.append(f"  structural tells /1k         {fmt(m['structural_tells_per_1k'])}")
    lines.append("Punctuation per 1k words")
    lines.append(f"  em-dash {fmt(m['em_dash_per_1k'])}  semicolon {fmt(m['semicolon_per_1k'])}  colon {fmt(m['colon_per_1k'])}  question {fmt(m['question_per_1k'])}  exclaim {fmt(m['exclamation_per_1k'])}  paren {fmt(m['paren_per_1k'])}  ellipsis {fmt(m['ellipsis_per_1k'])}")
    lines.append("Voice markers per 1k words")
    lines.append(f"  contractions {fmt(m['contraction_per_1k'])}  first-person {fmt(m['first_person_per_1k'])}  second-person {fmt(m['second_person_per_1k'])}  numerals {fmt(m['numeral_per_1k'])}")
    lines.append("Markdown")
    lines.append(f"  headers {m['headers']} ({fmt(m['header_per_500w'])}/500w)  bullets {m['bullets']} (share {fmt(m['bullet_share'])})  bold spans {m['bold_spans']} (mid-sentence {m['bold_mid_sentence']})  emoji {m['emoji_count']}")
    lines.append("")
    lines.append(f"FLAGS vs reference ranges: {len(ref_flags)}")
    for f in sorted(ref_flags, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]]):
        lines.append(f"  [{f['severity'].upper():6}] {f['metric']} = {f['value']}  (bound {f['bound']})  {f['note']}")
    if profile_name is not None:
        lines.append(f"FLAGS vs author profile '{profile_name}': {len(prof_flags)}")
        for f in prof_flags:
            lines.append(f"  [{f['severity'].upper():6}] {f['note']}  value={f['value']}" + (f" author={f['author_mean']}±{f['author_sd']}" if 'author_mean' in f else ""))
    lines.append("")
    if m["ai_phrase_hits"]:
        lines.append("Phrase evidence")
        for h in m["ai_phrase_hits"][:20]:
            lines.append(f"  L{h.get('line', '?')}: \"{h['match']}\"  <- {h['context']}")
    if m["structural_tells"]:
        lines.append("Structural evidence")
        for h in m["structural_tells"][:20]:
            lines.append(f"  [{h['tell']}] L{h.get('line', '?')}: \"{h['match']}\"")
    if ext:
        lines.append("")
        if "error" in ext:
            lines.append(f"avoid-ai-writing detector: error {ext['error']}")
        else:
            lines.append(f"avoid-ai-writing detector: score {ext['score']} ({ext['label']}), {len(ext['issues'])} issues")
            for i in ext["issues"][:15]:
                lines.append(f"  - {i.get('type')}: \"{i.get('text')}\" -> {i.get('suggestion', '')}")
    lines.append("")
    lines.append("Reading: flags are prompts to look at the evidence lines, not a verdict on who wrote this.")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Profile
# --------------------------------------------------------------------------

def build_profile(paths: list[str], name: str | None) -> dict:
    per_file = []
    all_words = Counter()
    openers = Counter()
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            raw = fh.read()
        m = analyze_text(raw, "newsletter")
        if m["word_count"] < 150:
            print(f"warning: {p} has only {m['word_count']} words; profile stats are noisy under ~300", file=sys.stderr)
        per_file.append({"file": p, "metrics": {k: m[k] for k in PROFILE_KEYS if k in m}})
        prose, _ = strip_markdown(raw)
        all_words.update(w.lower() for w in WORD.findall(prose))
        for w, c in m["opener_top"]:
            openers[w] += c
    metrics = {}
    for k in PROFILE_KEYS:
        vals = [f["metrics"][k] for f in per_file if k in f["metrics"]]
        if not vals:
            continue
        metrics[k] = {"mean": statistics.mean(vals), "sd": statistics.pstdev(vals) if len(vals) > 1 else 0.0, "min": min(vals), "max": max(vals)}
    total = sum(all_words.values())
    stop = {"the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "is", "it", "that", "this", "as", "by", "be", "are", "was", "were", "from", "i", "you", "we", "they", "he", "she", "my", "your", "our", "their", "not", "have", "has", "had", "do", "does", "did", "so", "if", "about", "what", "which", "when", "who", "how", "all", "can", "will", "just", "more", "one", "out", "up", "like", "than", "then", "there", "them", "into", "its", "it's", "i'm", "me", "no", "yes", "some", "any", "also", "been", "would", "could", "should", "because", "very", "get", "got", "much", "even", "only", "over", "here", "where", "these", "those", "his", "her", "him", "us", "an", "am", "s", "t"}
    favorites = [(w, c) for w, c in all_words.most_common(400) if w not in stop and len(w) > 2][:60]
    return {
        "name": name or "author",
        "samples": [f["file"] for f in per_file],
        "sample_words_total": total,
        "metrics": metrics,
        "vocabulary": {
            "all_words": sorted(w for w, c in all_words.items() if c >= 1),
            "favorites": favorites,
            "ai_lexicon_used": [w for w in all_words if w in LEXICON_A],
            "common_openers": openers.most_common(10),
        },
        "note": "Generated by stylometry.py profile. Pair with the qualitative voice profile written by the voice-profile skill.",
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def load_profile(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_analyze(a) -> int:
    try:
        with open(a.file, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    m = analyze_text(raw, a.context)
    ref_flags = flag_reference(m)
    prof_flags, pname = [], None
    if a.profile:
        prof = load_profile(a.profile)
        pname = prof.get("name", "author")
        prof_flags = flag_profile(m, prof)
    ext = run_avoid_ai_writing(a.file) if a.with_avoid_ai_writing else None
    win = window_report(raw, a.windows, a.context) if a.windows else None
    if a.format == "json":
        out = {k: v for k, v in m.items() if k != "sentence_lengths"}
        out["reference_flags"] = ref_flags
        out["profile_flags"] = prof_flags
        out["profile_name"] = pname
        out["avoid_ai_writing"] = ext
        out["windows"] = win
        print(json.dumps(out, indent=2, default=list))
    else:
        print(text_report(m, ref_flags, prof_flags, ext, pname))
        if win:
            print()
            print(f"Windows ({len(win['rows'])}):  words  sent-mean  sent-cv  mattr  contr/1k  1st-person/1k  nominal/1k  flesch")
            for r in win["rows"]:
                print(f"  w{r['window']}            {r['words']:5d}  {r['sentence_len_mean']:9.1f}  {r['sentence_len_cv']:7.3f}  {r['mattr_100']:5.3f}  {r['contraction_per_1k']:8.1f}  {r['first_person_per_1k']:13.1f}  {r['nominalization_per_1k']:10.1f}  {r['flesch_reading_ease']:6.1f}")
            for f in win["flags"]:
                print(f"  [{f['severity'].upper():6}] {f['note']}")
        elif a.windows:
            print("\nWindows: piece too short for window comparison (needs ~250 words per window).")
    high = any(f["severity"] == "high" for f in ref_flags + prof_flags)
    return 1 if high else 0


def cmd_profile(a) -> int:
    if len(a.samples) < 1:
        print("error: need at least one sample (3+ recommended)", file=sys.stderr)
        return 2
    prof = build_profile(a.samples, a.name)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(prof, fh, indent=2)
    print(f"wrote {a.out}: {len(prof['samples'])} samples, {prof['sample_words_total']} words")
    for k in ("sentence_len_mean", "sentence_len_cv", "burstiness", "contraction_per_1k", "first_person_per_1k", "em_dash_per_1k", "mattr_100"):
        if k in prof["metrics"]:
            s = prof["metrics"][k]
            print(f"  {k:24} {s['mean']:.3f} ± {s['sd']:.3f}")
    return 0


def cmd_compare(a) -> int:
    with open(a.file, encoding="utf-8") as fh:
        raw = fh.read()
    prof = load_profile(a.profile)
    m = analyze_text(raw, a.context)
    flags = flag_profile(m, prof)
    print(f"Drift from profile '{prof.get('name')}': {len(flags)} flags")
    for f in flags:
        print(f"  [{f['severity'].upper():6}] {f['note']}  value={f['value']}" + (f" author={f['author_mean']}±{f['author_sd']}" if 'author_mean' in f else ""))
    return 1 if any(f["severity"] == "high" for f in flags) else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("analyze")
    pa.add_argument("file")
    pa.add_argument("--profile")
    pa.add_argument("--format", choices=["text", "json"], default="text")
    pa.add_argument("--context", choices=list(CONTEXT_ADJUST), default="newsletter")
    pa.add_argument("--with-avoid-ai-writing", action="store_true", help="also run the avoid-ai-writing pattern detector if installed")
    pa.add_argument("--windows", type=int, nargs="?", const=3, default=0, help="compare N windows (default 3) across a long piece")
    pa.set_defaults(fn=cmd_analyze)
    pp = sub.add_parser("profile")
    pp.add_argument("samples", nargs="+")
    pp.add_argument("--out", required=True)
    pp.add_argument("--name")
    pp.set_defaults(fn=cmd_profile)
    pc = sub.add_parser("compare")
    pc.add_argument("file")
    pc.add_argument("--profile", required=True)
    pc.add_argument("--context", choices=list(CONTEXT_ADJUST), default="newsletter")
    pc.set_defaults(fn=cmd_compare)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
