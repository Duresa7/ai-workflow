# Profiles

A profile is a set of skills tweaked for one kind of work, such as game development, frontend, backend, or homelab. You pick the profile that fits a project.

## Format

```
profiles/<profile>/
  profile.toml     description and the skills used unchanged
  skills/<name>/   this profile's tweaked copies
```

`profile.toml`:

```toml
description = "What kind of work this profile is for."

# Skills this profile uses as they are. Paths point at skills/ or sources/.
include = [
  "sources/emilkowalski/animate",
  "skills/1password-cli",
]
```

When `skills/<name>/` in a profile has the same name as an included skill, the profile's copy replaces it. Two profiles can each have their own version of the same skill.

## Making a tweaked copy

Copy the template or skill into `profiles/<profile>/skills/<name>/`, edit it, and list the copy in [SOURCES.md](../SOURCES.md): add it to the template's **Customized as** cell, or to **Your own skills** if it's new. `python check.py` checks that every include path exists and every tweaked copy appears in SOURCES.md.

There is no install script yet. For now, copy or link a profile's skills into a project's `.claude/skills/` or `.agents/skills/` by hand.

## Profiles

| Profile | For |
|---|---|
| [`gamedev`](gamedev/profile.toml) | Game development |
