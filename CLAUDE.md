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

## Nucleus as JARVIS — shipped (2026-05-16)

Phases 1 and 2 are live. Phase 3 (productization) is deferred until dogfooding.

### Phase 1 — Front door + memory legibility

- **`nucleus-router` v0.1.1** — Shipped at `https://github.com/BrightWayAI/nucleus-router`. Always-loaded skill matches natural-language utterances to the right Nucleus command and asks for confirmation. No more memorizing 57 commands. Intent table covers all 13 plugins; v0.1.1 added rows for cortex v4.5 commands. Spec: `docs/proposals/nucleus-router.md`.

- **cortex v4.5.0** — Shipped at `https://github.com/BrightWayAI/claude-cortex`. Three additions:
  - `/reindex` + indexer skill — auto-maintained `memory/index.md` catalog (zero-LLM, deterministic). Runs from `/end-day` Step 5.5, `/cleanup` Step 4.5, and on `/remember` writes via `.reindex-queue` marker.
  - `/research-gaps` + `gap-researcher` subagent + `/merge-research-draft` — autonomous gap-finder. Seven detection rules; web research with ≥2 independent sources; private-individual privacy rule; user-gated merge. Optional Step 5.5 of `/end-week`.
  - Spec: `docs/proposals/cortex-v4.5-legibility.md`.

### Phase 2 — Human UI substrate

- **`/setup-obsidian` (cortex v4.5.0)** — Config-only scaffolding for `.obsidian/` workspace + `VAULT.md` home page over `<config-root>/`. Idempotent and non-destructive. Daily-brief snapshots become Obsidian daily notes via folder config — zero plugin code change. Mobile-readable via Obsidian's iOS/Android apps + iCloud or Obsidian Sync. Spec: `docs/proposals/obsidian-as-ui.md`.

### Phase 3 — Productization (shipped 2026-05-16, same session)

Strategic decisions locked:
- **Monetization:** free OSS, MIT-licensed everywhere; BrightWay AI sells consulting / setup / customization / training on top. Nucleus is the lead magnet.
- **Audience:** solo operators / fractional consultants. Not general SMBs, not enterprise teams.
- **Vs Anthropic SMB bundle:** position purely on Nucleus's own merits; do **not** mention Anthropic SMB in public docs. Internal competitive context lives in `docs/proposals/smb-connector-audit.md`.

Deliverables:
- `docs/proposals/smb-connector-audit.md` — internal-only audit of connector parity vs Anthropic's Claude for Small Business bundle. Confirms Nucleus differentiates on memory + voice + relationships + daily flow; defers finance/contracts/content/payments to Anthropic.
- `README.md` — production-quality rewrite. JARVIS-forward, talk-don't-memorize hero, full catalog organized by domain, install in 5 min, Obsidian-as-UI section, recommended install combos, daily/weekly rhythm, who-this-is-for, customization, BrightWay services contact at the bottom.
- `docs/proposals/productization.md` — internal strategy doc. ICP profile, monetization, BrightWay services menu (setup-in-a-day / custom plugin dev / memory-voice training / team rollout / retainer), onboarding flow, demo script (8 min), distribution channels (direct outbound > content > ecosystem visibility), what's explicitly NOT in scope.

Open items for future sessions: optional `/onboarding` chained command, marketplace.json description polishing pass, 6-minute demo screen recording.

### How to use the JARVIS flow

1. Speak naturally to Claude with cortex + nucleus-router installed.
2. Router suggests the right command; user confirms.
3. Output writes to `<config-root>/` markdown files.
4. Open `<config-root>/` in Obsidian to see the graph view; same files visible on phone.

## Recently completed work

