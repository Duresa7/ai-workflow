# AI Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

My skills and guidance for AI coding agents (Claude Code and Codex), plus untouched copies of the upstream skills I build on. Both agents read the same skill format: a folder with a `SKILL.md` file.

## Layout

```
skills/            My own skills, and my customized versions of templates. Used in any project.
work-in-progress/  Unfinished skills, with their notes and research.
profiles/          Skill sets tweaked for one kind of work, such as profiles/gamedev/.
sources/           Untouched upstream skills, the templates I customize from. Never edited.
guidance/          Notes an agent can read, such as how to select a model and divide work.
archive/           Retired skills (e2b-sandbox, orchestrate), kept for reference.
SOURCES.md         Where every skill comes from: upstream link, license, pinned commit, customized versions.
```

## How the pieces fit

1. **Templates.** `sources/<owner>/<skill>/` is a byte-for-byte copy of an upstream skill at one commit. `sources/sources.lock.json` records the hash of every file, and `check.py` fails if one changes.
2. **Customizing.** To change a template, copy its folder into `skills/<name>/` (for every project) or `profiles/<profile>/skills/<name>/` (for one kind of work), edit the copy, and list the copy in the template's **Customized as** cell in [SOURCES.md](SOURCES.md).
3. **Work in progress.** A skill being built lives in `work-in-progress/<project>/skills/<name>/`, next to the project's `notes/` and `research/`. It moves to `skills/` when it's finished. See [work-in-progress/README.md](work-in-progress/README.md).
4. **Profiles.** A profile is a `profile.toml` (description and an `include` list of skills to use unchanged) plus a `skills/` folder with that profile's tweaked copies. When a profile has its own copy of a skill, that copy replaces the version in `skills/` or `sources/` with the same name. See [profiles/README.md](profiles/README.md).

## My skills

| Skill | What it does |
|---|---|
| [`1password-cli`](skills/1password-cli/SKILL.md) | Uses the 1Password CLI (`op`) and keeps secret values out of the agent output. |

In progress: the [`human-voice`](work-in-progress/human-voice/README.md) suite, five skills for prose that reads as its author, not as AI.

## Templates

70 upstream skills from these repositories. [SOURCES.md](SOURCES.md) lists each one.

| Owner | Repository | License | Templates |
|---|---|---|---|
| `mattpocock` | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | 36 engineering, planning, and writing skills |
| `t3dotgg` | [t3dotgg/tstack](https://github.com/t3dotgg/tstack) | MIT | 9 pull request and workflow skills |
| `emilkowalski` | [emilkowalski/skills](https://github.com/emilkowalski/skills) | MIT | 21 UI and animation skills, plus two cheatsheets |
| `anthropics` | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 | `frontend-design` |
| `vercel-labs` | [vercel-labs/skills](https://github.com/vercel-labs/skills), [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop) | MIT, Apache-2.0 | `find-skills`, `agent-desktop` |
| `conorbronsdon` | [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | MIT | `avoid-ai-writing` |
| `petergyang` | [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | MIT | `no-ai-slop` |

Add a template:

```bash
python sources.py add OWNER/REPO path/to/skill     # pins upstream HEAD; --ref picks another commit
```

Then add its row to [SOURCES.md](SOURCES.md). Set `GITHUB_TOKEN` to avoid GitHub's anonymous rate limit.

## Install a skill

Link a skill folder into your user skills folder to make it available in every project:

```bash
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/skills/1password-cli" ~/.claude/skills/1password-cli    # Claude Code
ln -s "$PWD/skills/1password-cli" ~/.agents/skills/1password-cli    # Codex
```

On Windows, use PowerShell with Developer Mode on, or an elevated shell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills", "$HOME\.agents\skills" | Out-Null
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\1password-cli" -Target "$PWD\skills\1password-cli"
New-Item -ItemType SymbolicLink -Path "$HOME\.agents\skills\1password-cli" -Target "$PWD\skills\1password-cli"
```

There is no install script for profiles yet.

## Checks

```bash
python check.py              # templates untouched, skill names, SOURCES.md, profiles, skill tests
python check.py --upstream   # also confirms the lock file against GitHub
python -m unittest discover tests
```

Python 3.11 or newer, standard library only. CI runs all three on every push and pull request.

## License

MIT for my own work. See [LICENSE](LICENSE). Each template keeps its upstream license; see [SOURCES.md](SOURCES.md).
