# Cross-plugin contracts

_Enumerated 2026-05-20; refreshed for the 9-plugin consolidation on 2026-09-15. Update whenever a plugin starts reading from or writing to a file owned by a different plugin._

These are the **implicit file-format dependencies** between Nucleus plugins. Each row is a contract: one plugin owns the writer, another plugin reads. Changing either side without updating the other breaks the contract silently.

Use this doc as a checklist before merging plugin changes that touch any path listed below.

---

## Container rules

- Research finds.
- Comms Desk writes.
- Growth Engine decides who.
- Client Success owns the account after signature.
- Chief of Staff routes and monitors, owns no domain.
- Cortex remembers.
- Today's Brief is every "what's going on" surface at any cadence.
- Admin is money and paperwork.
- Team Alignment is internal coherence.

## Where things live

| Plugin | Owns | Explicitly does not own |
|---|---|---|
| cortex | Identity/voice data files (`memory/me/`), shared memory nodes, decay/rehearsal, indexing, `/listen` + `/morning` ingest pipeline, memory-as-git | Drafting, sending, deciding who to contact, any plugin's user-facing config schema |
| ops | `chief-of-staff` agent (`/cos`), `/status`, `/diagnose`, schedule library (`/register-schedules`), cross-plugin health checks | Any domain workflow (pipeline, drafting, client work, money) — it routes and monitors only |
| briefing | `/brief`, `/review`, `/timeline`, `/dashboard`, and every "what's going on" surface regardless of cadence (daily/weekly/ad hoc) | Deciding what to do about what it surfaces; it renders and annotates, downstream plugins act |
| growth | `pipeline-analyst`/`pipeline-forecast` agents, relationship ranking and outreach targeting decisions (`relationships-director`), signal/referral pipeline | Drafting outreach copy (that's comms), owning the client relationship post-signature (that's clients) |
| clients | The account after signature — engagement lifecycle, client-status drafts, deliverable QA | New-business decisioning (growth), invoicing/billing (admin) |
| comms | Voice capture (`setup-voice`), all drafting (`post-assembler` agent, `/post`, `/style*`) | Deciding who to contact or what to research; it writes, it doesn't decide or find |
| admin | Money and paperwork — time tracking, invoice generation | Any non-financial client or relationship workflow |
| research | Finding and ranking — `news-curator` agent, `/roundup` staging to `staged/roundup/` | Drafting the final post (comms owns `/post` via `post-assembler`) |
| alignment | Internal cross-team coherence — Slack scanning via `alignment-scanner` | External-facing communication or client/relationship decisions |

---

## Foundation files

`<config-root>/memory/me/identity.md`
- **Writer:** cortex `/setup-identity`
- **Readers:** every plugin (skipped in their setup if exists)
- **Format:** markdown with stable `Actor ID` plus person, company, primary tools, and communication-default sections
- **Version:** stable since cortex v4.0
- **Breaking change protocol:** if `identity.md` schema changes, every reader plugin needs a coordinated update. Treat as a Nucleus-wide major version bump.

