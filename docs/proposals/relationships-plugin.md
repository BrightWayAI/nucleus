# Proposal — `relationships` plugin (daily relationship cockpit)

**Status:** Open. Scaffold landed locally 2026-05-28; awaiting user review before deepening commands and shipping to GitHub.

**Owner:** BrightWay AI.

**Target ICP for this plugin (consistent with Nucleus productization):** solo operators and small fractional teams who need to be intentional across new business, relationship maintenance, and network expansion while running a real life. Time-constrained. Doesn't want a CRM that nags. Wants one command in the morning that says "here's the highest-leverage 3 things across each bucket, here's exactly what to say, do them in 15 minutes or move on."

---

## Motivation

Nucleus already has a strong BD substack (cortex person pages + identity + voice, `lead-engine` signals, `bizdev-outreach` drafting, `weekly-outreach` weekly prep, `referral-engine` warm-network activation, `core-ops` pipeline analyst). What's missing is a **daily orchestrator** that:

1. Looks across all three buckets simultaneously (new biz / relationship / network) rather than treating prospecting and relationship-maintenance as separate weekly rituals.
2. Is realistic about a busy operator's day — surfaces 3 options per bucket with a time estimate, supports "how much time do I have today?" filtering, and refuses to guilt-trip about a 40-deep overdue backlog.
3. Solves the "what do I actually say?" problem with a first-class templates library, not just freeform drafting. Channel recommendation + template-driven message that fills variables from cortex.
4. Treats personal close-relationship maintenance as a real track — separate from business but visible alongside it.

The existing `weekly-outreach` was the closest thing, but its scope is weekly BD prep (10–12 contacts, weekly cadence, CRM tasks + calendar placeholders). It is not a daily three-bucket cockpit, and it does not own templates.

---

## Architecture

### Plugin shape

One new plugin: **`relationships`** (functional name, matching marketplace convention).

```
relationships/
├── .claude-plugin/plugin.json
├── commands/
│   ├── setup-relationships.md
│   ├── relationships.md             # the daily brief
│   ├── network-rebalance.md         # quarterly tier review (Phase 3)
│   └── draft-touchpoint.md          # per-contact draft on demand (Phase 2)
├── skills/
│   ├── setup/SKILL.md
│   └── relationships/SKILL.md       # natural-language entrypoint
├── agents/
│   └── relationship-ranker.md       # subagent that scores + ranks contacts
├── references/
│   ├── framework.md                 # tiered cadence + Ferrazzi layer + reality layer (spec)
│   ├── person-page-extensions.md    # additive YAML fields on cortex person pages
│   ├── scoring.md                   # weighted scoring math + signals
│   ├── user-context.template.md
│   └── templates/
│       ├── comment/ dm/ email/ text/ call/ conference/
├── README.md / CHANGELOG.md / LICENSE / SECURITY.md / .gitignore
```

### Decomposition decision

Three plugins, not one monolith:

- **`relationships` (new)** — daily orchestrator. Owns the three-bucket brief, tier/cadence logic, templates library, person-page extensions.
- **`lead-engine` (refurbish)** — keep. Provides the `contact-researcher` subagent (used by ≥5 plugins per `nucleus/docs/contracts.md`) plus the signal taxonomy. `relationships` delegates new-biz research here.
- **`referral-engine` (refurbish)** — keep. Owns warm-network activation triggers (cooling rules, positive moments, fiscal-year triggers). `relationships` delegates relationship-bucket "ask" drafting here.

**Retire:**
- `weekly-outreach` — its weekly-prep role is subsumed by `relationships`'s daily brief plus a planned `--week` mode. Logic worth keeping (Step 9 person-page side-effects, the "should we even send?" filter, the CRM-tasks + calendar-placeholders pattern) gets ported into `relationships`.
- `bizdev-outreach` — its three-phase research-analyze-draft methodology becomes the contract for the `relationships` drafting layer + templates library. The standalone plugin is deprecated.

