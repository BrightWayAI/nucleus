# Cross-plugin contracts

_Enumerated 2026-05-20. Update whenever a plugin starts reading from or writing to a file owned by a different plugin._

These are the **implicit file-format dependencies** between Nucleus plugins. Each row is a contract: one plugin owns the writer, another plugin reads. Changing either side without updating the other breaks the contract silently.

Use this doc as a checklist before merging plugin changes that touch any path listed below.

---

## Foundation files

`<config-root>/identity.md`
- **Writer:** cortex `/setup-identity`
- **Readers:** every plugin (skipped in their setup if exists)
- **Format:** markdown with these sections — `## Identity`, `## Working hours`, `## Tools`, `## Communication preferences`
- **Version:** stable since cortex v4.0
- **Breaking change protocol:** if `identity.md` schema changes, every reader plugin needs a coordinated update. Treat as a Nucleus-wide major version bump.

`<config-root>/voice.md`
- **Writer:** cortex `/setup-voice` and writing-style `/style-learn`
- **Readers:** bizdev-outreach, weekly-outreach, lead-engine, news-curator (post-assembler), client-status, referral-engine, writing-style `/style`
- **Format:** markdown with `## Tone`, `## Vocabulary`, `## Banned phrases`, `## Style rules` sections
- **Version:** stable since cortex v4.0
- **Note:** writing-style v0.x adds entries via `/style-learn` two-stage triage; format remains compatible with cortex readers.

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

---

## Per-plugin user-context files

`<config-root>/plugins/cortex.user-context.md`
- **Writer:** cortex `/setup-sources` (sources section), `/setup-obsidian` (obsidian section); user-editable
- **Readers:** all cortex commands consulting autonomy, hot-cache config, decay config, sources, listen settings, sweep settings (future), memory_as_git settings (future)
- **Sections (as of cortex v4.8.0):** `autonomy:`, `hot_cache:`, `note_sources:`, `listen:`, `decay:`. Future: `sweep:`, `memory_as_git:`
- **Version:** stable schema; sections add over time

`<config-root>/plugins/daily-brief.user-context.md`
- **Writer:** daily-brief `/setup-brief`
- **Readers:** daily-brief `/brief`, `/process-brief`, `/plan-tomorrow`
- **Format:** section toggles, sort defaults, placeholder hints

`<config-root>/plugins/<plugin>.user-context.md`
- Same pattern for every plugin's setup output.

---

## Daily flow contracts

`<config-root>/briefs/<date>.md`
- **Writer:** daily-brief `/brief` (creates), `/end-day` Step 4 (appends `## Reflection` section in v4.6+), `/process-brief` (appends `### Processed annotations`)
- **Readers:** daily-brief next morning's `/brief` Section 6 (reads yesterday's `## Reflection`)
- **Format:** see daily-brief `commands/brief.md` markdown snapshot template
- **Critical contract:** the `## Reflection` section format MUST match between cortex `/end-day` Step 4 (writer) and daily-brief `/brief` Section 6 (reader). If cortex changes the section header or bullet shape, daily-brief breaks silently.

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

`<config-root>/plugins/core-ops/schedules.md` (post-`/register-schedules`)
- **Writer:** core-ops `/register-schedules` (copies from template, annotates with `last_registered_id`)
- **Reader:** Cowork's scheduled-tasks system (via core-ops invocation)
- **Format:** see `core-ops/references/schedules.template.md`
- **Schedule entries reference commands from multiple plugins** — implicit contract that those commands exist.

---

## Subagents (cross-command contracts)

`memory-librarian` (cortex)
- **Called by:** `/recall`, `/search`, `/research-gaps`
- **Returns:** synthesized summary with citations + confidence rating
- **Contract:** read-only; never writes memory

`transcript-reviewer`, `conversation-miner`, `activity-miner` (cortex)
- **Called by:** `/end-day` Step 2/2a, `/listen` Step 3, future `/sweep`
- **Returns:** structured proposal list (type / target node / content / confidence / source)
- **Contract:** read-only against memory; write only to `.commit-drafts/` (post-reorg: `staged/commit-drafts/`)
- **Open: consolidation** — these three agents are slated for consolidation into one `miner` agent with `scope` param (see `cleanup-pass-1.md` item E). If consolidated, callers update accordingly.

`gap-researcher` (cortex)
- **Called by:** `/research-gaps`
- **Returns:** web-researched proposals with ≥2-source rule + privacy rules
- **Contract:** writes only to `staged/research-drafts/` (post-reorg)

`contact-researcher` (lead-engine)
- **Called by:** bizdev-outreach, lead-brief, lead-pull, weekly-outreach, referral-ask
- **Returns:** deep single-contact research summary
- **Contract:** read-only against external systems (CRM, email, web); never writes

`pipeline-analyst`, `pipeline-forecast` (core-ops)
- **Called by:** weekly-outreach, plan-tomorrow, monthly forecast schedule
- **Returns:** ranked pipeline analysis / forward projection

`news-curator`, `post-assembler` (news-curator)
- **Called by:** `/ai-roundup`
- **Returns:** scanned-and-ranked stories / drafted post in user's voice

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
