# Claude Code project notes — Nucleus

This is the marketplace repo for Nucleus, BrightWay AI's plugin ecosystem for Claude
Cowork and Claude Code. It holds the catalog, the cross-plugin contracts, release
tooling and proposals. It is not a runtime plugin. Plugin code lives in nine separate
repos under `BrightWayAI/*`.

This file holds current instructions only. History is in `docs/HISTORY.md` and each
plugin's `CHANGELOG.md`. Do not add changelog entries here.

## Layout

```
.claude-plugin/marketplace.json   the catalog (9 plugins, with mirrored versions)
README.md                         user-facing overview
CONTRIBUTING.md                   contributor guide for every plugin
AGENTS.md                         the four checks to run before trusting a change
docs/
├── contracts.md                  cross-plugin file formats and ownership (read before changing shared behavior)
├── multi-agent-patterns.md       how sub-agents are chained inside plugins
├── RELEASING.md                  coordinated release process
├── HISTORY.md                    past work, moved out of this file
└── proposals/
    ├── ROADMAP.md                the active roadmap (start here)
    ├── *.md                      open specs
    ├── shipped/                  built specs
    └── parked/                   deferred, not on the roadmap
releases/                         coordinated release snapshots (index.json + one directory each)
scripts/ tests/                   release and adapter tooling
```

## The nine plugins

Local clones are siblings of this repo at `~/lab-bench/<id>/`, each with its own
`plugin.json`, `CHANGELOG.md`, `commands/`, `skills/`, `agents/` and `references/`.

| ID | Repo | Owns |
|---|---|---|
| `cortex` | BrightWayAI/cortex | Shared memory, identity and voice files, `/listen` and `/morning` ingest, decay, indexing, git sync, `cortex_cli.py` |
| `ops` | BrightWayAI/ops | `/cos` front door, `/status`, `/diagnose`, the schedule library, agent-run log |
| `briefing` | BrightWayAI/briefing | `/brief`, `/review`, `/timeline`, `/dashboard`, `/plan-tomorrow` |
| `growth` | BrightWayAI/growth | Pipeline analysis, relationship ranking, signal and referral pipeline |
| `clients` | BrightWayAI/clients | The account after signature: project setup, SOWs, status drafts, deliverable QA |
| `comms` | BrightWayAI/comms | Voice capture and all drafting |
| `admin` | BrightWayAI/admin | Time tracking and invoices |
| `research` | BrightWayAI/research | Finding and ranking news candidates |
| `alignment` | BrightWayAI/alignment | Slack cross-team alignment scanning |

The authoritative "owns / does not own" table is in `docs/contracts.md`. If this table
and that one disagree, that one is right.

## Where a change goes

- Plugin behavior goes in that plugin's repo, on its own branch and pull request.
- Shared release coordination, cross-plugin contracts and connector certification
  policy go here.
- Every plugin change bumps that plugin's `plugin.json`, adds a `CHANGELOG.md` entry,
  and is mirrored in `.claude-plugin/marketplace.json` and the README version table.
- Any change to a file format that more than one plugin reads or writes updates
  `docs/contracts.md` in the same piece of work.
- Bump pattern: minor for new commands or agents, patch for fixes and non-breaking
  refactors, major for breaking config-layout or contract changes.

## Config root

Plugins read and write user data under `<config-root>/`, resolved by
`cortex/scripts/lib/config_root.py`: explicit override, `CORTEX_CONFIG_ROOT`,
`~/.cortex/config-root`, the legacy pointer `~/Documents/.claude-plugin-config-root`,
`~/cortex-root` when materialized by `cortex_cli.py bootstrap`, then
`~/Documents/Claude`. New installs default to `~/cortex-root`.

- `memory/` is the shared (org) git repo. `.private/` is the private git repo and
  holds `me/`, `staged/`, `archive/`, `briefs/` and `plugins/`, reached through
  symlinks. `docs/contracts.md` has the full layout.
- Writes under `memory/` go through `cortex/scripts/cortex_cli.py`. Do not hand-edit
  memory files.
- Never write plugin runtime state outside the config root, and never commit a user's
  config-root contents to a plugin repo.

## Before calling a change done

Run the changed plugin's own checks (for cortex, `python3 scripts/check_repo.py`), then
from this repo:

```bash
python3 scripts/generate_openai_adapters.py --check
python3 scripts/check_openai_ecosystem.py
python3 scripts/smoke_codex_marketplace.py
python3 scripts/release_ecosystem.py check --all
```

The first two fail while `marketplace.json` lags a plugin's version, so sync the
catalog before running them.

## Releases

Coordinated releases are defined once under `releases/<release-id>/release.json`;
follow `docs/RELEASING.md`. Promoting a candidate to `released` requires live connector
evidence from `/test-connectors` and a matching git tag. Do not push, tag or publish
without the owner's explicit approval.

## Portability

The Codex and ChatGPT Work adapters are frozen as of 2026-11-16. Keep the generated
adapters and their checks passing when a source file changes. Do not extend them.
