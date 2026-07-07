# Nucleus

**The operating system for solo operators running on AI.**

You're a consultant, a fractional operator, a founder, a one-person agency. Your work is too varied for any single SaaS tool. Your relationships are too important to forget. Your voice is too specific to delegate to a generic AI. Your day is too dense to navigate by clicking through tabs.

Nucleus is what you install when you want Claude to actually run your operation — remember your world, draft in your voice, surface what needs your attention, and stay out of your way the rest of the time.

Compatible with **Claude Cowork (Desktop)** and **Claude Code**. 100% free and open source. MIT-licensed across every plugin.

---

## Talk, don't memorize

> *"What's on my plate today?"*
> Chief of Staff: "On it — pulling your calendar, inbox, CRM tasks, and yesterday's reflection. ~10 seconds."
>
> *"I just met Sarah at the AI Summit — VP Eng, sharp."*
> Chief: "Capturing — creating Sarah's person page, linking to the conference."
>
> *"Research Acme before our 2pm."*
> Chief: "Looking into Acme. I have a client node and Sarah's person page; kicking off fresh contact research in parallel. ~30 seconds."
>
> *"Wrap up the day."*
> Chief: "Closing the day — quick mode. Capturing reflection, pre-staging tomorrow's brief, refreshing the index and hot cache."

You talk in **verbs** — *catch me up, research, draft, capture, plan, track, review, status, bill, what's on my plate, what's missing, clean up, close day, close week, start day*. The Chief of Staff (the nucleus-router skill, v0.2+) routes each verb to the right specialist on your AI staff, invokes parallel work where independent, and narrates what it's doing.

You can also **address agents by role**: *"ask my Chief Financial Agent to bill this month"*, *"have my VP of Relationships prep the week"*. Each plugin's AI staff role title is a real handle.

The 60+ underlying slash commands are still there — power users can type `/lead-draft` directly when they want to — but they're plumbing, not the surface.

---

## What you get

A second brain that learns and forgets. A daily rhythm that compounds. A relationship engine that doesn't let connectors go cold. A voice that gets sharper every week. A graph view in Obsidian on desktop and phone. A Chief of Staff who runs the orchestration.

**13 plugins. 7+ subagents. Chief of Staff orchestrator with 15-verb surface + role-addressable fallback. Bidirectional memory (learning + decay). Workstream + DECISION node types. Daily/weekly closing rituals. Overnight ingest + morning review. Obsidian-as-UI. Adaptive voice. Pipeline analytics. Calendar-to-invoice loop.**

### The 15 verbs (your daily surface)

| Verb | What happens under the hood |
|---|---|
| **start day** / *what's on my plate* | Today's brief — calendar, inbox, CRM tasks, outreach, yesterday's reflection (parallel pulls) |
| **catch me up on X** | Memory recall against the person / client / topic / workstream node |
| **research X** | Memory lookup + (parallel) external research where appropriate |
| **capture / remember X** | Typed memory write; auto-graduates person pages; detects DECISION-shaped content |
| **draft X to Y** | Recipient context + voice + specialist (lead-engine, relationships, client-status, news-curator) |
| **plan X** | Disambiguated: tomorrow's calendar / week's outreach / new project / new workstream |
| **track X** | Disambiguated: time / pipeline / outreach touchpoint |
| **review X** | Doc QA / voice audit / memory hygiene / pipeline cleanup |
| **status update for X** | Client status draft from memory + project state + calendar + CRM |
| **bill / invoice** | Monthly invoicing from the time log |
| **what's missing in my memory** | Autonomous gap-finder + web research with ≥2 sources |
| **clean up X** | Memory / voice / pipeline |
| **close day** | Reflection + commit + pre-stage tomorrow + refresh index + refresh hot cache |
| **close week** | Transcript review + cleanup + rehearse + research-gaps + Monday outreach pre-stage |
| **start a workstream X** | Create a new ongoing-initiative node — current state, pinned context, linked entities |

Plus role-addressable fallback: *"ask my [Chief Knowledge Officer / Chief Financial Agent / Chief Marketing Agent / Communications Director / Executive Assistant / Head of Outbound / ...] to X"* routes directly to that plugin.

---

## Install in five minutes

