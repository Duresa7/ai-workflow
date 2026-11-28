# Lessons

What went wrong or surprisingly right, with the numbers, and the rule each incident produced. Dates are when the owner made the rule.

## Writers

- **Sonnet 5.5 and Gemini 4 Argon stopped writing code (2026-11-23).** In the first routing study (510 sessions, 80 PRs) Sonnet passed 1 of 6 first reviews and needed 4 to 6 rounds; Argon passed 0 of 2 and needed 7. Sonnet shipped a licence check that let unknown files through and races in the launcher that hands out engine Editors, and each time it patched only the exact line the reviewer named.
- **Neon stopped writing, then came back on a short leash (2026-11-23, 2026-11-24).** Its PRs had real bugs: a broken default build, a Windows build that didn't compile, a runner that couldn't start on a fresh install, and a test gate that could never fail. It returned only for work with a plan that spells out every build, test and threading step, with Opus taking over if it struggles. In the current data it passes round 1 on 2 of 10 tasks but lands cleanly once reviewed (9 of 11 first-time landing CI).
- **`medium` beat `high` for Opus (2026-11-23).** Opus 5.5 passed 6 of 11 first reviews at `medium` and 4 of 12 at `high`. Harder work got `high`, but no task class showed a gain from it, so `medium` became the default.
- **GPT-6.2 Astra and Sol earned well-defined work (2026-11-24).** On comment clean-ups and quick-fix batches they passed 9 of 10 and 6 of 8 first reviews, and nothing filed since points at a bug they shipped. Open-ended work and rendering stayed with Opus.
- **Physics moved to Astra (2026-11-25), and Astra was then held to mathematics only (2026-11-26)** to save its usage. Fable's two physics FAILs in the second study were real bugs: an object that couldn't be grabbed could block a valid grab, and a cut along a texture seam left stale IDs that a later cut could reuse.
- **A plan lets a cheaper writer do the work (2026-11-24).** Planned tasks go to the cheapest writer that fits. After the first wave, plans were limited to design work and kept short: decisions, acceptance bounds and stop rules, not guessed code steps.

## Reviewers