Net catalog change: 14 → 14 (gain `relationships`, lose `weekly-outreach` + `bizdev-outreach`, but those happen in a follow-up PR after `relationships` ships and proves it covers the use cases).

### Verb-router integration

`nucleus-router` already routes the verb pattern (chief-of-staff-evolution shipped 2026-05-20). Suggested router-intent rows to add in `nucleus-router` v0.2.x:

- "who should I reach out to today" → `/relationships`
- "what's my outreach plan today" → `/relationships`
- "help me draft a message to <name>" → `/draft-touchpoint <name>`
- "review my network" / "rebalance my tiers" → `/network-rebalance`
- "set up relationships" / "configure my relationships" → `/setup-relationships`

### Daily-brief integration

`daily-brief` currently shows an "outreach queue" section in `/brief`. Two options:

1. **Loose coupling (default for v0.1):** `relationships` writes `<config-root>/relationships/today.md` and `<config-root>/relationships/today.json`. `daily-brief` Section X reads `today.md` and renders a summary card linking out to `/relationships` for the full brief.
2. **Tight coupling (later):** `daily-brief`'s outreach section is replaced wholesale by a render of the `relationships` brief. Defer until both plugins have been used together for a few weeks.

### Eventual web app

Out of scope for this plugin. The `today.json` artifact is the structured contract that a future Next.js + Supabase web app (and/or the Operator desktop app from `jarvis-app.md`) would consume. Plugin produces the data; surfaces are decoupled.

---

## Framework

Documented fully in `relationships/references/framework.md` (to be written in Phase 1). Summary:

### Three buckets

1. **New Business Development** — outbound to ICP fits, active-deal follow-ups, warm intro asks.
2. **Relationship Building** — strategic peers, mentors, clients, partners; visually separated tab for **close personal** (family, close friends).
3. **Network Expansion** — LinkedIn engagement, conferences, meetups, content opportunities. Default supports **two voice streams** (configurable in setup) — e.g., personal brand and business brand.

### Four tiers (configurable, with defaults)

| Tier | Default size | Default cadence | Behavior |
|---|---|---|---|
| Inner Core | 10–15 | biweekly | Always surfaces when overdue |
| Strategic | 30–50 | monthly | Surfaces when overdue + trigger |
| Operational | 100–200 | quarterly | Surfaces on trigger only |
| Dormant | rest | on trigger only | Never proactively surfaced |

Setup interview asks "how many are you actively trying to be close to" — tier sizes are user-configurable. Acceptable to ship a 5-person inner core or a 30-person one.

### Scoring signals (weighted)

- **Cadence decay** — `(days_since_last_touch / tier_target_days)`, clamped
- **External triggers** — recent job change, funding, post worth engaging (via `lead-engine` signal taxonomy)
- **ICP fit** — alignment with user-context's current focus
- **Reciprocity debt** — WAITING:you open loops, recent giving from them
- **Quarterly goal alignment** — bonus weight if the contact is tied to a stated quarterly goal in user-context

Full math in `relationships/references/scoring.md`.

### Reality layer

- No guilt. If 40 contacts are overdue, surface the 3 highest-leverage; the rest stay quiet.
- "How much time do you have today?" filter (5 / 15 / 30 / 60+ min) re-ranks. Each card shows a time estimate so the user can construct their own block.
- Quarterly reset via `/network-rebalance` — bulk re-tagging and dormant-demotion.

### Templates approach

Channel-aware. Each surfaced action carries:
- A **recommended channel** (comment / DM / email / text / call / conference DM) determined by relationship class + tier + trigger.
- A **template-driven draft** with variables filled (`{{person.name}}`, `{{trigger.context}}`, `{{user.business}}`, `{{user.first_name}}`, etc.).
- A **time estimate** in minutes so the user can construct their own block.

Templates live at `relationships/references/templates/<channel>/<scenario>.md` (bundled defaults; user-editable). Plus user-added templates at `<config-root>/relationships/templates/` override the bundled ones with the same filename.