```
/plugin marketplace add BrightWayAI/nucleus
```

Then in Claude, just say it:

> **"Start nucleus"** — or "let's get started," "set me up," "onboard me." The router suggests `/start-nucleus`, which walks every foundational setup in order (identity → voice → note sources → Obsidian vault → per-plugin setups → diagnostics → optional schedule registration). Idempotent — re-running picks up where you left off. ~15-30 minutes depending on how many plugins you install.

Prefer to do it by hand? Run each setup explicitly:

1. `/setup-identity` — answer ~8 questions about who you are.
2. `/setup-voice` — paste two sample emails so cortex learns your voice.
3. `/setup-sources` — connect Granola / Gemini / Fireflies / Drive (optional but unlocks `/listen` overnight ingest).
4. `/setup-obsidian` — scaffolds an Obsidian vault over your config root.
5. Per-plugin `/setup-*` for each installed plugin (captures CRM, ICP, offerings, billing rates — whatever that plugin needs).
6. `/diagnose` (in core-ops) — verify everything is wired.
7. `/register-schedules` (in core-ops) — wire the standing daily/weekly/monthly automation.

After setup: `/route` prints the full cheat-sheet. You'll rarely need it — just talk.

---

## Your AI staff

13 plugins, but think of them as the team you wish you had — your AI org chart for solo operators who do everything. Each plugin is a teammate with a role; they work side-by-side, share context (identity + voice), and compound the longer you run them.

> **Start here.** The minimum-viable Nucleus is three plugins: **nucleus-router** + **claude-cortex** + **core-ops**. Install those, run `/start-nucleus`, and add specialists (BD, content, delivery) as you need them. Don't try to install all 13 on day one. The recommended install combos further down show common bundles by operator archetype.

### Foundation — your office of the operator

These are always on. No commands needed; they run in the background.

