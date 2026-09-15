# Nucleus

**A portable operating system for AI-powered work.**

Nucleus is a marketplace of 13 open-source plugins for memory, planning,
relationships, business development, client delivery, writing, research, and
operations. The same workflows run in ChatGPT, Codex, Claude Code, and Claude
Cowork while reading and writing one user-owned set of Markdown files.

Nucleus does not upload your memory to GitHub and does not create a separate
database for each AI host. Your data stays in a private `<config-root>` that you
choose.

| Host | How workflows appear | Local shared memory |
|---|---|---|
| ChatGPT desktop Local Work | Natural language or `@Plugin` | Supported with folder permission |
| Codex | Natural language or namespaced Agent Skills | Supported with sandbox permission |
| Claude Code / Cowork | Natural language or slash commands | Supported with folder permission |
| ChatGPT web/cloud | Plugin skills and connected apps | Requires an approved remote MCP bridge for local memory |

All plugins are MIT-licensed.

## Architecture in one minute

Nucleus has four layers:

1. **The Nucleus repository is the master marketplace.** Importing it discovers
   the full catalog; it is not a fourteenth plugin that recursively runs the rest.
2. **Nucleus Router is the front door.** Ask for work in plain English and it
   selects the appropriate installed workflow.
3. **Cortex is the shared context layer.** It owns memory, identity, voice, recall,
   learning, and the common config-root pointer.
4. **Specialist plugins do the domain work.** They share context where useful but
   remain independently installable.

```text
You
 └─ Nucleus Router
     ├─ Cortex                 memory, identity, voice
     ├─ Daily Brief            daily planning and annotations
     ├─ Relationships          relationship priorities and drafts
     ├─ Lead Engine            signal-driven outreach
     ├─ Project / Client Ops   setup, status, time, invoicing
     ├─ Writing / Research     voice and news curation
     └─ Core Ops               diagnostics, QA, pipeline, schedules

All plugins ────────────────> one private <config-root>
```

## Install

Start with three plugins:

- `nucleus-router` — natural-language routing;
- `cortex` — shared memory, identity, and voice;
- `core-ops` — diagnostics and operational utilities.

Add specialists only when they match your work.

### ChatGPT workspace and desktop

A ChatGPT workspace administrator:

1. Opens **Admin → Plugins → Add → Import marketplace**.
2. Enters `https://github.com/BrightWayAI/nucleus` as the Source.
3. Leaves **Path** blank because the marketplace is at the repository root.
4. Uses the default branch or selects `main`.
5. Reviews the import, then marks the desired plugins **Available** or
   **Installed** for the appropriate roles.

Importing the marketplace discovers all 13 entries; it does not automatically
install every plugin or grant access to local folders and connected services.
See OpenAI's [plugin-management documentation](https://learn.chatgpt.com/docs/enterprise/plugin-management).

Members should start a new **ChatGPT desktop Local Work** chat after installation.
Cortex declares a local MCP server, so it is desktop-only unless you configure the
documented remote bridge.

### Codex

```bash
codex plugin marketplace add https://github.com/BrightWayAI/nucleus
codex plugin add nucleus-router@nucleus
codex plugin add cortex@nucleus
codex plugin add core-ops@nucleus
```

Install a specialist with:

```bash
codex plugin add <plugin-name>@nucleus
```

Start a new thread after installation so Codex loads the new skills and role
bindings.

### Claude Code or Cowork

```text
/plugin marketplace add BrightWayAI/nucleus
```

Choose the same three-plugin starter or install any specialist from the catalog.

## First setup: choose one shared memory location

If you already use Cortex with Claude, keep that location. ChatGPT and Codex will
resolve the existing pointer and use the same files.

For a new ChatGPT desktop user:

```text
@Cortex configure my memory at ~/Documents/Cortex. Show me the exact path and
ask before creating anything.
```

From a trusted Cortex checkout, the equivalent terminal setup is:

```bash
python3 scripts/configure_cortex.py --config-root "$HOME/Documents/Cortex"
```

This writes the vendor-neutral pointer `~/.cortex/config-root` and initializes
only missing starter files. It does not migrate, replace, or delete an old memory
root.

Every host resolves `<config-root>` in this order:

1. explicit workflow or project override;
2. `CORTEX_CONFIG_ROOT`;
3. `~/.cortex/config-root`;
4. legacy `~/Documents/.claude-plugin-config-root`;
5. `~/Documents/Claude` for backward compatibility.

