# conorbronsdon

## [avoid-ai-writing](./avoid-ai-writing/SKILL.md)

Audit and rewrite content to remove AI writing patterns ("AI-isms"). Calibrated for English.

**Three modes:**

- **Rewrite** (default) — flags AI patterns, applies up to two editing passes, verifies the result when possible, and returns one final version.
- **Detect** — flags AI patterns without rewriting. Shows which flags are real problems vs. judgment calls. Useful when patterns might be intentional, when auditing content you don't want altered, or when you just want a quick scan.
- **Edit** — edits a prose file in place (via the Edit tool) with minimal, targeted changes, preserving passages that are already human. Source code, configuration, and generated data are refused because prose rewrites can corrupt structured content. Returns an edits-made + verification report, not the full file.

Use `--iterate 1|2` to set the editing-pass ceiling (`--iterate 1` allows the initial rewrite only; `--iterate 2` is the default maximum of an initial rewrite plus one correction or preservation repair). An optional **voice profile** (`casual` / `professional` / `technical` / `warm` / `blunt`) sets how the prose should sound, independent of the audience context profile.

### Triggering the skill

Ask your assistant to clean up AI writing:

- "Remove AI-isms from this post"
- "Audit this draft for AI tells"
- "Make this sound less like AI"
- "Clean up AI writing in this paragraph"

In **rewrite mode** (default), the skill returns:

1. **Final rewrite** — the verified or honestly qualified final version
2. **Changes** — a short summary when edits were made and the summary is useful
3. **Verification** — editing passes used, checks that ran, stop reason, and any intentional, protected, source-blocked, or unresolved findings

Ask for a detailed or exhaustive audit to add quoted findings before the final rewrite.

In **detect mode**, the skill returns:

1. **Issues found** — every AI-ism identified, grouped by severity (`P0`/`P1`/`P2`)
2. **Assessment** — which flags are clear problems vs. patterns that may be intentional or effective in context

Trigger detect mode with: "detect," "flag only," "audit only," "just flag," "scan," or similar.
