> **SHIPPED** — nucleus-router v0.2.0 + cortex v4.9.0 (2026-05-20): 15-verb surface, role-addressable fallback, workstream + DECISION primitives. Archived for historical context.

---

# Chief-of-Staff evolution — router becomes orchestrator, verbs become the surface

_Created: 2026-05-20_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Ready to build. ~1 week single-engineer. Spec + implementation in one cycle._
_Builds on: nucleus-router v0.1.4 (existing), cortex v4.8.1 (existing). Touches: nucleus-router (major rewrite to v0.2.0), cortex (minor bump to v4.9.0)._

---

## Why this exists

Today, the user-facing surface of Nucleus is ~60 slash commands, with a router that translates natural language into one of them. That's a CLI with NL matching, not a Chief of Staff.

The user's stated goal: a small set of **verbs they use deliberately**, with everything else **invoked through context**. The router needs to evolve from a translator into an orchestrator that:

1. **Reacts to the right cues.** Verbs are the primary surface. Role-addressable patterns are the fallback ("ask my Chief Financial Agent to bill this month").
2. **Routes intelligently with disambiguation.** "Research X" routes differently depending on what X is.
3. **Invites parallelism where genuinely independent.** Use Anthropic SDK's native parallel tool use; don't custom-orchestrate.
4. **Builds the second brain correctly.** Two new node primitives — workstream + DECISION — close real navigability gaps.

This is NOT a proactive Chief of Staff. No new heartbeats, no scheduled check-ins beyond what exists (`/listen` overnight, `/end-day` daily, weekly closes). The Chief is reactive but thorough.

---

## What's NOT in this proposal

- ❌ Proactive check-ins / new heartbeats (user explicitly deferred — `/sweep` proposal remains separate, not building)
- ❌ Recall-counter / citation-counter for smarter decay (sophistication; flagged for later)
- ❌ Custom parallelization layer (use Anthropic SDK native instead)
- ❌ New plugin (router evolves; no new plugin)
- ❌ Operator app build (separate spec; defer)

---

## Decisions locked (from user)

1. **Router evolves; no new plugin.** Existing nucleus-router becomes the Chief of Staff.
2. **15 verbs at the user-facing surface.** Listed below.
3. **Role-addressable fallback.** "Ask my X agent to Y" is a real pattern.
4. **Parallelization via Anthropic SDK's native parallel tool use.** No custom orchestrator. Structure prompts to *invite* parallel calls; trust the model.
5. **Add workstream node type.** New cortex primitive.
6. **Add DECISION knowledge entry type.** Decisions become first-class.
7. **Defer recall/citation counter.** Architectural sophistication; not blocking.

---

## Part 1 — The 15 verbs (user-facing surface)

The router's primary structure becomes a verb table. Each verb:
- Has natural-language patterns (replaces the current per-command intent rows)
- Routes by context to one or more roles (and the commands under them)
- Marks where parallel tool use is appropriate
- Respects autonomy mode per command

### Verb table

