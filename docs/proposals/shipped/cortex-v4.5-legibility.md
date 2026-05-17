# cortex v4.5.0 — Memory legibility upgrade (index + gap-fill)

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus marketplace_
_Status: Spec ready. No work has started._
_Inspiration: Karpathy LLM wiki pattern (`index.md` catalog) and `wiki-self-heal` (autonomous gap-filling research)._

---

## Why this exists

cortex v4.3 (mining) and v4.4 (decay) made memory **bidirectional** — it learns and forgets. v4.5 makes memory **legible** and **self-improving**: any human (or non-cortex agent) can read one file and understand what's in the second brain, and cortex can proactively identify weak spots and fill them.

Two additions, one cohesive theme:

1. **`memory/index.md`** — an always-current human-readable catalog of every memory node. Auto-maintained. Lets Obsidian show a flat catalog page; lets agents that don't have memory-librarian loaded find their way around with one file read.
2. **`/research-gaps`** — autonomous scan for missing/contradictory/thin content, web-researched filling, committed to a review draft for the user to merge. Active maintenance loop alongside the passive decay model.

Both directly answer the JARVIS productization question: a system you can hand to a new user (or a new Claude session, or another agent) and have them onboard from one document.

---

## Decisions to make (flag for user before implementing)

1. **Index format:** flat alphabetical, or grouped by node type (user / client / person / domain / topic / knowledge)? Recommend grouped — Obsidian's default catalog is alphabetical; grouped gives more signal for humans skimming.
2. **Index refresh trigger:** every memory write, or just `/end-day` and `/cleanup`? Recommend the latter — every-write is overkill and risks file-lock churn during heavy `/remember` sessions.
3. **Research-gaps web access:** does cortex use `WebSearch` / `WebFetch` directly, or call out to a separate research agent? Recommend a new `gap-researcher` subagent in `agents/` for isolation.
4. **Research-gaps writeback mode:** annotated draft for user review (safe), or auto-write with user gating at next `/cleanup` (more JARVIS-like)? Recommend annotated draft for v0.1; revisit after a few real runs.

---

## Part 1 — `memory/index.md` catalog

### What it looks like

```markdown
# Memory index

_Last updated: 2026-05-16 14:23. Auto-maintained by cortex; do not hand-edit._
_Total nodes: 47 (8 client, 12 person, 6 company, 9 topic, 8 domain, 4 system)._

## User profile

- [[user]] — Zach Wagner. CEO BrightWay AI. _Confirmed 2026-05-14._

## Clients

- [[client/acme]] — Acme Corp engagement. AI strategy + agentic ops build. _Fresh. Confirmed 2026-05-12._
- [[client/contoso]] — Contoso retainer. Monthly cadence. _Stale — last confirmed 89d ago. Rehearse?_
- [[client/initrode]] — Closed 2026-Q1. _Cold — last confirmed 142d ago._

## People

- [[person/sarah-chen]] — VP Eng, Acme. Procurement-sensitive. _Fresh._
- [[person/jamie-park]] — Connector, ex-McKinsey. _Cooling — last touch 41d ago._
- ...

## Companies

- [[company/acme-corp]] — F500 industrial. Stale RFP cycle. _Fresh._
- ...

## Topics

- [[topic/ai-governance]] — Active research. 12 entries. _Fresh._
- [[topic/agentic-pricing]] — _Stale — last entry 71d ago._
- ...

## Domain notes

- [[domain/consulting-economics]] — Heuristics for engagement pricing.
- [[domain/cowork-platform]] — Notes on Claude Cowork's runtime model.
- ...

## System

- [[DASHBOARD]] — Auto-recall entry point.
- [[.decay-config]] — Decay thresholds. Hand-editable.
- [[.rehearse-queue]] — Deferred-from-cleanup queue.
- ...

## Demoted knowledge (not active; preserved for context)

47 demoted entries across 18 nodes — see individual node `## Demoted knowledge` sections.

## Archived person pages

