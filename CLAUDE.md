# Claude Code project notes — Nucleus

This is the marketplace repo for **Nucleus — BrightWay AI's curated marketplace of plugins, agents, and shared memory. Tagline: "The operating core for how AI-powered teams get work done."**

The actual plugin source code lives in separate GitHub repos under `BrightWayAI/*`; this repo only holds the catalog manifest (`.claude-plugin/marketplace.json`), the marketplace README, contribution docs, and cross-cutting design proposals.

**Renamed from `claude-plugins` → `nucleus` on 2026-05-12.** GitHub auto-redirects old URLs. Local directory at `~/lab-bench/nucleus/`.

**Catalog currently lists 14 plugins.** Started at 12, gained `writing-style` and `daily-brief`, lost `plan-tomorrow` (folded into daily-brief), gained `nucleus-router` (JARVIS-style natural-language front door). Net 14.

## Layout

```
.claude-plugin/marketplace.json   ← the catalog (14 plugins)
README.md                          ← user-facing marketplace overview
CONTRIBUTING.md                    ← contributor guide for any plugin
SECURITY.md / LICENSE              ← standard repo files
docs/
├── multi-agent-patterns.md        ← pattern guide for chaining subagents inside plugins
└── proposals/                     ← future work / design specs awaiting pickup
    └── second-brain-extension.md  ← entity wiki pages, daily brief, /listen archive, etc.
```

## When picking up work on plugins

**Pending work lives in `docs/proposals/`.** Before starting any new feature, check that folder for an existing spec. Each proposal is a self-contained brief with motivation, architecture, per-plugin changes, implementation steps, and acceptance criteria — write was designed to be picked up cold by a future Claude Code session.

Currently open proposals:

- **`docs/proposals/second-brain-extension.md`** — entity wiki pages in cortex, interactive daily brief plugin, two-stage triage for memory commits, nightly `/listen` archive pipeline, `/end-day` orchestration chain. Based on Omar Ismail's second-brain pattern, adapted to this marketplace's existing stack.

## How plugins are organized

The marketplace contains 14 plugins, each in its own GitHub repo:

| Plugin | Repo | Purpose |
|---|---|---|
| nucleus-router | BrightWayAI/nucleus-router | JARVIS-style natural-language router. Always-loaded skill maps utterances to slash commands and confirms before running. `/route` prints the cheat sheet. |
| claude-cortex | BrightWayAI/claude-cortex | Always-on memory + shared `/setup-identity` and `/setup-voice` |
| core-ops | BrightWayAI/core-ops | Pipeline analyst + forecast subagents, /diagnose, /log-agent-run, /agent-metrics, /register-schedules |
| lead-engine | BrightWayAI/lead-engine | LinkedIn intent-based outbound + contact-researcher subagent |
| bizdev-outreach | BrightWayAI/Biz-Dev | Per-contact research + drafted outreach |
| weekly-outreach | BrightWayAI/weekly-outreach | Weekly BD prep |
| referral-engine | BrightWayAI/referral-engine | Connector network + referral asks |
| news-curator | BrightWayAI/news-curator | Weekly LinkedIn AI roundup (news-curator + post-assembler subagents) |
| client-status | BrightWayAI/client-status | Weekly client status drafts |
| project-setup | BrightWayAI/project-setup | New-engagement initialization |
| time-tracking | BrightWayAI/time-tracking | Calendar → time-log → invoices |
| weekly-alignment | BrightWayAI/weekly-alignment | Slack cross-team alignment scanner |
| writing-style | BrightWayAI/writing-style | Adaptive voice learning — drafts, edit-detection, pattern-based style-guide refinement |
| daily-brief | BrightWayAI/daily-brief | Daily flow plugin. /brief = today's working surface (Cowork artifact); /process-brief acts on annotations; /plan-tomorrow blocks the next business day. As of v0.2.0 absorbs the deprecated plan-tomorrow plugin. |

