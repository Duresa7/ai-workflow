#!/usr/bin/env python3
"""Tests for stylometry.py. Run: python3 -I test_stylometry.py"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stylometry as s  # noqa: E402

AI_TEXT = """# The Future of Remote Work: Navigating a New Landscape

In today's rapidly evolving world, remote work has become more than just a trend. It's a fundamental shift in how we approach productivity, collaboration, and work-life balance. As organizations navigate the complexities of this new landscape, it's important to note that the benefits extend far beyond convenience.

Remote work isn't just about working from home. It's about reimagining what work can be. Companies that embrace this paradigm shift are discovering that flexibility fosters innovation, enhances employee satisfaction, and drives meaningful results. Moreover, the ability to tap into a global talent pool serves as a testament to the transformative power of distributed teams.

However, this transition is not without its challenges. Leaders must leverage robust communication tools, foster a culture of trust, and ensure that every team member feels connected. Additionally, maintaining a healthy boundary between professional and personal life is crucial for long-term success.

Furthermore, organizations that prioritize employee well-being are seeing remarkable outcomes. By implementing comprehensive wellness programs, companies can unlock the full potential of their workforce, highlighting the importance of a holistic approach.

In conclusion, remote work represents a pivotal moment in the evolution of the modern workplace. Whether you're a seasoned executive or an emerging leader, embracing this change is essential. Ultimately, those who adapt will thrive in this dynamic, ever-evolving environment.
"""

HUMAN_TEXT = """I spent most of Tuesday trying to get a 2014 Thinkpad to boot off a USB stick, which is not what I had planned for Tuesday.

The plan was to write this issue. Instead I was on my knees in the hallway closet, because that's where the one working USB-A hub lives, swapping cables and muttering. My wife walked past twice. The second time she asked if the newsletter was "going well" and I said yes, which was a lie, but a small one.

Here's what happened. A reader (hi, Marcus) emailed last week asking whether I'd ever tried running the little note-taking tool I keep recommending on genuinely old hardware. Not old like "my 2021 MacBook feels slow." Old like a machine you'd find in a school district's e-waste pile. Fair question. I'd been telling people it was lightweight for two years and I had never actually checked.

So I checked. It took about nine hours, if you count the USB stuff, which I do.

Short version: it runs. It runs fine, actually. Startup is maybe four seconds on a spinning disk, and search over 3,000 notes comes back in under a second once the index warms up. The one thing that choked was the PDF preview, which I expected, and the one thing that surprised me was that sync didn't choke at all. I had assumed sync would be the problem. It wasn't.

I don't have a big lesson from this. Maybe a small one: I should test the claims I repeat.

