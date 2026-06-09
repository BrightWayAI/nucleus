> **SHIPPED (items A–D)** — cortex v4.8.1 (unified `memory/staged/` tree, `/migrate-staged-substrates`, `contracts.md`, README 'start here'). Items E–G (mining-agent consolidation, `/end-day` decomposition, autonomy-slider coverage) were deferred — tracked in `../ROADMAP.md`. Archived for historical context.

---

# Cleanup pass 1 — architectural debt backlog

_Created: 2026-05-20_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Backlog. Items A-D execute this session; items E-G defer to user review before changing._
_Related: every prior shipped proposal — this is the first deliberate "clean before extending" cycle._

---

## Why this exists

Five sub-versions of cortex shipped in one session (v4.4 → v4.8.0), a new plugin (`nucleus-router`), a daily-brief refactor, a core-ops patch. Real features. But architectural debt accumulated:

- Three mining agents doing overlapping work
- `/end-day` ballooned to 13 steps in one command file
- Eight different "staged" dotfiles in `memory/`
- Cross-plugin contracts are implicit (file-format dependencies between plugins, undocumented)
- Autonomy slider half-wired (some commands respect it, most don't)
- One-time migration pattern (Scope migration in `/end-day` Pre-chain B) is unnamed and re-invented per migration
- 14-plugin catalog with no "minimum viable starter" callout in the README

Each is fine on its own. Together they compound — anyone extending the codebase has to hold inconsistent patterns in their head. This pass cleans the substrate so the next feature cycle (e.g., `/sweep` heartbeat, Operator app) starts from a coherent base.

---

## Karpathy alignment check

Liu's "codex-maxxing" piece (and the LLM wiki gist) suggest these architectural principles. Mapping Nucleus's debt against them:

| Karpathy principle | Where Nucleus aligns | Where it drifts |
|---|---|---|
| Vault as the app; markdown as the substrate | ✅ `<config-root>/memory/` | — |
| `AGENTS.md` as standing instructions | ✅ cortex CLAUDE.md | — |
| Git diff as review surface for memory | ❌ Not yet wired (see `memory-as-git.md` proposal) | This is the big missing piece |
| Heartbeats / recurrence loops | ⚠ Partial — daily/weekly only; no sub-daily yet | See `sweep-heartbeat.md` proposal |
| Strong goals + verification oracles | ✅ `/research-gaps` ≥2-source rule | Not consistently applied across drafting plugins |
| Operating loops over single prompts | ⚠ Loops exist but called "rituals/commands" in copy | Reframe in future marketing |
| Single, scoped agent files (`AGENTS.md` per dir) | ❌ Cortex's CLAUDE.md is monolithic | Could decompose into per-section AGENTS.md once contracts.md exists |
| Steering / async instruction stacking | ❌ Not yet | Future cycle |
| Workstream primitive | ❌ Not yet | Future cycle |

Cleanup pass 1 addresses three of these directly:
- **Git diff as review surface** → spec in `memory-as-git.md`
- **Single scoped agent files** → `contracts.md` is the prerequisite (lists cross-plugin file-format dependencies); after that, decomposing CLAUDE.md is straightforward
- **Strong goals consistently** → flagged for future drafting-plugin pass

---

## Items, prioritized

Each item has: scope, cost, blast radius, recommended timing.

### A. Reorganize staged substrates under `memory/staged/` (do now)

**Problem:** Eight dotfiles/dirs scattered across `memory/`:
```
memory/.commit-drafts/        memory/.rehearse-queue.md
memory/.research-drafts/      memory/.rehearse-skip-log.md
memory/.heartbeat-drafts/     memory/.research-skip-log.md
memory/.reindex-queue          memory/.morning-reject-log.md
```

**Fix:** Reorganize under `memory/staged/`:
```
memory/staged/
├── commit-drafts/        (from /listen)
├── research-drafts/      (from /research-gaps)
├── heartbeat-drafts/     (from /sweep, future)
├── queues/
│   ├── rehearse.md
│   └── reindex
└── skip-logs/
    ├── rehearse.md
    ├── research.md
    └── morning-reject.md
```

**Touches:** Every cortex command that reads/writes one of these paths. ~15 file references across cortex.

**Cost:** ~1 hour — file renames + path updates + CHANGELOG note.

**Blast radius:** Existing users on cortex v4.8.x have files at the old paths. Need a one-shot migration step at next-load that detects old paths and moves them. Should be transparent.

**Decision:** **Do now.** Pure clarity win. Lower-friction before more staged substrates accumulate.

### B. Document migration pattern (`references/migrations.md`) (do now)

**Problem:** The Scope migration in `/end-day` Pre-chain B uses a marker-file pattern (`.scope-migration-done`) to gate a one-time data migration. The same pattern is implicit in: decay config init, `.gitignore` write, hot.md first-generation, etc. No formal convention.

**Fix:** A new `cortex/references/migrations.md` that:
- Names the pattern: "marker-gated one-time migration."
- Lists active migrations with their marker files.
- Documents how to add a new migration (template).
- Specifies that migrations live in their *own* command (`/migrate-X`), not bolted into chains.

**Cost:** ~30 min — pure docs.

**Decision:** **Do now.** Cheap; high leverage for keeping the codebase consistent. Also flags that the Scope migration *should* be extracted from `/end-day` (deferred to item F).

### C. Document cross-plugin contracts (`nucleus/docs/contracts.md`) (do now)

**Problem:** Implicit file-format dependencies between plugins:
- daily-brief Section 6 reads cortex's `## Reflection` section from yesterday's brief.
- `/start-nucleus` reads marker files written by ~10 setup commands.
- nucleus-router consults cortex's `autonomy:` user-context section.
- `/sweep` (future) reads cortex's `triage-log.md` for dedup.
- `/morning` reads `.commit-drafts/` directory; daily-brief reads `briefs/`.
- gap-researcher writes to `memory/.research-drafts/`; `/merge-research-draft` reads.

These work today but break silently if either side changes format.

**Fix:** A `nucleus/docs/contracts.md` that lists each cross-plugin file-format dependency with:
- File path (with `<config-root>` prefix)
- Writer (plugin + command)
- Reader (plugin + command)
- Format expectation (link to spec if exists)
- Version compatibility notes

**Cost:** ~30 min — pure docs. Enumeration not invention.

**Decision:** **Do now.** Prevents a class of subtle breakage as more plugins ship. Doubles as onboarding for anyone extending the marketplace.

### D. README "Start here" callout (do now)

**Problem:** A new user sees 14 plugins and doesn't know what to install. Recommended install combos are buried in section 8.

**Fix:** Add a one-paragraph callout at the top of the "Your AI staff" catalog:

> **Start here.** The minimum-viable Nucleus is three plugins: `nucleus-router` + `claude-cortex` + `core-ops`. Install those, run `/start-nucleus`, and add specialists (BD, content, delivery) as you need them. Don't try to install all 14 on day one.

10 minutes.

**Decision:** **Do now.** Smallest-cost / highest-leverage item in this pass.

### E. Consolidate mining agents (defer — flag for user review)

**Problem:** Three agents (`transcript-reviewer`, `conversation-miner`, `activity-miner`) do variants of the same job. Each is its own spec file. Each is invoked separately in `/end-day`, `/listen`, and (future) `/sweep`. ~600 lines of duplicated agent logic.

**Fix:** Consolidate into one `miner` agent with a `scope` parameter: `{ surfaces: [transcripts | conversations | gmail | slack | calendar | drive], date_range: today | yesterday | since:<ts>, dedup_against: [...] }`. The three current agents become invocation profiles. `/end-day`, `/listen`, `/sweep` all call the unified agent with different scope.

**Cost:** ~1 day refactor. Touches `/end-day` Step 2/2a/2b, `/listen` Step 3, `/sweep` (when built), the three agent specs.

**Blast radius:** Real. Three call sites change. Every cortex test would need rerunning (we don't have tests, but you'd need to manually verify the next `/listen` run produces equivalent proposals).

**Karpathy alignment:** Liu's autoresearch project says "the agent only touches `train.py` — keeps scope manageable, diffs reviewable." Same principle: one miner agent file instead of three is easier to read, easier to review changes to, easier to extend.

**Decision:** **Defer.** Worth doing before `/sweep` ships because `/sweep` would otherwise inherit the fragmentation. But the user should green-light this refactor explicitly — it's not a no-brainer.

### F. Decompose `/end-day` (defer — flag for user review)

**Problem:** `/end-day` has 13 steps in one ~400-line file. Pre-chain B (Scope migration) sits there forever after first run as cognitive weight. Step 5.5 (indexer) + Step 5.6 (hot cache) + Step 5.7 (log) are all "maintenance" — they fire from multiple commands, but their orchestration lives inline in `/end-day`.

**Fix (two-part):**

1. **Extract Pre-chain B (Scope migration) into a standalone `/migrate-scopes` command.** `/end-day` no longer references it. The marker-file check moves into the standalone command. (This is the recommended pattern from item B.)

2. **Extract the closing-rhythm orchestration into a `closing-chain` skill.** `/end-day` becomes a thin wrapper that invokes the skill with `mode: quick | full`. `/end-week` does the same. The shared orchestration (auto-commit + reflection + brief pre-stage + index + hot cache + log + close) lives in one place.

**Cost:** ~1 day. Touches `/end-day` (big rewrite), `/end-week` (smaller rewrite), new `/migrate-scopes` command, new `closing-chain` skill.

**Blast radius:** Higher than E. Two heavily-used commands restructure. Worth being careful.

**Karpathy alignment:** Single-purpose skill files are easier to evolve. Liu's `program.md` pattern is "markdown-based control file for one purpose" — `closing-chain` skill is exactly that.

**Decision:** **Defer.** Bigger architectural change; user should review the proposed split before refactor.

### G. Wire autonomy slider everywhere (defer)

**Problem:** Autonomy slider (cortex v4.7.1+) consulted at router level. Wired into command-level gates only for `/forget`, `/cleanup`, `/setup-obsidian`. Other commands with internal gates (`/remember`, `/end-day` reflection, `/morning` per-proposal, every drafting plugin's confirm step) have hardcoded gates that don't consult the slider.

**Fix:** Touch every command with an internal user-gate, add a "Step N — Consult autonomy" subsection that conditionally skips the gate based on the resolved mode.

**Cost:** ~2-3 days touching ~15 commands across 5 plugins.

**Blast radius:** Each command change is small. Aggregate is real — 15 separate edits, each a behavioral change.

**Decision:** **Defer.** Wait until at least one user complains "I set `/lead-draft: auto` and it still asks." If no one complains, the slider works well enough at the router level alone.

### H. README capture-verbs revisit (defer until dogfooding)

`/note`, `/learn`, `/remember` — three capture verbs with subtle shape differences. Router routes by phrasing so users don't pick wrong, but three commands for "capture something" adds catalog noise.

**Decision:** **Defer indefinitely.** If real users only use `/remember`, collapse the others later. If they use them distinctly, keep. Pure dogfooding question.

---

## Build sequence (this session)

| Order | Item | Cost | Outcome |
|---|---|---|---|
| 1 | A — Reorganize staged substrates | ~1 hr | `memory/staged/` directory tree; transparent migration on next load |
| 2 | B — `references/migrations.md` (cortex) | ~30 min | Named pattern; future migrations follow template |
| 3 | C — `docs/contracts.md` (nucleus) | ~30 min | Cross-plugin file-format dependencies documented |
| 4 | D — README "Start here" | ~10 min | Lower onboarding friction |
| — | Memory-as-git (`memory-as-git.md` proposal) | ~45 min | Spec only — implementation deferred |
| — | E, F | (deferred) | User review required before refactor |
| — | G | (deferred) | Wait for user signal |
| — | H | (deferred) | Wait for dogfooding |

Total this session: ~3 hours of cleanup + 45 min of proposal-writing.

---

## Versioning

- cortex bumps to v4.8.1 (patch — staged substrates reorg + migrations doc).
- nucleus repo gets new docs (contracts.md, memory-as-git proposal, this proposal) + README edit.
- No router / daily-brief / core-ops changes in this pass.

---

## Acceptance criteria

- [ ] `memory/staged/` directory tree exists. All cortex commands that previously read/wrote `.commit-drafts/`, `.research-drafts/`, `.heartbeat-drafts/`, `.rehearse-queue.md`, `.research-skip-log.md`, `.morning-reject-log.md`, `.rehearse-skip-log.md`, `.reindex-queue` now reference the new paths.
- [ ] Auto-migration step on next cortex load that detects old paths and moves them. No user action required.
- [ ] `cortex/references/migrations.md` exists with the named pattern + list of active migrations.
- [ ] `nucleus/docs/contracts.md` exists with cross-plugin file-format dependencies enumerated.
- [ ] README "Start here" callout sits at the top of the "Your AI staff" section.
- [ ] `nucleus/docs/proposals/memory-as-git.md` exists with the spec (implementation deferred).
- [ ] cortex CHANGELOG v4.8.1 entry written.
- [ ] All three repos (nucleus, claude-cortex) committed and pushed.

---

## Out of scope for this pass

- Building `/sweep` (separate proposal, dogfood `/listen` + `/morning` first).
- Implementing memory-as-git (separate proposal, spec this pass only).
- Items E, F, G, H (deferred to next pass after user review).
- The Operator app (separate spec, build later).
- Building any new heartbeats beyond the `/sweep` proposal.
