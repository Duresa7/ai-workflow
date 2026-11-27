# Skills

71 skills organized by category.

- [Design & UI](#design--ui)
- [Animation & Motion](#animation--motion)
- [Planning, Discovery & Specs](#planning-discovery--specs)
- [Architecture, Implementation & Debugging](#architecture-implementation--debugging)
- [Code Review, PRs & Shipping](#code-review-prs--shipping)
- [Writing & Editing](#writing--editing)
- [Workflow, Handoffs & Learning](#workflow-handoffs--learning)
- [Tooling, Setup & Automation](#tooling-setup--automation)

---

## Design & UI

- **[frontend-design](./frontend-design/SKILL.md)** — Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
- **[emil-design-eng](./emil-design-eng/SKILL.md)** — The main design-engineering skill, consisting of mostly animation plus design advice.
- **[apple-design](./apple-design/SKILL.md)** — Apple's principles for interface design and fluid motion, distilled from WWDC design talks and translated for the web.
- **[ui-prototype](./ui-prototype/SKILL.md)** — Build multiple different versions of a UI piece you describe and go through them using a switcher.
- **[pick-ui-library](./pick-ui-library/SKILL.md)** — Have your agent pick the right library for the task based on trusted libraries, instead of hand-rolling a toast component or installing an abandoned package.
- **[mobile-native](./mobile-native/SKILL.md)** — Make your web app feel native on a phone: sticky hover states, tap highlight flashes, the `100vh` bug, inputs that zoom the page, laggy taps, safe areas, and the small fixes that separate a website from an app.
- **[break-ui](./break-ui/SKILL.md)** — Try to break the UI you built with worst-case data: long names, unusual emails, one-letter names, huge counts, empty lists, and long labels.
- **[learn-taste](./learn-taste/SKILL.md)** — Run at the end of a session to collect every design correction you made (including your own edits) and turn each one into a rule with its reason in `DESIGN.md`, so the next agent doesn't make the same mistake.
- **[ask-sonner](./ask-sonner/SKILL.md)** — Guide to working with [Sonner](https://sonner.emilkowal.ski): setup, styling, recipes, and fixes for the most common issues.
- **[ask-emil](./ask-emil/SKILL.md)** — Not sure which UI/animation skill to use? Describe your situation and it points you to the right skill or sequence of them, from idea to shipped.

## Animation & Motion

- **[animate](./animate/SKILL.md)** — Builds a web animation from scratch while choosing the correct curve, duration, properties, and so on.
- **[animate-expo](./animate-expo/SKILL.md)** — The same animation bar for React Native and Expo: gestures, sheets, haptics, screen transitions, and keeping motion off the JS thread.
- **[choreograph](./choreograph/SKILL.md)** — Coordinate several elements that animate together: what leads, what follows, what runs in parallel, and what shouldn't move at all.
- **[gestures](./gestures/SKILL.md)** — Build drag, swipe, and sheet interactions that track the finger 1:1, carry the speed of the release, and can be caught mid-animation.
- **[animation-performance](./animation-performance/SKILL.md)** — Fix animations that drop frames, covering subtle issues that most agents miss.
- **[animation-vocabulary](./animation-vocabulary/SKILL.md)** — Get better animations from an AI by telling it exactly what you want using the right motion terms.
- **[review-animations](./review-animations/SKILL.md)** — Review your animations in a strict way against craft rules.
- **[improve-animations](./improve-animations/SKILL.md)** — Audit all the animations in your codebase and get prioritized, self-contained plans that any agent can execute.
- **[find-animation-opportunities](./find-animation-opportunities/SKILL.md)** — Search your UI for places that would genuinely benefit from motion, while also telling you what not to animate.
- **[remove-animations](./remove-animations/SKILL.md)** — The opposite of finding opportunities: remove animations your app doesn't need (motion on keyboard shortcuts, fade-ins on every section, delay on every tooltip in a group).

## Planning, Discovery & Specs

- **[grill-me](./grill-me/SKILL.md)** — Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved. *(User-invoked)*
- **[grill-with-docs](./grill-with-docs/SKILL.md)** — Grilling session that also builds your project's domain model, sharpening terminology and updating `GLOSSARY.md` and ADRs inline. *(User-invoked)*
- **[grilling](./grilling/SKILL.md)** — Reusable interview primitive behind `grill-me`, `grill-with-docs`, `triage`, `wayfinder`, and `improve-codebase-architecture`: interview the user relentlessly until every branch of a design tree is resolved. *(Model-invoked)*
- **[to-spec](./to-spec/SKILL.md)** — Turn the current conversation into a spec and publish it to the issue tracker. No interview — synthesizes what you've already discussed. *(User-invoked)*
- **[to-tickets](./to-tickets/SKILL.md)** — Break any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges, written as text in a local file or as native blocking links on a real tracker. *(User-invoked)*
- **[wayfinder](./wayfinder/SKILL.md)** — Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on the issue tracker, and resolve them one at a time until the way to the destination is clear. *(User-invoked)*
- **[loop-me](./loop-me/SKILL.md)** — Grill you about specs for the workflows you want to build, within this workspace.
- **[to-questionnaire](./to-questionnaire/SKILL.md)** — Turn a decision you can't answer alone into a Markdown questionnaire for the one person who can, filled in async or together over a meeting. Grills you about the send (who it's for, what you need back), not the subject. *(User-invoked)*
- **[triage](./triage/SKILL.md)** — Move issues through a state machine of triage roles. *(User-invoked)*

## Architecture, Implementation & Debugging

- **[codebase-design](./codebase-design/SKILL.md)** — Shared discipline and vocabulary for designing deep modules: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. *(Model-invoked)*
- **[domain-modeling](./domain-modeling/SKILL.md)** — Actively build and sharpen a project's domain model: challenge terms against the glossary, stress-test with edge-case scenarios, and update `GLOSSARY.md` and ADRs inline. *(Model-invoked)*
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)** — Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. *(User-invoked)*
- **[prototype](./prototype/SKILL.md)** — Build a throwaway prototype to answer a design question: either a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route. *(Model-invoked)*
- **[tdd](./tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time. *(Model-invoked)*
- **[implement](./implement/SKILL.md)** — Build the work described by a spec or set of tickets, driving `/tdd` at pre-agreed seams and closing out with `/code-review` before committing. *(User-invoked)*
- **[implement-spec](./implement-spec/SKILL.md)** — Implement a whole spec on one integration branch. Works the tickets as a task graph, running implementer subagents across the ready frontier for maximum concurrency, then closes out with `/code-review`. *(User-invoked)*
- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: build a feedback loop that goes red on this bug → minimise → hypothesise → instrument → fix → regression-test. *(Model-invoked)*
- **[write-swift](./write-swift/SKILL.md)** — Write modern Swift well: modeling with value types, Swift 6 data-race safety and approachable concurrency (`@concurrent`, main-actor-by-default, actors, task groups), protocols and generics (`some` vs `any`), API design, performance and ARC, Swift Testing, and macros.
- **[migrate-to-shoehorn](./migrate-to-shoehorn/SKILL.md)** — Migrate test files from `as` type assertions to `@total-typescript/shoehorn`.

## Code Review, PRs & Shipping

- **[code-review](./code-review/SKILL.md)** — Two-axis review of the diff since a fixed point: **Standards** (coding standards + Fowler smell baseline) and **Spec** (faithful implementation of the originating issue/spec), run as parallel subagents so neither pollutes the other. *(Model-invoked)*
- **[council](./council/SKILL.md)** *(say: "council")* — Gets review from three models from different providers, and loops until they agree.
- **[sol-loop](./sol-loop/SKILL.md)** *(say: "sol loop")* — Reviews a change with GPT Sol in a loop until both agents agree.
- **[file-pr](./file-pr/SKILL.md)** *(say: "file a PR")* — Files a short PR that leads with the problem, not an inventory of changes. Uses `leaving-pr-comments`.
- **[babysit-pr](./babysit-pr/SKILL.md)** *(say: "babysit")* — Watches a PR through CI and review bots, and fixes the real findings. Uses `leaving-pr-comments`; requires `gh` and `python3`.
- **[leaving-pr-comments](./leaving-pr-comments/SKILL.md)** *(automatic)* — Formats comments that an agent posts on your behalf.
- **[modernize](./modernize/SKILL.md)** *(say: "modernize")* — Rebases an old PR and decides if it should still exist. Uses `leaving-pr-comments`.
- **[takeover](./takeover/SKILL.md)** *(say: "take over")* — Finishes someone else's PR, branch, or agent thread, and keeps their credit. Uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- **[full-send](./full-send/SKILL.md)** *(say: "full send")* — Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. Uses `sol-loop`, `file-pr`, and `babysit-pr`.
- **[full-stop](./full-stop/SKILL.md)** *(say: "full stop")* — Same as `full-send`, but stops when the PR is ready for you to merge.

## Writing & Editing

- **[avoid-ai-writing](./avoid-ai-writing/SKILL.md)** — Audit and rewrite English prose to remove AI writing patterns ("AI-isms"). Supports **Rewrite** (default, up to two passes via `--iterate 1|2`), **Detect** (flag only, grouped by `P0`/`P1`/`P2`), and **Edit** (targeted in-place edits), plus optional voice profiles (`casual` / `professional` / `technical` / `warm` / `blunt`).
- **[no-ai-slop](./no-ai-slop/SKILL.md)** — Remove 20+ patterns of AI slop (binary contrasts, throat-clearing openers, faux-insight setups, dramatic fragments, importance puffery, etc.) without flattening your personal voice. Use `/no-ai-slop (your writing)` to edit, `/no-ai-slop is this slop? (your writing)` to detect, or ask it to draft satire slop.
- **[writing-for-agents](./writing-for-agents/SKILL.md)** — Writing documents for agents: skills, `AGENTS.md`/`CLAUDE.md`, and any doc an agent reaches by a pointer. *(Model-invoked)*
- **[writing-fragments](./writing-fragments/SKILL.md)** — Writing, explore: mine raw fragments with no structure yet.
- **[writing-beats](./writing-beats/SKILL.md)** — Writing, exploit: assemble raw material into a journey of beats, grounding each term before a beat leans on it.
- **[writing-shape](./writing-shape/SKILL.md)** — Writing, exploit: shape raw material into an article, paragraph by paragraph.

## Workflow, Handoffs & Learning

- **[ask-matt](./ask-matt/SKILL.md)** — Ask which engineering/productivity skill or flow fits your situation. A router over the user-invoked skills. *(User-invoked)*
- **[find-skills](./find-skills/SKILL.md)** — Helps discover and install agent skills from [skills.sh](https://skills.sh) using the `npx skills` CLI (`find`, `add`, `update`) when looking for tools, templates, or workflows to extend agent capabilities.
- **[handoff](./handoff/SKILL.md)** — Compact the current conversation into a handoff document so another agent can continue the work. *(User-invoked)*
- **[claude-handoff](./claude-handoff/SKILL.md)** — Hand the current conversation off to a fresh background agent that picks up the work immediately.
- **[retro](./retro/SKILL.md)** — Suggest improvements to the coding agent's environment (navigation, automated checks, coding standards, steering files, tooling) after a session, most severe first. *(User-invoked)*
- **[research](./research/SKILL.md)** — Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo, run as a background agent. *(Model-invoked)*
- **[teach](./teach/SKILL.md)** — Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace. *(User-invoked)*
- **[wait-what](./wait-what/SKILL.md)** — Fire this the moment a message doesn't land. The agent re-pitches it with the context you're missing, in plain English, using your `GLOSSARY.md` vocabulary. *(User-invoked)*

## Tooling, Setup & Automation

- **[1password-cli](./1password-cli/SKILL.md)** — Drive the 1Password CLI (`op`) without putting secret values into output: read, use, create, rotate, and share secrets via `op://` references, and manage items, documents, vaults, users, groups, service accounts, Connect servers, and SSH keys.
- **[agent-desktop](./agent-desktop/SKILL.md)** — Computer use for AI agents: see and operate desktop apps on macOS, Windows, and Linux through the OS accessibility tree without screenshots or pixel matching (`snapshot` → act on `@ref` → observe again to verify; headless by default, `--headed` for physical input, `--stdin` for piped text).
- **[setup-matt-pocock-skills](./setup-matt-pocock-skills/SKILL.md)** — Configure a repo for the engineering skills (issue tracker, triage labels, domain doc layout). Run once per repo before using the other engineering skills. *(User-invoked)*
- **[setup-pre-commit](./setup-pre-commit/SKILL.md)** — Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo.
- **[setup-ts-deep-modules](./setup-ts-deep-modules/SKILL.md)** — Wire `dependency-cruiser` into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only through its entry-point files. *(User-invoked)*
- **[git-guardrails-claude-code](./git-guardrails-claude-code/SKILL.md)** — Set up Claude Code hooks to block dangerous git commands (`push`, `reset --hard`, `clean`, `branch -D`, etc.) before they execute.
- **[wizard](./wizard/SKILL.md)** — Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning infrastructure, setting up credentials or CI secrets, walking a third-party dashboard, or running a one-off migration or cutover. *(Model-invoked)*
- **[scaffold-exercises](./scaffold-exercises/SKILL.md)** — Create exercise directory structures with sections, problems, solutions, and explainers that pass linting.
