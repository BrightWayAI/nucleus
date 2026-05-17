# Karpathy pattern survey — what Nucleus has, what's still missing

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus_
_Sources: Karpathy's [LLM wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), [autoresearch project](https://github.com/karpathy/autoresearch), [Software 3.0 talk (YC 2025)](https://karpathy.bearblog.dev/year-in-review-2025/)._

After cortex v4.7 (overnight learning + hot.md + immutable archive), Nucleus implements most of Karpathy's published patterns. This survey enumerates every concrete pattern, maps it to Nucleus state, and ranks the remaining gaps by value-to-cost ratio.

---

## Pattern coverage matrix

### From the LLM wiki pattern

| Pattern | Source | Nucleus status |
|---|---|---|
| Three-layer architecture (raw / wiki / schema) | LLM wiki | ✅ **Shipped v4.7** — `<config-root>/archive/` (raw, immutable) + `<config-root>/memory/` (LLM-owned wiki) + `claude-cortex/CLAUDE.md` (schema) |
| Three operations (ingest / query / lint) | LLM wiki | ✅ Ingest = `/remember`, `/listen`, `/end-day`. Query = `/recall`, `/search`, `memory-librarian`. Lint = `/cleanup`, `/research-gaps`, `/rehearse` |
| `index.md` — content catalog | LLM wiki | ✅ Shipped v4.5 (`memory/index.md`, auto-maintained) |
| `log.md` — append-only chronicle, grep-friendly prefixes | LLM wiki | ❌ **Missing.** Cortex has `triage-log.md` (commit-triage only) and per-node changelogs. No unified `## [YYYY-MM-DD] <op> \| <subject>` log spanning ingest / query / lint runs |
| `CLAUDE.md` as schema | LLM wiki | ✅ Cortex has it; pointed to by Obsidian VAULT.md |
| `hot.md` — rolling buffer | LLM wiki | ✅ Shipped v4.7 |
| Folder-is-the-app | LLM wiki | ✅ Cortex memory is exactly this; Obsidian setup makes it visible |
| Source-of-truth precedence ("raw sources always win") | LLM wiki | ⚠️ **Partial.** v4.4 drift detection handles entry-vs-entry conflicts. Raw-vs-entry conflicts (transcript disagrees with old node entry) aren't explicitly resolved — `/morning` merges proposal-by-proposal, but doesn't auto-default to "supersede" when raw substrate contradicts old content |
| Obsidian as IDE | LLM wiki | ✅ Shipped v4.5 (`/setup-obsidian`) |
| Wikilinks + graph view | LLM wiki | ✅ Cortex convention; renders in Obsidian |
| LLM owns bookkeeping | LLM wiki | ✅ Indexer, mining agents, drift detection — all LLM-side bookkeeping |

### From autoresearch

| Pattern | Source | Nucleus status |
|---|---|---|
| Autonomous experimentation loop with fixed budget | autoresearch | ⚠️ **Partial.** `/listen` is a nightly loop. `/research-gaps` is on-demand. Neither has a per-iteration fixed-time budget like autoresearch's 5-min cap. Not clearly needed for Nucleus's use cases but a pattern worth knowing |
| Single-metric greedy acceptance | autoresearch | ❌ **Missing.** Nucleus has no measurement loop. Writing-style could track "% of drafts accepted without edit"; voice rules with high acceptance retained, low-acceptance demoted. Future work |
| `program.md` — markdown control file for agents | autoresearch | ✅ Nucleus's per-plugin `user-context.md` files are this pattern. Plus cortex CLAUDE.md |
| Narrow scope (modify only one file) | autoresearch | ✅ Each cortex command writes a known set of locations; mining agents are read-only against active memory; `gap-researcher` writes only to `.research-drafts/`. Strong containment |
| Overnight batch experiments | autoresearch | ✅ Shipped v4.7 (`/listen` runs at 11pm or 5am via cron) |
| File-based separation (fixed / agent-modifies / human-edits) | autoresearch | ✅ archive/ (fixed) / memory/ (agent-modifies) / identity.md, voice.md, user-context (human-edits) |
| No autonomous direction-setting | autoresearch | ✅ Nucleus is purely user-directed; agents act within user-set scope |

### From Software 3.0 (YC 2025)