Each plugin has its own repo with `commands/`, `skills/`, `agents/`, `references/`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE`. Local dev clones live as siblings to this marketplace repo in `~/lab-bench/`.

## Config-root convention

All plugins read user-specific config from `<config-root>/`, where `<config-root>` is the path stored in `~/Documents/.claude-plugin-config-root` (a single-line text file in the user's home directory, populated on first plugin setup). Layout:

```
<config-root>/
├── identity.md                                    (cortex /setup-identity)
├── voice.md                                       (cortex /setup-voice)
├── memory/                                        (cortex working memory)
├── plugins/
│   └── <plugin>.user-context.md                   (per-plugin config)
├── archive/YYYY-MM-DD/                            (raw daily archive — proposed in second-brain-extension)
├── daily-briefs/YYYY-MM-DD.md                     (interactive daily working doc — proposed)
└── time-log.csv                                   (time-tracking plugin)
```

This is the canonical write location for plugin runtime data. Don't write plugin runtime state anywhere else.

## Versioning

- Plugins are individually versioned in their own `plugin.json`.
- Marketplace itself doesn't track per-plugin versions (Cowork resolves the latest from each plugin's GitHub repo on next pull).
- Bump pattern: minor for new commands/agents, patch for fixes or non-breaking refactors, major for breaking API or config-layout changes.

## Open proposals (newly added — 2026-05-16)

The "Nucleus as JARVIS" initiative has three phases. Phase 1 (router) is shipped to GitHub; Phases 1 (cortex v4.5) and 2 (Obsidian) are specced.

- **`docs/proposals/nucleus-router.md`** — Phase 1 front door. New standalone plugin adds a natural-language router that maps utterances to slash commands and asks before running. Decisions locked: new plugin (not folded into cortex), suggest+confirm (no auto-dispatch). **Shipped** at `~/lab-bench/nucleus-router/` v0.1.0 and pushed to `https://github.com/BrightWayAI/nucleus-router`. Catalog updated to 14 plugins.