- **Sol at `high` caught no more than at `medium`** (first study), so reviews run at `medium`, and fix-only re-checks at `low`.
- **Sol's later rounds drifted to rare edge cases.** Its round-1 blockers were nearly all real; later rounds raised syntax corner cases. Two rules followed: round 1 lists everything and later rounds check only the fixes (2026-11-23), and every blocker names the normal-path input that triggers it (2026-11-24). An Opus `xhigh` audit of one such PR found that both FAIL rounds were on rare cases, cut the fix down, and the next round passed.
- **Neon passed a PR with a 13° shading seam (2026-11-24).** GPT-6.2 Sol found it at the council. Since then, an Astra PR touching physics or looks also gets an Opus review, and a PR whose reviewer missed something moves up a tier.
- **One reviewer per round, by tier (2026-11-25).** "Both must pass" pairings cost two reviews per round for little gain. The tiers (Neon, then GPT, then Opus, never the writer's family) replaced them, with Neon plus Astra as the one allowed pair.

## Council

- **Three rounds in one evening all failed on gaps one reviewer could have caught (2026-11-25).** Reference footage that showed tissue instead of the smoke effect it was meant to prove, a "before" picture that didn't isolate the change, and design contracts with uncovered cases. Pre-council checks followed: a cheap visual pass on look PRs and a cross-family contract read on designs.
- **A council seat whose model is out of usage is reported, not silently swapped (2026-11-23).** The owner names the replacement when present; otherwise the seat's listed stand-in runs and the owner is told.

## CI and machines

- **Seven lanes building the engine at once pushed the lint job past its timeout on 10 of 25 CI runs (2026-11-25).** Main turned red and every landing stopped. The cap went to about 6 building lanes, then to 1, then to 2 (2026-11-27), and is now 4 on trial with CI times recorded.
- **CI moved to once per PR, at landing (2026-11-25),** on one 32 GB Windows PC, with a local pre-push check on every push. Landing CI now passes first time on 44 of 49 runs.
- **A coding agent running git through a Linux compatibility layer rewrote the main clone's worktree setting (2026-11-23)** and broke every git command in it. Agents of that harness were restricted to read-only git on that PC until each got its own worktree.
- **The Linux CI runner crashed under load,** and the Linux PC was taken out of service (2026-11-25). The project plans as if it won't return.
- **Videos on every PR held up every other engine job (2026-11-27).** Recording runs alone, so PRs now carry pictures and videos are kept for milestone demos.

## Usage

- **Fast and priority tiers burn usage faster (2026-11-23).** They are off everywhere except on two accounts where the owner allowed them.
- **Usage limits are a routing event, not an error.** When an account hits its limit, the lane moves to the same row's other model, then the same model on another account, and resumes from its notes file. Only 1 limit hit is recorded in the data so far: the count is filled in only when a launch report establishes it, so treat the column as a lower bound.

## Case study: the 2026-11-28 swarm

**Setup.** Three feature clusters of the simulator's game layer (scoring, guidance and coaching) were each given to one lead: Opus 5.5 at `high` in Claude Code. Each lead wrote and froze the interfaces first (headers, a design annex, a calibration note), then cut the work into slices and handed each slice to a worker: Gemini 4 Hydrogen at `high` in Antigravity, or SWE-2.1 in Devin. There was no planner, no per-slice PR and no separate reviewer: the lead read each slice's diff, fixed what was wrong, and merged it into the cluster branch, which then goes through the normal pipeline as one PR.

**Slices finished by midday:**

| Cluster | Slice | Worker | Effort | Minutes | Lines added | Fixes the lead made |
|---|---|---|---|---|---|---|
| coaching | debouncer and its tests | Hydrogen | high | 4 | 500 | none (one redundant line left as a nit) |
| coaching | golden-checklist test | Hydrogen | high | 6 | 313 | none |
| guidance | branch content and score table | Hydrogen | high | 2 | 115 | none |
| guidance | hint-ladder logic and tests | Hydrogen | high | 3 | 378 | none |
| guidance | step guidance text for 27 steps | Hydrogen | high | 4 | 311 | none |
| guidance | unachievable-branch tests | Hydrogen | high | 6 | 495 | one line (a numeric cast) |
| guidance | camera assistant handover tests | Hydrogen | high | 9 | 351 | rewrote one test (about 30 lines) that assumed the wrong reset state |
| guidance | camera assistant policy tests (38) | Hydrogen | high | 14 | 1908 | none; two tests partial for sound reasons |
| scoring | core invariant and tests | Hydrogen | high | about 10 | 100 | none |
| scoring | tier-0 replay score | Hydrogen | high | about 15 | 613 | none |
| scoring | scoring test port (28 methods) | Hydrogen | high | about 20 | 876 | none |
| guidance | camera assistant driver and obstacle adapter | SWE-2.1 | high | 22 | 154 | none |

**What it shows so far.**

- Hydrogen finished 11 of 11 slices, at a median of 6 minutes, adding about 6,000 lines; 9 of the 11 needed no fix. Its two fixes were small and both were wrong assumptions about state the interface left implicit.
- The one SWE-2.1 slice took 22 minutes and needed no fix.
- This is the opposite of Hydrogen's long-horizon results (47.8% on an independent multi-hour benchmark, [external.md](external.md)) and of the project's rule that Hydrogen writes no production code. The difference is the frozen interface: each slice was small, fully specified and checkable by its own tests.
- The cost moved to the leads, who wrote the interfaces and read every diff. Their time is not yet in the table.

**End-of-day result.**

> **Placeholder, to be filled after the clusters land:** each cluster PR's review rounds, landing CI result and council outcome; the leads' own minutes and tokens; the full slice table from every cluster; and whether any slice's code was found wrong after it merged.