| Pattern | Source | Nucleus status |
|---|---|---|
| Iron Man suit metaphor — augmentation with autonomy sliders | Software 3.0 | ⚠️ **Partial.** Router has one mode (suggest+confirm). No per-capability slider. A user might want `/note` to be auto (no confirm), `/remember` to be suggest+confirm, `/lead-draft` to be always-confirm regardless of context |
| Partial autonomy with custom GUIs | Software 3.0 | ✅ daily-brief's Cowork artifact (annotated textareas) is exactly this pattern |
| Cursor-for-X domain-specialized orchestrators | Software 3.0 | ✅ Each Nucleus plugin is a Cursor-for-an-operator-workflow (lead-engine = Cursor for LinkedIn outbound; daily-brief = Cursor for the day; etc.) |
| LLM-readable interfaces / `llms.txt` | Software 3.0 | ❌ **Missing.** Nucleus has README.md for humans. No `llms.txt` at the repo root explicitly designed for an LLM agent to onboard from. Karpathy: "create markdown-readable interfaces, machine-consumable documentation (like llms.txt), and avoid GUI-only affordances." |
| Prompts as programs | Software 3.0 | ✅ Cortex commands are prompts-as-programs in markdown. So are skill files |
| AI agents as consumers (not just humans) | Software 3.0 | ⚠️ **Partial.** Cortex memory is structured for agent consumption (typed nodes, decay tags), but Nucleus as a whole doesn't have a "here's how an agent should onboard" entry point |

---

## Summary — what's already done

**v4.5 + v4.6 + v4.7 closed all the major Karpathy gaps from the LLM wiki pattern:**
- Immutable raw-source room ✅
- Wiki / schema separation ✅
- index.md, hot.md, CLAUDE.md ✅
- Folder-is-the-app ✅
- Obsidian as IDE ✅
- Lint loop (`/cleanup` + `/research-gaps`) ✅
- Bookkeeping owned by the LLM ✅

What remains is **three small additions** with high value-to-cost ratio, and a few larger ideas worth proposing but not building yet.

---

## High-value additions to ship now

These three additions take ~2-3 hours combined and close the remaining gaps without adding meaningful complexity.

### A. Unified `log.md` (Karpathy chronicle pattern)

**What:** A single append-only file at `<config-root>/memory/log.md` with one line per Nucleus operation across ingest / query / lint / merge. Grep-friendly date prefixes.

**Format:**
```
## [2026-05-16 14:23] listen | archived 2026-05-15 (8 events, 12 inbox, 3 mentions, 2 transcripts)
## [2026-05-16 09:12] morning | merged 14/17 proposals from 2026-05-15 draft
## [2026-05-16 17:45] end-day | quick mode, 3 commitments, reflection captured
## [2026-05-16 17:46] reindex | 47 nodes (28 fresh, 12 stale, 5 dormant, 2 cold)
## [2026-05-16 18:01] research-gaps | scanned 47 nodes, found 6 gaps, researched 3
## [2026-05-17 09:30] recall | auto-fire, loaded hot.md + user.md (cold-start avoided)
```

**Why:** Every command's audit trail in one grep-able place. Answers "what did I do on 2026-05-12" with `grep '## \[2026-05-12' log.md`. Cheap observability. Useful when something goes wrong, for telemetry, and for onboarding a fresh Claude session.

**How:** Each major command appends one line at completion. Pure side-effect; no new logic.

**Cost:** ~30 min cortex change. Touch ~6 commands (listen, morning, end-day, reindex, research-gaps, cleanup, recall). Add to CLAUDE.md.

### B. `llms.txt` at the nucleus repo root (Karpathy machine-readable docs)

