# External benchmarks

Third-party results for the models this project used, kept apart from our own data. They measure different tasks under different harnesses, so they don't combine with our tables. The figures come from a comparison compiled on 2026-11-28 for the project's routing decisions; that report itself notes that its figures were carried forward from earlier research and not re-verified, so check each source before relying on a number. Results describe a model in a harness (Hydrogen in Antigravity, the SWE models in Devin), not the model alone.

## Independent coding leaderboards

**AI Coding Daily, 2026-11-26** ([leaderboard](https://aicodingdaily.com/leaderboard)). Score out of 90 on a shared task set.

| Model | Effort | Score / 90 | Average task |
|---|---|---|---|
| Gemini 4 Hydrogen | high | 78.01 | 3m 42s |
| SWE-2.1 | max | 76.78 | 21m 30s |
| SWE-2.1 | high | 75.10 | 16m 13s |
| Gemini 4 Hydrogen | medium | 73.44 | 1m 43s |
| SWE-2 | max | 72.45 | 11m 59s |
| SWE-2 Flash | high | 68.62 | 11m 29s |

By category (normalised score): Hydrogen `high` led bug finding (79.2%) and edge-case testing (93.8%); SWE-2.1 `max` led React and TypeScript (93.4%).

**Ramp SWE-Bench v2** ([results](https://mypriors.com/benchmarks/ramp-swebench-v2)): 500 tasks from production software, each model in its native harness, highest tested effort.

| Model | Resolved |
|---|---|
| GPT-6.2 Astra | 76.4% |
| Gemini 4 Neon | 76.2% |
| Fable 5.2 | 73.4% |
| GPT-6.2 Sol | 73.4% |
| Gemini 4 Hydrogen | 72.4% |
| Opus 5.5 | 67.8% |
| Sonnet 5.5 | 63.2% |

**SWE-Marathon v1.2** ([leaderboard](https://www.swemarathon.org/)): long, multi-hour engineering assignments, highest tested effort.

| Model | Resolved |
|---|---|
| GPT-6.2 Astra | 82.5% |
| Fable 5.2 | 75.0% |
| Opus 5.5 | 73.1% |
| GPT-6.2 Sol | 68.8% |
| Sonnet 5.5 | 64.0% |
| Gemini 4 Neon | 58.1% |
| Gemini 4 Argon | 49.4% |
| Gemini 4 Hydrogen | 47.8% |

**ModelDial, 2026-11-26** ([leaderboard](https://modeldial.com/en/leaderboard/coding), [method](https://modeldial.com/en/method)): Hydrogen `xhigh` 59.7 overall against SWE-2.1 `max` 57.4; Hydrogen stronger on frontend engineering (71.1 against 52.7), SWE-2.1 stronger on maintainability (55.0 against 48.0). Total evaluation time 2h 7m against 4h 29m.

**Scale Labs SWE Atlas v1.1** ([leaderboard](https://labs.scale.com/leaderboard/swe-atlas)): Hydrogen `xhigh` 71.98% overall (repository comprehension 75.00%, test writing 76.67%, refactoring 64.29%), 5th of 33. No SWE-model results.

## Effort studies

**Artificial Analysis** ([Hydrogen](https://artificialanalysis.ai/models/gemini-4-hydrogen), [coding agents](https://artificialanalysis.ai/agents/coding-agents)). Intelligence Index by Hydrogen effort:

| Effort | Index | Average time per task | Output tokens for the suite |
|---|---|---|---|
| low | 27 | 1.6m | 20.3M |
| medium | 41 | 3.8m | 54.4M |
| high | 51 | 7.8m | 110M |
| xhigh | 54 | 14.3m | 304M |

`high` to `xhigh` adds 3 points for 2.76 times the tokens. No comparable index exists for the SWE models.

**MajorMinorLabs Devin agent benchmark** ([repository](https://github.com/majorminorlabs/research-devin-agent-benchmark)): SWE-2 `medium` against `max` on 30 bugs and 60 runs. `medium` repaired 80.0% and `max` 76.7%; `max` did better only on the very hard subset (90% against 70%). In a five-case pilot `medium` used about a third of the prompt tokens and half the time.

## Vendor-reported results

Self-reported by Cognition, not independently measured:

| Benchmark | SWE-2.1 |
|---|---|
| FrontierCode 2.0 | 41.3 |
| SWE Marathon v1.2 | 54.9 |
| Terminal-Bench 4.1 | 50.0 |
| ExploitBench | 80.0 |
| ExploitGym | 27.3 |

## Swarms

No study found ranks these models as members of a collaborating swarm. A Replit study of up to 32 agents on performance engineering ([report](https://frontier.replit.com/throwing-headcount-at-the-problem/)) reported that Opus 5.5 improved a NumPy benchmark 3.7 times with one agent and 18.9 times with 32, while GPT-6.2 Astra, the strongest single agent, did worse as its team grew. See also [AsynCodeBench](https://arxiv.org/abs/2609.32662) and [ParallACT](https://arxiv.org/abs/2611.00314).

## How this compares with our data

- **Hydrogen** scores well on short tasks and badly on long ones (47.8% on SWE-Marathon). In our swarm it finished 11 of 11 small, fully specified slices with 9 needing no fix ([lessons.md](lessons.md)), consistent with the short-task results.
- **Astra** leads both production benchmarks above. In our data it was strong on well-defined work and mixed on open-ended physics, where 1 of 4 tasks passed landing CI first time.
- **Opus 5.5** ranks below Astra and Neon on Ramp SWE-Bench v2, yet it was our most dependable writer on first review. Our first reviewer was often the strictest model, and the benchmarks don't measure how well code survives review.
- **SWE-2.1** is slow in both the leaderboard and our data (a median of 57 to 117 minutes per session), and good when it finishes.
