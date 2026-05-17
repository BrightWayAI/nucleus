# nucleus-router — JARVIS front door for the Nucleus marketplace

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus marketplace_
_Status: Spec ready. No work has started._

---

## Why this exists

Nucleus ships 57 slash commands across 13 plugins. To use it well, a user has to remember which command does what — `/brief` vs `/plan-tomorrow`, `/recall` vs `/search`, `/lead-pull` vs `/lead-connect`, etc. That friction is the difference between a CLI and an assistant.

The fix: an always-loaded skill (the **router**) that maps natural-language intent to the right command, suggests it, and confirms before running. The user types or speaks how they think — the router translates to the catalog.

Two design influences:
- **Karpathy's LLM wiki "map" pattern.** A single `CLAUDE.md` document at the root of a vault tells the AI which room to enter for which task. The router is the same idea applied to the Nucleus catalog: one routing document, always in context, that lists every command and the natural-language patterns that should invoke it.
- **JARVIS / ambient assistant UX.** No command memorization. Conversational. The router is the AI front door.

This proposal is for Phase 1 of the "Nucleus as JARVIS" initiative. Phase 2 is Obsidian as the human UI; Phase 3 is productization (see separate proposals).

---

## Decisions (locked)

1. **Distribution:** new standalone plugin `nucleus-router` in the catalog. Lives at `~/lab-bench/nucleus-router/`, repo `BrightWayAI/nucleus-router`. Catalog grows 13 → 14.
2. **Behavior:** **suggest + confirm**. Router responds with "sounds like you want to run `/brief` — proceed?" and waits for yes. Never auto-dispatches.
3. **Always-on:** ships one skill with eager triggers so it loads at conversation start, similar to `cortex/recall`.

---

## Layout

```
nucleus-router/
├── .claude-plugin/plugin.json
├── README.md
├── CHANGELOG.md
├── LICENSE
├── SECURITY.md
├── commands/
│   └── route.md             # explicit /route command (also surfaces help)
└── skills/
    └── route/
        └── SKILL.md         # the always-loaded intent table
```

`plugin.json` — minimal, version `0.1.0`, author BrightWay AI, repository `https://github.com/BrightWayAI/nucleus-router`.

---

## How the router works (runtime flow)