**What:** A top-level `llms.txt` file in `BrightWayAI/nucleus` following the [llms.txt standard](https://llmstxt.org/) — designed for an LLM agent (cold Claude session, future Anthropic evaluator, researcher) to onboard on Nucleus in one file read.

**Format:**
```markdown
# Nucleus

> The operating system for solo operators running on AI. 14 plugins, JARVIS-style natural-language router, bidirectional memory.

## Marketplace

- [Plugin catalog](.claude-plugin/marketplace.json): manifest of all 14 plugins.

## Docs

- [README](README.md): full overview for humans.
- [Proposals](docs/proposals/): all design specs (shipped and in-flight).
- [Multi-agent patterns](docs/multi-agent-patterns.md): chaining subagents inside plugins.

## Core plugin

- [claude-cortex CLAUDE.md](https://raw.githubusercontent.com/BrightWayAI/claude-cortex/main/CLAUDE.md): the memory schema. Read this first if you want to understand how Nucleus thinks.

## Optional
...
```

**Why:** Karpathy's Software 3.0 emphasis: "design with agents in mind." A new agent (or a curious developer at Anthropic) can find their way around Nucleus in 30 seconds via `llms.txt` instead of skimming a 300-line README.

**Cost:** ~15 min.

### C. Per-command autonomy slider (Karpathy Iron Man pattern)

**What:** A new `<config-root>/plugins/cortex.user-context.md` (and/or `nucleus-router.user-context.md`) section that lets the user set per-command autonomy:

```yaml
autonomy:
  /note: auto              # no confirm; just capture (it's a one-liner)
  /remember: suggest       # current behavior
  /recall: auto            # never confirm; just load
  /lead-draft: confirm     # always confirm even if obvious
  /listen: auto            # already runs unattended
  /morning: confirm        # per-proposal gating
  /research-gaps: suggest
  default: suggest         # fallback
```

The router consults this before suggesting confirmations. Individual commands consult this before any "are you sure?" prompts.

**Why:** Iron Man suit with autonomy sliders. Some commands deserve high autonomy (`/note`, `/recall`); others need explicit confirmation every time (`/lead-draft`, `/morning` proposals). Today everything's at "suggest+confirm" which is the cautious middle. Users develop trust unevenly across capabilities — let them tune it.

**Cost:** ~1.5 hours. Touches the router skill, a handful of high-value cortex commands, and one new reference doc.

---

## Medium-value additions (propose now, build later)

### D. Source-of-truth precedence in `/morning`

When a `/listen` proposal contradicts an existing memory entry AND the source agent is `transcript-reviewer` or `activity-miner` (i.e., grounded in archive substrate), the default `/morning` action should be **supersede** not **keep both**. Raw substrate wins over old entries. ~30 min cortex change.

### E. Generic `/lint <node>` for non-memory configs

`/research-gaps` lints memory. But what about `voice.md` (contradictory style rules?), `identity.md` (stale role/tools?), plugin `user-context.md` files (inconsistent settings)? A general `/lint <path>` applies gap-detection patterns to any markdown config under `<config-root>/`. ~1 hour cortex change.

### F. Acceptance-metric feedback for writing-style

Track per-voice-rule acceptance rates: when `/style` drafts and the user edits before sending, log which rules likely contributed. Promote high-acceptance rules; demote consistently-edited-out ones. Karpathy's autoresearch greedy-acceptance pattern applied to voice. ~3-4 hours, touches writing-style plugin. Build after a few weeks of dogfooding so there's real data.

---

## Aspirational (worth knowing about; not building soon)

### G. Generalized overnight loops (autoresearch pattern)

`/listen` is the first overnight loop. The pattern generalizes:
- `/refine-voice` — overnight: re-read last 7 days of drafts vs sends, propose new voice rules.
- `/sweep-pipeline` — overnight: re-score CRM pipeline against the week's signals, propose new rankings.
- `/audit-decay` — overnight: scan for entries crossing decay-state boundaries today.

Each loop is fixed-scope, append-only proposals, user-gated merge in the morning. Real work; defer until v4.7 dogfooding establishes the pattern.

### H. Memex associative trails

A `/trail <topic>` command that produces a *reading path* through the memory graph — not just "here are 5 related nodes" but "start here, then because of X read this, then Y, then Z to arrive at your current understanding." Karpathy's Memex framing. Niche but interesting.

### I. Software 3.0 multi-modal interfaces

Karpathy points to LLM apps as Iron Man suits with custom GUIs. Daily-brief's Cowork artifact is one. Future plugins could ship richer interactive surfaces — e.g., a pipeline-analyst that renders an interactive table where you drag deals between stages and the underlying CRM updates. Out of scope for now.

---

## Recommendation

**Ship A, B, C this session.** They're small, high-value, and close out the survey gaps with no risk:

- `log.md` chronicle (audit + observability)
- `llms.txt` (agent-readable repo entry)
- Autonomy slider (Iron Man suit per-capability)

**Defer D-F to dogfooding.** Real usage will tell you whether source-precedence default needs tuning, whether config-lint is worth a new command, and whether voice-acceptance metrics actually correlate with quality.

**G-I are notebook ideas.** Worth knowing; not worth building until the previous tier has been used in earnest.

---

## What's missing from Karpathy and why it's fine to skip

A few patterns from his broader writing don't translate to Nucleus's use case and aren't worth porting:

- **5-minute experimentation budget** (autoresearch) — Nucleus mining isn't bound by training-run physics. Per-task timeouts already exist where needed.
- **`prepare.py` / `train.py` separation** (autoresearch) — domain-specific to ML training loops.
- **Vocab-size-independent metrics** (autoresearch) — irrelevant to memory mining.
- **Some Software 3.0 framing** (e.g., "natural language as programming language") — true and lovely but not actionable as a feature.

The implementable ideas are the ones above. Everything else from Karpathy is already in Nucleus or doesn't apply.