There is no separate GPT config file. ChatGPT desktop needs Local Work permission
for the resolved folder. Codex needs that absolute path in its sandbox readable or
writable roots, depending on the workflow.

Then establish the two shared context files:

- set up identity → `<config-root>/identity.md`;
- set up voice → `<config-root>/voice.md`.

All specialist plugins read those files. Their own settings live under
`<config-root>/plugins/`.

## Use the same workflows from any host

You can normally ask in plain English. Explicit forms are useful for discovery and
repeatability:

| Goal | ChatGPT | Codex | Claude |
|---|---|---|---|
| Start setup | `@Cortex start Nucleus setup` | `$cortex:start-nucleus` | `/start-nucleus` |
| Recall context | `@Cortex recall Acme` | `$cortex:recall Acme` | `/recall Acme` |
| Save a conversation | `@Cortex preview what you would remember, then ask before saving` | `$cortex:remember` | `/remember` |
| Build today's brief | `@Daily Brief build today's brief` | `$daily-brief:brief` | `/brief` |
| Draft in your voice | `@Writing Style draft this in my voice` | `$writing-style:style` | `/style` |
| Review stack health | `@Core Ops diagnose my Nucleus setup` | `$core-ops:diagnose` | `/diagnose` |
| Find the right workflow | `@Nucleus Router route this request` | `$nucleus-router:route` | `/route` |

Exact skill rendering can vary by client version, but the workflow names and data
contracts are shared.

## Talk in outcomes, not commands

The router recognizes a compact set of everyday intents:

| Intent | Typical result |
|---|---|
| Start my day / what's on my plate | Calendar, inbox, tasks, outreach, and recent context |
| Catch me up on X | Cross-node memory recall with sources |
| Research X | Existing context plus current external research when available |
| Capture / remember X | Typed knowledge or conversation commit with confirmation |
| Draft X to Y | Relevant context, shared voice, and the right specialist |
| Plan tomorrow / this project | Calendar plan, engagement plan, or workstream |
| Track time / pipeline / touchpoint | Domain-specific log or analysis |
| Review this | Deliverable QA, voice audit, memory cleanup, or pipeline review |
| Status update for X | Client-status draft from available evidence |
| Bill last month | Invoice drafts from the approved time log |
| What's missing | Memory-gap detection and optional cited research |
| Close the day / week | Reflection, capture, cleanup, rehearsal, and preparation |

If a requested plugin or connector is unavailable, the router identifies the missing
capability instead of pretending the work ran.

## Plugin catalog

| Role | Plugin | What it provides |
|---|---|---|
| Chief of Staff | [nucleus-router](https://github.com/BrightWayAI/nucleus-router) | Natural-language routing across installed workflows |
| Knowledge and context | [cortex](https://github.com/BrightWayAI/claude-cortex) | Shared memory, identity, voice, recall, learning, cleanup, and Obsidian support |
| Executive assistant | [daily-brief](https://github.com/BrightWayAI/daily-brief) | Daily brief, annotation processing, and next-day planning |
| Relationship manager | [relationships](https://github.com/BrightWayAI/relationships) | Prioritized relationship actions and context-aware drafts |
| Head of outbound | [lead-engine](https://github.com/BrightWayAI/lead-engine) | Buying signals, warm outreach, cadence, and call preparation |
| Head of partnerships | [referral-engine](https://github.com/BrightWayAI/referral-engine) | Referral opportunities, cooling periods, and draft asks |
| Project manager | [project-setup](https://github.com/BrightWayAI/project-setup) | Engagement interview, folder blueprint, portable workspace prompt, and project plan |
| Account manager | [client-status](https://github.com/BrightWayAI/client-status) | Weekly client-status drafts from available project evidence |
| Finance | [time-tracking](https://github.com/BrightWayAI/time-tracking) | Calendar-based time classification and invoice drafts |
| Communications | [writing-style](https://github.com/BrightWayAI/writing-style) | Voice-matched drafting and learning from approved edits |
| Marketing research | [news-curator](https://github.com/BrightWayAI/news-curator) | Cited news research and voice-matched roundup drafts |
| Operations | [core-ops](https://github.com/BrightWayAI/core-ops) | Diagnostics, deliverable QA, pipeline analysis, metrics, and schedules |
| Cross-team liaison | [weekly-alignment](https://github.com/BrightWayAI/weekly-alignment) | Slack-based overlap, conflict, decision, and risk scanning |

## Agents and connectors

Nucleus includes focused research and ranking roles such as memory librarian,
contact researcher, pipeline analyst, relationship ranker, news curator, and post
assembler.

- When the host supports delegation, read-only agents return findings to the parent
  workflow.
- When delegation is unavailable, the parent follows the same role inline.
- Agents do not receive independent permission to write memory, mutate a CRM, send
  messages, or register schedules.

Slack, CRM, email, calendar, Apollo, Drive, and similar services remain separate
apps or MCP connectors. Plugins check availability at runtime, list skipped sources,
and use pasted or local context where the workflow supports it. Installing Nucleus
does not grant access to those services.

Host-specific fallbacks are explicit:

- Cowork HTML artifacts become Markdown or supported document artifacts elsewhere.
- Connector writes require a preview and confirmation at the point of action.
- Outbound messages, invoices, and client updates remain drafts by default.
- Schedule definitions are returned for manual setup when the host has no scheduler.
- ChatGPT web/cloud cannot silently substitute another store for local Cortex memory.

## Suggested bundles

**Minimum starter**

```text
nucleus-router + cortex + core-ops
```

**Business development**

```text
nucleus-router + cortex + core-ops + lead-engine + relationships + referral-engine
```

**Client delivery**

```text
nucleus-router + cortex + core-ops + project-setup + client-status + time-tracking + daily-brief
```

**Content and relationships**

```text
nucleus-router + cortex + writing-style + news-curator + relationships + referral-engine
```

**Cross-team operator**

```text
nucleus-router + cortex + weekly-alignment + daily-brief + core-ops
```

## Daily and weekly rhythm

A complete setup can support this cadence:

```text
Morning       build today's brief and relationship priorities
During work   recall context, capture decisions, draft, and track
End of day    reflect, commit approved memory, and prepare tomorrow
End of week   review, clean up, rehearse knowledge, and stage next week
Monthly       prepare invoices and pipeline forecasts
```

Scheduling is optional and host-dependent. Nucleus never treats registration as
successful unless the active host actually exposes a scheduler.

## Customize without forking

Each specialist has a setup workflow that captures its CRM mappings, ICP, offerings,
billing rules, templates, or other domain context. The workflow writes user-owned
settings beneath `<config-root>/plugins/`; repository updates do not overwrite those
files.

Fork only when you want to change methodology or add a new capability. If you fork:

1. change the canonical skills or workflow files in the specialist repository;
2. keep `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` aligned;
3. update both Nucleus marketplace manifests to reference the fork;
4. run the ecosystem validation before publishing;
5. sync or refresh the marketplace in each host.

See [multi-agent patterns](docs/multi-agent-patterns.md) and the
[proposal roadmap](docs/proposals/ROADMAP.md) for extension guidance.

## Validation

With the 13 repositories checked out as siblings:

```bash
python3 scripts/generate_openai_adapters.py --check
python3 scripts/check_openai_ecosystem.py
python3 scripts/smoke_codex_marketplace.py
python3 ../claude-cortex/scripts/check_repo.py
```

These checks validate marketplace structure, native manifests, command-to-skill
coverage, version agreement, read-only role bindings, isolated Codex installation,
and config-root precedence using temporary homes and fixtures. They do not read or
write real Cortex memory.

## Current versions

| Plugin | Version |
|---|---:|
| nucleus-router | 0.2.2 |
| cortex | 4.15.0 |
| core-ops | 0.3.3 |
| lead-engine | 0.2.5 |
| relationships | 0.2.4 |
| referral-engine | 0.2.5 |
| news-curator | 0.2.4 |
| client-status | 0.2.5 |
| project-setup | 0.2.5 |
| time-tracking | 0.2.4 |
| weekly-alignment | 1.4.4 |
| writing-style | 0.1.3 |
| daily-brief | 0.6.2 |

The native OpenAI catalog is
[`/.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json). The
Claude-compatible catalog is
[`/.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).

## Help and license

Open plugin-specific issues in the corresponding repository. Use
[BrightWayAI/nucleus issues](https://github.com/BrightWayAI/nucleus/issues) for
marketplace import, catalog, or cross-plugin problems.

Each plugin is MIT-licensed. Use it, fork it, customize it, and share it.