| # | Verb | Natural-language patterns | Routes to (by context) | Parallel? |
|---|---|---|---|---|
| 1 | **start day** | "start my day", "good morning", "let's go", "what's first" | Executive Assistant `/brief` + CKO load hot.md/pending-drafts check | Yes (read brief sources + memory simultaneously) |
| 2 | **catch me up on X** | "catch me up on X", "remind me about X", "what do we know about X", "what's the status of X" | CKO `/recall` (X = node) or memory-librarian (X = cross-node query) | Yes (multi-node reads independent) |
| 3 | **research X** | "research X", "look into X", "dig into X", "what's the latest on X" | Disambiguated: in-memory person → CKO `/recall` + (parallel) Account Executive `contact-researcher`; topic with sparse memory → CKO `/research-gaps`; pure external → web research with ≥2 sources | Yes (memory + web independent) |
| 4 | **draft X to Y** | "draft X to Y", "compose Y for X", "write a [reply/post/status]" | Communications Director (voice) → specialist by recipient type: lead-engine, bizdev-outreach, weekly-outreach, news-curator, client-status, referral-engine | No (specialist needs voice file loaded first) |
| 5 | **capture / remember X** | "capture this", "remember X", "I just learned X", "log Y", "take a note about Z" | CKO `/remember` (full) or `/note` (one-liner) — picks by content shape. Auto-graduates person pages on threshold. | No |
| 6 | **plan X** | "plan tomorrow", "plan my week", "plan my outreach", "start a new project" | Disambiguated: tomorrow → EA `/plan-tomorrow`; week → VP Relationships `/weekly-outreach`; project → Project Manager `/project-setup` | No |
| 7 | **track X** | "track my time", "log this touchpoint", "what's my pipeline look like" | Disambiguated: time → CFO `/track-time`; pipeline → COO `pipeline-analyst`; outreach → Head of Outbound `/lead-log` | No |
| 8 | **review X** | "review this doc", "QA this deck", "audit my voice", "review my memory" | Doc/deliverable → COO `/review-deliverable`; voice → Communications Director `/style-review`; memory → CKO `/cleanup` | No |
| 9 | **status update for X** | "draft status for X", "weekly status for client X" | Account Manager `/client-status` | No |
| 10 | **bill / invoice** | "bill this month", "generate invoices", "what should I invoice" | CFO `/generate-invoices` (reads time-log) | No |
| 11 | **what's on my plate** | "what's on my plate", "what's my day", "what should I do today" | Executive Assistant `/brief` | Yes (multi-source pull) |
| 12 | **what's missing in my memory** | "what's missing", "find gaps", "audit my knowledge" | CKO `/research-gaps` | Yes (scan + research independent per-gap) |
| 13 | **clean up X** | "clean up my memory", "prune stale", "audit my pipeline" | By target: memory → `/cleanup`; voice → `/style-review`; pipeline → `pipeline-analyst` cleanup mode | No |
| 14 | **close day** | "wrap up the day", "end of day", "close today" | EA + CKO `/end-day` (quick or full mode) | Partial (Steps 5.5, 5.6, 5.7 independent) |
| 15 | **close week** | "wrap up the week", "weekly retro", "end of week" | CKO + specialists `/end-week` | Partial (Step 2 + Step 3 + Step 5 partially independent) |

### Role-addressable fallback

For anything not matched by a verb, the user can address an agent by role:

| Pattern | Routes to |
|---|---|
| "Ask my Chief Knowledge Officer to ..." | claude-cortex |
| "Have my Chief of Staff ..." | nucleus-router itself (meta — for capability questions) |
| "Ask my Communications Director ..." | writing-style |
| "Have my Executive Assistant ..." | daily-brief |
| "Ask my Head of Outbound ..." | lead-engine |
| "Ask my Account Executive ..." | bizdev-outreach |
| "Have my VP of Relationships ..." | weekly-outreach |
| "Ask my Head of Partnerships ..." | referral-engine |
| "Have my Project Manager ..." | project-setup |
| "Ask my Account Manager ..." | client-status |
| "Ask my Chief Financial Agent ..." | time-tracking |
| "Ask my Chief Marketing Agent ..." | news-curator |
| "Ask my Chief Operating Officer ..." | core-ops |
| "Have my Cross-Team Liaison ..." | weekly-alignment |

Each plugin's name + role title becomes a real handle.

### Disambiguation procedure

When a verb is invoked with ambiguous context (e.g., "research X" without enough signal to route), the Chief of Staff asks ONE clarifying question:

> "Quick clarify — are you researching a person, a topic, or a company? (Or just say 'either, run a broad search.')"

When two routes match equally well, list both and let the user pick. Never silently dispatch on ambiguous input.

### Voice change

The router's response pattern shifts from:

> "Sounds like you want to run `/lead-draft`. Run it?"

to:

> "On it — drafting outreach to Sarah. Loading her person page and recent thread context, then composing in your voice. ~30 seconds."

The new voice is **direct, competent, narrating**. It tells you what it's about to do, then does it. Confirmation is implicit unless the autonomy slider for that command is `confirm` mode — in which case it still surfaces the destructive-action gates.

For "auto" autonomy mode commands, the router doesn't surface any prompt — just narrates:

> *(user says "capture this")*
> "Got it — logging to memory."

For "confirm" autonomy mode commands, it preserves the gate:

> *(user says "draft outreach to Sarah")*
> "Drafting now. I'll surface the draft before anything goes to Gmail. ~30 seconds."

---

## Part 2 — Parallel tool use