`<config-root>/memory/me/voice.md`
- **Writer:** comms `/setup-voice` and comms `/style-learn`
- **Readers:** growth, comms (`post-assembler`), clients `/client-status`, comms `/style`
- **Format:** markdown with `## Tone`, `## Vocabulary`, `## Banned phrases`, `## Style rules` sections
- **Version:** stable since cortex v4.0
- **Note:** the file itself is cortex-owned data (lives under cortex's `memory/me/` scope), but the capture/interview command moved to comms's `/setup-voice` in the Phase 2 capability moves (2026-09-15). `/style-learn` two-stage triage still adds entries; format remains compatible with cortex readers.

---

## Memory files

`<config-root>/memory/index.md`
- **Writer:** cortex `indexer` skill (auto-maintained; zero-LLM)
- **Readers:** cortex `memory-librarian` agent, Obsidian users browsing the vault, any non-cortex agent that wants a catalog entry point
- **Format:** see `cortex/references/memory-index.md`
- **Version:** added in cortex v4.5.0
- **Refresh triggers:** `/end-day` Step 5.5, `/cleanup` Step 4.5, explicit `/reindex`, `/listen`/morning post-merge

`<config-root>/memory/hot.md`
- **Writer:** cortex hot-cache regeneration (zero-LLM file walk)
- **Readers:** cortex `/recall` Step 0 auto-fire
- **Format:** see `cortex/references/hot-cache.md`
- **Version:** added in cortex v4.7.0
- **Refresh triggers:** `/listen`, `/morning` post-merge, `/end-day` Step 5.6
- **Configurable:** `cortex.user-context.md` `hot_cache.enabled: false` disables

`<config-root>/memory/log.md`
- **Writer:** cortex `log-writer` skill (centralized v4.7.2+)
- **Readers:** humans (via `grep`), Obsidian, `/diagnose` for activity audit
- **Format:** see `cortex/references/log-chronicle.md`
- **Version:** centralized in cortex v4.7.2; format stable
- **Append rule:** never modify prior entries; entries are `## [YYYY-MM-DD HH:MM] <op> | <summary>`

`<config-root>/memory/triage-log.md`
- **Writer:** cortex `/remember` Step 0 cheap-tier triage (v4.2+)
- **Readers:** `/remember` (dedup against recent triage decisions), `/sweep` (when shipped, for dedup)
- **Format:** see `cortex/CLAUDE.md` triage-log section
- **Version:** stable since cortex v4.2

`<config-root>/memory/DASHBOARD.md`
- **Writer:** cortex `/remember` Step 3 (active node summaries)
- **Readers:** cortex `/recall` auto-fire, `memory-librarian`
- **Format:** see `cortex/commands/remember.md` Dashboard File Format
- **Version:** stable since cortex v4.0

`<config-root>/memory/.decay-config.md`
- **Writer:** cortex (auto-created on first v4.4+ run); user-editable
- **Readers:** `indexer`, `memory-librarian`, `/recall` decay flagging, `/cleanup`, `/rehearse`
- **Format:** YAML thresholds + per-type modifiers
- **Version:** added cortex v4.4.0

---

## Staged-state files (post-v4.8.1 reorg paths)

`<config-root>/memory/staged/commit-drafts/<date>.md`
- **Writer:** cortex `/listen` Step 4
- **Reader:** cortex `/morning`
- **Format:** structured proposals with type / target node / confidence / source
- **Pre-v4.8.1 path:** `<config-root>/memory/.commit-drafts/<date>.md` (auto-migrated on next load)

`<config-root>/memory/staged/research-drafts/<date>-research-gaps.md`
- **Writer:** cortex `gap-researcher` agent (invoked by `/research-gaps`)
- **Reader:** cortex `/merge-research-draft`
- **Format:** see `cortex/agents/gap-researcher.md` output section
- **Pre-v4.8.1 path:** `<config-root>/memory/.research-drafts/<date>-research-gaps.md`

`<config-root>/memory/staged/heartbeat-drafts/<today>.md` (proposed; not yet shipped)
- **Writer:** cortex `/sweep` (future)
- **Reader:** cortex `/end-day` Step 3.5 (future)
- **Spec:** `nucleus/docs/proposals/sweep-heartbeat.md`

`<config-root>/memory/staged/queues/reindex`
- **Writer:** cortex `/remember` Step 3.5 (deferred refresh marker)
- **Reader:** cortex `indexer` skill (consumes on next run, deletes marker)
- **Format:** appendable, one line per touched node; ignored if > 200 lines (just full regenerate)
- **Pre-v4.8.1 path:** `<config-root>/memory/.reindex-queue`

`<config-root>/memory/staged/queues/rehearse.md`
- **Writer:** cortex `/cleanup` section I (deferred entries)
- **Reader:** cortex `/rehearse` (priority queue)
- **Pre-v4.8.1 path:** `<config-root>/memory/.rehearse-queue.md`

`<config-root>/memory/staged/skip-logs/rehearse.md`
- **Writer:** cortex `/rehearse` (skip + suppress 30 days)
- **Reader:** cortex `/rehearse` (next-batch selection respects skip-log)
- **Pre-v4.8.1 path:** `<config-root>/memory/.rehearse-skip-log.md`

`<config-root>/memory/staged/skip-logs/research.md`
- **Writer:** cortex `/research-gaps` and `/merge-research-draft` (rejected gaps)
- **Reader:** cortex `/research-gaps` (suppress repeats for 90 days)
- **Pre-v4.8.1 path:** `<config-root>/memory/.research-skip-log.md`

`<config-root>/memory/staged/skip-logs/morning-reject.md`
- **Writer:** cortex `/morning` (rejected proposals)
- **Reader:** future `/listen` runs (suppress proposing the same thing)
- **Pre-v4.8.1 path:** `<config-root>/memory/.morning-reject-log.md`

`<config-root>/staged/roundup/<date>.md`
- **Writer:** research `/roundup` (stages picked candidates; never drafts)
- **Reader:** comms `/post` (drafts the roundup post in the user's voice via `post-assembler`); `/roundup --draft` chains straight into `/post` when comms is installed
- **Format:** summaries + source links + themes; see `research/commands/roundup.md`
- **Contract:** research finds and stages, comms writes; `/roundup` completes normally with a "drafting unavailable" note if comms isn't installed

---

## Per-plugin user-context files

`<config-root>/plugins/cortex.user-context.md`
- **Writer:** cortex `/setup-sources` (sources section), `/setup-obsidian` (obsidian section); user-editable
- **Readers:** all cortex commands consulting autonomy, hot-cache config, decay config, sources, listen settings, sweep settings (future), memory_as_git settings (future)
- **Sections (as of cortex v4.8.0):** `autonomy:`, `hot_cache:`, `note_sources:`, `listen:`, `decay:`. Future: `sweep:`, `memory_as_git:`
- **Version:** stable schema; sections add over time

`<config-root>/plugins/briefing.user-context.md`
- **Writer:** briefing `/setup-brief`
- **Readers:** briefing `/brief`, `/process-brief`, `/plan-tomorrow`
- **Format:** section toggles, sort defaults, placeholder hints

`<config-root>/plugins/clients.user-context.md`
- **Writer:** clients `/setup-projects`; user-editable
- **Readers:** clients project workflows, clients `/client-status`, admin invoice/project resolution
- **Format:** engagement catalog, client/project aliases, commercial defaults, and connector mapping
- **Migration:** may import once from `project-setup.user-context.md`; runtime must not depend on the retired plugin path

`<config-root>/plugins/clients-status.user-context.md`
- **Writer:** clients `/setup-status`; user-editable
- **Readers:** clients `/client-status`
- **Format:** reporting cadence, audiences, sections, delivery channels, and approval defaults
- **Migration:** may import once from `client-status.user-context.md`; runtime must not depend on the retired plugin path

`<config-root>/plugins/<plugin>.user-context.md`
- Same pattern for every plugin's setup output.

---

## Daily flow contracts

`<config-root>/briefs/<date>.md`
- **Writer:** briefing `/brief` (creates), `/end-day` Step 4 (appends `## Reflection` section in v4.6+), `/process-brief` (appends `### Processed annotations`)
- **Readers:** briefing next morning's `/brief` Section 5 (Yesterday's Reflection — reads yesterday's `## Reflection`)
- **Format:** see briefing `commands/brief.md` markdown twin template
- **Critical contract:** the `## Reflection` section format MUST match between cortex `/end-day` Step 4 (writer) and briefing `/brief` Section 5 (reader). If cortex changes the section header or bullet shape, briefing breaks silently. cortex `/end-day` Step 4.2 also appends the same reflection to `<config-root>/memory/me/reflections.md` (longitudinal store).

`<config-root>/briefs/` directory (folder-level contract)
- **Daily-notes integration:** cortex `/setup-obsidian` writes `.obsidian/daily-notes.json` pointing at this folder. Obsidian's daily-notes plugin reads it. Contract: `briefs/<YYYY-MM-DD>.md` filename format must hold.

---

## Archive + raw substrate

`<config-root>/archive/<date>/`
- **Writer:** cortex `/listen`
- **Readers:** cortex mining agents (read-only against own archive), `/listen --remine`
- **Format:** see `cortex/references/archive-layout.md`
- **Immutability rule:** archives are append-only after creation; `/listen` refuses to overwrite an existing date unless `--rewrite`.
- **Privacy:** the most sensitive directory in `<config-root>/`. Always excluded from git via the v4.7.2 gitignore template.

---

## Schedule library

`<config-root>/plugins/ops/schedules.md`
- **Writer:** user or ops `/register-schedules` when copying the immutable starter
- **Reader:** ops `/register-schedules`; host schedulers receive translated definitions
- **Format:** see `ops/references/schedules.template.md`
- **Schedule entries reference commands from multiple plugins** — implicit contract that those commands exist.

`<config-root>/plugins/ops/schedule-registrations/<host-id>.json`
- **Writer:** ops `/register-schedules`, atomically after a confirmed scheduler mutation
- **Reader:** ops `/register-schedules` reconciliation on that host
- **Format:** schema `1.0.0`; scheduler ID + definition fingerprint + registration/verification timestamps
- **Host boundary:** never sync an ID as if it were portable; live scheduler state wins over the cache

`<config-root>/plugins/ops/schedule-runs/<schedule>/<run-id>.json`
- **Writer:** scheduled workflow when the host permits local receipt writes
- **Readers:** `/diagnose`, `/nucleus-status`, humans auditing automation
- **Format:** metadata only — outcome, source coverage statuses, output paths/hashes, sanitized error codes; never connector payloads or memory content

---

## Collaborative memory writes

`<config-root>/memory/proposals/<actor-id>/<date>/<proposal-id>.md`
- **Writer:** the actor's proposal-producing workflow; append-only/immutable after creation
- **Reader:** the designated Cortex merge workflow
- **Format:** Cortex `references/shared-memory-writes.md` schema `1.0.0`
- **Boundary:** required before multiple actors write the same shared memory; raw connector content and `memory/me/` data are forbidden

`<proposal-id>.decision.jsonl`
- **Writer:** designated merge workflow under the shared Cortex lock
- **Reader:** humans and replay/idempotency checks
- **Format:** append-only decision events (`accepted`, `rejected`, `conflict`, `superseded`) with reviewer actor and resulting revision

---

## Subagents (cross-command contracts)

`memory-librarian` (cortex)
- **Called by:** `/recall`, `/search`, `/research-gaps`
- **Returns:** synthesized summary with citations + confidence rating
- **Contract:** read-only; never writes memory

`note-taker` (cortex; mode: transcript / conversation / activity)
- **Called by:** `/end-day` Step 2/2a, `/listen` Step 3, future `/sweep`
- **Returns:** structured proposal list (type / target node / content / confidence / source)
- **Contract:** read-only against memory; write only to `.commit-drafts/` (post-reorg: `staged/commit-drafts/`)
- **Version:** the three former mining roles were consolidated into this explicit mode-dispatched role in cortex v4.19.0.

`gap-researcher` (cortex)
- **Called by:** `/research-gaps`
- **Returns:** web-researched proposals with ≥2-source rule + privacy rules
- **Contract:** writes only to `staged/research-drafts/` (post-reorg)

`relationships-director` (growth; mode: rank / research)
- **Called by:** growth ranking and touchpoint workflows, including the absorbed signal and referral flows
- **Returns:** ranked relationship actions or a deep single-contact research summary, according to the caller-selected mode
- **Contract:** read-only against external systems (CRM, email, web); never writes

`pipeline-analyst`, `pipeline-forecast` (growth)
- **Called by:** growth (new-business bucket), briefing planning, clients, admin, and forecast schedules
- **Returns:** ranked pipeline analysis / forward projection
- **Version:** moved from ops to `growth/agents/` in the Phase 2 capability moves (2026-09-15); ops retains only `/status` and `/diagnose`.

`news-curator` (research)
- **Called by:** `/roundup`
- **Returns:** scanned-and-ranked stories with citations, staged for handoff (never drafts)

`post-assembler` (comms)
- **Called by:** `/post`
- **Returns:** drafted post in the user's voice from research's staged candidates or pasted material
- **Version:** moved from research to `comms/agents/` in the Phase 2 capability moves (2026-09-15).

---

## Growth plugin

`<config-root>/plugins/relationships.user-context.md`
- **Writer:** growth `/setup-relationships`
- **Readers:** growth `/relationships`, `/network-rebalance`, `/draft-touchpoint`, `/relationships-action`
- **Sections (v0.3.0+):** `## Identity`, `## Companion plugins`, `## ICP & signal sourcing`, `## Referral network`, `## Tiers`, `## Close personal track`, `## Buckets`, `## Network-expansion voices`, `## Time budget`, `## Scoring overrides`, `## Standalone-install fallbacks`, `## Provenance`.
- **Peer-import behavior:** identity, voice, and CRM are read from their canonical Cortex, comms, and ops files when present. ICP, Apollo/signal preferences, referral taxonomy, and cooling rules are native to growth as of v0.3.0; setup may migrate them once from legacy lead-engine/referral-engine config files, but runtime does not depend on those retired plugins.
- **Version:** added in growth v0.1.0; native signal/referral sections added in v0.3.0.

`<config-root>/relationships/today.md`
- **Writer:** growth `/relationships` (Phase 2)
- **Readers:** humans, Obsidian, briefing (loose-coupling integration TBD), future web-app / Operator desktop reader
- **Format:** markdown brief — header + 3 buckets × 3 options × (person + why-now + channel + time + draft body) + carrying footnote
- **Version:** added in growth v0.1.0

`<config-root>/relationships/<YYYY-MM-DD>.md`
- **Writer:** growth `/relationships` (date-stamped copy of today.md; today.md is symlinked or duplicated)
- **Readers:** historical audit, Obsidian daily-notes (if folder is included in daily-notes config), future web-app
- **Version:** added in growth v0.1.0

`<config-root>/relationships/today.json`
- **Writer:** growth `/relationships`
- **Readers:** future web-app, Operator desktop, briefing render layer (if tight coupling adopted later), sync daemon
- **Format:** see growth `references/today-json-schema.md`. Schema version `0.1.0`. Includes `brief_id` (UUID v4) and stable option IDs in form `<bucket>_<slug>_<date>`.
- **Version:** added in growth v0.1.0; stable-ID + brief_id added in v0.1.1

`<config-root>/relationships/events.jsonl`
- **Writer:** growth `/relationships-action` (and inline path in `/relationships` Step 7 — both write the same event shape)
- **Readers:** future web-app (analytics: completion rate, channel mix, response time, late-action patterns), `/relationships-stats` (future)
- **Format:** append-only newline-delimited JSON. One event per line. See growth `commands/relationships-action.md` Step 3 for the event shape.
- **Append rule:** never modify prior entries. Atomic appends only.
- **Version:** added in growth v0.1.1

`<config-root>/relationships/snoozes.json`
- **Writer:** growth `/relationships-action` when `action: snoozed`
- **Readers:** growth `/relationships` Step 3 (filter candidate pool against active snoozes), future web-app
- **Format:** JSON array of `{ slug, until_date, reason?, snoozed_at, brief_id }` objects. Entries with `until_date < today` are auto-expired (kept for audit).
- **Version:** added in growth v0.1.1

`<config-root>/relationships/inbox/` (directory)
- **Writer:** future UI / sync daemon — drops `<uuid>.json` event payloads here
- **Reader:** growth `/relationships-action --file=<path>` — processes one event per invocation, moves file to `inbox/processed/` on success or `inbox/quarantine/` if malformed
- **Format:** JSON event payload per file. See growth `commands/relationships-action.md` Step 1 for the schema.
- **Version:** added in growth v0.1.1

`<config-root>/relationships/templates/<channel>/<scenario>.md` (optional user overrides)
- **Writer:** user (manually)
- **Readers:** growth template loader — overrides bundled defaults by filename
- **Format:** frontmatter schema documented at growth `references/templates/README.md`
- **Version:** added in growth v0.1.0

`<config-root>/memory/team/<slug>.md` (cortex-owned; internal team members)
- **Convention emerging from growth v0.1.x:** internal team members (BrightWay contractors, employees) live under `memory/team/` instead of `memory/person/`. The growth plugin **explicitly does not scope `team/` into its briefing candidate pool** — internal team are collaborators, not subjects of relationship maintenance.
- **Migration trigger:** `/network-rebalance` proposes migrating a `person/` page to `team/` when the page indicates an internal-team role (same-domain email, "Role at BrightWay" section, contractor agreement, etc.). User-gated.
- **Cortex coordination (still pending formal cortex schema bump):** formalize `team/` as a recognized node type in `cortex/references/node-taxonomy.md`. Cortex v4.12.0 shipped memory-as-git + sync-linked-entities + DASHBOARD provenance but did NOT include the `team/` taxonomy formalization — that remains a separate cortex PR. Until then, `team/` works because cortex is permissive about new prefixes (the indexer walks all `memory/*/` subdirs).

`<config-root>/memory/person/<slug>.md` (cortex-owned; growth reads + appends additively)
- **Existing writer:** cortex (graduation, /recall, /remember)
- **New behavior:** growth `/relationships` Step 7 appends to **## Recent interactions** log when the user marks a card "done." Never modifies Identity, Notes, or other sections.
- **Schema additions (additive YAML frontmatter under the `relationships:` namespace):** `tier`, `intent` (v0.2.0+), `buckets`, `relationship_class`, `icp_fit`, `next_touch_target`, `cadence_days_override` (v0.2.0+), `preferred_channels` (array, v0.1.2+; single `preferred_channel` accepted for backward compat), `generosity_ledger`. The `intent` field encodes the dynamic of engagement (client_delivery / drive_active / door_opening / reciprocal / advising / content_share / keep_warm / passive_visibility / awaiting_reply) as an axis orthogonal to but constrained by `tier`. See growth `references/person-page-extensions.md` for the full schema and validation rules.
- **Cortex coordination:** small additive schema bump (candidate cortex v4.12.0). Existing pages remain valid; plugin treats missing frontmatter as sensible defaults. Future plugins writing to person pages should use their own frontmatter namespace (e.g., `referral_engine:`, `weekly_outreach:`) to avoid collisions.

---

## Memory-as-git (cortex v4.12.0+)

`<config-root>/memory/.git/`
- **Writer:** cortex `/setup-identity` Step 3.6 (init) · cortex `/end-day` Step 5.8 (daily commit) · cortex `/morning` Step 0.5 (read for diff)
- **Readers:** cortex `/morning` Step 0.5 (`git diff HEAD~1..HEAD`); humans via Obsidian Git plugin if installed; optional remote (private GitHub / self-hosted)
- **Format:** standard git repo at memory/ root. Initial commit by `/setup-identity`; per-day commits by `/end-day`.
- **Version:** added cortex v4.12.0. Backward compat: `/end-day` Step 5.8 is a no-op if `.git/` doesn't exist (memory-as-git not enabled).

`<config-root>/memory/.gitignore`
- **Writer:** cortex `/setup-identity` Step 3.6 (from `cortex/references/memory-gitignore-template.md`)
- **Readers:** git itself; humans editing memory-tracking rules
- **Format:** see `cortex/references/memory-gitignore-template.md`. Excludes `staged/`, `hot.md`, `index.md`, `log.md`, `.state.json`, deprecated pre-v4.8.1 dotfiles.
- **Version:** added cortex v4.12.0

`<config-root>/plugins/cortex.user-context.md` — `memory_as_git:` section (additive)
- **Writer:** cortex `/setup-identity` Step 3.6 (writes section when user opts in to a remote); user-editable thereafter
- **Readers:** cortex `/end-day` Step 5.8 (reads `push_on_close`); cortex `/morning` Step 0.5 (reads `morning_diff`)
- **Fields:** `enabled`, `remote`, `push_on_close`, `morning_diff`
- **Version:** added cortex v4.12.0

---

## Dashboard artifact template

`briefing/references/nucleus-dashboard-template.html`
- **Writer/owner:** briefing (`/dashboard`)
- **Reader:** briefing's `dashboard` skill when rendering the Cowork HTML artifact
- **Version:** moved from ops (`core-ops`, pre-rename) to `briefing/references/` in the Phase 2 capability moves (2026-09-15), alongside the `/dashboard` command itself. `ops/commands/nucleus-dashboard.md` remains a thin deprecated-alias redirect; ops retains only `/status` and `/diagnose` as real commands.

## DASHBOARD line provenance (cortex v4.12.0+)

`<config-root>/memory/DASHBOARD.md` — provenance comments on every line
- **Writer:** cortex `/remember` Step 3 emits `<!-- by:<command> @ <YYYY-MM-DD> -->` on every DASHBOARD line write/update
- **Reader:** cortex `/cleanup` Section L (DASHBOARD staleness scan) — surfaces lines whose owning command hasn't refreshed in N days, lines with missing provenance, and lines referencing archived/renamed nodes
- **Format:** HTML-comment syntax renders invisibly in Markdown previews. Per-line stale thresholds: auto-mining commands (7d), user-driven (30d), manual (60d). Override per-line via `<!-- by:<cmd> @ <date> · stale-after:<days> -->`.
- **Version:** added cortex v4.12.0. Backward compat: lines without provenance still parse; `/cleanup` Section L surfaces them as "missing-provenance" candidates.

---

## Cross-plugin: briefing artifact id ↔ cortex /end-day Step 5

`mcp__cowork__update_artifact(id: "todays-brief", ...)` — the canonical interactive brief surface
- **Writers:**
  - briefing `/brief` (Steps 3-3a — render full artifact)
  - cortex `/end-day` Step 5 (pre-stage tomorrow's brief; uses same `todays-brief` id and same 5-section canonical format)
- **Readers:**
  - briefing `/process-brief` Step 1 (reads `tasks` + `annotations` + `outreach_actions` via `read_widget_context`)
  - cortex `/end-day` **Step 2c** (mines `tasks` + `annotations` + `outreach_actions` → memory write-backs + suppression learning) and Step 4.0 (reflection pre-fill)
  - humans via Cowork artifact UI
- **Artifact id rule:** the id is ALWAYS `todays-brief` — both plugins reference the same persistent surface. **Never** create a new artifact with a different id. Never produce a markdown-only fallback when Cowork is available.
- **Canonical 5-section format (v0.5.0 + cortex v4.13 — End-Day Routine Improvement Spec, supersedes the v0.4 6-section format):**
  1. **Center of Gravity** — accent banner, the single most important thing; not interactive
  2. **Calendar Block** — visual timeline strip + written list with per-meeting notes
  3. **Priority Tasks** — P0/P1, richer per-row actions (done/delegate/skip/not_important/annotate) + progress bar
  4. **Outreach Queue** — per-contact actions (sent/nudge/skip/let_go) + always-visible bucket/signal/value-add selects + per-contact research link
  5. **Yesterday's Reflection** — read-only
- **Template layout source (v0.5.0):** `references/brief-artifact-template.html` follows the handoff spec-v2 reference (`todays-brief.reference-2026-06-09.html`). The visual calendar strip is built client-side by `buildTimeline()` from a JS `BLOCKS` array — the skill fills `{{TL_BLOCKS_JSON}}` (decimal-hour `{s,e,label,cls}`, cls meeting/focus/personal) + `{{TL_START_HOUR}}`/`{{TL_END_HOUR}}`, NOT pre-positioned divs. Token scheme: `{{DATE_LONG}}`/`{{DATE_ISO}}`/`{{CENTER_OF_GRAVITY}}`/`{{EVENT_*}}`/`{{TASK_*}}`/`{{CONTACT_*}}`/`{{REFLECT_*}}` + tokenized `cowork-artifact-meta` (`{{META_DESCRIPTION}}`/`{{META_MCP_TOOLS}}`/`{{META_MCP_SERVERS}}`) + auto-sync tokens (v0.6.1: `{{FS_WRITE_TOOL}}` = verified fully-qualified MCP write tool or empty, `{{STATE_MIRROR_PATH}}` = absolute state-file path). Outreach signal auto-fills by emitting the matching `<option>` first.
- **localStorage state contract (canonical v0.6.0 shape):** SINGLE JSON-blob at key `brief-YYYY-MM-DD`: `{schema_version:"0.6.0", tasks:{<task_id>:{action,detail,priority,reprioritized,ts,name}}, annotations:{<item_id>:str}, outreach_actions:{<id>:{name,action,bucket,signal,value_add,detail,ts}}, tasks_checked:{<task_id>:bool}, last_interaction_at:iso8601}`. `tasks_checked` is a **back-compat mirror** — the template sets it `(action==="done")` on every task action so v0.4.x readers keep working; new readers use `tasks`. `outreach_actions.detail` is **reader-optional** — the v2 brief UI has no outreach detail prompt, so it's typically absent; readers that defer on `skip` default to ~3 days when it's empty.
- **Brief-state read chain (v0.6.1 + cortex v4.13.2):** localStorage is sandboxed inside the artifact and Cowork exposes **no widget-context handle for persisted artifacts**, so readers (`/end-day` Step 2c + 4.0, `/process-brief` Step 1) use: **(1)** state-mirror file `<config-root>/briefs/<date>.state.json` → **(2)** `read_widget_context` (legacy) → **(3)** paste path (user clicks 🔄 Sync for end-day, pastes blob; reader validates and writes the state file itself) → **(4)** `/end-day`'s multi-select fallback gate.
- **State-mirror file contract:** `<config-root>/briefs/<date>.state.json` — verbatim copy of the localStorage blob. **Writers:** the artifact's `mirrorState()` on every action, but ONLY when `/brief` Step 3.0 resolved a filesystem MCP write tool, verified it in-session, and declared it in the artifact's `mcp_tools` allowlist (the Cowork sandbox rejects undeclared / non-`mcp__<server>__<tool>` names, and has no built-in file access — this is why the v0.6.0 mirror silently never fired); `/brief` Step 3.0's verify-write (empty blob if missing — a zero-action day still yields a file); `/end-day` 2c.0p + `/process-brief` paste paths. **Readers:** cortex `/end-day` Step 2c/4.0, briefing `/process-brief`. Freshness: readers treat a file whose `last_interaction_at` predates the target date as absent.
- **Brief filtering contract:** briefing `/brief` reads `<config-root>/memory/me/surfacing-prefs.md` and filters priority tasks + outreach before render. cortex `/end-day` Step 2c.3 writes that file (not_important actions + repeat-ignore rule). See the surfacing-prefs contract below.
- **Tomorrow seed contract:** cortex `/end-day` Steps 4.5/4.6 write `<config-root>/briefs/<tomorrow>.seed.json` `{priorities:[...], outreach:[...]}`; briefing `/brief` reads it (when `target_date` matches) to seed sections 3 & 4.
- **Data-flow trace for annotations:** content may transit artifact localStorage → `.state.json` mirror (or paste path) → cortex `/end-day` Step 2c/4.0 → memory write-backs / reflection prompts → `<config-root>/briefs/<today>.md` + `memory/me/reflections.md` → if memory-as-git enabled, committed. **`/end-day` sanitizes annotations** (paraphrase, do NOT copy verbatim) to keep sensitive client content out of the committed trail.
- **Version:** briefing v0.6.1 + cortex v4.13.2 (state-mirror fix + paste path, 2026-07-07; base 5-section format from briefing v0.5.0 + cortex v4.13.0, 2026-06-08).

### surfacing-prefs.md (cortex /end-day writer ↔ briefing /brief reader)

`<config-root>/memory/me/surfacing-prefs.md`
- **Writer:** cortex `/end-day` Step 2c.3 (not_important actions + repeat-ignore rule); created from `cortex references/surfacing-prefs-template.md` if missing.
- **Readers:** briefing `/brief` Step 0D (filters priority-task + outreach pulls before render); cortex miners (skip dismissed classes).
- **Format:** markdown — `## Do-not-resurface`, `## Surfacing rules`, `## Action taxonomy (brief priority tasks)`, `## Outreach action taxonomy`, `## Changelog`.
- **Related:** per-task skip counts in `<config-root>/memory/.brief-skip-counts.json` (`{task_id:{count,last_skipped,title}}`).

### reflections.md (longitudinal reflection store)

`<config-root>/memory/me/reflections.md`
- **Writer:** cortex `/end-day` Step 4.2 (append newest-first); created from `cortex references/reflections-template.md`.
- **Readers:** `/end-week`, `/review`, surfacing decisions.
- **Format:** markdown, one `## YYYY-MM-DD (Day)` block per day with biggest-thing-done / blocker / one-thing-tomorrow bullets. Decays slowly; excluded from the v4.4 decay sweep.

---

## Sync linked entities (cortex v4.12.0+)

`<config-root>/memory/staged/skip-logs/sync-linked.md`
- **Writer:** cortex `/sync-linked-entities` on user `(s)kip` action (logs candidates suppressed for 30 days)
- **Reader:** cortex `/sync-linked-entities` (consults to skip recently-suppressed candidates)
- **Format:** append-only `(source-slug, linked-slug, candidate-id, skip-date, reason)` tuples
- **Version:** added cortex v4.12.0

---

## events.jsonl unified shape (growth v0.2.2+)

`<config-root>/relationships/events.jsonl`
- **Writers:** growth `/relationships-action`, `/relationships` Step 7, `/touchpoint`. All three append using the unified v0.2.2 shape.
- **Reader contract — v0.2.2 unified shape:**
  ```json
  {
    "schema_version": "0.2.2",
    "ts": "<ISO 8601 with TZ>",
    "brief_id": "<UUID or null>",
    "option_id": "<id or null>",
    "person_slug": "<slug>",
    "bucket": "<bucket or null>",
    "channel": "<channel>",
    "action": "copied" | "sent" | "skipped" | "snoozed" | "touchpoint",
    "notes": "<user-supplied text; truncated to keep total event <4KB>",
    "meta": {
      "snooze_until": "<YYYY-MM-DD or null>",
      "late_action": "<bool or null>",
      "source": "<inline|file|natural-language|explicit-args or null>",
      "direction": "<in|out or null>",         // touchpoint-only
      "intent_at_time": "<intent value or null>",  // touchpoint-only
      "tier_at_time": "<tier value or null>"       // touchpoint-only
    }
  }
  ```
- **Backward-compat reader rule:** if `schema_version` missing → treat as v0.2.0 (pre-meta) format; read top-level `snooze_until`, `late_action`, `source` directly. If `meta` missing on a v0.2.0 event, fields read from the top level.
- **Forward-compat rule:** readers MUST ignore unknown `action` enum values gracefully (treat as a generic logged event) and unknown fields inside `meta`.
- **Atomic-append safety (v0.2.2+):** each event line MUST be ≤ 4000 bytes to guarantee POSIX `O_APPEND` atomicity (PIPE_BUF is typically 4096 on macOS/Linux). Writers truncate `notes` if needed and append a `[truncated]` marker; full text lives on the person page Recent Interactions section. Use single `write()` system call (not multiple appends — they're not atomic across calls).
- **Concurrent-writer guarantee:** with the 4KB cap + O_APPEND, three writers in parallel can safely append without corruption. Without the cap, interleaving would corrupt the JSONL.
- **Version history:** v0.1.1 introduced events.jsonl. v0.2.0 added `schema_version` and basic event shape. v0.2.1 added `/touchpoint` with divergent shape (bug). v0.2.2 unified the shape with `meta` nesting + atomic-append cap.

---

## How to use this doc

When you propose a change to a plugin that touches a path listed above:

1. Identify the row in this doc.
2. Note all readers.
3. Plan coordinated updates if the format changes.
4. If a format change is breaking, treat as a Nucleus-wide version event — not a per-plugin patch.

When you write a new plugin or feature that reads from / writes to a path owned by another plugin:

1. Add a row to this doc.
2. Link to the format spec.
3. Note the writer's version + your reader's expectations.

This is a living doc. Append entries; don't delete unless the path is removed entirely.