Voice-tuning: templates respect `<config-root>/voice.md` and any additional voices defined in setup (e.g., personal brand voice vs. business brand voice). Banned-phrases list is inherited from cortex + writing-style.

---

## Contracts (additions to `nucleus/docs/contracts.md`)

### New files this plugin writes

`<config-root>/plugins/relationships.user-context.md`
- **Writer:** `relationships` `/setup-relationships`
- **Readers:** all `relationships` commands; eventually a future web-app reader
- **Sections:** identity, ICP, current quarter focus, tiers (configurable sizes + cadences), buckets (sizing + emphasis), voices (named — e.g., `personal`, `business`), CRM property mapping, integrations (lead-engine? referral-engine? core-ops? apollo?), time-budget defaults
- **Format:** stable, sections additive over time

`<config-root>/relationships/today.md`
- **Writer:** `relationships` `/relationships`
- **Readers:** the user; optionally `daily-brief` (later, via contract); optionally a future web app or Operator desktop app
- **Format:** markdown brief with three buckets, three options per bucket, channel + draft + time estimate

`<config-root>/relationships/today.json`
- **Writer:** `relationships` `/relationships`
- **Readers:** future web app, Operator desktop app, any downstream surface
- **Format:** JSON Schema documented in `relationships/references/today-json-schema.md` (TBD Phase 2)

`<config-root>/relationships/templates/` (optional user overrides)
- **Writer:** user, manually
- **Readers:** `relationships` template loader (overrides bundled defaults by filename)

### Existing files this plugin reads

- `<config-root>/identity.md` (cortex)
- `<config-root>/voice.md` (cortex)
- `<config-root>/memory/person/*.md` (cortex person pages — additive write to `## Recent interactions` only)
- `<config-root>/memory/hot.md` (cortex hot cache — for recent context)
- `<config-root>/memory/workstream/*.md` (cortex workstreams — for quarterly goals)
- CRM MCP (read-only)
- Calendar MCP (read-only)
- Email MCP (read-only)
- Apollo MCP (optional, read-only)

### Existing subagents this plugin invokes

- `contact-researcher` (lead-engine) — per-contact deep dives when needed
- `pipeline-analyst` (core-ops) — new-biz bucket ranking
- `memory-librarian` (cortex) — cross-cortex queries

---

## Person-page extensions (additive)

The plugin proposes these YAML fields on cortex person pages (`<config-root>/memory/person/<slug>.md`):

```yaml
relationships:
  tier: inner | strategic | operational | dormant   # defaults to operational
  buckets: [new_biz, relationship, network]         # which buckets this person is eligible for
  relationship_class: business | personal           # affects channel + voice selection
  icp_fit: primary | secondary | none               # for new-biz weighting
  next_touch_target: YYYY-MM-DD                     # auto-computed from tier + last contact
  generosity_ledger:
    - date: YYYY-MM-DD
      direction: gave | received
      note: short string
```

These live in YAML frontmatter or in a dedicated `## Relationships` section (TBD with cortex maintainers — see "Open questions" below). The plugin treats untagged people as `tier: operational`, `relationship_class: business`, `icp_fit: none`. Migration handled by `/network-rebalance` (Phase 3).

Full spec in `relationships/references/person-page-extensions.md`.

---

## Phased build

### Phase 1 — Scaffold + setup + templates + framework spec (~2-3 sessions)
- Plugin directory + manifest + README/CHANGELOG/LICENSE/SECURITY ✅ (this PR)
- Proposal in nucleus/docs/proposals/ ✅ (this PR)
- `/setup-relationships` command — interview-driven, idempotent
- `user-context.template.md`
- Templates library v1 (~20 bundled defaults across all six channels)
- `framework.md`, `scoring.md`, `person-page-extensions.md`
- Nucleus marketplace.json entry (not yet pointing at a published GitHub repo)
- Nucleus contracts.md rows added

