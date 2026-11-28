# The workflow the agents worked in

One human owner, one lead agent, and many short-lived agents. The owner sets priorities and keeps a few decisions for themselves (starting the port, the sales model). Everything else runs without waiting on them.

## Roles

| Role | Who | Does |
|---|---|---|
| Chief of staff | One lead session (Claude Code) | Plans, writes briefs, starts every other agent, shares out the scarce resources, settles conflicts, runs councils, lands work, reports to the owner. |
| Planner | Opus 5.5 at `high` | Writes short plans for design work that has none: the decisions, the acceptance bounds and the stop rules, not code steps. Writes no code. |
| Fixer | Opus 5.5 at `medium` | Answers a writer's stop with a plan amendment, so stops don't queue behind new plans. |
| Task owner and writer | One thread per task | Owns the task from brief to merge: writes, self-verifies, opens the PR, answers reviews. |
| Reviewer | A model from another family | Reviews a PR it didn't write. |
| Council | Three seats from three families | Judges look changes and hard-to-reverse decisions. |

## The pipeline

1. **Plan.** Work that needs a decision gets a short plan on its issue: the files to change, ordered steps, tests that can fail with pass bounds, the pictures, the review route, and the conditions under which the writer must stop and report. Well-defined work goes straight from the issue to a writer. Opus writers and the mathematics writer plan their own work and post the plan before writing code.
2. **Write.** Each task runs in its own git worktree. The writer follows the plan; it may correct a plan's test setup or tolerance only when it can cite the source (a code line, a calibration note, a design record), and it lists each correction for the reviewer. Before review it reads its own diff against the coding standards and the review checklist, and runs the local pre-push check: the build, the headless tests and the lint. The check result goes on the PR.
3. **Review.** One reviewer per round, from a different model family than the writer (below). Round 1 lists every finding. Later rounds check only the fixes. Only blockers go back to the writer, and each blocker must name the normal-path input that triggers it; everything else becomes one follow-up checklist issue. A fix of at most 10 lines with no new files is checked by the task owner instead of another round. After two FAILs, an Opus 5.5 `xhigh` audit reads the whole PR and its history and names the root cause before round 3. After a third FAIL the task stops for a decision.
4. **Council.** Every change to how the simulator looks is judged side by side with real laparoscopic footage, and every hard-to-reverse decision (the solver, public interfaces, data formats) is argued, by three seats: Gemini 4 Neon, Opus 5.5 and GPT-6.2 Sol. All three must vote SHIP. Before a look PR sits, a cheap visual pass checks that every claim has a picture showing it; before a design sits, a reviewer from another family reads it for contract gaps.
5. **Land.** A landing script is the only way to merge. It requires CI green against the current main, a review record for the reviewed commit, and untouched protected paths. CI runs once per PR, at landing, which makes it the merge queue; several ready PRs are tested together as a train.

## Tiered review

| Tier | Reviewer | Used for |
|---|---|---|
| 1 | Gemini 4 Neon | The first reviewer when the writer isn't Neon. |
| 2 | GPT-6.2 Astra or Sol | Reviews of Neon's work; Claude-written work. |
| 3 | Opus 5.5 | GPT-written work after Neon; the top tier. |

- A model never reviews work from its own family: GPT-written work goes Neon, then Opus; Neon-written work goes Astra, then Opus.
- Neon and Astra review together, at the same time, on CI, security-sensitive and physics work that neither wrote.
- A PR moves up a tier when something its reviewer passed is caught later (at landing, at the council, or as a later bug), and the next PRs of that kind start at the higher tier.
- Re-checks of fixes run at `low` effort.

## Caps and shared limits

- **Writers per subscription account:** 3 or 4 at once, depending on the account. Reviewers, the planner and the lead don't count.
- **The most capable model** (Fable 5.2) runs at most 2 sessions at once, only for work that needs it (3D modelling), and only after the owner says yes.
- **Unreal Engine builds:** at most two agent Editors per PC, and a small number of lanes building or running the engine at once (6, then 1, then 2, now 4 on trial). More lanes only queue.
- **CI speed budget:** a PR's CI result in 3 minutes typical and 6 minutes on a bad day. No retries: a check that fails at random is a bug to fix, never re-run until green.
- **Effort:** default `medium`; `low` for simple, well-scoped work; `high` for complex or ambiguous work; `xhigh` only when `high` isn't enough; `max` never, except for experiments. Raise effort only when a failure shows too little reasoning, not missing information.
- **No fast or priority tiers,** except on two accounts where the owner allowed them: they burn usage faster.

## Who writes what (end of 2026-11-28)

| Work | Writer |
|---|---|
| Mathematics and physics (solver, constraints, contact, tearing) | GPT-6.2 Astra |
| Rendering, realism, complex features, UI design (`high`), debugging | Opus 5.5 at `medium` |
| Tools, CI, routine C++, clean-ups, quick fixes | GPT-6.2 Sol, or SWE-2.1 during its free trial (`max`) |
| Work not yet started, from a plan | Gemini 4 Neon at `high` or SWE-2.1 |
| 3D modelling, geometry, bakes | Fable 5.2 |
| Research, searches, documentation, log triage | Gemini 4 Hydrogen at `high`, with its claims checked |

Sonnet 5.5 and Gemini 4 Argon write no code. Hydrogen is never the only code reviewer or a judge of physics or looks. [lessons.md](lessons.md) gives the incident behind each rule.
