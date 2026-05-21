# Wikilink density — make the graph view actually show edges

_Created: 2026-05-20_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Ships as cortex v4.10.0 same-session._
_Trigger: real-user diagnostic. Memory scan showed 28 wikilinks across 30 node files; Obsidian graph view mostly disconnected._

---

## Diagnosis

A diagnostic scan against the user's `<config-root>/memory/` returned:
- 30 .md node files (3 client, several domain, no person pages)
- 28 total `[[` openings across all files
- ~1 wikilink per file average → almost no graph edges

The Obsidian graph view requires `[[wikilink]]` syntax to draw edges between files. Without wikilinks, the graph shows isolated nodes.

Four root causes:

1. **No person pages have graduated.** `memory/person/` doesn't exist. The v4.2 graduation pattern (recall counter ≥ 3 → propose graduation) doesn't seem to be firing in practice — either the counter file isn't being written, the explicit `/recall person:X` / `/recall @X` paths aren't being hit (auto-recall doesn't increment), or the prompt was dismissed and never re-surfaced.

2. **Cortex schemas use brackets as *placeholders*, not as wikilinks.** When `commands/remember.md` shows `[Name] ([role]) — [context]`, those brackets are template placeholders. Real entries get written as `Kim Smith (CEO) — primary contact` without any `[[...]]` syntax. Obsidian needs the double-bracket wikilink form.

3. **Mining agents emit entity mentions as plain strings.** When `/listen` or `/remember` extracts "Sarah mentioned X," the entity name is written as a string, not as `[[person/sarah]]`. Even when a person page exists, mining doesn't link to it.

4. **Changelog and cross-node references are plain text.** `[2026-05-15] Talked with Kim about the proposal` doesn't link to Kim. Each daily changelog entry is an opportunity for an edge that's currently missed.

## The four-part fix (shipping as cortex v4.10.0)

### A. Schema wikilink discipline

Update cortex command, agent, and reference files to use real wikilink syntax where edges should exist. Key replacements:
- `[Name] ([role]) — [context]` → `[[person/<slug>]] ([role]) — [context]`
- `[node-id]` (when used as a *content reference*, not a slash-command argument placeholder) → `[[<node-id>]]`
- Changelog entries mentioning entities → `[date] Talked with [[person/<slug>]] about [[topic/<slug>]]`
- DECISION `Affected:` field → `[[entity]], [[entity]]` (already wikilink-formatted in v4.9 schema)
- Workstream `Linked entities:` → `[[<type>/<slug>]]` (already wikilink-formatted)

Touches: `CLAUDE.md`, `commands/remember.md` Step 2 templates, `commands/recall.md` output templates, `agents/transcript-reviewer.md`, `agents/conversation-miner.md`, `agents/activity-miner.md`, `agents/memory-librarian.md`, `skills/observe/SKILL.md`.

### B. Mining-time wikilink injection

Mining agents (and `/remember` Step 2 extraction) get explicit logic:

> "When emitting a person, client, company, topic, workstream, or domain mention: check whether a matching node file exists at `memory/<type>/<slug>.md`. If yes, emit as `[[<type>/<slug>]]`. If no, emit as plain text — and increment a `mention-counter` for potential future graduation."

The slug derivation is deterministic: `kim-smith` from "Kim Smith"; `acme-corp` from "Acme Corp"; etc. The check is a single file-exists test per entity.

### C. Person-page graduation, fixed

Two changes:

1. **Passive graduation in `/end-day` Step 3 cheap-tier triage.** When the triage sees a person mentioned across ≥ 2 nodes with ≥ 3 total mentions, propose graduation right there: "I've seen Kim Smith mentioned 8 times across 4 nodes. Graduate to a person page? (y/n/later)." This catches graduations that the recall-counter path misses.

2. **Graduation backfill in `/relink-memory`** (next item). Walk existing memory, count mentions per person, propose graduation for anyone with heavy mention density.

### D. `/relink-memory` retroactive command

A new cortex command that:

1. Scans every node file in `memory/` for plain-text entity mentions.
2. For each existing entity (every node file in `memory/client/`, `memory/person/`, `memory/topic/`, `memory/workstream/`, `memory/company/`, plus root-level domain nodes): propose converting matching plain-text mentions in *other* nodes to wikilinks.
3. For person-shaped mentions with ≥ 3 occurrences across ≥ 2 nodes but no person page yet: propose graduation to `memory/person/<slug>.md` with a one-shot synthesis pass over all node files mentioning them.
4. User-gated:
   - **Accept all** — relink everything + graduate everyone above threshold
   - **Links only** — relink to existing nodes; defer graduation
   - **Select** — walk per-entity with confirmation
   - **Cancel**
5. Idempotent. Gated by `memory/.migration-wikilink-relink-done` marker so it only proposes-and-asks once. Re-running with `--rerun` is supported.
6. After completion: regenerate `memory/index.md` and `memory/hot.md` to reflect new links.

Touches: new `commands/relink-memory.md` + `skills/relink-memory/SKILL.md`. Updates `references/migrations.md` with the new migration entry.

---

## Does the fix apply downstream?

Yes, but in two distinct ways:

**Schema + mining changes (parts A, B, C):** These are *code* (cortex skill / agent / command files). They ship via `git push BrightWayAI/claude-cortex` → marketplace picks up on Cowork's next startup. **Every user who installs or updates cortex v4.10.0+ gets the new behavior automatically.** New users with empty memory have correctly-wikilinked output from their first `/remember`. Existing users get correctly-wikilinked output from any new mining run.

**Retroactive fix (part D):** `/relink-memory` is a command shipped in cortex v4.10.0. The command code itself reaches every user via the marketplace — but the *operation* it performs only affects the user's own `<config-root>/memory/`. **Each user has to run `/relink-memory` once** to back-fill their existing memory. New users with empty memory don't need to run it (nothing to relink). It auto-detects whether there's anything to do.

So the answer to the user's question: **yes, the fix is in the marketplace; everyone benefits automatically going forward; existing users run a one-time `/relink-memory` to clean up their own accumulated memory.**

---

## Expected outcome

Before fix:
- 30 nodes, 28 wikilinks, mostly isolated graph
- No person pages

After fix (user runs `/relink-memory --accept-all`):
- Same 30 nodes
- ~150-400 wikilinks (depends on plain-text density)
- 5-15 new person pages graduated from heavy-mention persons
- Graph view becomes a real network: people connect to clients, clients connect to topics, topics connect to workstreams, etc.

Going forward, new mining + new `/remember` calls automatically emit wikilinks, so the graph stays dense as memory grows.

---

## Acceptance criteria

- [ ] Schema updates landed across cortex (CLAUDE.md, command templates, agent specs)
- [ ] Mining agents emit wikilinks for known entities
- [ ] `/end-day` Step 3 has passive graduation pass
- [ ] `/relink-memory` command exists and is idempotent
- [ ] `references/migrations.md` lists the new migration
- [ ] Router intent table includes "relink my memory" / "fix my wikilinks" triggers
- [ ] CHANGELOG entry for cortex v4.10.0
- [ ] All changes pushed
- [ ] User runs `/relink-memory --accept-all` and reports graph density (target: 5-15× edge count)

---

## What this is NOT

- Not a one-off patch to the user's specific memory. It's a marketplace-wide improvement.
- Not auto-merging existing plain-text mentions without user review. Every retroactive conversion is user-gated.
- Not deleting content. Conversions are surgical: plain text → wikilink. Content stays.
- Not changing decay states or memory semantics. Wikilinks are navigation, not knowledge.