- **v0.2 refactor (2026-05-11):** all 12 plugins migrated from plugin-folder-relative paths to `<config-root>/plugins/` paths, eliminating writes to Cowork's read-only mount. See each plugin's CHANGELOG for the v0.2.0 / v0.2.1 entries.
- **Phase 0 platform-agnostic Step 0 (2026-05-12):** every `request_cowork_directory(...)` call in setup commands is wrapped in a Cowork/Claude-Code conditional so the same plugin source works in both runtimes. All 13 plugin patch versions bumped: cortex 4.1.3, weekly-alignment 1.4.3, writing-style 0.1.1, the rest 0.2.3.
- **Phase 1 daily-brief plugin (2026-05-12):** new plugin `daily-brief` v0.1.0 shipped — `/brief` builds a Cowork artifact "Today's Brief" with seven annotated sections; `/process-brief` reads the annotations and routes them (drafts/reschedules/talking-points/dismissals). Phase 1 of the second-brain v2 extension; spec at `docs/proposals/SECOND-BRAIN-V2-SPEC.md`.
- **Phases 3-6 second-brain v2 (2026-05-12):** Phase 2 (separate inbox-triage plugin) deliberately skipped — `daily-brief` keeps its direct Gmail fallback. Shipped: Phase 3 person pages (cortex 4.2.0 + 6 plugins → 0.2.4), Phase 4 cheap-tier commit triage (cortex), Phase 5 `/end-day` orchestration chain (cortex), Phase 6 orphan + duplicate-topic guardrails (cortex). All plugin code pushed to GitHub.
- **Known design note:** `daily-brief` and `plan-tomorrow` overlap significantly on data sources (calendar / CRM / inbox / cortex). Different verbs (`/brief` = today's working surface with annotations + `/process-brief` action loop; `/plan-tomorrow` = tomorrow's calendar blocks). Decision to keep both was deferred — revisit once both are in daily use.
- **cortex v4.3.0 — `/end-day` mining layer (2026-05-12):** three read-only agents at Step 2a (`transcript-reviewer` expanded to two output streams, `conversation-miner` new, `activity-miner` new — scoped to events). Source-agnostic via adapter pattern at `agents/lib/note-source-adapters.md` (Granola / Gemini / Fireflies / Otter / Notion / generic Drive / generic Gmail / custom). Step 2b unified review gate with high-confidence-only toggle, auto-expanded cross-refs, dismissal log. Domain-node Scope convention via one-time migration in `/end-day` Pre-chain B (generic detection, no hardcoded names). New `/setup-sources` command with mandatory adapter health-check. `code-miner` deferred. `[confirmed/recalled]` substrate tags added on knowledge entries.
- **cortex v4.4.0 — forgetting / decay layer (2026-05-12):** the other half of the bidirectional second-brain. Decay model with four states (Fresh / Stale / Dormant / Cold) driven by `[confirmed:...]` age. Defaults at `<config-root>/memory/.decay-config.md` (60/180/365 days; GOTCHA and RECIPE decay 1.5× slower; CORRECTION immune). Per-node `decay_profile: fast | normal | slow` front-matter override. `/recall` flags aging entries inline and offers recall-time triage (re-confirm / demote / archive). `/remember` runs concept-drift detection on new INSIGHT/MODEL/GOTCHA/LESSON writes (Haiku-tier) and prompts the user on supersede/keep-both/edit/skip. New `/rehearse` command + skill: active retention loop, picks 3-5 aging entries weekly via `/end-week` Step 3.5. `/cleanup` deepened with section I for dormant knowledge and section H for cooling/dormant/cold-archive person pages (auto-archive to `memory/person/archive/`). `memory-librarian` ranks Fresh higher and skips `## Demoted knowledge` by default. Content is never auto-deleted; every transition is user-gated.

