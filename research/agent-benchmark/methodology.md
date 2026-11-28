# Methodology

## The project

BuildMed is porting a laparoscopic surgery simulator (gallbladder and appendix removal) from Unity to Unreal Engine 5. The port started on 2026-11-21. One human owner sets priorities and makes the reserved decisions. A lead agent (the chief of staff) plans, writes briefs, starts every other agent, and lands the work. Nearly all code, tests, assets, reviews and documents are written by agents. [workflow.md](workflow.md) describes the pipeline.

## What counts as a run

A run is one agent session with one job: a writer, a reviewer, a council seat, a planner, a fixer, a researcher or an auditor. Each run records:

| Field | Meaning |
|---|---|
| `run` | Sequence number in this export. Not stable across exports. |
| `day` | UTC date the run started. |
| `task` | An opaque label (`T001`, …) shared by every run on the same piece of work, so a writer and its reviewers group together. |
| `role` | writer, reviewer, council seat, planner, fixer, researcher, auditor. |
| `model`, `effort` | The model and the reasoning effort the run was started with. |
| `harness` | The app that ran the model: Claude Code, Codex, Antigravity, Devin or OpenCode. |
| `task_type` | physics, rendering, routine or complex Unreal C++, CI/tools, tests, UI/UX, 3D, materials, asset pipeline, debugging, research. |
| `tier`, `seat`, `round` | A reviewer's tier, a council seat, and the review or council round. |
| `evidence` | `live` (a recorded agent session), `study` (one of the project's two hand-checked routing studies) or `github` (a review record or council ruling posted on a pull request). |
| `outcome` | How the session ended (completed, failed, interrupted, cancelled) or the verdict it gave (pass, fail, SHIP, NOT YET). |
| `minutes`, `tokens`, `usage_limit_hits` | Wall-clock length, summed per-turn input and output tokens as the harness reported them, and how often the run hit a usage limit. |
| `measures` | Role-specific outcomes, below. |

`data/landings.jsonl` holds one row per landing CI run: day, result, minutes, queue minutes, and how many PRs were tested together.

## Outcome measures

**Writers.** The writer's work is joined to its pull request. A run that named its PR at launch uses it. Otherwise it takes the earliest PR that closes the run's issue, was still open when the run started, and opened within 48 hours of the run ending, unless a writer on a different model took over the same issue before that PR opened. From the PR:

- `rounds_to_pass`: the number of distinct review verdicts up to and including the first pass. Repeated postings of the same verdict on the same commit count once.
- `third_fail_stop`: three or more FAILs before any pass, which stops the PR for a decision.
- `landed`: the PR merged. Open PRs are unknown.
- `landing_ci_first_pass`: the first CI run at landing that tested this PR passed.
- `real_stops`, `wasted_stops`: stops the writer raised against its plan, and whether the stop was needed.

**Reviewers.** The verdict, plus, when assessed later, `miss` (it passed work in which a defect was later found), `blockers` and `false_blockers` (blockers that were not real).

**Council seats.** The vote (SHIP or NOT YET), `matched_ruling` (the vote matched the council's final ruling) and `ship_overturned` (a SHIP later shown to be wrong).

**Researchers, planners and fixers.** `claims_checked` and `claims_failed` for researchers; `stops_caused` for planners and fixers.

Every measure is null unless it was observed. Rates use only known values in both numerator and denominator.

## Counting

The tables count **tasks, not sessions,** for writer outcomes: several sessions on one PR share its outcome, so a model that needed eight sessions for one PR counts once in the rates and eight times in `runs`. Session counts, minutes, tokens and limit hits are per run. A cell with fewer than 5 runs is marked † and should be read as an anecdote. The project's own rule is not to change routing on fewer than 5 observations.

## Known biases

- **Selection.** Only work that reached a pull request gets a landing outcome. A writer whose work was abandoned before a PR stays unknown, so `landed` is close to 100% by construction. `rounds_to_pass` and `landing_ci_first_pass` are the informative writer measures.
- **Effort follows difficulty.** Harder tasks were given higher effort, so comparing efforts within a model compares different work.
- **Reviewer strictness varies.** The first review of a PR came from different models over time (see the tiered review in [workflow.md](workflow.md)). A first-round pass under a lenient reviewer is weaker evidence than one under a strict reviewer.
- **Model and harness are confounded.** Each model ran mostly in one harness, so the results describe the pair.
- **Sessions split.** Some harnesses split one job into several sessions (resumes after a limit, sub-sessions). Minutes per run are therefore not minutes per task.
- **Tokens.** Summed per-turn input counts cached context again on every turn, so totals are far larger than the unique text the model read. Devin reports no tokens.
- **Rules changed during the record.** The routing rules changed almost daily ([lessons.md](lessons.md)); later work was routed using earlier results.
- **Small samples.** Most cells hold under ten tasks.

## Sources and backfill

The private project keeps a metrics history: CI runs and jobs, pull request lifecycles, review records and council rulings posted on pull requests, a launch ledger in which the lead labels every agent it starts (role, task type, model, effort, harness), and the agent sessions themselves. A curated backfill covers the routing studies of 2026-11-23 and 2026-11-24 (510 and 650 sessions, matched by hand to 80 and 99 PRs). Runs from 2026-11-21 onward were joined to their PRs once, and the nightly refresh joins new runs the same way.

## Privacy

The export is written from the private metrics by a tool in the private repository, and a privacy scrubber runs over every file before anything is written here. The export fails if it finds a file path, source code, a link into the private repository or any other private link, an issue or pull request title or number, an account name, an email address, a token, a webhook, or a long identifier such as a session ID. Account names are reduced to the harness. Pull request and issue numbers are replaced by the opaque task label.

## Reproducing the tables

```
python scripts/build.py
python scripts/build.py --check
```

The first rebuilds every table, chart and the README block from `data/`; the second fails if any of them is stale. Both need only Python 3.11 or newer.
