# Nucleus on ChatGPT Work and Codex

Nucleus runs the same workflows against the same memory folder whether you use it from Claude, ChatGPT, or Codex. This guide covers the two OpenAI hosts. If you only use Claude, you don't need it.

The GitHub repositories contain workflow code and templates only. They never contain, upload, or sync anyone's memory. Each person uses their own private memory folder; don't point several people at one folder as a shared database.

---

## Quickstart in ChatGPT Work (about 20 minutes)

You need the **ChatGPT desktop app** with **Local Work** enabled. Nucleus keeps memory in a local folder, so it works in desktop Local Work chats, not in the web app (see [Web and cloud](#chatgpt-web-and-cloud) below).

### 1. Admin: import the marketplace (once per workspace)

1. Open **Admin → Plugins → Add → Import marketplace**.
2. Enter `https://github.com/BrightWayAI/nucleus` as the source. Leave **Path** blank; the catalog is at the repository root. Use the default branch, or pin a reviewed release tag if the import screen offers a revision selector.
3. Review the nine referenced repositories, then mark **Cortex**, **Chief of Staff**, and **Comms Desk** as **Available** (or **Installed**) for the roles that need them. Add specialists the same way when people ask.

Importing makes the plugins available; it does not install anything for anyone or grant folder or connector access. The native catalog ChatGPT reads is `.agents/plugins/marketplace.json`.

### 2. Member: enable the three starter plugins

Open a **new Local Work chat** and enable **Cortex**, **Chief of Staff**, and **Comms Desk** for the chat, either from the plugin picker or by `@`-mentioning them the first time.

| Plugin | What it does |
|---|---|
| **Cortex** | The shared brain: clients, people, projects, decisions, your identity and voice. Every other plugin reads from it. |
| **Chief of Staff** | The front door. Say what you want in plain English and it routes to the right specialist. Also health checks. |
| **Comms Desk** | Captures your voice once, then drafts anything that goes out in your name. |

### 3. Make a folder for your memory

Create an empty folder you control, for example `~/Documents/Nucleus`. Already using Nucleus in Claude on this computer? Skip this and reuse that folder; ChatGPT will find the same memory.

### 4. Run setup

```
@Cortex start Nucleus setup
```

Setup walks you through, in order, and lets you skip anything that doesn't apply:

1. **Where to store memory** — give it the folder from step 3. ChatGPT asks you to grant Local Work access to that folder; approve it. Cortex records the location in `~/.cortex/config-root` so every host finds it.
2. **Identity** — name, role, company, time zone, tools. Asked once; every plugin reads it.
3. **Voice** — paste two emails or messages you wrote. Comms Desk makes every draft sound like you.
4. **Autonomy policy** — what Nucleus may do on its own vs. must ask about. Accept the defaults or adjust.
5. **Note sources** — connect Granola, Fireflies, Otter, Gemini, or a Drive folder if you use one for meeting notes.
6. **Per-plugin setup** for anything else you enabled.
7. **Health check.**

Say `@Cortex start Nucleus setup` again any time; it only runs what's still missing.

### 5. Your first day

```
@Cortex run my morning
```

`run my morning` shows anything Nucleus learned since yesterday, lets you accept or reject each item, captures a short reflection, and sets today's priorities. Five minutes. It's the one thing you do every day.

Then talk to the chief of staff:

```
@Chief of Staff catch me up on Acme
@Chief of Staff who should I follow up with this week?
@Chief of Staff draft a check-in to Jordan about the proposal
```

### What's different from Claude

- **Overnight refresh.** In Claude Cowork a scheduled task runs the ingest at night. ChatGPT runs it only if your host exposes a scheduler and you confirm the registration. If it doesn't, say `@Cortex listen` before `run my morning` and it does the same ingest on demand.
- **Connected apps.** Gmail, Calendar, HubSpot, Slack, Drive, and Apollo come from your workspace's apps and connectors, not from Nucleus. Plugins check at runtime and tell you which sources they skipped; they never invent data for a connector that isn't there.
- **Artifacts.** Where Cowork renders an interactive HTML brief, ChatGPT and Codex get Markdown or a supported document artifact with the same content. Actions you state in chat (done, delegate, snooze, reprioritize, annotate, or reflect) are saved to the same local v0.7 brief-state file that Cortex `/listen` mines overnight; silence never becomes an inferred action.

---

## Quickstart in Codex

```bash
codex plugin marketplace add https://github.com/BrightWayAI/nucleus
codex plugin add cortex@nucleus
codex plugin add ops@nucleus
codex plugin add comms@nucleus
```

Add specialists with `codex plugin add <plugin-name>@nucleus`. A local checkout can be registered by replacing the URL with the repository's absolute path.

Start a new thread, then:

```
$cortex:start-nucleus
```

Codex needs your memory folder as a **readable root** for recall and a **writable root** for anything that saves (setup, `remember`, `morning`). Grant the resolved absolute path in the sandbox settings when Codex asks. Then `$cortex:morning` each day, and `$ops:cos <request>` for everything else.

### Scheduled listen verification

The nightly-listen fix is pinned for review in
[`2026.09.18-rc.1`](../releases/2026.09.18-rc.1/release.json). It remains a
candidate with [known release blockers](../releases/2026.09.18-rc.1/NOTES.md).
Installing that catalog does not repair an existing scheduled task.

OpenAI documents desktop scheduled tasks running in a local project or worktree,
with the computer on and the app running. Web tasks cannot directly use a folder on
your computer, and Codex CLI has no Scheduled management interface.
See [OpenAI scheduled-task documentation](https://learn.chatgpt.com/docs/automations?surface=app)
(reviewed 2026-09-18).

The Cowork names `scheduler.register`, `create_trigger`, `list_triggers`,
`requires_local_device`, and `derived_state.folders_state` are not a verified Codex
API mapping. This review found no scheduler management tool exposed in the active
Codex session, and the official documentation does not establish an equivalent
programmatic folder-binding response. Local task metadata can describe the intended
environment and working directories; it cannot prove live folder access.

For an OpenAI-host registration to satisfy the shared contract:

1. Resolve the absolute Cortex root and select the local execution environment
   that can reach it. A worktree must still reach the original root.
2. Use only the scheduler tools actually exposed by that host. Verify the saved
   task's execution environment and folder access through a supported live readback;
   do not substitute a cached `ACTIVE` flag or invent Cowork response fields.
3. Verify read/write access in the scheduled execution context and obtain a
   terminal metadata-only receipt. An interactive session's permissions do not
   prove the unattended run has those permissions.
4. Report the loop healthy only with verified binding and a successful receipt
   from the same host/task within 26 hours. If verification is unavailable, say
   **unverified**; return manual setup instructions or run `$cortex:listen` on demand.

The published plugins write receipts to
`<config-root>/plugins/ops/schedule-runs/<schedule>/<run-id>.json`; the handoff's
`memory/staged/queues/receipts/` path was not implemented. The pinned receipt
success fields also disagree, as recorded in the candidate audit. A failed root
probe must stop the workflow and emit failure metadata to an authorized fallback
or the run log when the root cannot be written. A failed shell command alone does
not establish how the host will classify the overall agent run; verify this before
claiming unattended failure propagation works.

### Brief state without Cowork

The shared v0.7.0 `<config-root>/briefs/<date>.state.json` remains the OpenAI
input for explicit chat actions and fallback closure derivation. A Markdown brief
does not need a `.artifact-runtime.json` file. An existing pointer from Claude is
only a locator: `capability: "db"` does not make a hosted artifact readable by Codex.
Use an available authorized bridge, or report missing readback and retain local
state. Do not overwrite newer local actions with an unverified hosted snapshot.

If neither closures nor readable state exists, the brief must disclose that
yesterday's state is missing. Fallback closures help with explicit completions,
but the pinned fallback still has snooze, suppression, reflection, and later-remine
gaps documented in the candidate audit. It is not proof that nightly ingest ran.

---

## Everyday commands, side by side

| Goal | ChatGPT | Codex | Claude |
|---|---|---|---|
| Set up | `@Cortex start Nucleus setup` | `$cortex:start-nucleus` | `/start-nucleus` |
| Morning | `@Cortex run my morning` | `$cortex:morning` | `/morning` |
| Recall | `@Cortex recall Acme` | `$cortex:recall Acme` | `/recall Acme` |
| Save this conversation | `@Cortex show what you'd remember, then ask before saving` | `$cortex:remember` | `/remember` |
| Today's brief | `@Today's Brief build today's brief` | `$briefing:brief` | `/brief` |
| Draft in my voice | `@Comms Desk draft this in my voice` | `$comms:style` | `/style` |
| Health check | `@Chief of Staff diagnose my Nucleus setup` | `$ops:diagnose` | `/diagnose` |
| Anything else | `@Chief of Staff …` | `$ops:cos …` | `/cos …` |

Ask naturally in ChatGPT; `@`-mention a plugin when you want to be explicit. Codex exposes namespaced skills. The workflows and data formats underneath are identical.

---

## Where your memory lives

Every host resolves the memory folder in this order:

1. an explicit workflow or project override;
2. the `CORTEX_CONFIG_ROOT` environment variable;
3. `~/.cortex/config-root` (written by setup);
4. `~/Documents/.claude-plugin-config-root` (older Claude installs);
5. `~/Documents/Claude` as a last resort.

There is no separate ChatGPT or Codex config. If you'd rather set the location from a terminal, from a trusted Cortex checkout:

```bash
python3 scripts/configure_cortex.py --config-root "$HOME/Documents/Nucleus"
```

This writes the pointer and creates only missing starter files; it never migrates, replaces, or deletes an existing folder.

Inside the folder, `memory/me/` (identity, voice, preferences, reflections) is private and excluded from any git remote by default. Everything else (clients, people, workstreams, company knowledge) is shareable and can be versioned to a private repo for backup.

---

## ChatGPT web and cloud

Plugins and connected apps work in the web app, but a local memory folder is unreachable from there. Nucleus will not quietly substitute another store. To use memory from the web, configure an approved remote MCP bridge to the folder; otherwise use the desktop app's Local Work.

---

## Safety

One autonomy policy governs every command, skill, and agent, in every host:

- **Always** — read memory before acting; stage proposals instead of writing memory unattended; cite sources.
- **Ask first** — send any email, DM, or Slack message; create or change CRM deals or stages; delete or archive a memory node; register a schedule; spend API credits.
- **Never** — send on your behalf without a per-message approval; write memory from an unattended run (staged drafts only); store secrets or personal IDs; overwrite a fact instead of superseding it with a date.

Outbound messages, invoices, and status updates are always drafts. Specialist agents (`note-taker`, `memory-librarian`, `relationships-director`, `pipeline-analyst`, `post-assembler`, `alignment-scanner`, and others) have read-only bindings: when the host can delegate, they return findings to the parent workflow; when it can't, the parent does the same work inline. They never get independent authority to write files, change a CRM, send mail, or register schedules.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `@Cortex` or `@Chief of Staff` isn't recognized | The admin hasn't marked the plugin available for your role, or you're in a web chat. Start a new desktop **Local Work** chat. |
| Setup keeps asking where to store memory | Local Work access to the folder wasn't granted, or `~/.cortex/config-root` points to a moved folder. Re-run `@Cortex start Nucleus setup` and re-point it. |
| Codex can't save | The memory folder isn't a writable sandbox root. Add the absolute path. |
| A connector's data is "skipped" | That app isn't connected in your workspace. Connect it and start a new chat. |
| Drafts don't sound like you | `@Comms Desk set up my voice` again with fresh samples. |

---

## For developers: validating a checkout

Place the nine plugin repositories as siblings of this one under a single parent directory, then run:

```bash
python3 scripts/generate_openai_adapters.py --check
python3 scripts/check_openai_ecosystem.py
python3 scripts/smoke_codex_marketplace.py
python3 scripts/release_ecosystem.py check --all
python3 ../claude-cortex/scripts/check_repo.py
```

These validate manifests, marketplace ordering, versions, command-to-skill coverage, read-only role bindings, and config-root precedence using a temporary home and fixtures. They never read or write a real memory folder.

Each plugin ships `references/openai-portability.md`, which maps every Claude/Cowork capability to its ChatGPT/Codex equivalent or fallback. Static checks prove honest degradation and binding coverage; they can't prove access to connectors whose credentials weren't supplied. Before promoting a coordinated release, run Chief of Staff's `test-connectors` in each required host and validate the sanitized reports per `CONNECTOR_INTEGRATION_TESTING.md`. A real tool call is required for a pass.