Use Anthropic SDK's native parallel tool use. Don't build a custom orchestrator. Three places in the router skill where the prompt should *invite* parallel calls:

### Where parallel is genuinely efficient

1. **Multi-source mining fan-out** (`/listen`, future `/sweep`). Transcript-reviewer + conversation-miner + activity-miner read different surfaces, produce independent proposals. Already in the spec for `/listen`; rewrite to invite parallel invocation: "These three agents read disjoint substrate; invoke them in parallel and aggregate proposals after."

2. **Multi-node reads** (`/recall person:X` + `/recall client:Y` + `/recall topic:Z`). When the user asks a cross-cutting question or "research X" routes to memory + web simultaneously, the reads are independent. Prompt: "These node reads are independent; invoke in parallel; synthesize after."

3. **Pre-fetching during user-gate pauses** (`/morning` walking proposals, `/end-day` between steps). While the user is reviewing proposal N, the next proposal's context can be pre-loaded. This is a UX optimization — same total work, lower felt latency.

### Where parallel doesn't help

- Drafting (output of one tool informs next).
- Anything with user gates between steps.
- Sub-100ms operations (overhead exceeds benefit).
- Anything writing to the same file (race conditions).

### Implementation pattern

In each router prompt where parallel is appropriate, add a sentence like:

> "The following operations read independent sources. You may invoke them in parallel (the API supports parallel tool use) and aggregate results after."

The Anthropic API handles the rest. No new infrastructure in cortex or router.

---

## Part 3 — Workstream node type (new cortex primitive)

### Why

Operators run **ongoing initiatives** that span multiple projects, people, and topics. Examples:
- "BrightWay 2026 product strategy" — touches multiple clients, multiple advisors, multiple decisions.
- "Ops platform evaluation" — touches multiple vendors, multiple internal stakeholders, multiple criteria.
- "Q3 outbound campaign" — touches dozens of contacts, multiple message variants, multiple results.

Today these end up as project nodes (`client/<slug>`), topic nodes (`topic/<slug>`), or domain nodes (root `<name>.md`). None capture the *ongoing pipeline of activity* shape — current state, pinned context, recent activity, open loops, linked entities.

### Schema

New directory: `<config-root>/memory/workstream/<slug>.md`.

Schema:

```markdown
---
type: workstream
status: active | paused | completed | archived
created: YYYY-MM-DD
last_active: YYYY-MM-DD
decay_profile: slow  # workstreams should decay slowly; they're ongoing
---

# <Workstream Name>

## Current state
<One paragraph — where we are right now. What's true today. What's next.>

## Pinned context
<Background that doesn't change — the goal, the constraints, the players.>

## Recent activity
- YYYY-MM-DD — <one line>
- YYYY-MM-DD — <one line>
(rolling — last 20 entries)

## Open loops
- [P0] <thing waiting on me>
- [WAITING:them] <thing waiting on someone else>
- [DECIDED:date] <resolved loop — kept for traceability>

## Linked entities
- People: [[person/<slug>]], ...
- Clients: [[client/<slug>]], ...
- Topics: [[topic/<slug>]], ...
- Domains: [[<root-domain>]], ...

## Knowledge (workstream-scoped)
### Insights
- [confirmed:date] <entry>
### Models
### Gotchas
### Lessons
### Recipes
### Corrections
### Decisions  ← NEW (Part 4)

## Changelog
[YYYY-MM-DD] <event line>
```

### How workstreams differ from existing node types