If you've got an old machine in a closet somewhere and want to try this yourself, reply and tell me what you've got. I'll send the stick image. It's 1.9 GB and it works, eventually, even if your BIOS is labeled wrong.
"""


class SentenceSplitting(unittest.TestCase):
    def test_abbreviations_do_not_split(self):
        out = s.split_sentences("Dr. Smith arrived at 3 p.m. on Tuesday. She left early.")
        self.assertEqual(len(out), 2)

    def test_quotes_and_parens(self):
        out = s.split_sentences('He said "no." Then he left. (It was late.) Fine.')
        self.assertEqual(len(out), 4)

    def test_numbers_do_not_split(self):
        out = s.split_sentences("It cost 3.5 million. That is a lot.")
        self.assertEqual(len(out), 2)


class Markdown(unittest.TestCase):
    def test_strip_counts(self):
        text = "---\ntitle: x\n---\n# Head\n\n- one\n- two\n\nSome **bold** text here. And `code`.\n\n```\nprint(1)\n```\n[link](http://x.y) end.\n"
        prose, info = s.strip_markdown(text)
        self.assertEqual(info["headers"], 1)
        self.assertEqual(info["bullets"], 2)
        self.assertEqual(info["code_blocks"], 1)
        self.assertEqual(info["links"], 1)
        self.assertEqual(info["bold_mid_sentence"], 1)
        self.assertNotIn("print(1)", prose)
        self.assertNotIn("title: x", prose)
        self.assertIn("link end", prose)


class Metrics(unittest.TestCase):
    def test_mattr_bounds(self):
        words = ["a", "b", "c", "d"] * 50
        self.assertLess(s.mattr(words, 100), 0.1)
        words = [f"w{i}" for i in range(200)]
        self.assertAlmostEqual(s.mattr(words, 100), 1.0)

    def test_burstiness_sign(self):
        self.assertLess(s.burstiness([10, 10, 10, 10]), -0.9)
        self.assertGreater(s.burstiness([2, 30, 3, 28, 1, 25]), -0.3)

    def test_cv(self):
        self.assertEqual(s.cv([5, 5, 5]), 0.0)
        self.assertGreater(s.cv([1, 10]), 0.5)

    def test_syllables(self):
        self.assertEqual(s.syllables("cat"), 1)
        self.assertEqual(s.syllables("table"), 2)
        self.assertGreaterEqual(s.syllables("organization"), 4)


class Separation(unittest.TestCase):
    def setUp(self):
        self.ai = s.analyze_text(AI_TEXT, "newsletter")
        self.hu = s.analyze_text(HUMAN_TEXT, "newsletter")

    def test_lexicon_separates(self):
        self.assertGreater(self.ai["ai_lexicon_per_1k"], 20)
        self.assertEqual(self.hu["ai_lexicon_per_1k"], 0)

    def test_phrases_separate(self):
        self.assertGreater(self.ai["ai_phrase_per_1k"], 10)
        self.assertEqual(self.hu["ai_phrase_count"], 0)

    def test_rhythm_separates(self):
        self.assertLess(self.ai["sentence_len_cv"], self.hu["sentence_len_cv"])
        self.assertLess(self.ai["burstiness"], self.hu["burstiness"])

    def test_grammar_markers_separate(self):
        self.assertGreater(self.ai["nominalization_per_1k"], self.hu["nominalization_per_1k"] * 5)
        self.assertGreater(self.ai["transition_opener_share"], self.hu["transition_opener_share"])

    def test_flags(self):
        ai_flags = s.flag_reference(self.ai)
        hu_flags = s.flag_reference(self.hu)
        self.assertTrue(any(f["severity"] == "high" for f in ai_flags))
        self.assertFalse(any(f["severity"] == "high" for f in hu_flags), [f["metric"] for f in hu_flags])

    def test_min_count_guard(self):
        # one colon reveal in a short human piece must not produce a HIGH structural flag
        flags = [f for f in s.flag_reference(self.hu) if f["metric"] == "structural_tells_per_1k"]
        self.assertEqual(flags, [])

    def test_short_text_skips_rhythm(self):
        m = s.analyze_text("Short. Very short. Three words here. Done now.", "newsletter")
        flags = s.flag_reference(m)
        self.assertFalse(any(f["metric"] in ("sentence_len_cv", "burstiness", "mattr_100") for f in flags))
        self.assertIsNone(m["mtld"])


class Profile(unittest.TestCase):
    def test_profile_roundtrip_and_drift(self):
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for i, t in enumerate((HUMAN_TEXT, HUMAN_TEXT.replace("Tuesday", "Friday"), HUMAN_TEXT.replace("I", "we"))):
                p = os.path.join(d, f"s{i}.md")
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(t)
                paths.append(p)
            prof = s.build_profile(paths, "T")
            self.assertEqual(prof["name"], "T")
            self.assertIn("sentence_len_cv", prof["metrics"])
            ai = s.analyze_text(AI_TEXT, "newsletter")
            drift = s.flag_profile(ai, prof)
            self.assertTrue(any(f["severity"] == "high" for f in drift))
            self.assertTrue(any(f["metric"] == "vocabulary_foreign_to_author" for f in drift))
            for f in drift:
                if "z" in f:
                    self.assertLess(abs(f["z"]), 100, f)  # floors keep z sane on zero-variance baselines
            same = s.flag_profile(s.analyze_text(HUMAN_TEXT, "newsletter"), prof)
            self.assertFalse(any(f["severity"] == "high" for f in same), same)


class Windows(unittest.TestCase):
    def test_windows_on_long_text(self):
        long = "\n\n".join([HUMAN_TEXT, HUMAN_TEXT, HUMAN_TEXT, HUMAN_TEXT])
        w = s.window_report(long, 3)
        self.assertIsNotNone(w)
        self.assertEqual(len(w["rows"]), 3)
        # identical repeated text produces near-identical windows -> similarity flag fires
        self.assertTrue(any(f["metric"] == "window_similarity" for f in w["flags"]))

    def test_windows_short_returns_none(self):
        self.assertIsNone(s.window_report(HUMAN_TEXT, 3))


class CLI(unittest.TestCase):
    def test_json_output_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "ai.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(AI_TEXT)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = s.main(["analyze", p, "--format", "json"])
            self.assertEqual(code, 1)
            data = json.loads(buf.getvalue())
            self.assertIn("reference_flags", data)
            h = os.path.join(d, "h.md")
            with open(h, "w", encoding="utf-8") as fh:
                fh.write(HUMAN_TEXT)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = s.main(["analyze", h])
            self.assertEqual(code, 0)
            self.assertIn("STYLOMETRY REPORT", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
