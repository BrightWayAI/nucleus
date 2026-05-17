# Nucleus

**The operating core for how AI-powered teams get work done.**

BrightWay AI's curated marketplace of plugins, agents, and shared memory. Turns Claude into the daily operating layer for solo operators, consultants, and teams running an agentic operating model. Memory that learns and forgets, business development, daily planning, time tracking, client retention, news curation, deliverable QA, cross-team alignment — each plugin works on its own, and they get sharper when paired together.

Compatible with **Cowork (Claude Desktop)** and **Claude Code**.

**14 plugins. 7 subagents. JARVIS-style natural-language router. Shared identity and voice. Bidirectional learning (mining + decay). Daily/weekly closing rituals. Telemetry. Schedule library.**

> **New: speak how you think.** [nucleus-router](https://github.com/BrightWayAI/nucleus-router) is an always-loaded skill that maps natural-language utterances to the right Nucleus command and asks before running. Say "what's on my plate today" — it suggests `/brief`. Say "I just met Sarah at the conference" — it suggests `/remember`. No more memorizing 57 commands.

---

## Install

```
/plugin marketplace add BrightWayAI/nucleus
```

Then install plugins individually (see catalog below).

After installing, run **`/setup-identity`** and **`/setup-voice`** (both in cortex) **first**. They populate canonical config files at `~/Documents/Claude/identity.md` and `~/Documents/Claude/voice.md` that every other plugin reads — captures name, company, role, tools, voice descriptors, banned phrases once, in one place. Then run each plugin's individual setup.

Updates flow automatically — push to a plugin's repo on GitHub → marketplace picks it up on Cowork's next startup. No marketplace re-install needed for content changes.

---

## What's in the marketplace

14 plugins, organized by what they do.

### Front door

| Plugin | What it does | Setup |
|---|---|---|
| **[nucleus-router](https://github.com/BrightWayAI/nucleus-router)** | JARVIS-style natural-language router. Always-on skill matches utterances ("what's on my plate," "I just met X," "wrap up the day") to the right Nucleus command and asks for confirmation before running. `/route` prints the full cheat sheet of every capability. | None — auto-loads at conversation start |

### Memory & knowledge

| Plugin | What it does | Setup |
|---|---|---|
| **[claude-cortex](https://github.com/BrightWayAI/claude-cortex)** | Always-on learning system. v4.5+: auto-maintained `memory/index.md` catalog, `/research-gaps` autonomous gap-fill, `/setup-obsidian` for graph-viewable mobile-ready vault. Passively observes preferences, captures knowledge, adapts every conversation. Ships `/setup-identity` and `/setup-voice` (shared config), `/end-day` and `/end-week` (closing rituals), and the existing memory commands. The memory layer for everything else. | None — auto-recall works out of the box; run `/setup-identity` and `/setup-voice` for shared config |

**Hosts subagents:** `memory-librarian` (broad-query memory synthesis), `transcript-reviewer` (weekly call commitment delta).

### Business development & sales

| Plugin | What it does | Setup |
|---|---|---|
| **[lead-engine](https://github.com/BrightWayAI/lead-engine)** | Intent-based LinkedIn outbound. Catch buying signals, warm prospects, draft DMs in your voice, run a 3-touch cadence, generate pre-call briefs. | `/lead-setup` |
| **[bizdev-outreach](https://github.com/BrightWayAI/Biz-Dev)** | Research a contact across your CRM, email, and the web; draft personalized outreach in your voice. Knows when *not* to send. | `/setup` |
| **[weekly-outreach](https://github.com/BrightWayAI/weekly-outreach)** | Weekly relationship management and BD prep. Prioritized outreach queue (10–12 contacts), call prep for the week's external meetings, drafted messages, plus CRM tasks and calendar placeholders. | `/setup-outreach` |
| **[referral-engine](https://github.com/BrightWayAI/referral-engine)** | Latent revenue engine. Weekly digest of connectors gone quiet, recent positive moments, and approaching triggers. Drafts voice-faithful asks for specific connectors. Honors cooling periods. | `/setup-referrals` |

**Hosts subagent:** `contact-researcher` (in lead-engine — single-contact deep dive across CRM, email, web).

### Marketing & content

| Plugin | What it does | Setup |
|---|---|---|
| **[news-curator](https://github.com/BrightWayAI/news-curator)** | Curate and draft a weekly LinkedIn news roundup post. Configurable per topic and audience — works for AI, climate, fintech, anything. | `/setup-news` |

**Hosts subagents:** `news-curator` (scan + rank), `post-assembler` (drafts in your voice — reads `~/Documents/Claude/voice.md`).

### Daily operations

| Plugin | What it does | Setup |
|---|---|---|
| **[project-setup](https://github.com/BrightWayAI/project-setup)** | End-to-end client engagement initialization. Drive folder structure, Claude Project system prompt, phased project plan, memory node — all in one interview. Templates user-customizable. | `/setup-projects` |
| **[time-tracking](https://github.com/BrightWayAI/time-tracking)** | Calendar-driven time tracking and monthly invoice generation. `/track-time` classifies billable time per client. `/generate-invoices` drafts monthly invoices from the log. Closes the calendar-to-money loop. | `/setup-time` |

### Client ops

| Plugin | What it does | Setup |
|---|---|---|
| **[client-status](https://github.com/BrightWayAI/client-status)** | Weekly client status updates auto-drafted from cortex memory, project-setup engagement data, calendar, and CRM. Drafts go for your review and send. Closes the retention loop. | `/setup-status` |
| **[daily-brief](https://github.com/BrightWayAI/daily-brief)** | Daily flow plugin. `/brief` is today's working surface as a Cowork artifact (calendar, inbox, CRM, outreach, yesterday's reflection — annotated by you). `/process-brief` routes the annotations to Gmail drafts, CRM reschedules, meeting talking points. `/plan-tomorrow` blocks the next business day on your calendar. Drafts only. As of v0.2.0 absorbs the deprecated plan-tomorrow plugin. | `/setup-brief`, `/setup-plan` |

### Voice & writing

| Plugin | What it does | Setup |
|---|---|---|
| **[writing-style](https://github.com/BrightWayAI/writing-style)** | Adaptive writing-style plugin. Learns your voice from real edits over time. `/style` drafts in your voice (email, social, doc, dm). `/style-learn` analyzes draft-vs-final diffs with two-stage triage. `/style-review` audits style files for contradictions and stale rules. | `/setup-style` |

### Cross-team & toolkit

| Plugin | What it does | Setup |
|---|---|---|
| **[core-ops](https://github.com/BrightWayAI/core-ops)** | Shared business-ops toolkit. Hosts `pipeline-analyst` and `pipeline-forecast` subagents. Slash commands: `/review-deliverable` (QA on client artifacts), `/diagnose` (ecosystem health), `/log-agent-run` + `/agent-metrics` (telemetry), `/register-schedules` (bulk-register standing schedules from a versioned schedule library). | `/setup-core` |
| **[weekly-alignment](https://github.com/BrightWayAI/weekly-alignment)** | Weekly cross-team alignment scanner for Slack. Surfaces overlapping initiatives, conflicting priorities, and decisions that affect other teams. Delivers a Monday morning brief. | `/setup` (via skills) |

**Hosts subagents:** `pipeline-analyst` (point-in-time CRM ranking), `pipeline-forecast` (forward-looking revenue projection).

---

## How the plugins work together

Each plugin is independently useful, but several get sharper when paired. **Three layers of connective tissue:**

### Layer 1 — Shared user-level config

Two canonical files live at `~/Documents/Claude/`. Populated once, read by every plugin:

| File | Created by | Read by |
|---|---|---|
| `identity.md` | `cortex /setup-identity` | All 12 plugins (skip identity questions in their setups) |
| `voice.md` | `cortex /setup-voice` | All drafting plugins (bizdev-outreach, weekly-outreach, lead-engine, news-curator's post-assembler, client-status, referral-engine) |

Without these, every plugin asks the same questions over and over. With these, identity and voice live in one place and you update them in one place.

### Layer 2 — Subagents

| Subagent | Lives in | Used by |
|---|---|---|
| `memory-librarian` | claude-cortex | `/search` (broad cross-node queries) |
| `transcript-reviewer` | claude-cortex | `/end-week`, scheduled weekly run |
| `contact-researcher` | lead-engine | `/bizdev-outreach`, `/lead-brief`, `/lead-pull`, `/weekly-outreach`, `/referral-ask` |
| `pipeline-analyst` | core-ops | `/weekly-outreach`, `/plan-tomorrow`, any pipeline-review |
| `pipeline-forecast` | core-ops | `/forecast` (monthly), board-prep workflows |
| `news-curator` | news-curator | `/ai-roundup` (scan + rank) |
| `post-assembler` | news-curator | `/ai-roundup` (drafts the post) |

Confidence-aware delegation: when an agent returns Low confidence, parent skills pause and ask for context rather than proceeding silently with thin data.

### Layer 3 — Closing rituals + infrastructure

| Capability | Lives in | What it does |
|---|---|---|
| `/end-day` | cortex | 5-min daily close — recap, reflect, commit to memory, optionally pre-stage tomorrow |
| `/end-week` | cortex | 15-min Friday close — transcript-reviewer + cleanup + review + reflection + optional pre-stage Monday |
| `/diagnose` | core-ops | Ecosystem health check — surfaces missing setups, connector gaps, subagent availability |
| `/log-agent-run` + `/agent-metrics` | core-ops | Lightweight telemetry — meta-only logs of agent quality/acceptance over time |
| `/register-schedules` | core-ops | Bulk-register standing schedules from a versioned `schedules.md` library — make new-machine setup repeatable |

These don't add new user-facing capabilities so much as they make the rest of the stack durable, observable, and reproducible.

### Recommended install combinations

**Solo consultant / founder running BD on Claude:**
```
claude-cortex + core-ops + lead-engine + bizdev-outreach + weekly-outreach + referral-engine + time-tracking
```
Memory + pipeline + signal-driven outbound + per-contact drafting + weekly prep + referral engine + billing.

**Agency operator with multiple client engagements:**
```
claude-cortex + core-ops + project-setup + weekly-outreach + plan-tomorrow + time-tracking + client-status
```
Memory + pipeline + new-engagement onboarding + BD + daily calendar + billing + client retention.

**Content-focused operator:**
```
claude-cortex + news-curator + bizdev-outreach + referral-engine
```
Memory + weekly LinkedIn roundup + per-contact outreach + referral engine.

**Cross-team operator (manager / chief-of-staff):**
```
claude-cortex + weekly-alignment + plan-tomorrow + core-ops
```
Memory + Slack alignment scan + daily calendar + deliverable QA + diagnostics.

**Minimum viable starter:** claude-cortex + core-ops. Run `/setup-identity` and `/setup-voice` first. Everything else builds on top.

**The full stack** (all 13 plugins): heavy but durable. The closing rituals (`/end-day`, `/end-week`) are what make compound value real — without them, plugins still work but you carry more in your head.

---

## Setup flow

Recommended order:

1. **`/setup-identity`** (cortex) — captures name/company/role/tools once. Other plugins skip these questions.
2. **`/setup-voice`** (cortex) — captures voice descriptors and banned phrases. Drafting plugins read from here.
3. Per-plugin **`/setup-*`** for each installed plugin (tables above for command names) — captures plugin-specific stuff (CRM properties, ICP, offerings catalog, billing rates, etc.).
4. **`/diagnose`** (core-ops) — verify everything is wired up.
5. **`/register-schedules`** (core-ops) — register the standing schedules from `core-ops/references/schedules.md` for daily / weekly / monthly automation.

| Plugin | Setup command | Captures |
|---|---|---|
| claude-cortex | `/setup-identity`, `/setup-voice` (shared) | Identity (name/company/role/tools) + voice (descriptors/banned phrases) |
| core-ops | `/setup-core` | CRM, brand, deliverable conventions |
| lead-engine | `/lead-setup` | Company, ICP, voice, value-adds, signal preferences |
| bizdev-outreach | `/setup` | Company, positioning, products, target market, voice |
| weekly-outreach | `/setup-outreach` | ICP, CRM custom properties, cadence tiers, weekly target |
| news-curator | `/setup-news` | Topic, audience, sources, voice, post format |
| plan-tomorrow | `/setup-plan` | Working hours, CRM, calendar conventions |
| project-setup | `/setup-projects` | Offerings catalog, drive layout, communication defaults |
| time-tracking | `/setup-time` | Clients, billing models, calendar tagging, invoice prefs |
| client-status | `/setup-status` | Cadence, status template, per-client overrides, delivery channel |
| referral-engine | `/setup-referrals` | Connector taxonomy, quiet threshold, trigger patterns, ask cadence |
| weekly-alignment | `/setup` | Slack channels, teams, risk patterns to watch |

**Don't skip setup.** All plugins return "run `/setup-*` first" if their context file is missing or empty.

---

## Daily and weekly rhythm (when fully wired up)

```
Every workday
  Morning      → /plan-tomorrow ran last night; just open calendar
  Throughout   → cortex auto-recall + passive observation (no commands)
  ~5pm         → /end-day (recap, reflect, commit to memory)
  Evening      → /track-time (classify yesterday's calendar)

Every Friday
  Morning      → news-curator pre-stages candidates (scheduled)
  Afternoon    → /end-week (transcript review, cleanup, weekly digest, reflection)
  Afternoon    → /referrals (latent network surfacing)
  Afternoon    → /client-status (drafts for active engagements)
  Pre-end      → /weekly-outreach pre-stages Monday's BD plan

Every Monday morning
  → /weekly-outreach plan ready for review (staged Friday)
  → /pipeline-analyst snapshot ready (scheduled 6am)

Monthly
  1st          → /generate-invoices (bill last month from time-log)
  1st          → /forecast (pipeline-forecast for the new month/quarter)
```

Schedules are versioned in `core-ops/references/schedules.md` and registered with `/register-schedules`.

---

## Develop / fork

Each plugin lives in its own GitHub repo. To customize one:

1. Fork the plugin repo (e.g., `BrightWayAI/lead-engine` → `yourname/lead-engine`).
2. Update `marketplace.json` in your marketplace fork (or create your own marketplace) to point at your repo instead.
3. Edit, commit, push. Cowork picks up your changes on next startup.

Templates inside plugins (e.g., `references/templates/` in `project-setup`, `time-tracking`, `client-status`, `referral-engine`) are intended to be edited per-firm. The starter content reflects BrightWay AI's offerings — replace it with your own.

See [`docs/multi-agent-patterns.md`](docs/multi-agent-patterns.md) for guidance on chaining subagents inside your own plugins.

---

## Issues & feedback

Each plugin manages its own issues:

- [claude-cortex](https://github.com/BrightWayAI/claude-cortex/issues)
- [core-ops](https://github.com/BrightWayAI/core-ops/issues)
- [lead-engine](https://github.com/BrightWayAI/lead-engine/issues)
- [bizdev-outreach](https://github.com/BrightWayAI/Biz-Dev/issues)
- [weekly-outreach](https://github.com/BrightWayAI/weekly-outreach/issues)
- [news-curator](https://github.com/BrightWayAI/news-curator/issues)
- [plan-tomorrow](https://github.com/BrightWayAI/plan-tomorrow/issues)
- [project-setup](https://github.com/BrightWayAI/project-setup/issues)
- [time-tracking](https://github.com/BrightWayAI/time-tracking/issues)
- [client-status](https://github.com/BrightWayAI/client-status/issues)
- [referral-engine](https://github.com/BrightWayAI/referral-engine/issues)
- [weekly-alignment](https://github.com/BrightWayAI/weekly-alignment/issues)
- [writing-style](https://github.com/BrightWayAI/writing-style/issues)
- [daily-brief](https://github.com/BrightWayAI/daily-brief/issues)
- [nucleus-router](https://github.com/BrightWayAI/nucleus-router/issues)

For marketplace-level issues (manifest problems, install errors, discovery), use [BrightWayAI/nucleus](https://github.com/BrightWayAI/nucleus/issues).

---

## License

Each plugin is MIT-licensed. See the `LICENSE` file in each repo.
