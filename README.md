# Claude Code configuration

My portable [Claude Code](https://claude.com/claude-code) setup — engineering standards and
settings — kept in version control so it can be replicated on another machine or borrowed by
colleagues.

## What's in here

| File | What it does |
|---|---|
| `CLAUDE.md` | Engineering standards loaded into every session: TDD, SOLID, naming, complexity, architecture, code smells. |
| `settings.json` | Model, theme, permissions, and `enabledPlugins` — the list of plugins to install. |
| `claude-config.py` | Moves those two files between this repo and `~/.claude`. |

## Using it

```bash
git clone git@github.com:giovanni-orciuolo/.claude.git claude-config
cd claude-config
python3 claude-config.py apply
```

The repo is *named* `.claude`, so cloning without a target directory gives you a hidden folder.
The `claude-config` argument above avoids that.

`apply` overwrites `~/.claude/CLAUDE.md` and `~/.claude/settings.json`. It backs up whatever was
there first, as `<name>.bak-<timestamp>` — but if you already have config you care about, read
both files before running it.

**Plugins install themselves.** `settings.json` lists 67 plugins from the official marketplace;
Claude Code fetches them on next launch. Nothing is vendored here, so the repo stays ~20 KB
instead of hundreds of megabytes, and there are no machine-specific install paths to go stale.

### Just want the standards?

Copy `CLAUDE.md` to `~/.claude/CLAUDE.md` and ignore everything else. It's standalone and has no
dependency on the rest of this repo.

### Commands

| Command | Direction |
|---|---|
| `python3 claude-config.py apply` | repo → `~/.claude` (backs up existing files) |
| `python3 claude-config.py capture` | `~/.claude` → repo (for committing local edits) |
| `python3 claude-config.py check` | report which tracked files differ |

Requires Python 3.8+. Without Python, `apply` is just two file copies:

```bash
cp CLAUDE.md settings.json ~/.claude/
```

## What is deliberately not here

This is a **public** repository, and `~/.claude` holds credentials and conversation history. Those
never enter this repo:

- `.credentials.json` — OAuth tokens
- `projects/` — conversation transcripts and auto-memory
- `history.jsonl`, `sessions/`, `session-env/`, `shell-snapshots/`, `file-history/`, `backups/`
- `plugins/cache`, `plugins/marketplaces`, `installed_plugins.json` — vendored clones and absolute
  install paths, wrong on every other machine
- `settings.local.json` — the machine-local override layer, by design not shared

The protection is structural rather than rule-based: `claude-config.py` copies a hardcoded
two-name allowlist and never globs, so private files are not in the working tree at all and no
`.gitignore` mistake can publish them. `.gitignore` denies them by name anyway, because the cost
of being wrong is a leaked credential.

## Updating it

```bash
python3 claude-config.py check     # what drifted?
python3 claude-config.py capture   # pull local edits into the repo
git diff                           # read before committing
git commit -am "..." && git push
```