### Phase 2 — `/relationships` daily command (~2 sessions)
- Commands/relationships.md — orchestrates: read cortex → score → rank → pick templates → draft → present
- skills/relationships/SKILL.md — natural-language entrypoint
- agents/relationship-ranker.md — scoring subagent
- `today.md` + `today.json` writers; JSON schema documented
- Time-budget filter (5/15/30/60+)
- Two-voice support
- Optional delegation to `contact-researcher` and `pipeline-analyst`

### Phase 3 — Migration + tagging (~1-2 sessions)
- `/network-rebalance` — walks existing person pages, proposes tier + bucket + icp_fit, user approves in batches
- LinkedIn-export staging importer
- iCloud-contacts staging importer
- HubSpot tag cross-reference
- Decide on schema location for the new YAML (frontmatter vs. dedicated section) — coordinate with cortex v4.x

### Phase 4 — Retire predecessors (~1 session)
- Migrate weekly-outreach Step 9 person-page side-effect into `relationships`
- Move `bizdev-outreach` drafting tone-mirroring + "should we even send?" filter into templates + scoring
- Deprecate weekly-outreach + bizdev-outreach repos with redirect READMEs
- Drop marketplace.json entries

### Phase 5 — Network expansion module (~1-2 sessions)
- Conference/event discovery: AI web search + Eventbrite/Luma/Meetup APIs
- LinkedIn posting cadence (two voice streams: personal vs. business brand)
- Quarterly review dashboard

### Phase 6 — Web app (deferred; separate proposal)
- Decide after Phase 2 has been in daily use for 2+ weeks
- Likely Next.js + Supabase + Vercel, reading `today.json`
- Mobile-first responsive UI; PWA install
- Coordinate with `jarvis-app.md` proposal if Operator desktop ships first

---

## Open questions

1. ~~**Person-page YAML location**~~ — **RESOLVED 2026-05-28:** YAML frontmatter under a `relationships:` namespace at the top of the person-page file. Treated as candidate cortex v4.12.0 additive schema bump. Other plugins writing person-page state should use their own frontmatter namespace.
2. **Voice file extensions** — Cortex has a single `voice.md`. For two-voice support, do we add `voices/<name>.md` to cortex, or keep voice as a per-plugin override in `relationships.user-context.md`? Defer to cortex v4.x roadmap.
3. **Daily-brief integration timing** — Loose coupling for v0.1, tight integration later? Or coordinate from the start?
4. **Sync interval (web-app phase)** — User suggested 50 min for the web-app sync layer. Defer until Phase 6.
5. **Multi-user web app from day one** — Build agnostic plugin (cheap), single-user web app v1 (cheap), multi-user web app v2 (deferred until distribution).

---

## Acceptance criteria for Phase 1 (the current scope)

- `relationships/` plugin directory exists in `~/lab-bench/` with full scaffold (manifest, README, CHANGELOG, LICENSE, SECURITY, .gitignore, all subdirectories).
- `/setup-relationships` command file exists with the standard Step 0 (config-root resolve) + interview structure, even if not yet exercised.
- `references/user-context.template.md` documents the full user-context schema.
- `references/templates/` contains ≥15 bundled default templates across all six channels.
- `references/framework.md`, `references/scoring.md`, `references/person-page-extensions.md` exist and are coherent enough to drive Phase 2 implementation.
- `nucleus/docs/proposals/relationships-plugin.md` (this doc) exists.
- `nucleus/.claude-plugin/marketplace.json` has the row for `relationships` (pointing at the future BrightWayAI/relationships repo; not yet published).
- `nucleus/docs/contracts.md` has rows for the new files this plugin writes.
- No code shipped to GitHub yet. All changes local until user review.

---

## What this proposal does NOT cover (out of scope)

- Web app / mobile UI — defer to Phase 6 proposal.
- Multi-user / multi-tenant — defer to Phase 6.
- Conference discovery deep-features — Phase 5.
- LinkedIn posting cadence orchestration — Phase 5.
- Real refurbish of `lead-engine` and `referral-engine` (they stay as-is for Phase 1; `relationships` calls them as available).
- Retirement of `weekly-outreach` and `bizdev-outreach` — Phase 4.