1. **Conversation start.** The `route` skill auto-loads via its eager trigger description. Claude now has the full intent table in context for the rest of the session.
2. **User speaks naturally.** "What's on my plate today?" / "I just met Sarah Chen at the AI Summit." / "Who haven't I followed up with in two weeks?"
3. **Router matches intent.** Walks the table top-to-bottom; picks the first matching row. Each row is `pattern → command → optional clarifying question`.
4. **Suggest and confirm.**
   > Sounds like you want to run **`/brief`** (today's working surface). Run it?
5. **User confirms.** Yes → Claude invokes the command. No / "do something else" → router asks one clarifying question or proposes a different command.
6. **Ambiguous match.** When two commands match equally well, the router asks: "I can route this to `/recall` (search memory) or `/search` (full-text search the wiki). Which one?"
7. **No match.** Router says: "I don't have a command for that yet. Here's what's closest: …" and offers the nearest two.

The router never invokes commands silently. The user always sees the choice before it runs.

---

## The intent table (initial coverage)

Format: each row is one line in `SKILL.md`. Pattern is shown as the kind of utterance, not a regex — Claude matches semantically.

### Memory and knowledge (cortex)

| Natural language | Command |
|---|---|
| "what do we know about X" / "remind me about X" / "catch me up on X" | `/recall` |
| "I just learned…" / "remember that…" / "make a note that…" | `/remember` |
| "save this thought" / "scratch note" | `/note` |
| "I just met X" / "add a person page for X" | `/remember` (person flow) |
| "search my memory for…" / "find the entry where…" | `/search` |
| "forget that…" / "that's wrong, X is actually Y" | `/forget` |
| "what happened on/around DATE" / "show me my timeline" | `/timeline` |
| "review my open threads" / "what's stale" | `/review` |
| "what's an important lesson I learned" / "drill me on…" | `/rehearse` |
| "wrap up the day" / "end of day" / "checkpoint" | `/end-day` |
| "wrap up the week" / "weekly retro" | `/end-week` |
| "clean up my memory" / "prune stale entries" | `/cleanup` |
| "observe X passively" | `/observe` |
| "I learned X from working on Y" | `/learn` |

### Daily flow (daily-brief)

| Natural language | Command |
|---|---|
| "what's on my plate" / "what's today" / "build my brief" | `/brief` |
| "I left notes in the brief" / "act on my annotations" / "process the brief" | `/process-brief` |
| "block out tomorrow" / "plan tomorrow" / "what's tomorrow look like" | `/plan-tomorrow` |

### Business development (lead-engine + bizdev-outreach + weekly-outreach + referral-engine)

| Natural language | Command |
|---|---|
| "pre-call brief on X" / "research X before the call" | `/lead-brief` |
| "capture this lead" / "add X to the pipeline" | `/lead-capture` |
| "draft a connection request to X" / "warm up X" | `/lead-connect` |
| "draft a message to X" / "draft outreach to X" | `/lead-draft` |
| "log that I messaged X" / "record that touchpoint" | `/lead-log` |
| "show me the pipeline" / "who's hot right now" | `/lead-pipeline` |
| "pull new leads from LinkedIn" | `/lead-pull` |
| "warm sequence to X" / "3-touch cadence" | `/lead-warm` |
| "research X and draft outreach" (cold contact, not in LinkedIn) | `/setup` (bizdev-outreach) |
| "plan this week's outreach" / "weekly BD prep" / "who should I reach out to this week" | `/weekly-outreach` |
| "ask X for a referral to Y" / "draft a referral ask" | `/referral-ask` |
| "who are my best connectors" / "referral network" | `/referrals` |

### Client and project ops (client-status + project-setup + time-tracking)

| Natural language | Command |
|---|---|
| "weekly status update for X" / "client status draft for X" | `/client-status` |
| "set up a new engagement" / "kick off project X" / "new client" | `/project-setup` |
| "log my time" / "what did I work on today" / "process calendar into time entries" | `/track-time` |
| "generate invoices" / "bill out this month" | `/generate-invoices` |

### Content and roundups (news-curator)

| Natural language | Command |
|---|---|
| "draft this week's AI roundup" / "LinkedIn news post" / "weekly news" | `/ai-roundup` |

### Slack / cross-team (weekly-alignment)

| Natural language | Command |
|---|---|
| "scan Slack for alignment issues" / "what's the team talking about" / "Monday brief" | (auto-fires; skill-only plugin) |

### Voice / writing-style

| Natural language | Command |
|---|---|
| "rewrite this in my voice" / "polish this to sound like me" | `/style` |
| "learn from this edit" / "I just rewrote this — capture the pattern" | `/style-learn` |
| "audit my voice guide" / "review the style guide" | `/style-review` |

### Ops and health (core-ops + cortex setup)

| Natural language | Command |
|---|---|
| "show me Nucleus status" / "what's running" / "system health" | `/nucleus-status` |
| "open the dashboard" / "give me the full view" | `/nucleus-dashboard` |
| "something's broken" / "diagnose X" | `/diagnose` |
| "review this deck/doc/spreadsheet" / "QA pass on this deliverable" | `/review-deliverable` |
| "log an agent run" | `/log-agent-run` |
| "agent metrics" / "how often does X fire" | `/agent-metrics` |
| "set up identity" / "first-time setup" | `/setup-identity` |
| "set up my voice" | `/setup-voice` |
| "set up note sources" / "connect Granola/Gemini/Fireflies" | `/setup-sources` |

### Setup commands (catch-all)

When a user says "set up X" and X matches a plugin, route to that plugin's setup command (`/setup-brief`, `/setup-plan`, `/setup-news`, `/setup-outreach`, `/setup-projects`, `/setup-time`, `/setup-referrals`, `/setup-core`, `/setup-style`). When ambiguous, list the available setup commands.

---

## SKILL.md structure

```markdown
---
name: route
description: >
  Natural-language router for the Nucleus marketplace. Auto-fires at conversation
  start to load the intent table. When the user speaks naturally about something
  Nucleus can do, this skill suggests the right slash command and asks for
  confirmation before running.

  Trigger patterns:
  - Any verb-ish utterance that maps to a Nucleus capability (see intent table).
  - Explicit /route invocation lists the table and offers help.
  - Ambiguous utterances ("help me with X") get clarifying questions, not commands.
---

# Nucleus router

## When to fire

[Detailed trigger rules]

## How to route

[3-step procedure: match → suggest → confirm]

## The intent table

[Full table from this proposal]

## Failure modes

- No match → propose closest two.
- Ambiguous → ask one clarifying question.
- Setup needed → check if plugin's setup command has been run; if not, route to setup first.
- Multi-step intent ("draft outreach to X and log it") → run commands sequentially, confirming each.
```

---

## /route command (commands/route.md)

The explicit `/route` command does three things:

1. Lists every Nucleus capability grouped by domain — a printed cheat sheet.
2. Accepts a natural-language argument and runs the same routing logic as the skill (useful when the user wants to *explicitly* invoke the router instead of relying on auto-fire).
3. Shows installed-plugin-only commands. If a plugin isn't installed, its rows are hidden.

Example:
```
/route "what should I do today"
→ Sounds like you want /brief. Run it?
```

---

## How it interacts with cortex's auto-recall

`cortex/recall` also auto-fires at conversation start to load memory. Two always-on skills loading on the same trigger is fine — they do different things:

- **`recall`** loads *content* (memory nodes for the user/projects mentioned).
- **`route`** loads the *routing table* (capabilities and how to invoke them).

Order doesn't matter; both contribute context. Document this in the router's SKILL.md.

---

## Installed-only filtering

The router should not propose commands from plugins the user hasn't installed. Detection:

- At conversation start, the skill reads `~/.claude/plugins/` (or whatever Cowork/Claude Code expose) to see which Nucleus plugins are present.
- Rows from missing plugins are skipped during matching.
- If a user asks for something only a missing plugin provides, the router responds: "That capability lives in the `lead-engine` plugin. Want install instructions?"

If plugin detection isn't reliable in Cowork, fall back to running everything and letting Claude Code surface the "command not found" error — the router still offers value as a translation layer.

---

## Acceptance criteria

- [ ] `nucleus-router` plugin lives at `~/lab-bench/nucleus-router/` with the standard plugin layout.
- [ ] `plugin.json` v0.1.0, repository points to `BrightWayAI/nucleus-router`.
- [ ] `skills/route/SKILL.md` contains the intent table covering all 57 commands across the 13 plugins (writing-style commands included).
- [ ] `commands/route.md` provides explicit `/route` for cheat-sheet and explicit-invocation use.
- [ ] Auto-fires at conversation start without conflicting with cortex's `recall`.
- [ ] Suggest+confirm flow: never invokes a command without the user agreeing.
- [ ] Marketplace `marketplace.json` updated to include `nucleus-router`.
- [ ] README.md updated to mention the router as the front door.

---

## Out of scope (future work)

- **Voice input.** A user speaking "what's on my plate" instead of typing it is a Cowork/Claude Code platform feature, not a router feature. Router treats it as text.
- **Multi-command chains.** Initial version handles one command per turn. Chains like "do X then Y" can be added in v0.2 once the single-command flow is solid.
- **Learning the user's phrasing.** Eventually the router could capture which utterances the user uses for which commands and bias future matches. Out of scope for v0.1.
- **Productization positioning.** Covered separately in `docs/proposals/productization.md` (TBD).
