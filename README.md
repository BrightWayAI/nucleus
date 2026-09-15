# Nucleus

**Give Claude a memory of your business and a small staff that works from it.**

Nucleus is a free, open-source set of plugins for Claude Cowork and Claude Code (with ports for ChatGPT Work and Codex). Install it and Claude remembers your clients, people, decisions, and voice across every conversation; briefs you each morning; drafts outreach and client updates the way you would write them; and keeps your memory current overnight so you don't have to.

Everything lives in plain Markdown files in a folder you choose on your own computer. Nothing is uploaded anywhere unless you set that up yourself.

**Built for:** solo operators, fractional consultants, and small teams who run their business through Claude and are tired of re-explaining context every session.

---

## Your Nucleus staff

Nucleus is nine plugins, organized like a small team. You start with three and add the rest when you need them.

| Start here | ID | What it does |
|---|---|---|
| **Cortex** | `cortex` | The shared brain. Remembers clients, people, projects, decisions, and your identity. Learns overnight. Every other plugin reads from it. |
| **Chief of Staff** | `ops` | The front door. Say what you want in plain English (`/cos draft a status update for Acme`) and it routes to the right specialist. Also health checks and schedules. |
| **Comms Desk** | `comms` | Captures your voice once, then drafts emails, messages, and posts that sound like you, and learns from your edits. |

| Add when you need it | ID | What it does |
|---|---|---|
| **Today's Brief** | `briefing` | Your morning working surface: calendar, priorities, outreach queue, yesterday's reflection. Also the weekly review and the dashboard. |
| **Growth Engine** | `growth` | Who to reach out to today and what to say. Signal-driven outreach, referral asks, pre-call briefs, pipeline analysis. |
| **Client Success** | `clients` | Everything after the contract is signed: kickoff plans, weekly status drafts, deliverable QA. |
| **Admin** (hours and invoices) | `admin` | Turns your calendar into a time log and invoice drafts. The back office. |
| **Research** | `research` | Finds and cites material: news roundups, market and competitor research, pre-meeting research. |
| **Team Alignment** | `alignment` | Scans Slack for cross-team conflicts, decisions, and risks. |

The one-line version of who does what: **Research finds, Comms Desk writes, Growth Engine decides who, Client Success owns the account, Chief of Staff routes, Cortex remembers.**

---

## Quickstart in Claude Cowork (about 20 minutes)

You need the Claude desktop app with Cowork. No terminal, no code.

### 1. Add the Nucleus marketplace

1. In the Claude desktop app, open **Customize** in the sidebar, then **Plugins**.
2. Click **Add marketplace**.
3. Paste `https://github.com/BrightWayAI/nucleus` (or the shorthand `BrightWayAI/nucleus`) and confirm.

Nucleus now appears as a marketplace you can browse. Adding it does not install anything yet.

### 2. Install the three starter plugins

1. Click **Browse plugins** and pick the Nucleus marketplace.
2. Install **Cortex**, **Chief of Staff**, and **Comms Desk**.

Install each plugin **once**. If you see the same plugin listed twice later, one copy came from a second marketplace source; uninstall the duplicate.

### 3. Make a folder for your memory

Create an empty folder anywhere you control, for example `~/Documents/Nucleus`. This is where Nucleus will keep your memory, identity, voice, and plugin settings as Markdown files. You can open it in Finder, Obsidian, or any editor at any time.

### 4. Run setup

Start a **new** Cowork session (so the new plugins load) and type:

```
/start-nucleus
```

Setup walks you through, in order, and lets you skip anything that doesn't apply:

1. **Where to store memory** — point it at the folder from step 3. Cowork will ask you to grant access; approve it.
2. **Identity** — name, role, company, time zone, the tools you use. Asked once; every plugin reads it.
3. **Voice** — paste two emails or messages you wrote. Comms Desk extracts your tone and banned phrases so every draft sounds like you.
4. **Autonomy policy** — what Nucleus may do on its own vs. must ask about (see [Safety](#safety-what-nucleus-will-and-wont-do)). Accept the defaults or adjust.
5. **Note sources** — if you use Granola, Fireflies, Otter, Gemini, or a Drive folder for meeting notes, connect them so overnight ingest can read them.
6. **Obsidian** (optional) — turns your memory folder into a graph you can browse on desktop and phone.
7. **Per-plugin setup** for anything else you've installed.
8. **Health check** and optional scheduling of the nightly memory refresh.

Re-run `/start-nucleus` any time; it only runs what's still missing.

### 5. Your first day

```
/morning
```

`/morning` is the one thing you do every day. It shows anything Nucleus learned overnight, lets you accept or reject each item, captures a two-line reflection, and sets today's priorities. Five minutes.

Then just talk:

```
/cos catch me up on Acme
/cos who should I follow up with this week?
/cos draft a check-in to Jordan about the proposal
/cos ask Client Success for this week's Acme status
```

You don't need to learn the other commands. The Chief of Staff knows them, and you can address any specialist by name.

---

## Quickstart in ChatGPT Work (about 20 minutes)

You need the **ChatGPT desktop app** with **Local Work** enabled, and a workspace admin to import the marketplace once for everyone. Nucleus keeps memory in a local folder, so it works in desktop Local Work chats, not in the web app.

### 1. Admin: import the Nucleus marketplace (once per workspace)

1. Open **Admin → Plugins → Add → Import marketplace**.
2. Enter `https://github.com/BrightWayAI/nucleus` as the source. Leave **Path** blank; the catalog is at the repository root. Use the default branch.
3. Review the import, then mark **Cortex**, **Chief of Staff**, and **Comms Desk** as **Available** (or **Installed**) for the roles that need them. Add specialists the same way when people ask for them.

Importing makes the nine plugins available; it does not install anything for anyone or grant access to folders or connected apps.

### 2. Member: enable the three starter plugins

Open a **new Local Work chat** in the ChatGPT desktop app and enable **Cortex**, **Chief of Staff**, and **Comms Desk** for the chat (from the plugin picker, or by `@`-mentioning them the first time).

### 3. Make a folder for your memory

Create an empty folder you control, for example `~/Documents/Nucleus`. Already using Nucleus in Claude on the same computer? Skip this and reuse that folder; ChatGPT will find the same memory.

### 4. Run setup

In the Local Work chat, say:

```
@Cortex start Nucleus setup
```

Setup asks the same things as in Cowork, in the same order, and lets you skip anything that doesn't apply: where to store memory (ChatGPT asks you to grant Local Work access to the folder; approve it), identity, voice, autonomy policy, note sources, per-plugin setup, health check.

Say `@Cortex start Nucleus setup` again any time; it only runs what's still missing.

### 5. Your first day

```
@Cortex run my morning
```

Then talk to the Chief of Staff:

```
@Chief of Staff catch me up on Acme
@Chief of Staff who should I follow up with this week?
@Chief of Staff draft a check-in to Jordan about the proposal
```

Two things differ from Cowork. Overnight refresh runs only if your host exposes a scheduler; if ChatGPT doesn't offer one on your plan, say `@Cortex listen` in the morning before `run my morning` and it does the same ingest on demand. And connected apps (Gmail, Calendar, HubSpot, Slack, Drive) come from your workspace's connectors, not from Nucleus; plugins tell you which sources they couldn't reach. Full details in [OpenAI setup](docs/OPENAI_SETUP.md).

---

## Using Nucleus day to day

### Talk in outcomes, not commands

| You say | Who handles it | What happens |
|---|---|---|
| Start my day / what's on my plate | Today's Brief | Calendar, priorities, outreach queue, recent context |
| Catch me up on X | Cortex | Everything in memory about X, with sources |
| Remember that… / capture this | Cortex | Saved to the right client, person, or project |
| Draft X to Y | Comms Desk | Pulls context, writes in your voice, hands you a draft |
| Who should I reach out to? | Growth Engine | Ranked outreach with ready-to-send drafts |
| Status update for Acme | Client Success | Weekly client status from the week's evidence |
| Review this deliverable | Client Success | Structured QA against your brand and the brief |
| Bill last month | Admin | Invoice drafts from your approved time log |
| Research X | Research | Cited findings from memory plus the open web |
| What's the team misaligned on? | Team Alignment | Conflicts, decisions, and risks from Slack |
| Close the week | Today's Brief + Cortex | Weekly review, cleanup, next-week prep |

If a plugin or connector you'd need isn't installed or connected, the Chief of Staff tells you, rather than pretending the work ran.

### The daily rhythm

```
Overnight      Cortex reads yesterday's meetings, inbox, and calendar and
               stages what it learned as proposals   (needs the nightly schedule, below)
Morning        /morning — review proposals, reflect, set priorities   (5 min, required)
During work    ask /cos for context, drafts, and captures
Friday         /end-week — weekly review, cleanup, next-week prep     (optional)
Monthly        /invoices                                              (optional)
```

Nothing depends on an end-of-day ritual. `/morning` alone keeps memory current, committed, and (if you configured a private git remote) backed up.

### Turn on the overnight refresh

The nightly refresh is what makes Nucleus feel like it learns while you sleep. In Cowork:

```
/register-schedules
```

This registers `nightly-listen` (runs `/listen` at 11 pm) as a Cowork scheduled task. Two things to know: the task needs your computer awake with the Claude app open at run time (it catches up on the next wake if it missed), and on its first run Cowork will ask you to approve each tool it uses — approve with "always allow" so later runs don't stall.

---

## Where your data lives

Everything Nucleus knows is in the folder you chose during setup:

```
<your folder>/
├── memory/
│   ├── me/            your identity, voice, preferences, reflections  (private)
│   ├── client/        one file per client
│   ├── person/        one file per person
│   ├── bizdev/        opportunities
│   ├── workstream/    ongoing initiatives
│   ├── hot.md         the short "what matters right now" cache loaded every session
│   ├── index.md       catalog of everything (generated)
│   └── staged/        overnight proposals waiting for /morning
├── briefs/            one Markdown copy of each daily brief
├── plugins/           each plugin's settings (cortex.md, ops.md, growth.md, …)
└── Projects/          deliverables, organized by client
```

Two rules keep this safe to share later:

- **`memory/me/` is private.** It's excluded from any git remote by default. Keep it local or push it to a remote only you control.
- **Everything else is shareable.** Clients, people, workstreams, and company knowledge can be versioned to a private git repo for backup, and eventually shared with teammates. `/morning` commits and pushes automatically once a remote is configured.

Nucleus never deletes a fact. When something changes, the old entry is marked superseded with a date, so you can always see what was true when.

---

## Safety: what Nucleus will and won't do

One autonomy policy governs every command, skill, and agent. You review it during setup and can tighten or loosen any tier.

| Always | Ask first | Never |
|---|---|---|
| Read memory before acting | Send any email, DM, or Slack message | Send on your behalf without a per-message approval |
| Stage proposals instead of editing memory unattended | Create or change CRM deals or stages | Write memory from an unattended run (staged drafts only) |
| Cite sources for every proposed fact | Delete or archive a memory node | Store secrets, card numbers, or government IDs |
| | Register or change a scheduled task | Silently overwrite a fact (it supersedes with a date) |
| | Spend API credits (e.g. Apollo enrichment) | |

Outbound messages, invoices, and client updates are always drafts. Connectors (Gmail, Calendar, HubSpot, Slack, Drive, Apollo, and others) are separate; installing Nucleus doesn't grant access to any of them, and plugins tell you which sources they skipped.

---

## Adding more plugins

Install any specialist the same way as the starters (**Browse plugins → Nucleus → Install**), then run its setup command once, or just re-run `/start-nucleus` and it will pick it up.

| If you mostly… | Add |
|---|---|
| Run client engagements | Client Success, Today's Brief, Admin |
| Do business development | Growth Engine, Today's Brief |
| Write and publish | Research (Comms Desk is already installed) |
| Coordinate across teams in Slack | Team Alignment |

Each plugin's setup writes its settings to `<your folder>/plugins/`. Updating a plugin never overwrites those files.

---

## Updating, troubleshooting, uninstalling

**Update:** in **Customize → Plugins**, click **Update** on the Nucleus marketplace, then update individual plugins that show a new version. Start a new session afterward.

**Something feels off:** `/diagnose` runs a green/red checklist with specific fixes. `/status` is the ten-second version.

| Symptom | Fix |
|---|---|
| Commands not recognized after install | Start a new Cowork session; plugins load at session start. |
| "Can't find memory" / setup asks for a folder again | The pointer file (`~/.cortex/config-root`) is missing or points to a moved folder. Run `/start-nucleus` and re-point it. |
| A plugin appears twice | It was installed from two marketplace sources. Uninstall one copy under **Customize → Plugins**. |
| Overnight refresh never runs | Your computer was asleep or the app was closed at 11 pm, or the first run is still waiting for tool approvals. Run the task once manually from the Scheduled tasks list and approve with "always allow". |
| Drafts don't sound like you | Re-run `/setup-voice` with two or three fresh samples; Comms Desk improves from your edits over time. |
| Upgrading from a pre-rename install (`claude-cortex`, `core-ops`, `daily-brief`, …) | Install the new plugins, then uninstall the old ones. Your memory folder and settings carry over automatically. |
| Team/Enterprise admin can't add the marketplace | Organization-managed marketplaces must be private repos. Members can add Nucleus individually under **Customize → Plugins → Add marketplace** instead. |

**Uninstall:** remove plugins under **Customize → Plugins**. Your memory folder is untouched; delete it yourself if you want it gone.

---

## Installing on other hosts

The same workflows and the same memory folder work everywhere. Set up once in any host and the others find it.

<details>
<summary><strong>Claude Code</strong></summary>

```
/plugin marketplace add BrightWayAI/nucleus
/plugin install cortex@nucleus
/plugin install ops@nucleus
/plugin install comms@nucleus
```

Then `/start-nucleus`. Claude Code reads and writes the memory folder directly; no folder permission step.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add https://github.com/BrightWayAI/nucleus
codex plugin add cortex@nucleus
codex plugin add ops@nucleus
codex plugin add comms@nucleus
```

Start a new thread, then `$cortex:start-nucleus`. Codex needs your memory folder in its sandbox's readable/writable roots. Full details in [OpenAI setup](docs/OPENAI_SETUP.md).

</details>

<details>
<summary><strong>ChatGPT Work</strong></summary>

See the [ChatGPT Work quickstart](#quickstart-in-chatgpt-work-about-20-minutes) above. ChatGPT web/cloud can't reach a local memory folder without a remote MCP bridge; use the desktop app's Local Work. Full details in [OpenAI setup](docs/OPENAI_SETUP.md).

</details>

| Goal | Cowork / Claude Code | Codex | ChatGPT |
|---|---|---|---|
| Set up | `/start-nucleus` | `$cortex:start-nucleus` | `@Cortex start Nucleus setup` |
| Morning | `/morning` | `$cortex:morning` | `@Cortex run my morning` |
| Anything else | `/cos …` | `$ops:cos …` | `@Chief of Staff …` |

How every host finds your memory folder, in order: an explicit override, `CORTEX_CONFIG_ROOT`, `~/.cortex/config-root`, `~/Documents/.claude-plugin-config-root` (older installs), then `~/Documents/Claude` as a last resort.

---

## Plugin catalog

| Plugin | ID | What it owns | Repository |
|---|---|---|---|
| Cortex | `cortex` | Memory, identity, recall, overnight learning, maintenance | [BrightWayAI/cortex](https://github.com/BrightWayAI/cortex) |
| Chief of Staff | `ops` | `/cos` routing, diagnostics, schedules, metrics, connector tests | [BrightWayAI/ops](https://github.com/BrightWayAI/ops) |
| Today's Brief | `briefing` | Daily brief, annotations, tomorrow planning, weekly review, dashboard | [BrightWayAI/briefing](https://github.com/BrightWayAI/briefing) |
| Growth Engine | `growth` | Relationship cockpit, buying signals, referral asks, pre-call briefs, pipeline analysis and forecast | [BrightWayAI/growth](https://github.com/BrightWayAI/growth) |
| Client Success | `clients` | Engagement kickoff, weekly client status, deliverable QA | [BrightWayAI/clients](https://github.com/BrightWayAI/clients) |
| Comms Desk | `comms` | Voice capture, voice-matched drafting, post assembly, style learning | [BrightWayAI/comms](https://github.com/BrightWayAI/comms) |
| Admin | `admin` | Time log, invoices | [BrightWayAI/admin](https://github.com/BrightWayAI/admin) |
| Research | `research` | Cited research, news roundup candidates, memory-gap research | [BrightWayAI/research](https://github.com/BrightWayAI/research) |
| Team Alignment | `alignment` | Slack cross-team alignment scanning | [BrightWayAI/alignment](https://github.com/BrightWayAI/alignment) |

Current versions are in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Earlier plugin names (`claude-cortex`, `core-ops`, `daily-brief`, `relationships`, `delivery`, `voice`, `time-tracking`, `news-curator`, `weekly-alignment`, and the retired `lead-engine`, `referral-engine`, `client-status`, `project-setup`, `nucleus-router`, `weekly-outreach`, `bizdev-outreach`, `plan-tomorrow`) all map to the nine above; their old repos redirect here.

---

## How it fits together

```
You
 └─ Chief of Staff (/cos)          routes, monitors, owns no domain
     ├─ Cortex                     remembers
     ├─ Today's Brief              every "what's going on" surface, at any cadence
     ├─ Growth Engine              decides who and when
     ├─ Client Success             owns the account after signature
     ├─ Comms Desk                 decides how it sounds; writes
     ├─ Admin                      money and paperwork
     ├─ Research                   finds and cites; doesn't write the post
     └─ Team Alignment             internal coherence

All plugins read and write one private folder of Markdown files.
```

Specialist agents inside the plugins (`note-taker` and `memory-librarian` in Cortex, `chief-of-staff` in Chief of Staff, `relationships-director`, `pipeline-analyst`, and `pipeline-forecast` in Growth Engine, `gap-researcher` and `news-curator` in Research, `post-assembler` in Comms Desk, `alignment-scanner` in Team Alignment) do research and synthesis and hand findings back with evidence. They never get their own permission to write memory, change a CRM, send a message, or register a schedule.

---

## For developers and contributors

- [CONTRIBUTING.md](CONTRIBUTING.md) — how the plugins are structured and how to propose changes
- [docs/contracts.md](docs/contracts.md) — the shared files and formats plugins depend on, and the container rules for what belongs where
- [docs/RELEASING.md](docs/RELEASING.md) — coordinated releases, version pins, and validation scripts
- [docs/CONNECTOR_INTEGRATION_TESTING.md](docs/CONNECTOR_INTEGRATION_TESTING.md) — live connector certification
- [docs/multi-agent-patterns.md](docs/multi-agent-patterns.md) — how subagents are chained inside plugins
- [docs/proposals/ROADMAP.md](docs/proposals/ROADMAP.md) — what's next
- [llms.txt](llms.txt) — one-file onboarding for an AI agent working on this repo

You don't need to fork to customize: every plugin's `/setup-*` interview writes your settings to your memory folder, and updates never overwrite them. Fork only to change methodology or add a capability.

---

## Help and license

Marketplace, install, or cross-plugin issues: [BrightWayAI/nucleus/issues](https://github.com/BrightWayAI/nucleus/issues). Plugin-specific issues go in that plugin's repository.

Every plugin is MIT-licensed. Use it, fork it, share it. Setup, customization, and team rollout services from [BrightWay AI](https://brightwayai.com).