3 in `memory/person/archive/` — last archived 2026-04-22.
```

Each line: wikilink, one-sentence descriptor (auto-extracted from the file's first H1 or front-matter), latest `[confirmed:...]` date with decay-state flag. Demoted/archived material is summarized at the bottom, not listed.

### Generation logic

A new lightweight subroutine, **`indexer`**, lives at `skills/indexer/SKILL.md`. Pure file-walk + string-extraction logic. **Zero LLM calls** in steady state — it's a deterministic regenerator.

Inputs:
- `<config-root>/memory/**.md` — all node files.

Outputs:
- `<config-root>/memory/index.md` — regenerated wholesale on each run.

Logic:
1. Walk `<config-root>/memory/` recursively. Skip dotfiles except `.decay-config.md`, `.rehearse-queue.md` (those go in the system section).
2. For each file:
   - Determine node type from path (`memory/client/X.md` → client; `memory/person/X.md` → person; `memory/topic/X.md` → topic; etc.).
   - Extract one-sentence descriptor: first H1, then first line after H1 if non-empty, else front-matter `description`.
   - Find max `[confirmed:YYYY-MM-DD]` tag across all entries in the file. Classify against `.decay-config.md` thresholds.
   - Count active knowledge entries vs. `## Demoted knowledge` entries.
3. Render grouped catalog. Sort each group by decay state (Fresh → Stale → Dormant → Cold) then alphabetically.
4. Append demoted/archived summary footer.
5. Write `<config-root>/memory/index.md`.

### Refresh triggers

- `/end-day` (Step 6, after auto-commit) — keeps index fresh daily.
- `/cleanup` (final step) — refresh after any user-gated demotions/archives.
- `/remember` (silent) — flagged in CLAUDE.md as a *deferred* refresh: queue an index regeneration in a marker file but don't run synchronously. `/end-day` notices the marker and runs the indexer if queued.
- Explicit: new `/reindex` command (fast, no-op if up-to-date). Useful after manual edits.

### Why this matters

- **Obsidian becomes a usable UI immediately.** The user opens `<config-root>/` in Obsidian, sees `index.md` as their home page, navigates by wikilink. No plugin code needed in Obsidian itself.
- **Non-cortex agents can now read memory cold.** Any future Nucleus plugin (or a one-off agent) can read `index.md` first and find its way around without loading `memory-librarian`.
- **Health snapshot in one file.** Stale/dormant counts at the top give the user an at-a-glance audit before they ask `/cleanup` to do work.
- **Zero ongoing model cost.** Deterministic. Runs in milliseconds.

### File-format compatibility

`index.md` uses pure Markdown + wikilinks (`[[node-path]]`). Compatible with:
- Obsidian (native wikilink resolution).
- Foam, Logseq, Dendron, and other wiki-style tools that resolve `[[name]]`.
- Plain Markdown viewers (GitHub renders, VS Code, mdcat) — links don't resolve but file is still legible.

### Acceptance criteria

- [ ] `skills/indexer/SKILL.md` exists with deterministic generation logic.
- [ ] `commands/reindex.md` exists for on-demand regeneration.
- [ ] `/end-day` Step 6 runs the indexer after auto-commit.
- [ ] `/cleanup` final step runs the indexer.
- [ ] `/remember` queues a deferred refresh via `.reindex-queue` marker file.
- [ ] First v4.5 run regenerates `<config-root>/memory/index.md` from scratch.
- [ ] CLAUDE.md updated: new "Memory index" section pointing at `references/memory-index.md` (new spec doc).
- [ ] No model calls in the steady-state indexer path.

---

## Part 2 — `/research-gaps` autonomous gap-fill

### What it does

Scans memory for gaps that the user couldn't easily see on their own. Researches the highest-priority ones via web (≥2 independent sources per claim). Writes findings to a single annotated draft for user review. Never auto-merges into memory — every claim is user-gated at merge time.

Inspired by the `wiki-self-heal` skill in NulightJens/ai-second-brain-skills, adapted to cortex's typed node model and decay states.

### Gap types it detects

| Gap | Detection signal | Example |
|---|---|---|
| **Thin entity** | Person/company page with ≤1 active entry but referenced by ≥3 other nodes | Sarah Chen mentioned in 4 client nodes, has only 1 entry on her own page → research her |
| **Stale fact** | INSIGHT/MODEL with `[confirmed:...]` > `threshold_dormant` AND topic is in active rotation (mentioned in ≥1 Fresh node within 30d) | "Anthropic uses RLHF" confirmed 200d ago, still actively referenced → re-verify |
| **Contradiction** | Two active entries on the same node with opposing claims (semantic check via cheap classifier) | One entry says "Acme uses HubSpot," another says "Acme uses Salesforce" → flag |
| **Orphan** | Node with zero inbound wikilinks AND no `[confirmed:...]` in last 90d | `topic/agentic-pricing` is unused — propose archive or merge |
| **Under-cited claim** | INSIGHT marked `[high-confidence]` but no source/citation in the entry body | "AI agents will replace junior analysts by 2027" tagged high-confidence but no source → research and either add citation or downgrade confidence |
| **Decision gap** | A project/client node mentions an upcoming decision in its `## Open threads` that's past its mentioned date | Acme node says "decide on stack by 2026-04-15" — today is 2026-05-16, no resolution captured → prompt user |

### Workflow

1. **Trigger.** User runs `/research-gaps`. Optional argument: scope (`person`, `topic`, `client/acme`, etc.) — default is all.
2. **Scan phase.** New `gap-researcher` subagent walks memory, applies each detection rule, produces ranked gap list. Pure file-read + rule application; no web calls yet.
3. **User review of gap list.** Surface gaps grouped by type. Per-gap actions: research now / skip / mark as known-and-OK / archive node. User picks which to research.
4. **Research phase.** For each chosen gap:
   - Compose targeted query (e.g., "Acme Corp 2026 technology stack" or "Sarah Chen Acme VP Eng").
   - Search via `WebSearch`.
   - Pull top results via `WebFetch`.
   - Require ≥2 independent sources for any claim; if fewer, mark "unverified — manual research needed."
   - For person/company gaps, prefer LinkedIn, official sites, press releases. For topic/domain gaps, prefer primary sources, peer-reviewed work, named experts.
   - Compose findings as a delta against the existing node: "current entry says X, sources confirm/contradict/expand: …"
5. **Draft writeback.** All findings go into one file: `<config-root>/memory/.research-drafts/YYYY-MM-DD-research-gaps.md`. Structured as one section per gap, each with: existing entry, proposed update, source links, suggested action (replace / merge / add as new entry / discard).
6. **User merge.** A companion command `/merge-research-draft` (or just walk-through via `/research-gaps` once the draft exists) takes the user through each finding: accept → write to the node with `[confirmed:today]`; reject → log to `.research-skip-log.md`; defer → leave in draft for next time.
7. **Cleanup.** Once all findings are merged or skipped, archive the draft to `memory/.research-drafts/archive/`.

### Where the research lives

```
<config-root>/memory/
├── .research-drafts/
│   ├── 2026-05-16-research-gaps.md       ← current draft
│   └── archive/
│       └── 2026-05-09-research-gaps.md   ← merged or fully reviewed
├── .research-skip-log.md                 ← gaps the user explicitly marked as known/OK
```

### Subagent: `gap-researcher`

New file at `agents/gap-researcher.md`. Tools: `WebSearch`, `WebFetch`, file read/write within `<config-root>/memory/.research-drafts/` only. No memory writes outside the draft directory.

Confidence-aware: returns Low confidence (and pauses for user input) when:
- Fewer than 2 independent sources agree on a claim.
- All sources are from social media (LinkedIn, Twitter) without corroboration.
- Sources are older than 18 months for a "current state" question.

### Failure modes

- **No internet / WebSearch unavailable.** Skip research phase; still surface the gap list and let the user manually annotate.
- **User has rate-limited gaps.** Cap at 5 researched gaps per `/research-gaps` run by default. Otherwise tokens balloon and the user is overwhelmed at review time.
- **Memory writes during research.** Draft is staged before any merge prompts the user; concurrent `/remember` calls don't conflict.
- **Personal info on the open web.** For person gaps, the agent must not surface speculative claims about private individuals. Limit to verifiable professional facts (role, employer, public talks, published work). No "Sarah Chen recently bought a house" even if a real estate database surfaces it.

### Cost profile

- Scan phase: ~5K input tokens (walks memory once via cheap-tier classifier for contradiction detection only).
- Research phase: ~5 WebSearch + ~10 WebFetch + ~3K output per gap. At 5 gaps: ~25K total tokens. Roughly $0.05-0.15 per run.
- User merge phase: one-shot review at sub-second per gap.

Total: a `/research-gaps` run costs less than a `/end-week` run. Designed for weekly cadence.

### Schedule

- Default: weekly, Saturday morning (low-priority slot). Optional registration in `core-ops/references/schedules.md`.
- Triggered manually any time.
- Integrated into `/end-week` as an optional Step 6: "Run /research-gaps to fill knowledge gaps from the week?"

### Acceptance criteria

- [ ] `commands/research-gaps.md` exists with the full workflow.
- [ ] `skills/research-gaps/SKILL.md` exists with trigger conditions.
- [ ] `agents/gap-researcher.md` exists with tool allowlist and confidence rules.
- [ ] `commands/merge-research-draft.md` exists for the merge step.
- [ ] `references/gap-detection-rules.md` exists with the formal rule definitions.
- [ ] `/end-week` chain offers `/research-gaps` as optional Step 6.
- [ ] Person-gap research respects the private-individual privacy rule.
- [ ] All research findings land in `.research-drafts/`, never in active memory, until user accepts.
- [ ] CLAUDE.md updated with `/research-gaps` and `/merge-research-draft` in the command list.

---

## Combined v4.5.0 release notes (preview)

```
## [4.5.0] — Legibility upgrade: memory index + research-gaps (2026-05-XX)

### Why this exists
v4.3 (mining) made memory grow with the user. v4.4 (decay) made it forget gracefully.
v4.5 makes memory *legible* and *self-improving*: a single auto-maintained catalog
file (`memory/index.md`) gives a one-glance overview of the whole second brain, and
a new `/research-gaps` command actively finds and fills weak spots with web-sourced
research, gated by user review.

### Added — memory/index.md
[as specified above]

### Added — /research-gaps + gap-researcher subagent
[as specified above]

### Why this matters
- Obsidian becomes a first-class human UI immediately (the index renders as a
  wikilink graph).
- Non-cortex agents can read memory cold via index.md without loading
  memory-librarian.
- Active gap-filling complements passive decay: the brain doesn't just forget;
  it asks itself "what's missing?" and proposes answers for review.
- Productization-ready: shareable second-brain demos start with `index.md`.
```

---

## Out of scope (future versions)

- **Auto-merge with confidence thresholds.** v0.1 always gates merges through the user. A v5.0 feature could be: if all sources agree and confidence is High, auto-merge with a notification.
- **Cross-vault research.** Future support for researching across multiple `<config-root>` vaults (consultant working with multiple firms).
- **Bidirectional updates to source systems.** If `/research-gaps` learns that Acme moved from HubSpot to Salesforce, eventually push that update into the user's CRM. Out of scope for v4.5.
- **Voice-input gap review.** Reviewing 5 gaps by voice while walking — out of scope, depends on platform.
- **Real-time research suggestions.** Surface gap-fill suggestions during `/recall`. Belongs in a later version once gap detection is proven.

---

## Implementation order (when greenlit)

1. **Memory index first.** Lower risk, zero LLM cost, big legibility win. Ship as cortex v4.4.1 if the user wants it independently of `/research-gaps`.
2. **`/research-gaps` second.** Bigger feature, needs web access, requires the privacy rule. Ship as cortex v4.5.0 once index is stable.
3. **Both together in v4.5.0** if user wants a single release. Recommended path.