| Role | Plugin | What they do |
|---|---|---|
| **Chief Knowledge Officer** | [claude-cortex](https://github.com/BrightWayAI/claude-cortex) | Your second brain. Typed memory nodes (people, clients, topics, domain knowledge, **workstreams**), bidirectional learning (mining + decay), auto-maintained `memory/index.md` catalog, autonomous gap-finder (`/research-gaps`), `/listen` overnight ingest, `/morning` proposal walker, Obsidian vault scaffolding. **DECISION** knowledge entries with Revisit-when triggers (v4.9+). |
| **Chief of Staff** | [nucleus-router](https://github.com/BrightWayAI/nucleus-router) | The orchestrator (v0.2+). 15 verbs at the user-facing surface + role-addressable fallback. Routes verbs to specialists by context, invokes parallel work where independent, narrates execution instead of asking permission. The 60+ underlying slash commands are plumbing; verbs are the interface. `/route` prints the cheat sheet. |
| **Communications Director** | [writing-style](https://github.com/BrightWayAI/writing-style) | Keeps everything sounding like you. `/style` drafts in your voice. `/style-learn` updates the voice file from real edits (two-stage triage). `/style-review` audits style rules for contradictions. |

**CKO's subagents:** `memory-librarian`, `transcript-reviewer`, `conversation-miner`, `activity-miner`, `gap-researcher`.

### Daily operations — your executive assistant

The teammate who runs your day.

| Role | Plugin | What they do |
|---|---|---|
| **Executive Assistant** | [daily-brief](https://github.com/BrightWayAI/daily-brief) | Today's working surface. `/brief` builds a Cowork artifact with calendar + inbox + CRM + outreach + yesterday's reflection. `/process-brief` routes your annotations to Gmail drafts, CRM reschedules, outreach drafts. `/plan-tomorrow` blocks the next workday. As of v0.3+: meetings are read-only context cards; only inbox / tasks / outreach take annotations. |

### Revenue & relationships — your AI BD team

Three roles split the relationship-and-pipeline workload.

| Role | Plugin | What they do |
|---|---|---|
| **Head of Outbound** | [lead-engine](https://github.com/BrightWayAI/lead-engine) | LinkedIn intent-based outbound. Catches buying signals, drafts warm DMs in your voice, runs 3-touch cadences, generates pre-call briefs. |
| **VP of Relationships** | [relationships](https://github.com/BrightWayAI/relationships) | Daily relationship cockpit. `/relationships` produces a prioritized 3-bucket brief (new business / relationship building / network expansion) with 3 actions per bucket — each ships with a recommended channel, time estimate, and a copy-ready draft from a 17-template library. `/draft-touchpoint` drafts on demand per contact. `/network-rebalance` re-tags tiers quarterly. Drafts only — never sends. |
| **Head of Partnerships** | [referral-engine](https://github.com/BrightWayAI/referral-engine) | Latent revenue from connectors who've gone quiet. Weekly digest of who to re-engage, drafted asks honoring cooling periods. |

**Their shared subagent:** `contact-researcher` (deep single-contact dives across CRM / email / web).

### Client delivery — your AI delivery team

Three roles run the engagement lifecycle.

| Role | Plugin | What they do |
|---|---|---|
| **Project Manager** | [project-setup](https://github.com/BrightWayAI/project-setup) | New-engagement initialization. One interview produces Drive folder structure, Claude Project system prompt, phased plan, and a memory node. Templates user-customizable. |
| **Account Manager** | [client-status](https://github.com/BrightWayAI/client-status) | Weekly client status drafts auto-built from memory, project state, calendar, and CRM activity. Closes the retention loop most consultants leave on the table. |
| **Chief Financial Agent** | [time-tracking](https://github.com/BrightWayAI/time-tracking) | The calendar-to-money loop. `/track-time` classifies billable time per client. `/generate-invoices` emits monthly invoice rows ready for QuickBooks / Wave / Stripe / manual delivery. |

### Marketing — your content team

| Role | Plugin | What they do |
|---|---|---|
| **Chief Marketing Agent** | [news-curator](https://github.com/BrightWayAI/news-curator) | Weekly LinkedIn news roundup. Scans newsletters and the open web, ranks the week's stories for your audience, drafts the post in your voice. |

(Voice itself is handled by your Communications Director in the foundation tier.)

### Operations & insight — your ops team

The teammates who keep the machine running and surface what needs attention.

| Role | Plugin | What they do |
|---|---|---|
| **Chief Operating Officer** | [core-ops](https://github.com/BrightWayAI/core-ops) | Pipeline analytics (`pipeline-analyst` + `pipeline-forecast` subagents), deliverable QA (`/review-deliverable`), ecosystem health (`/diagnose`), telemetry (`/log-agent-run`, `/agent-metrics`), schedule library (`/register-schedules`), dashboards (`/nucleus-status`, `/nucleus-dashboard`). |
| **Cross-Team Liaison** | [weekly-alignment](https://github.com/BrightWayAI/weekly-alignment) | Weekly Slack cross-team alignment scanner. Surfaces overlapping initiatives, conflicting priorities, decisions that affect other teams. Monday morning brief. |

---

## How the plugins compose

Three layers of connective tissue:

### Shared identity and voice

Two canonical files live at your `<config-root>/` (typically `~/Documents/Claude/`). Populated once, read by every plugin.

| File | Created by | Read by |
|---|---|---|
| `identity.md` | `cortex /setup-identity` | All 12 other plugins (no duplicate questions in their setups) |
| `voice.md` | `cortex /setup-voice` | All drafting plugins (relationships, lead-engine, news-curator's post-assembler, client-status, referral-engine, writing-style) |

Without these, every plugin asks the same questions over and over. With these, identity and voice live in one place — you update them in one place.

### Subagents that flow across plugins

| Subagent | Lives in | Used by |
|---|---|---|
| `memory-librarian` | claude-cortex | `/search`, `/research-gaps` |
| `transcript-reviewer` | claude-cortex | `/end-week`, weekly scheduled run |
| `conversation-miner` / `activity-miner` | claude-cortex | `/end-day` Step 2a (v4.3+) |
| `gap-researcher` | claude-cortex | `/research-gaps` (v4.5+) |
| `contact-researcher` | lead-engine | relationships (`/relationships`, `/draft-touchpoint`), lead-brief, lead-pull, referral-ask |
| `pipeline-analyst` | core-ops | relationships (new-business bucket), plan-tomorrow, ad-hoc pipeline review |
| `relationship-ranker` | relationships | `/relationships` (one call per bucket) |
| `pipeline-forecast` | core-ops | monthly forecasting, board prep |
| `news-curator` | news-curator | `/ai-roundup` (scan + rank) |
| `post-assembler` | news-curator | `/ai-roundup` (drafts in your voice) |

Confidence-aware delegation: when an agent returns Low confidence, parent skills pause and ask for context rather than running thin.

### Closing rituals + infrastructure

| Capability | Lives in | What it does |
|---|---|---|
| `/end-day` | cortex | 10-15 min daily close — inbox triage, transcript review, two-stage memory triage, reflective prompts, pre-stage tomorrow's brief, refresh memory index |
| `/end-week` | cortex | 15-min Friday close — transcript review, cleanup, rehearsal, weekly digest, reflection, optional research-gaps, pre-stage Monday outreach |
| `/research-gaps` | cortex | Autonomous memory gap-finder. Scans for thin entities, stale facts, contradictions, orphans, under-cited claims; web-researches; user-gated merge (v4.5+) |
| `/setup-obsidian` | cortex | Scaffolds Obsidian vault over `<config-root>/` — graph view, daily notes, mobile sync (v4.5+) |
| `/diagnose` | core-ops | Ecosystem health check — surfaces missing setups, connector gaps |
| `/log-agent-run` + `/agent-metrics` | core-ops | Lightweight telemetry — meta-only logs of agent quality over time |
| `/register-schedules` | core-ops | Bulk-register standing schedules from a versioned library |

These don't add new user-facing capabilities so much as they make the rest of the stack durable, observable, and reproducible.

---

## Obsidian as the human UI

After `/setup-obsidian`, your `<config-root>/` becomes a graph-viewable, mobile-readable Obsidian vault:

- **Graph view** of every person, client, topic, and domain node — connected by real wikilinks.
- **Daily notes** = daily-brief's snapshots. Today's date in Obsidian is today's brief.
- **Memory index** (`memory/index.md`) is your home page — every node, grouped by type, with decay-state flags.
- **Dataview queries** in `VAULT.md` render active engagements, active people, active topics.
- **Mobile** via free Obsidian iOS/Android apps + iCloud or Obsidian Sync.

Same files. Two interaction surfaces. Speak to Claude on desktop; browse the vault on your phone.

---

## Daily and weekly rhythm

When the full stack is wired up:

```
Every workday
  Morning     → /plan-tomorrow ran last night; just open calendar
  Throughout  → cortex auto-recall + passive observation (no commands)
  ~5pm        → /end-day (recap, reflect, commit, pre-stage tomorrow)
  Evening     → /track-time (classify yesterday's calendar)

Every Friday
  Morning     → news-curator pre-stages candidates (scheduled)
  Afternoon   → /end-week (transcript review, cleanup, rehearsal, weekly retro, /research-gaps, optional Monday pre-stage)
  Afternoon   → /referrals (latent network surfacing)
  Afternoon   → /client-status (drafts for active engagements)

Every workday morning
  → /relationships brief — 3 buckets × 3 actions × copy-ready drafts
  → pipeline-analyst snapshot (Monday 6am, scheduled)

Monthly
  1st         → /generate-invoices (bill last month from time-log)
  1st         → pipeline-forecast (next month/quarter)
```

Schedules are versioned in `core-ops/references/schedules.md` and registered with `/register-schedules`. The system runs itself; you mostly review and confirm.

---

## Who this is for

You run client work as a solo or near-solo operator. You're a fractional CTO, COO, or CMO; an independent consultant; a founder of a 1-3-person firm; an agency owner who still does delivery. You bill by the hour or by the project. You care about your relationships and your voice. You hate that "AI tools" usually means "another tab to check."

Nucleus is built for the operator's workflow: relationships, daily rhythm, client engagements, deliverable quality. Not for marketing funnels at scale or general SMB workflows. If you want a hand-built operating system rather than a generic one, this is the right tool.

---

## Recommended install combos

**Solo consultant running BD on Claude:**
```
nucleus-router + claude-cortex + core-ops + lead-engine + relationships + referral-engine + time-tracking
```
Memory + pipeline + signal-driven outbound + daily relationship cockpit (orchestration + per-contact drafting + quarterly tier review) + referral engine + billing.

**Agency operator with multiple client engagements:**
```
nucleus-router + claude-cortex + core-ops + project-setup + relationships + daily-brief + time-tracking + client-status
```
Memory + pipeline + new-engagement onboarding + daily relationship cockpit + daily flow + billing + client retention.

**Content-focused operator:**
```
nucleus-router + claude-cortex + writing-style + news-curator + relationships + referral-engine
```
Memory + voice + weekly LinkedIn roundup + daily relationship cockpit + referral engine.

**Cross-team operator (manager / chief-of-staff):**
```
nucleus-router + claude-cortex + weekly-alignment + daily-brief + core-ops
```
Memory + Slack alignment scan + daily calendar + deliverable QA + diagnostics.

**Minimum viable starter:** `nucleus-router + claude-cortex + core-ops`. Run `/setup-identity` and `/setup-voice` first. Everything else builds on top.

---

## Setup flow

The simplest path: say **"start nucleus"** to Claude. The router suggests `/start-nucleus` — the foundational walker that chains every setup in order, gates each step so you can skip what doesn't apply, and is safe to re-run any time (it picks up where you left off).

Manual order if you'd rather drive it yourself:

1. **`/setup-identity`** (cortex) — captures name/company/role/tools once.
2. **`/setup-voice`** (cortex) — captures voice descriptors and banned phrases.
3. **`/setup-sources`** (cortex, optional) — connect Granola / Gemini / Fireflies / Drive so `/listen` can run overnight ingests.
4. **`/setup-obsidian`** (cortex, optional) — scaffolds Obsidian vault for graph view + mobile.
5. Per-plugin **`/setup-*`** for each installed plugin (captures plugin-specific stuff: CRM, ICP, offerings catalog, billing rates).
6. **`/diagnose`** (core-ops) — verify everything is wired up.
7. **`/register-schedules`** (core-ops) — register daily / weekly / monthly automation (nightly `/listen`, daily `/end-day`, weekly `/end-week`, monthly `/generate-invoices`, etc.).

**Don't skip setup.** All plugins return "run `/setup-*` first" if their context file is missing or empty.

---

## Customize for your firm

**Customization happens automatically through setup.** Each plugin's `/setup-*` command interviews you about your specifics — CRM properties, ICP definitions, voice descriptors, offerings catalog, billing rates, template content — and writes the answers to `<config-root>/plugins/<plugin>.user-context.md`. Plugins read that file at runtime, so the same plugin behaves differently for every operator. No forking. No code edits. Re-run `/setup-*` any time to update.

Plugins that ship with content templates (engagement plan structure in `project-setup`, invoice format in `time-tracking`, status update format in `client-status`, ask templates in `referral-engine`) put those templates in `references/templates/` inside the plugin repo. The starter content reflects BrightWay AI's defaults; on first run, the plugin copies a working template to your `<config-root>/plugins/<plugin>/templates/` directory. **Edit your local copy** to make it yours — the plugin reads from your local copy, not from the source repo. Updates to the plugin repo never overwrite your edited templates.

### When forking is the right move

Only fork if you want to change a plugin's **methodology** — not its content. Examples:

- You want `lead-engine` to score signals with a different algorithm than BrightWay's.
- You want `relationships` to produce a different shape of daily brief.
- You want to add a plugin that doesn't exist yet for your firm's specific workflow.

For those cases:

1. Fork the plugin repo (e.g., `BrightWayAI/lead-engine` → `yourfirm/lead-engine`).
2. Fork `BrightWayAI/nucleus` and update `.claude-plugin/marketplace.json` to point at your fork.
3. Edit the plugin's skill / command markdown, commit, push.
4. Cowork picks up your fork on next startup.

But for the **99% case — customizing what the plugin knows about you and your firm — `/start-nucleus` and `/setup-*` are the whole story.**

See [`docs/multi-agent-patterns.md`](docs/multi-agent-patterns.md) if you want to chain subagents inside a custom plugin.

---

## Plugin versions

Most-up-to-date version of each plugin (also recorded per-entry in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json); authoritative source is each plugin's own `plugin.json`). Cowork still resolves the latest from each repo on pull — this table is for at-a-glance reference.

| Plugin | Version |
|---|---|
| nucleus-router | 0.2.1 |
| claude-cortex (cortex) | 4.13.2 |
| core-ops | 0.3.2 |
| lead-engine | 0.2.4 |
| relationships | 0.2.3 |
| referral-engine | 0.2.4 |
| news-curator | 0.2.3 |
| client-status | 0.2.4 |
| project-setup | 0.2.4 |
| time-tracking | 0.2.3 |
| weekly-alignment | 1.4.3 |
| writing-style | 0.1.2 |
| daily-brief | 0.6.1 |

## Roadmap and open proposals

The active roadmap lives at [`docs/proposals/ROADMAP.md`](docs/proposals/ROADMAP.md). Convention: **top-level `docs/proposals/*.md` = open / not-yet-built**; [`docs/proposals/shipped/`](docs/proposals/shipped/) = archived (with a SHIPPED banner); [`docs/proposals/parked/`](docs/proposals/parked/) = deferred indefinitely, not on the roadmap.

### 🟢 Active / next up
- **sweep-heartbeat.md** — every-3h work-hours heartbeat that mines today's surfaces + in-progress Cowork conversations, dedups, stages proposals reviewed at `/end-day`. ~1–2 week build. Gated on dogfooding `/listen` + `/morning` first.
- **cleanup-pass-1 items E–G** (deferred from cortex v4.8.1) — mining-agent consolidation, `/end-day` decomposition, autonomy-slider coverage. See `shipped/cleanup-pass-1.md`.

### ✅ Recently shipped (in `docs/proposals/shipped/`)
- **End-Day Routine Improvement** — daily-brief v0.5.0 + cortex v4.13.0 + core-ops v0.3.2 (5-section brief, brief mining, cost gate, forgettings, reflections store, taxonomy consolidation).
- **memory-as-git** — cortex v4.12.0 + v4.13.0 + core-ops v0.3.2 (versioned vault, daily commit, `/morning` diff review, `/diagnose` health).
- **chief-of-staff-evolution** (router v0.2.0 + cortex v4.9.0), **relationships-plugin** (v0.1.0 → v0.2.3), **wikilink-density** (cortex v4.10.0), **cleanup-pass-1 A–D** (cortex v4.8.1), plus earlier cortex v4.5–4.7, nucleus-router v0.1, Obsidian, and productization specs.

### ⏸️ Parked (in `docs/proposals/parked/` — not on the roadmap)
- **jarvis-app.md** — standalone Tauri "Operator" desktop app. Separate product bet; revisit only on a strong marketplace-demand signal.

---

## Help, feedback, and customization

Each plugin manages its own issues:

- [nucleus-router](https://github.com/BrightWayAI/nucleus-router/issues)
- [claude-cortex](https://github.com/BrightWayAI/claude-cortex/issues)
- [core-ops](https://github.com/BrightWayAI/core-ops/issues)
- [lead-engine](https://github.com/BrightWayAI/lead-engine/issues)
- [relationships](https://github.com/BrightWayAI/relationships/issues)
- [news-curator](https://github.com/BrightWayAI/news-curator/issues)
- [daily-brief](https://github.com/BrightWayAI/daily-brief/issues)
- [project-setup](https://github.com/BrightWayAI/project-setup/issues)
- [time-tracking](https://github.com/BrightWayAI/time-tracking/issues)
- [client-status](https://github.com/BrightWayAI/client-status/issues)
- [referral-engine](https://github.com/BrightWayAI/referral-engine/issues)
- [weekly-alignment](https://github.com/BrightWayAI/weekly-alignment/issues)
- [writing-style](https://github.com/BrightWayAI/writing-style/issues)

Marketplace-level issues (manifest problems, install errors): [BrightWayAI/nucleus](https://github.com/BrightWayAI/nucleus/issues).

Want it set up for your firm, customized for your offerings, or trained on your voice and stack? [BrightWay AI](https://brightwayai.com) offers Nucleus implementation and customization for solo operators and small consulting firms. Reach out — `zach@brightwayai.com`.

---

## License

Each plugin is MIT-licensed. Use it, fork it, customize it, ship it.