- **cortex v4.5.0 — legibility upgrade: memory index + research-gaps + Obsidian (2026-05-16):** Phase 1 finish + Phase 2 of the Nucleus-as-JARVIS initiative. Three additions: (1) `/reindex` + indexer skill auto-maintains `<config-root>/memory/index.md` (zero-LLM, deterministic walk + decay classification; runs from `/end-day` Step 5.5, `/cleanup` Step 4.5, and via `/remember`'s `.reindex-queue` marker). (2) `/research-gaps` + new `gap-researcher` subagent + `/merge-research-draft` — seven gap-detection rules (thin entity, stale fact in active rotation, contradiction within a node, orphan, under-cited high-confidence claim, decision gap, sparse domain), web research with ≥2-source rule, private-individual privacy rule enforced, user-gated merge; optional Step 5.5 of `/end-week`. (3) `/setup-obsidian` + `references/obsidian-config-templates/` — idempotent config-only scaffolding for `.obsidian/` + `VAULT.md` over `<config-root>/`; daily-brief snapshots become Obsidian daily notes via folder config; no plugin code change. All shipped to `BrightWayAI/claude-cortex` main.

- **nucleus-router v0.1.0 + v0.1.1 (2026-05-16):** new standalone plugin shipped to `BrightWayAI/nucleus-router`. Always-loaded `route` skill translates natural-language utterances to the right Nucleus slash command and asks for confirmation. Suggest+confirm flow (never auto-dispatches). Initial table covers all 57 commands across 13 prior plugins; v0.1.1 added rows for cortex v4.5 commands. Catalog updated to 14 plugins. Pushed to `BrightWayAI/nucleus`.

- **daily-brief v0.3.0 + cortex v4.6.0 cleanup pass (2026-05-16):** real-user feedback dogfooding the JARVIS flow — `/brief` and `/end-day` felt like overhead because too many fields and steps fired with no actionable downstream. Cuts: (1) daily-brief drops Section 7 (end-of-day prompts), removes meeting annotation textareas (meetings become read-only context cards), hides empty sections in the artifact, hides Section 5 until `/process-brief` produces drafts; removes `add_talking_point` action from `/process-brief`. (2) cortex `/end-day` defaults to quick mode (Steps 3, 4, 5, 5.5, 6) — 30s-3 min; `/end-day --full` adds the heavy steps (1, 2, 2a, 2b) for transcript-heavy days; auto-offer prompt only fires when transcripts ≥ 2 or inbox ≥ 5. Step 4 reflection now writes `## Reflection` to today's brief markdown — the new contract between the two plugins. Both shipped to GitHub.

- **cortex v4.7.0 — overnight learning + hot.md (2026-05-16):** answers "how does this learn while I sleep?" Two new commands and a rolling cache. (1) `/listen` is the nightly autonomous ingest pipeline — pulls yesterday's calendar / Gmail / Slack / Drive / transcripts (via configured note-source adapters) into immutable `<config-root>/archive/YYYY-MM-DD/`. Runs `transcript-reviewer`, `conversation-miner`, `activity-miner` against the archive read-only. Stages all proposed memory commits to `<config-root>/memory/.commit-drafts/YYYY-MM-DD.md`. No user gates — designed for cron via `core-ops /register-schedules` at 11pm or 5am. Modes: default (yesterday), `--date`, `--backfill N`, `--remine` (re-mine existing archive without re-pulling), `--rewrite`. (2) `/morning` is the interactive merge — reads latest `.commit-drafts/`, walks each proposal (accept/reject/edit/defer/skip-remaining), runs v4.4 drift detection on accepts, refreshes `memory/index.md` + `memory/hot.md`, optionally chains into `/brief`. (3) `memory/hot.md` is a rolling 7-day cache — verbatim citations from active nodes (last-week reflections, active people, open threads, recent commitments), capped at 3K words. Loaded first by `/recall` auto-fire so every session opens warm. Refreshed by `/listen` nightly, `/morning` after merge, and `/end-day` Step 5.6. Inspired by Karpathy's LLM-wiki `raw/` immutable source pattern and `hot.md` warm-start. Cortex v4.4.0 → v4.7.0 across three sub-sessions today. Router v0.1.1 → v0.1.2 added intent rows for `/listen` and `/morning`.

- **Karpathy pattern survey (2026-05-16):** `docs/proposals/karpathy-pattern-survey.md` audits every Karpathy pattern (LLM wiki, autoresearch, Software 3.0 talk) against Nucleus's current state. Most major gaps closed by v4.5-4.7. Three remaining high-value, low-cost additions identified: (A) unified `<config-root>/memory/log.md` grep-friendly chronicle of all Nucleus operations, (B) `llms.txt` at the nucleus repo root for agent onboarding (Karpathy Software 3.0 pattern), (C) per-command autonomy slider via `cortex.user-context.md` (`/note: auto`, `/lead-draft: confirm`, etc. — Karpathy Iron Man suit pattern). Status: specced, not yet implemented.
- **Nucleus visibility + consolidation (2026-05-12):** core-ops 0.2.3 → 0.3.0 — new `/nucleus-status` (terse text snapshot) and `/nucleus-dashboard` v1 (Cowork HTML artifact with 6 section cards: stack overview, this-week activity, memory health, outreach pipeline, time+invoicing, impact-loop placeholder). daily-brief 0.1.0 → 0.2.0 — absorbs the deprecated plan-tomorrow plugin (`/plan-tomorrow` + `/setup-plan` now live in daily-brief; user-context backward-compatible). Marketplace catalog count drops 14 → 13. Standalone plan-tomorrow repo deprecated with a redirect README and archived on GitHub.