| Type | Captures | Time horizon | Updates |
|---|---|---|---|
| **client/** | A specific engagement | Engagement lifetime | Per session |
| **person/** | A relationship | Indefinite | Per interaction |
| **topic/** | A subject area | Indefinite | Per learning |
| **domain/** (root) | A persistent area of work | Indefinite | Per session |
| **workstream/** (new) | An ongoing initiative pipeline | Defined start; eventual end | Per session, with explicit current-state |

Workstreams sit *above* projects (one workstream may include multiple client engagements) and *below* domains (one domain may have multiple parallel workstreams).

### Integration

- **`/remember`** Step 2 routing — detect workstream-shaped content (initiatives, ongoing efforts, multi-entity threads) and route to workstream nodes.
- **`memory-librarian`** — queries that say "what's happening with X initiative" → workstream lookup preferred.
- **`indexer`** — adds `## Workstreams` section to `memory/index.md` catalog.
- **`/recall workstream:<slug>`** — surfaces a workstream's current state + open loops + recent activity (~20 lines).
- **Hot cache** — recently-active workstreams (last 7 days) appear in `hot.md`.
- **Decay** — workstreams default to `decay_profile: slow` (1.5x multiplier on freshness thresholds). Workstream entries that go 6+ months without activity prompt "is this still active?" via `/cleanup`.

### Creation

The user creates a workstream by saying any of:
- "Start a new workstream: X"
- "I'm working on a new initiative — X"
- "Begin tracking X as a workstream"

The Chief of Staff routes to a new `/start-workstream <slug>` command (added in cortex v4.9.0) that prompts: name, current state (one paragraph), pinned context, initial linked entities. Then writes the new node file. Idempotent.

---

## Part 4 — DECISION knowledge entry type (new cortex primitive)

### Why

Currently the knowledge taxonomy is: INSIGHT / MODEL / GOTCHA / LESSON / RECIPE / CORRECTION. None of these captures **decisions you've made**. "We decided to go with Pipedrive over HubSpot" today gets recorded as either a CHANGELOG line (transient) or a LESSON (retrospective). Neither is right.

Decisions need their own type because:
- They're *commitments* (forward-looking, not lessons learned)
- They're worth revisiting when context changes (cheaper to re-evaluate a decision than to rediscover one)
- They affect downstream actions (any future "should we use X" is informed by past decisions)

### Schema

DECISION entries follow the standard knowledge-entry shape with these required fields:

```markdown
- DECISION [confirmed:YYYY-MM-DD] <one-line decision>
  - **What was decided:** <the choice>
  - **When:** YYYY-MM-DD
  - **Why:** <reasoning at the time>
  - **Affected:** [[entity1]], [[entity2]] (linked entities)
  - **Revisit when:** <trigger condition, if any — "if Pipedrive raises prices" / "if we hire a 3rd person" / "annually">
  - **Status:** active | superseded | revisit-now
```

The `Revisit when` field is the key innovation. Most decisions become invisible once made; tagging them with a re-evaluation trigger means `/cleanup` and `/recall` can surface them when the trigger fires.

### Decay behavior

DECISION entries decay slowly (1.5x multiplier, same as RECIPE) — they stay relevant longer than INSIGHTs. They never auto-archive. They can be:

- **Marked superseded** when a new DECISION on the same topic explicitly overrides — old moves to `## Demoted knowledge` with `↳ superseded by: <new>`.
- **Marked revisit-now** by `/cleanup` when their `Revisit when` trigger appears to have fired.
- Otherwise: persistent.

### Integration

- **`/remember`** Step 2's knowledge extraction — recognize decision-shaped content. Cues: "we decided," "I'm going with," "settled on," "the call is," "going forward we'll." Auto-tag as DECISION type. Prompt for the `Revisit when` field if not provided.
- **`memory-librarian`** — rank DECISION entries higher when the query is about a past choice or current strategy ("why are we using X" / "what was our approach to Y").
- **`/cleanup`** section J (new) — scan DECISIONs for `Revisit when` triggers that appear to have fired (e.g., the named condition is mentioned in recent activity). Surface for user re-evaluation.
- **`/research-gaps`** — under-cited DECISION entries get the same source-rule as under-cited INSIGHTs.
- **Hot cache** — recent DECISIONs (last 7 days) appear in `hot.md` "Recent decisions" section (already part of the spec, just now properly typed).

---

## Part 5 — Implementation plan

### Day 1 — Router rewrite (nucleus-router v0.2.0)

- Rewrite `skills/route/SKILL.md` with the verb table as primary structure
- Add role-addressable fallback section
- Add parallel-tool-use guidance for `/listen`, `/recall` cross-node reads, `/sweep` (when shipped), `/morning` pre-fetching
- Shift voice from "Sounds like you want to run /X" to "On it — [doing what]"
- Keep the legacy command table as the second-tier fallback (for power users typing exact commands)
- Bump router to v0.2.0; CHANGELOG entry

### Day 2 — Workstream node type (cortex v4.9.0 part 1)

- New `references/workstream-schema.md` — formal schema doc
- Update CLAUDE.md storage layout to include `memory/workstream/`
- New `commands/start-workstream.md` + `skills/start-workstream/SKILL.md`
- Update `/remember` Step 2 routing to detect workstream-shaped content
- Update `memory-librarian` agent to handle workstream queries
- Update `indexer` skill + `references/memory-index.md` to include `## Workstreams` section
- Add `decay_profile: slow` default to workstream front-matter
- Update `references/decay-model.md` with workstream rules

### Day 3 — DECISION knowledge type (cortex v4.9.0 part 2)

- Update CLAUDE.md knowledge taxonomy to add DECISION (alongside INSIGHT / MODEL / GOTCHA / LESSON / RECIPE / CORRECTION)
- Update `/remember` Step 2 extraction to recognize decision cues
- Update `references/decay-model.md` — DECISION decays 1.5x (slow) like RECIPE; supersede via concept-drift detection
- Update `memory-librarian` agent to rank DECISIONs appropriately
- Update `/cleanup` to add section J (DECISION revisit-trigger scan)
- Update hot.md spec to formalize "Recent decisions" section
- Update CHANGELOG; bump cortex to v4.9.0

### Day 4 — Nucleus updates + commits

- Rewrite README to lead with the 15-verb framing (replaces the AI staff catalog as the primary section; AI staff stays as the role reference)
- Update CLAUDE.md notes in nucleus
- Commit + push cortex v4.9.0, router v0.2.0, nucleus repo

### Day 5 — Dogfood + adjust

- Run the new router for a day
- Tune verb table based on what feels off
- Patch as needed (v4.9.1 / v0.2.1)

Total: ~1 week single-engineer.

---

## Karpathy alignment

This proposal closes the remaining gaps from the codex-maxxing takeaways:

| Karpathy pattern | Status before | Status after |
|---|---|---|
| Vault-as-app + AGENTS.md schema | ✅ | ✅ |
| Heartbeats / recurrence loops | ⚠ (`/listen` only) | ⚠ (still only `/listen`; `/sweep` separately deferred) |
| Strong goals + verification oracles | ✅ | ✅ |
| Git diff as review surface | 📋 | 📋 (still `memory-as-git` proposal) |
| **Operating loops over single prompts** | ⚠ | ✅ — verbs are loops; voice narrates the loop |
| Steering / async instruction stacking | ❌ | ⚠ partial — parallel tool use is a form of fan-out steering |
| **Workstream primitive** | ❌ | ✅ |
| **Decision primacy** | (not in Karpathy; original) | ✅ |
| Single-purpose files | ✅ | ✅ |

The "operating loop" reframe + workstream primitive together represent the bulk of what was missing.

---

## Acceptance criteria

- [ ] nucleus-router v0.2.0 shipped with verb table as primary skill structure
- [ ] Role-addressable patterns documented and routed
- [ ] Parallel tool use guidance present for `/listen`, `/recall` cross-node, `/sweep` future, `/morning` pre-fetching
- [ ] Router voice updated (narrating Chief of Staff, not "Sounds like /X")
- [ ] cortex v4.9.0 ships workstream node type + DECISION knowledge type
- [ ] `/start-workstream` command exists and creates workstream nodes
- [ ] `/remember` routes decision-shaped content to DECISION type, workstream-shaped content to workstream nodes
- [ ] memory-librarian, indexer, `/cleanup`, `hot.md`, decay-model all updated for both new primitives
- [ ] CLAUDE.md schema updates in both nucleus + cortex
- [ ] README rewrite leads with the 15-verb framing
- [ ] All three repos committed and pushed

---

## What this enables

After this ships:

- The user says "research Acme before our 2pm" → Chief routes: pulls Acme client node + Sarah's person page (parallel), kicks off contact-researcher for fresh context (parallel), composes a one-page brief.
- The user says "we decided to go with Pipedrive" → DECISION captured with Revisit-when prompt. Six months later when "we should consider Salesforce" comes up, `/cleanup` surfaces the original DECISION for re-evaluation.
- The user says "start a workstream: Q3 outbound campaign" → workstream node created. Future "what's happening with Q3 outbound" → workstream lookup. The pipeline of activity has somewhere to live.
- The user says "ask my Chief Financial Agent to bill this month" → routes to time-tracking directly via role addressability.

The 60+ commands stay in place. They're just no longer the surface. The user thinks in verbs and roles; the Chief routes; specialists do the work.
