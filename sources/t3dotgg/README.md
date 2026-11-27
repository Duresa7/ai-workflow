# t3dotgg

## Skills

| Skill | Say | What it does |
|---|---|---|
| [`full-send`](./full-send/SKILL.md) | "full send" | Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. |
| [`full-stop`](./full-stop/SKILL.md) | "full stop" | Same as `full-send`, but stops when the PR is ready for you to merge. |
| [`council`](./council/SKILL.md) | "council" | Gets review from three models from different providers, and loops until they agree. |
| [`sol-loop`](./sol-loop/SKILL.md) | "sol loop" | Reviews a change with GPT Sol in a loop until both agents agree. |
| [`file-pr`](./file-pr/SKILL.md) | "file a PR" | Files a short PR that leads with the problem, not an inventory of changes. |
| [`takeover`](./takeover/SKILL.md) | "take over" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. |
| [`babysit-pr`](./babysit-pr/SKILL.md) | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. |
| [`modernize`](./modernize/SKILL.md) | "modernize" | Rebases an old PR and decides if it should still exist. |
| [`leaving-pr-comments`](./leaving-pr-comments/SKILL.md) | (automatic) | Formats comments that an agent posts on your behalf. |

Some skills call others:

- `full-send` uses `sol-loop`, `file-pr`, and `babysit-pr`.
- `full-stop` uses `full-send`.
- `takeover` uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr`, `babysit-pr`, and `modernize` use `leaving-pr-comments`.

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`).
- `python3` for `babysit-pr`'s `pr-wait` script.
- `council` and `sol-loop` need subagents on other providers' models. T3 Code does this with `delegate_task`. Otherwise you need a harness that can run those models.
