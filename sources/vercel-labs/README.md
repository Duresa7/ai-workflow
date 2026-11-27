# vercel-labs

## [agent-desktop](./agent-desktop/SKILL.md)

Computer use for AI agents: see and operate desktop apps on macOS, Windows, and Linux through the OS accessibility tree without screenshots or pixel matching. It reads a desktop app's accessibility tree and returns JSON with a ref for every element the agent can act on; the agent clicks or types on a ref, reads the UI again to verify, and repeats.

### Quick start

```bash
agent-desktop snapshot --app Finder -i      # interactive elements, each with a ref
agent-desktop click @s8f3k2p9:e8            # act on a ref from that snapshot
agent-desktop snapshot --app Finder -i      # observe again to verify
```

- **Refs belong to their snapshot.** When the UI changes, an action returns `STALE_REF` or `AMBIGUOUS_TARGET`: take a new snapshot and use its refs.
- **Several windows** give `AMBIGUOUS_TARGET`; pass a candidate window id with `--window-id`.
- **Dense apps:** map first with `snapshot --skeleton --app Slack -i --compact`, then drill into one region with `snapshot --root @s8f3k2p9:e3 -i --compact`.
- **Headless by default.** Ref actions use the accessibility API without moving the pointer or taking focus. The global `--headed` flag allows physical input.
- `type`, `set-value`, and `clipboard-set` accept `--stdin` for piped text, keeping it out of process arguments.

### Commands

| Group | Commands |
|---|---|
| Observe | `snapshot`, `find`, `get`, `is`, `screenshot`, `list-surfaces` |
| Act on a ref | `click`, `double-click`, `triple-click`, `right-click`, `type`, `set-value`, `clear`, `focus`, `select`, `toggle`, `check`, `uncheck`, `expand`, `collapse`, `scroll`, `scroll-to` |
| Keyboard and mouse | `press`, `hover`, `drag`, `mouse-move`, `mouse-click`, `mouse-wheel`, `key-down`, `key-up`, `mouse-down`, `mouse-up` |
| Apps and windows | `launch`, `close-app`, `list-apps`, `list-windows`, `list-displays`, `focus-window`, `resize-window`, `move-window`, `minimize`, `maximize`, `restore`, `open-system-surface` |
| Notifications | `list-notifications`, `dismiss-notification`, `dismiss-all-notifications`, `notification-action` |
| Clipboard | `clipboard-get`, `clipboard-set`, `clipboard-clear` |
| Wait | `wait` |
| Sessions | `session`, `trace`, `cursor-overlay` |
| Sandboxes | `sandbox` |
| System | `status`, `permissions`, `version`, `batch`, `skills` |

## [find-skills](./find-skills/SKILL.md)

Helps users discover and install agent skills from the open agent skills ecosystem ([skills.sh](https://skills.sh)) using the `npx skills` CLI (`npx skills find`, `npx skills add`, `npx skills update`).

Use when the user asks "how do I do X", "find a skill for X", "is there a skill for X", or wants to search for tools, templates, or workflows to extend agent capabilities.
