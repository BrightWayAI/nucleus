# Nucleus

**The operating system for solo operators running on AI.**

You're a consultant, a fractional operator, a founder, a one-person agency. Your work is too varied for any single SaaS tool. Your relationships are too important to forget. Your voice is too specific to delegate to a generic AI. Your day is too dense to navigate by clicking through tabs.

Nucleus is what you install when you want Claude to actually run your operation — remember your world, draft in your voice, surface what needs your attention, and stay out of your way the rest of the time.

Compatible with **Claude Cowork (Desktop)** and **Claude Code**. 100% free and open source. MIT-licensed across every plugin.

---

## Talk, don't memorize

> *"What's on my plate today?"* → Claude runs `/brief`.
>
> *"I just met Sarah at the AI Summit — VP Eng, sharp."* → Claude runs `/remember`, creates her person page, links it to the conference.
>
> *"Wrap up the day."* → Claude runs `/end-day` — five-minute reflection, commits to memory, pre-stages tomorrow's brief.
>
> *"What's missing from my memory?"* → Claude runs `/research-gaps`, finds thin pages and stale facts, researches them via the web, hands you a draft.

Nucleus ships 14 plugins. You never have to remember which one does what. The always-loaded **router** maps natural-language utterances to the right capability and asks before running.

---

## What you get

A second brain that learns and forgets. A daily rhythm that compounds. A relationship engine that doesn't let connectors go cold. A voice that gets sharper every week. A graph view in Obsidian on desktop and phone.

**14 plugins. 7 subagents. JARVIS-style natural-language router. Bidirectional memory (learning + decay). Daily/weekly closing rituals. Obsidian-as-UI. Adaptive voice. Pipeline analytics. Calendar-to-invoice loop.**

| What you say | What runs |
|---|---|
| *"What's on my plate today"* | `/brief` (your daily working surface) |
| *"Plan tomorrow"* | `/plan-tomorrow` (blocks the next workday on your calendar) |
| *"I just met X"* | `/remember` (capture + person page) |
| *"What do we know about X"* | `/recall` (surface relevant memory) |
| *"Draft outreach to X"* | `/lead-draft` or `/bizdev-outreach` (voice-faithful) |
| *"Plan this week's outreach"* | `/weekly-outreach` (prioritized 10-12-contact plan) |
| *"Weekly LinkedIn news roundup"* | `/ai-roundup` (curated, drafted in your voice) |
| *"Status update for Acme"* | `/client-status` (drafted from memory + calendar + CRM) |
| *"Log my time"* | `/track-time` (calendar → billable log) |
| *"Generate invoices"* | `/generate-invoices` (monthly billing) |
| *"Wrap up the day"* | `/end-day` (reflection + commit + pre-stage tomorrow) |
| *"Wrap up the week"* | `/end-week` (transcript review + cleanup + retro + Monday prep) |
| *"Set up Obsidian"* | `/setup-obsidian` (graph view + mobile sync) |
| *"What's missing from my memory"* | `/research-gaps` (autonomous gap-fill) |

---

## Install in five minutes

```
/plugin marketplace add BrightWayAI/nucleus
```

Then in Claude:

1. `/setup-identity` — answer 8 questions about who you are.
2. `/setup-voice` — paste two sample emails so cortex learns your voice.
3. `/setup-obsidian` — scaffolds an Obsidian vault over your config root.
4. Open `~/Documents/Claude/` in [Obsidian](https://obsidian.md) — graph view shows you and your context.
5. Talk to Claude. The router takes it from there.

After install: `/route` prints the full cheat-sheet. You'll rarely need it.

---

## The catalog

14 plugins, organized by what they do. Each one is independently useful. Several get sharper when paired.

### Front door

| Plugin | What it does | Setup |
|---|---|---|
| **[nucleus-router](https://github.com/BrightWayAI/nucleus-router)** | The JARVIS layer. Always-loaded skill maps natural-language utterances ("what's on my plate," "I just met X," "wrap up the day") to the right Nucleus command and confirms before running. `/route` prints the full cheat sheet. | None — auto-loads at conversation start |

### Memory & knowledge

| Plugin | What it does | Setup |
|---|---|---|
| **[claude-cortex](https://github.com/BrightWayAI/claude-cortex)** | Your second brain. Typed memory nodes (people, clients, topics, domain knowledge), bidirectional learning (mining + decay), auto-maintained `memory/index.md` catalog, autonomous gap-finder (`/research-gaps`), Obsidian vault scaffolding (`/setup-obsidian`). v4.5+. | `/setup-identity`, `/setup-voice` |

**Subagents:** `memory-librarian` (cross-node synthesis), `transcript-reviewer` (weekly commitment delta), `conversation-miner` + `activity-miner` (note-source extraction), `gap-researcher` (web-research for memory gaps).

### Business development & relationships

| Plugin | What it does | Setup |
|---|---|---|
| **[lead-engine](https://github.com/BrightWayAI/lead-engine)** | LinkedIn intent-based outbound. Catches buying signals, drafts warm DMs in your voice, runs 3-touch cadences, generates pre-call briefs. | `/lead-setup` |
| **[bizdev-outreach](https://github.com/BrightWayAI/Biz-Dev)** | Per-contact research + voice-faithful drafted outreach. Works across HubSpot, Salesforce, Pipedrive, Close — and Gmail or Outlook. | `/setup` |
| **[weekly-outreach](https://github.com/BrightWayAI/weekly-outreach)** | Weekly relationship management. Prioritized 10-12-contact queue, call prep for external meetings, drafted messages, CRM tasks. | `/setup-outreach` |
| **[referral-engine](https://github.com/BrightWayAI/referral-engine)** | Latent revenue from connectors who've gone quiet. Weekly digest, drafted asks honoring cooling periods. | `/setup-referrals` |

**Subagent:** `contact-researcher` — deep single-contact research across CRM, email, and web.

### Daily rhythm

| Plugin | What it does | Setup |
|---|---|---|
| **[daily-brief](https://github.com/BrightWayAI/daily-brief)** | Today's working surface. `/brief` builds a Cowork artifact (calendar, inbox, CRM, outreach, yesterday's reflection — annotated by you). `/process-brief` routes annotations to drafts and reschedules. `/plan-tomorrow` blocks the next workday on your calendar. | `/setup-brief`, `/setup-plan` |

### Client & project operations

| Plugin | What it does | Setup |
|---|---|---|
| **[project-setup](https://github.com/BrightWayAI/project-setup)** | New-engagement initialization. Drive folder structure, Claude Project system prompt, phased plan, memory node — one interview. Templates user-customizable. | `/setup-projects` |
| **[client-status](https://github.com/BrightWayAI/client-status)** | Weekly client status drafts auto-built from memory, project state, calendar, and CRM activity. Closes the retention loop. | `/setup-status` |
| **[time-tracking](https://github.com/BrightWayAI/time-tracking)** | Calendar-driven time tracking and monthly invoice generation. Classifies billable time per client; emits invoice rows ready for QuickBooks / Wave / Stripe / manual delivery. | `/setup-time` |

### Marketing & content

| Plugin | What it does | Setup |
|---|---|---|
| **[news-curator](https://github.com/BrightWayAI/news-curator)** | Weekly LinkedIn news roundup. Scans + ranks + drafts in your voice. Configurable per topic / audience. | `/setup-news` |
| **[writing-style](https://github.com/BrightWayAI/writing-style)** | Adaptive voice. `/style` drafts in your voice. `/style-learn` learns from real edits with two-stage triage. `/style-review` audits style files. Companion to cortex's `/setup-voice`. | `/setup-style` |

**Subagents:** `news-curator` (scan + rank), `post-assembler` (drafts in your voice).

### Cross-team & toolkit

| Plugin | What it does | Setup |
|---|---|---|
| **[core-ops](https://github.com/BrightWayAI/core-ops)** | Generic business-ops toolkit. `pipeline-analyst` + `pipeline-forecast` subagents. `/review-deliverable` (QA on client docs/decks), `/diagnose` (ecosystem health), `/log-agent-run` + `/agent-metrics` (telemetry), `/register-schedules` (bulk-register standing schedules), `/nucleus-status` + `/nucleus-dashboard`. | `/setup-core` |
| **[weekly-alignment](https://github.com/BrightWayAI/weekly-alignment)** | Weekly Slack cross-team alignment scanner. Surfaces overlapping initiatives, conflicting priorities, decisions affecting other teams. Monday morning brief. | `/setup` (via skills) |

---

## How the plugins compose

Three layers of connective tissue:

### Shared identity and voice

Two canonical files live at your `<config-root>/` (typically `~/Documents/Claude/`). Populated once, read by every plugin.

| File | Created by | Read by |
|---|---|---|
| `identity.md` | `cortex /setup-identity` | All 13 other plugins (no duplicate questions in their setups) |
| `voice.md` | `cortex /setup-voice` | All drafting plugins (bizdev-outreach, weekly-outreach, lead-engine, news-curator's post-assembler, client-status, referral-engine, writing-style) |

Without these, every plugin asks the same questions over and over. With these, identity and voice live in one place — you update them in one place.

### Subagents that flow across plugins

| Subagent | Lives in | Used by |
|---|---|---|
| `memory-librarian` | claude-cortex | `/search`, `/research-gaps` |
| `transcript-reviewer` | claude-cortex | `/end-week`, weekly scheduled run |
| `conversation-miner` / `activity-miner` | claude-cortex | `/end-day` Step 2a (v4.3+) |
| `gap-researcher` | claude-cortex | `/research-gaps` (v4.5+) |
| `contact-researcher` | lead-engine | bizdev-outreach, lead-brief, lead-pull, weekly-outreach, referral-ask |
| `pipeline-analyst` | core-ops | weekly-outreach, plan-tomorrow, ad-hoc pipeline review |
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

Every Monday morning
  → /weekly-outreach plan ready for review (staged Friday)
  → pipeline-analyst snapshot ready (scheduled 6am)

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
nucleus-router + claude-cortex + core-ops + lead-engine + bizdev-outreach + weekly-outreach + referral-engine + time-tracking
```
Memory + pipeline + signal-driven outbound + per-contact drafting + weekly prep + referral engine + billing.

**Agency operator with multiple client engagements:**
```
nucleus-router + claude-cortex + core-ops + project-setup + weekly-outreach + daily-brief + time-tracking + client-status
```
Memory + pipeline + new-engagement onboarding + daily flow + billing + client retention.

**Content-focused operator:**
```
nucleus-router + claude-cortex + writing-style + news-curator + bizdev-outreach + referral-engine
```
Memory + voice + weekly LinkedIn roundup + per-contact outreach + referral engine.

**Cross-team operator (manager / chief-of-staff):**
```
nucleus-router + claude-cortex + weekly-alignment + daily-brief + core-ops
```
Memory + Slack alignment scan + daily calendar + deliverable QA + diagnostics.

**Minimum viable starter:** `nucleus-router + claude-cortex + core-ops`. Run `/setup-identity` and `/setup-voice` first. Everything else builds on top.

---

## Setup flow

Recommended order:

1. **`/setup-identity`** (cortex) — captures name/company/role/tools once.
2. **`/setup-voice`** (cortex) — captures voice descriptors and banned phrases.
3. **`/setup-obsidian`** (cortex, optional) — scaffolds Obsidian vault for graph view + mobile.
4. Per-plugin **`/setup-*`** for each installed plugin (captures plugin-specific stuff: CRM, ICP, offerings catalog, billing rates).
5. **`/diagnose`** (core-ops) — verify everything is wired up.
6. **`/register-schedules`** (core-ops) — register daily / weekly / monthly automation.

**Don't skip setup.** All plugins return "run `/setup-*` first" if their context file is missing or empty.

---

## Customize for your firm

Each plugin lives in its own GitHub repo. To customize one:

1. Fork the plugin repo (e.g., `BrightWayAI/lead-engine` → `yourfirm/lead-engine`).
2. In your fork of `BrightWayAI/nucleus`, update `.claude-plugin/marketplace.json` to point at your repo.
3. Edit, commit, push. Cowork picks up your changes on next startup.

Templates inside plugins (e.g., `references/templates/` in `project-setup`, `time-tracking`, `client-status`, `referral-engine`) are intended to be edited per-firm. The starter content reflects BrightWay AI's offerings — replace it with your own.

See [`docs/multi-agent-patterns.md`](docs/multi-agent-patterns.md) for guidance on chaining subagents inside your own plugins.

---

## Roadmap and open proposals

Active proposals at [`docs/proposals/`](docs/proposals/). Pick one up if you want to contribute:

- **`nucleus-router.md`** — shipped 2026-05-16 as `BrightWayAI/nucleus-router` v0.1.1.
- **`cortex-v4.5-legibility.md`** — shipped 2026-05-16 as cortex v4.5.0 (memory index, `/research-gaps`, gap-researcher).
- **`obsidian-as-ui.md`** — shipped 2026-05-16 as part of cortex v4.5.0 (`/setup-obsidian`).
- **`second-brain-extension.md`** — earlier proposal; mostly shipped across v4.2-4.5.

---

## Help, feedback, and customization

Each plugin manages its own issues:

- [nucleus-router](https://github.com/BrightWayAI/nucleus-router/issues)
- [claude-cortex](https://github.com/BrightWayAI/claude-cortex/issues)
- [core-ops](https://github.com/BrightWayAI/core-ops/issues)
- [lead-engine](https://github.com/BrightWayAI/lead-engine/issues)
- [bizdev-outreach](https://github.com/BrightWayAI/Biz-Dev/issues)
- [weekly-outreach](https://github.com/BrightWayAI/weekly-outreach/issues)
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