- **`docs/proposals/cortex-v4.5-legibility.md`** — Phase 1 finish. Two cortex additions: (a) auto-maintained `memory/index.md` catalog (Karpathy borrow — zero LLM cost, makes Obsidian's home page possible and gives non-cortex agents a one-file entry point); (b) `/research-gaps` + new `gap-researcher` subagent (wiki-self-heal borrow — scans memory for thin/stale/contradictory/orphan/under-cited content, web-researches with ≥2 sources, writes findings to `.research-drafts/` for user merge). Status: spec-ready, not implemented.

- **`docs/proposals/obsidian-as-ui.md`** — Phase 2 human UI. Add `/setup-obsidian` to cortex that scaffolds a `.obsidian/` workspace config + `VAULT.md` home page over `<config-root>/`. Daily-brief snapshots automatically become Obsidian daily notes (config-only — no plugin code change). Documents recommended Obsidian community plugins (Dataview, Tasks, Calendar). Status: spec-ready, not implemented.

Phase 3 (productization vs Anthropic's Claude for Small Business bundle: positioning, connector parity audit for QuickBooks/HubSpot/Canva/DocuSign, pricing/packaging) is **deferred per user decision** until Phases 1+2 are shipped and dogfooded.

## Recently completed work

- **v0.2 refactor (2026-05-11):** all 12 plugins migrated from plugin-folder-relative paths to `<config-root>/plugins/` paths, eliminating writes to Cowork's read-only mount. See each plugin's CHANGELOG for the v0.2.0 / v0.2.1 entries.
- **Phase 0 platform-agnostic Step 0 (2026-05-12):** every `request_cowork_directory(...)` call in setup commands is wrapped in a Cowork/Claude-Code conditional so the same plugin source works in both runtimes. All 13 plugin patch versions bumped: cortex 4.1.3, weekly-alignment 1.4.3, writing-style 0.1.1, the rest 0.2.3.
- **Phase 1 daily-brief plugin (2026-05-12):** new plugin `daily-brief` v0.1.0 shipped — `/brief` builds a Cowork artifact "Today's Brief" with seven annotated sections; `/process-brief` reads the annotations and routes them (drafts/reschedules/talking-points/dismissals). Phase 1 of the second-brain v2 extension; spec at `docs/proposals/SECOND-BRAIN-V2-SPEC.md`.
- **Phases 3-6 second-brain v2 (2026-05-12):** Phase 2 (separate inbox-triage plugin) deliberately skipped — `daily-brief` keeps its direct Gmail fallback. Shipped: Phase 3 person pages (cortex 4.2.0 + 6 plugins → 0.2.4), Phase 4 cheap-tier commit triage (cortex), Phase 5 `/end-day` orchestration chain (cortex), Phase 6 orphan + duplicate-topic guardrails (cortex). All plugin code pushed to GitHub.
- **Known design note:** `daily-brief` and `plan-tomorrow` overlap significantly on data sources (calendar / CRM / inbox / cortex). Different verbs (`/brief` = today's working surface with annotations + `/process-brief` action loop; `/plan-tomorrow` = tomorrow's calendar blocks). Decision to keep both was deferred — revisit once both are in daily use.
- **cortex v4.3.0 — `/end-day` mining layer (2026-05-12):** three read-only agents at Step 2a (`transcript-reviewer` expanded to two output streams, `conversation-miner` new, `activity-miner` new — scoped to events). Source-agnostic via adapter pattern at `agents/lib/note-source-adapters.md` (Granola / Gemini / Fireflies / Otter / Notion / generic Drive / generic Gmail / custom). Step 2b unified review gate with high-confidence-only toggle, auto-expanded cross-refs, dismissal log. Domain-node Scope convention via one-time migration in `/end-day` Pre-chain B (generic detection, no hardcoded names). New `/setup-sources` command with mandatory adapter health-check. `code-miner` deferred. `[confirmed/recalled]` substrate tags added on knowledge entries.
- **cortex v4.4.0 — forgetting / decay layer (2026-05-12):** the other half of the bidirectional second-brain. Decay model with four states (Fresh / Stale / Dormant / Cold) driven by `[confirmed:...]` age. Defaults at `<config-root>/memory/.decay-config.md` (60/180/365 days; GOTCHA and RECIPE decay 1.5× slower; CORRECTION immune). Per-node `decay_profile: fast | normal | slow` front-matter override. `/recall` flags aging entries inline and offers recall-time triage (re-confirm / demote / archive). `/remember` runs concept-drift detection on new INSIGHT/MODEL/GOTCHA/LESSON writes (Haiku-tier) and prompts the user on supersede/keep-both/edit/skip. New `/rehearse` command + skill: active retention loop, picks 3-5 aging entries weekly via `/end-week` Step 3.5. `/cleanup` deepened with section I for dormant knowledge and section H for cooling/dormant/cold-archive person pages (auto-archive to `memory/person/archive/`). `memory-librarian` ranks Fresh higher and skips `## Demoted knowledge` by default. Content is never auto-deleted; every transition is user-gated.
- **Nucleus visibility + consolidation (2026-05-12):** core-ops 0.2.3 → 0.3.0 — new `/nucleus-status` (terse text snapshot) and `/nucleus-dashboard` v1 (Cowork HTML artifact with 6 section cards: stack overview, this-week activity, memory health, outreach pipeline, time+invoicing, impact-loop placeholder). daily-brief 0.1.0 → 0.2.0 — absorbs the deprecated plan-tomorrow plugin (`/plan-tomorrow` + `/setup-plan` now live in daily-brief; user-context backward-compatible). Marketplace catalog count drops 14 → 13. Standalone plan-tomorrow repo deprecated with a redirect README and archived on GitHub.
