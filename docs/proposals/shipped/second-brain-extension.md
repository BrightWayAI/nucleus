# Second-Brain Extension — Tech Spec for the BrightWayAI Plugin Marketplace

_Created: 2026-05-11_
_For: Zach Wagner / BrightWayAI marketplace_
_Inspiration: Omar Ismail's second-brain setup — https://omarismail.com/projects/second-brain_
_Status: Ready to execute. No work has started._

---

## Part 1 — Why this exists

Omar Ismail's "second brain" is a deliberate counterpoint to vector-database memory systems. Three claims:

1. **Vector search loses context, isn't human-readable, and doesn't compound.** Synthesize knowledge into wiki-style markdown pages — one per entity — that link to each other.
2. **Automate capture entirely.** Human error during note-taking is the single biggest failure mode. Nightly pulls from calendar, email, Slack, transcripts → immutable archive.
3. **Interactive daily working document drives execution.** A 7:45am markdown brief becomes the day's planning + draft-review + action-tracking artifact. User leaves inline comments; Claude executes against them.

The BrightWayAI marketplace already implements **most** of Omar's architecture (cortex's wiki nodes, draft-first plugins with confirmation gates, end-of-day rituals). Five specific gaps remain. Closing them yields a system that compounds in the way Omar's does, without forcing users into Obsidian-or-bust tooling.

### What's already true in the marketplace

| Pattern | Plugin |
|---|---|
| Wiki-style markdown memory, never vector DB | claude-cortex |
| Draft-first with explicit user confirmation | every drafting plugin (lead-engine, bizdev-outreach, weekly-outreach, client-status, referral-engine, news-curator) |
| Read-only Slack guardrail | weekly-alignment |
| Synthesized state in Claude context, archive stays out | cortex's 20-file cap, memory-librarian's read-only design |
| End-of-day / end-of-week reflection rituals | claude-cortex `/end-day`, `/end-week` |
| Configurable per-user (no hardcoded firm assumptions) | post-refactor: every plugin via `<config-root>/plugins/<plugin>.user-context.md` |

### What's missing — the five gaps

1. **Entity wiki pages** — per-person, per-company, per-topic, with fixed schemas. Cortex has project-state nodes (`client:acme`) but not relationship/entity nodes (`person:sarah-chen`, `company:acme-corp`, `topic:ai-governance`).
2. **Interactive daily brief** — a single markdown document the user comments on inline, with a `/process-brief` companion that executes the user's annotations.
3. **`/end-day` orchestration chain** — pieces exist; they need to chain deterministically into one ritual.
4. **Two-stage triage for memory commits** — cheap classifier first ("commit-worthy? which nodes?"), expensive synthesis second.
5. **Nightly `/listen` archive pipeline** — automated daily pulls from calendar, email metadata, Slack, transcripts into an immutable archive that synthesis runs against (but that never enters Claude's runtime context).

---

## Part 2 — Cross-cutting concerns (read before building any gap)

### 2.1 Claude Code compatibility

Every plugin must work in both Cowork and Claude Code. The current marketplace mostly does — except for one thing introduced in the recent refactor.

**Problem:** Step 0 in every plugin's setup command currently says `Call request_cowork_directory(<path>)` before reading or writing. This call doesn't exist in Claude Code (filesystem access is direct).

**Fix (low effort, do this first):** Rewrite Step 0's directory-access instructions to be platform-agnostic. Replace:

> "Call `request_cowork_directory(<path>)` to mount it."

with:

> "Ensure access to `<path>`. In Cowork, call `request_cowork_directory(<path>)` once if not already granted. In Claude Code, filesystem access is direct — no call needed."

Apply this across all 12 plugins' Step 0 blocks. Single perl pass; 5 minutes of work.

### 2.2 Config root convention (already established by the v0.2 refactor)

- Pointer file: `~/Documents/.claude-plugin-config-root` (single-line text, contains absolute path of user-chosen config root)
- Layout:
  ```
  <config-root>/
  ├── identity.md           (cortex /setup-identity)
  ├── voice.md              (cortex /setup-voice)
  ├── memory/               (cortex working memory — unchanged location, pinned)
  │   ├── DASHBOARD.md
  │   ├── user.md
  │   ├── client/*.md
  │   ├── person/*.md       ← NEW (Gap 1)
  │   ├── company/*.md      ← NEW (Gap 1)
  │   └── topic/*.md        ← NEW (Gap 1)
  ├── plugins/              (per-plugin user-context files)
  │   ├── core-ops.user-context.md
  │   ├── lead-engine.user-context.md
  │   ├── ...
  ├── archive/              (raw daily archive — NEW, Gap 5)
  │   └── YYYY-MM-DD/
  │       ├── calendar.md
  │       ├── inbox.md
  │       ├── slack.md
  │       └── transcripts.md
  ├── daily-briefs/         (interactive daily working document — NEW, Gap 2)
  │   └── YYYY-MM-DD.md
  └── time-log.csv          (time-tracking plugin)
  ```

### 2.3 Cost discipline

All five gaps must respect Omar's cost rules:

- **Synthesized state lives in Claude's context. Raw archive does not.** Agents read from synthesized entity pages, never from archive directly.
- **Triage cheap, synthesize expensive.** Haiku-class for routing/classification; Sonnet (or Opus where genuinely needed) for synthesis and drafting.
- **Hard caps on agent file-reads.** Memory-librarian already has 20-file cap; preserve this discipline as entity pages proliferate.

### 2.4 Backward compatibility

- Existing cortex project nodes (`client/`, `bizdev/`, `strategy/`) keep working unchanged.
- New entity directories (`person/`, `company/`, `topic/`) are added alongside, not in place of.
- No automatic migration of existing project nodes into entity pages. Graduation rule applies to NEW mentions going forward.
- If a user is running v0.2.x and never installs the second-brain extension, nothing breaks.

### 2.5 Privacy

- `<config-root>/archive/` contains potentially sensitive content: email subjects/snippets, transcript bodies, Slack message text. Recommend gitignored. Optional encryption-at-rest is out of scope for v1.
- Entity pages may contain personal/relationship info about contacts. Same guidance as cortex memory today: treat as confidential, back up like financial records.

---

## Part 3 — Gap 1: Entity wiki pages in cortex

### 3.1 Motivation

Cortex today has **project-state** nodes:
- `client:acme-corp.md` → engagement status, decisions, knowledge entries, threads
- `bizdev:partnerships.md` → bizdev pipeline state
- `strategy:q2-growth.md` → strategic project state

What's missing: **entity** nodes that aggregate relationship and topic knowledge across projects. Sarah Chen mentioned in three client engagements lives across three separate nodes. There's no canonical "what do I know about Sarah Chen?" page.

Omar's insight: every person, company, topic gets a wiki page with a fixed schema. Pages link to each other. Retrieval becomes one read instead of many. Knowledge compounds because each new mention REWRITES the relevant page, not appends to a log somewhere.

### 3.2 Architecture

**New directories under `<config-root>/memory/`:**

```
memory/
├── person/                 ← NEW
│   ├── sarah-chen.md
│   ├── tom-reyes.md
│   └── ...
├── company/                ← NEW
│   ├── acme-corp.md
│   └── ...
├── topic/                  ← NEW
│   ├── ai-governance.md
│   ├── pricing-strategy.md
│   └── ...
└── [existing: client/, bizdev/, strategy/, archive/, DASHBOARD.md, user.md]
```

**Page schemas** (cortex CLAUDE.md must document and enforce these):

**Person page (`person/firstname-lastname.md`):**
```markdown
# person:firstname-lastname

> Last updated: YYYY-MM-DD

## Identity
- **Full name:** ...
- **Title / role:** ...
- **Company:** [link to company/...]
- **Email:** ...
- **LinkedIn / other:** ...
- **First mentioned:** YYYY-MM-DD (which conversation/source)

## Relationship
- **How we know each other:** ... (intro source, shared event, prior client, etc.)
- **Relationship temperature:** [Cold | Warm | Active | Dormant]
- **Last meaningful contact:** YYYY-MM-DD ([type: email / meeting / DM])
- **Relationship owner:** [you, or someone else]

## Recent interactions (last 90 days)
- YYYY-MM-DD — [event/meeting/email] — one-line summary

## Open threads
- [WAITING:them] — promised to do X by [date]
- [WAITING:you] — owe them Y
- [P0] — decision pending on Z

## Notes
- [Anything not in the above sections — context, observations, preferences]

## Linked entities
- Topics: [topic/ai-governance], [topic/...]
- Companies: [company/acme-corp]
- Projects: [client/acme-corp]
```

**Company page (`company/company-name.md`):**
```markdown
# company:company-name

> Last updated: YYYY-MM-DD

## About
- **Industry:** ...
- **Size:** ...
- **Stage:** ...
- **Website:** ...
- **Headquartered:** ...

## Relationship
- **Status:** [Prospect | Active client | Past client | Connector firm | Not a fit]
- **First contact:** YYYY-MM-DD
- **Most recent activity:** YYYY-MM-DD

## Key people
- [person/sarah-chen] — VP, primary contact
- [person/tom-reyes] — PM
- ...

## Recent activity (last 90 days)
- YYYY-MM-DD — event — summary

## Open threads
- [...]

## Notes
- [...]

## Linked entities
- Projects: [client/...]
- Topics: [topic/...]
```

**Topic page (`topic/topic-slug.md`):**
```markdown
# topic:topic-slug

> Last updated: YYYY-MM-DD

## Definition
[1-3 sentence definition. What this topic IS, in your framing.]

## Current state
[Where things stand on this topic right now. The thing you'd say if someone asked "what's happening with X?"]

## History
- YYYY-MM-DD — [event/decision] — summary
- ...

## People involved
- [person/...] — role, perspective
- ...

## Decisions
- YYYY-MM-DD — [decision] — rationale, who was in the room
- ...

## Open questions
- [Q1]
- [Q2]
```

### 3.3 Graduation rules (when does an entity become a page?)

A name or topic auto-graduates to its own page when **any of the following** triggers:

- **Person**: mentioned by name in 2+ conversations across any project node, OR captured by name in 1+ meeting transcript, OR explicitly tagged with `[ENTITY:person]` in a session commit, OR returned by `contact-researcher` as a researched contact
- **Company**: mentioned in 2+ conversations OR is the company of any graduated person OR explicitly tagged `[ENTITY:company]` OR appears in time-log.csv with a billing model
- **Topic**: explicitly tagged `[ENTITY:topic]`, OR mentioned with `Topic:` prefix in /remember, OR Omar's hand-curated approach — don't auto-graduate topics (they're judgment calls)

**Person and company are auto-graduating; topics are manual.**

When an entity graduates, cortex:
1. Creates `<entity-dir>/<slug>.md` from the entity-page template
2. Populates the template using context from existing mentions (cross-reference all project nodes for prior context)
3. Adds the entity to `DASHBOARD.md`'s Entities section
4. Backfills cross-links: any existing project node that mentions this person/company gets a "Linked: [person/...]" annotation in its "People" section

### 3.4 Plugins affected

| Plugin | Change |
|---|---|
| **claude-cortex** | Add entity-page schemas to CLAUDE.md. Update `/remember` to graduate entities on commit. Update `/recall` to recognize `person:`, `company:`, `topic:` query prefixes. Update `memory-librarian` agent to search entity pages first when query type is entity-style. Add `entity-graduation` skill that runs at commit time. |
| **lead-engine** | `contact-researcher` agent: when it produces a dossier, ALSO write/update the `person/<slug>.md` page if cortex is installed. The dossier IS the person page when first created; subsequent runs UPDATE the page rather than re-synthesize from scratch (cost saving). |
| **bizdev-outreach** | Skill body: after drafting outreach for a contact, append a Recent interaction entry to that contact's person page (if cortex installed). |
| **weekly-outreach** | After /weekly-outreach generates the queue, update Recent interactions on each queued contact's person page. |
| **client-status** | When generating status drafts, ALSO update the company page's Recent activity section. |
| **referral-engine** | When `/referral-ask` is sent, log a Recent interaction on the connector's person page. |
| **project-setup** | When initializing a new client, ALSO create the company page (if not already graduated) and a person page for the primary contact. |

### 3.5 Implementation steps

1. **Cortex CLAUDE.md update** — document the entity-page schemas, graduation rules, query syntax (`person:slug`, `company:slug`, `topic:slug`).
2. **Cortex /remember update** — at the end of commit logic, scan extracted entities. Apply graduation rules. Create or update entity pages.
3. **Cortex /recall update** — when query starts with `person:` / `company:` / `topic:`, read that single file directly (fast path). Otherwise existing behavior.
4. **Memory-librarian update** — when query mentions a person/company/topic name, check for an entity page first; if exists, return that as Source #1 with full citation. Otherwise fall through to general search.
5. **Cross-plugin writes** — update each downstream plugin's main skill body to write to entity pages where appropriate. Each write should be additive (append to Recent interactions, etc.) — never destructive of existing entity-page content.
6. **DASHBOARD.md update** — add an Entities section that lists all graduated entities with their last-updated dates, sorted by recency.

### 3.6 Acceptance criteria

- After installing the extension and using the marketplace for 2 weeks, the user has 10+ person pages, 3+ company pages, and 2+ topic pages auto-created.
- Querying `/recall person:sarah-chen` returns the page in <500ms (single file read).
- Memory-librarian, asked "what do we know about Sarah Chen?", reads the person page first and synthesizes from there, not from scratch.
- Contact-researcher's second run on the same person is ~30% faster (because it updates instead of synthesizing fresh).
- DASHBOARD.md has a populated Entities section.

### 3.7 Open questions

- Should topics graduate manually or via a 3+-mention rule? Recommend manual to avoid topic-page sprawl. Revisit after 2 weeks of usage.
- How to handle name disambiguation (two "Sarah Chen"s)? Suggestion: include company in slug — `sarah-chen-acme-corp.md`. Document the convention.
- Pre-existing project nodes (`client/acme-corp.md`) — keep them, or fold into `company/acme-corp.md`? Recommend KEEP both: `client:` is project-state, `company:` is relationship-state. Different purposes.

---

## Part 4 — Gap 2: Interactive daily brief (`/brief` + `/process-brief`)

### 4.1 Motivation

Omar's morning brief is the missing "interactive day driver" in the BrightWayAI stack. Today:

- `/plan-tomorrow` creates calendar blocks (good)
- `/end-day` captures reflection (good)
- But there's no single document the user opens in the morning, comments on, and has Claude execute against.

Omar's flow: read brief over coffee → annotate inline (`draft the reply`, `move to tomorrow`, `ask about the COO conversation`) → Claude executes within minutes. The brief becomes a working surface, not a read-only dashboard.

### 4.2 Architecture

**New plugin: `daily-brief`** (new GitHub repo: `BrightWayAI/daily-brief`)

**Files in plugin:**
```
.claude-plugin/plugin.json
commands/
  brief.md              ← /brief — generate today's brief
  process-brief.md      ← /process-brief — read inline annotations, execute
  setup-brief.md        ← /setup-brief — configure delivery time, sections, etc.
skills/
  brief/SKILL.md
  process-brief/SKILL.md
  setup/SKILL.md
references/
  user-context.template.md
  brief-template.md     ← markdown template for the brief itself
```

**Brief file location:** `<config-root>/daily-briefs/YYYY-MM-DD.md` (one per day, retained)

**Brief structure (template):**
```markdown
# Daily Brief — Monday, May 12, 2026

_Generated: 2026-05-12 07:45 (America/New_York)_
_Annotation format: leave comments after `[action]:` markers. Run /process-brief when done._

---

## 1. Today's meetings (3)

### 10:00am — Acme Corp kickoff (60 min)
**Attendees:** [person/sarah-chen] (VP), [person/tom-reyes] (PM)
**Context:** Phase 1 kickoff per SOW. Stakeholder interviews scheduled for weeks 2-3.
**Prior thread:** Sarah replied warmly last Friday confirming attendees. Tom hasn't responded but will be there per Sarah.
**Suggested talking points:**
- Confirm scope per SOW (AI Op Model 6-week engagement)
- Walk through stakeholder interview plan
- Establish weekly cadence
**Open commitments:** [WAITING:you] send the kickoff agenda 24h before

**[action]:** _← leave annotation here. Examples: "draft the agenda email", "skip prep", "add talking point on data governance"_

### 1:00pm — ...

---

## 2. Inbox action items (5)

### Inbound: Beta Inc — proposal feedback request
**From:** [person/jane-doe] @ [company/beta-inc]
**Subject:** "Quick clarification on Phase 2 scope"
**Snippet:** "Could you confirm whether the Phase 2 production batch is included in the original SOW or a separate engagement..."
**Suggested response:** Confirm Phase 2 is in the SOW with the volume cap; note Phase 3 (scaling beyond cap) would be separate.

**[action]:** _← examples: "draft reply", "draft reply but ask if they want the call instead", "I'll handle this manually"_

### ...

---

## 3. Today's priority tasks (from CRM + memory)

- [P0] Send the kickoff prep email to [person/sarah-chen] (due today, per project-setup phase 1)
- [P1] Follow up with [person/marcus-bell] @ [company/gamma-co] — 45 days since last touch
- [P2] Review the deliverable draft for client:beta-inc

**[action]:** _← edit any of these. Examples: "move P1 to tomorrow", "ask Marcus about Q3 budget timing"_

---

## 4. Outreach (from weekly queue, if installed)

3 contacts due today per weekly-outreach. See [<config-root>/plugins/weekly-outreach.user-context.md] for full queue.

**[action]:** _← "draft all 3", "skip outreach today", "draft just #1"_

---

## 5. Drafted replies awaiting your approval

(Generated when /process-brief runs the actions above. Empty on first generation.)

---

## 6. Yesterday's reflection (from /end-day)

- Biggest thing done: ...
- Blocked on: ...
- One thing to move today: ... ← carried into Today's priority tasks above

---

## 7. End-of-day prompt (fill in at /end-day)

- Biggest thing done today: _____
- What blocked you: _____
- One thing to move tomorrow: _____
```

### 4.3 The two-command pattern

**`/brief`** (or auto-fires at user's configured morning time):
1. Reads `<config-root>/identity.md`, `voice.md`, all relevant plugin user-context files.
2. Pulls today's calendar (via calendar connector). For each external meeting, looks up attendee person pages from cortex memory.
3. Pulls today's inbox action items (Gmail, last 24h, unread or flagged).
4. Pulls today's priority tasks from CRM (delegates to `pipeline-analyst` if installed).
5. Pulls today's outreach queue if `weekly-outreach` is installed.
6. Reads yesterday's `daily-briefs/<yesterday>.md` for the end-of-day reflection section.
7. Renders the brief at `<config-root>/daily-briefs/<today>.md` using the template.
8. Notifies user: "Brief ready at `<config-root>/daily-briefs/<today>.md`. Open it, annotate `[action]:` blocks, then run `/process-brief`."

**`/process-brief`** (user runs after annotating):
1. Reads `<config-root>/daily-briefs/<today>.md`.
2. Parses each `[action]:` block. Extracts the user's instruction.
3. For each annotation, dispatches:
   - `"draft reply"` → delegate to `bizdev-outreach` (or inline drafting if not installed). Queue draft in Gmail.
   - `"draft the agenda email"` → draft per project-setup template, queue in Gmail.
   - `"move P1 to tomorrow"` → update CRM task due date.
   - `"add talking point on data governance"` → append to meeting prep section in the brief itself.
   - Free-form action → ask user "what do you want me to do exactly?" if unclear.
4. Updates section 5 (Drafted replies awaiting your approval) with full drafts ready to copy.
5. Reports back: "Processed [N] annotations. [M] drafts in Gmail awaiting your review. [K] tasks updated. See section 5 of today's brief for details."

### 4.4 Setup interview

`/setup-brief` captures:
- Preferred brief generation time (default 7:30am, user's TZ from identity)
- Which sections to include (defaults: all 7)
- Whether to auto-generate or wait for `/brief` invocation (default: scheduled via `register-schedules`)
- Whether section 4 (Outreach) appears if no weekly queue exists (default: hide)
- Annotation marker (default `[action]:`; could be `> ACTION:` for users who prefer blockquote style)

### 4.5 Plugins affected

- **New:** `daily-brief` plugin
- **claude-cortex:** add convention for `<config-root>/daily-briefs/` to memory layout doc
- **plan-tomorrow:** add note that calendar blocks can be triggered via `/process-brief` actions (e.g., annotation "block 90 min for the proposal draft" → plan-tomorrow creates the block)
- **core-ops/register-schedules:** add a default schedule for `/brief` (weekday 7:30am)

### 4.6 Acceptance criteria

- User runs `/brief` Monday morning → opens today's file in their editor → annotates 3-4 `[action]:` blocks → runs `/process-brief` → drafts appear in Gmail within 2 minutes, tasks update in CRM, brief's section 5 shows all drafts ready.
- Scheduled generation works: brief appears at 7:30am without manual invocation.
- Yesterday's reflection (filled in by `/end-day`) appears in today's section 6.
- Section 7 (end-of-day prompt) is what `/end-day` fills in at 5pm — closing the loop.

### 4.7 Open questions

- File format alternatives — should the brief be JSON for easier parsing? **No.** Markdown is the point — the user reads and edits in a normal editor. Parsing `[action]:` blocks from markdown is straightforward.
- What if the user doesn't annotate? `/process-brief` just reports "no actions found" and does nothing. Idempotent.
- Multi-day brief retention — keep all briefs indefinitely (markdown is small, history is valuable) or archive after N days? Recommend: keep indefinitely. Add a `/brief-archive` skill later if it becomes a problem.

---

## Part 5 — Gap 3: `/end-day` orchestration chain

### 5.1 Motivation

Today's `/end-day` does each step *optionally*. Omar's 7pm wrap does them deterministically as one ritual:

1. Process today's transcripts → surface uncaptured commitments
2. Update wiki pages (entity + project nodes)
3. Prepare tomorrow's brief

These three actions exist in the marketplace but aren't chained. The user has to invoke each separately. Friction kills the ritual.

### 5.2 Architecture

Rewrite `cortex/commands/end-day.md` to deterministically chain (with user gates between):

1. **`/listen` for today's archive** (Gap 5; if `listen` skill is available, run it; otherwise skip)
2. **transcript-reviewer agent** → uncaptured commitments table. User picks which to convert to CRM tasks.
3. **Cortex auto-commit with two-stage triage** (Gap 4): Haiku triage → Sonnet synthesis. Updates project nodes AND entity pages (Gap 1).
4. **Reflective prompts** (existing in `/end-day`): biggest win, biggest miss, tomorrow's one thing.
5. **`/brief` generation for tomorrow** (Gap 2): with yesterday's reflection (section 6) prepopulated, tomorrow's calendar pulled, tasks loaded.
6. **`/plan-tomorrow` calendar pre-stage** (optional, existing): user confirms calendar blocks before bed.

### 5.3 User gates

Between steps, the user is asked one decision:
- After step 2: "Convert [N] uncaptured commitments to CRM tasks?" (Y/N per item)
- After step 5: "Brief generated for tomorrow at `<config-root>/daily-briefs/<tomorrow>.md`. Want to review it now or wait until morning?"

Default if no user response: skip to next step. Don't block the ritual.

### 5.4 Plugins affected

- **claude-cortex:** rewrite `/end-day` body
- **daily-brief plugin** (Gap 2): provide a `pre-stage` invocation that generates tomorrow's brief with optional yesterday-reflection-injection

### 5.5 Acceptance criteria

- User runs `/end-day` at 5pm. Within 10-15 minutes: transcripts reviewed, memory updated (entity + project), tomorrow's brief generated, optional calendar blocks staged. User closes laptop. Next morning the brief is waiting.
- If `/listen` isn't installed (Gap 5 not built yet), `/end-day` skips step 1 silently.

### 5.6 Open questions

- Should `/end-day` be scheduled (e.g., 5pm weekday auto-invoke) or user-triggered? Recommend: user-triggered, but the schedule library (`core-ops/references/schedules.md`) includes a daily reminder at 5pm.

---

## Part 6 — Gap 4: Two-stage triage for memory commits

### 6.1 Motivation

Cortex's `/remember` and auto-commit currently process every conversation at the same tier. Cheap when conversations are trivial; expensive when substantive — but with no early-exit for "nothing here worth committing." Over time this wastes tokens.

Omar's approach: cheap Haiku triage → expensive synthesis only for affected nodes.

### 6.2 Architecture

**Step 0 of `/remember` and auto-commit (NEW):**

Cheap-tier call (Haiku):

> "Read the last N exchanges of this conversation. Decide:
> 1. Is this commit-worthy? (Did any decisions get made? Knowledge shared? Corrections given? Entities mentioned?)
> 2. If yes, which nodes are affected? Return as JSON: `{commit: true, nodes: ['client:acme', 'person:sarah-chen', 'topic:ai-governance']}`. If no, return `{commit: false, reason: 'trivial conversation'}`.
> 3. Only list nodes that need updating. Don't over-attribute."

**Step 1+ (existing, but scoped):**

If `commit: false` → return silently. Don't bother the user.

If `commit: true` → run synthesis only on listed nodes. Pass the node list to the Sonnet-tier call so the model focuses on those specific files rather than scanning the whole memory.

### 6.3 Plugins affected

- **claude-cortex:** edit `commands/remember.md` and `commands/observe.md` (the auto-commit skill body)

### 6.4 Acceptance criteria

- Trivial conversations (greetings, simple Q&A) produce `commit: false` and no synthesis runs.
- Substantive conversations produce a targeted node list. Token usage on synthesis drops 30-50% on average (because the model doesn't scan unrelated nodes).
- Quality of commits doesn't degrade — entity pages and project nodes still get the right updates.

### 6.5 Open questions

- Which exact model for triage? Recommend Haiku for cost. Sonnet is fine if cost isn't a constraint; both work.
- Should the user see the triage decision (e.g., a one-line confirmation "Committed to nodes: X, Y, Z. Skipped Q (trivial).")? Recommend: silent by default; surface only on `--verbose` flag or when explicitly invoked via `/remember`.

---

## Part 7 — Gap 5: `/listen` nightly archive pipeline

### 7.1 Motivation

Omar's "Listen" runs nightly. Eight sources → immutable archive folder. This becomes the raw material that synthesis (the "Organise" pass) runs against. The archive itself never enters Claude's context — only synthesized state does.

The marketplace today has `transcript-reviewer` (cortex) which is one source, and it runs manually/weekly. Nothing pulls calendar, email metadata, or Slack proactively.

### 7.2 Architecture

**New skill in cortex (or new small plugin `archive-listener`):**

`/listen` runs scheduled (default 11pm weekday) and pulls today's:

- **Calendar events** — titles, attendees, durations. No descriptions (privacy default; opt-in to include).
- **Email metadata** — sender, recipient(s), subject, snippet (first 200 chars). No full bodies unless flagged.
- **Slack threads** from monitored channels (per weekly-alignment's channel list, or a separate listen-channels config). Read-only.
- **Granola/Fireflies transcripts** from today's meetings.

Writes to `<config-root>/archive/YYYY-MM-DD/`:

```
archive/2026-05-12/
├── calendar.md       (today's events, structured)
├── inbox.md          (today's email metadata)
├── slack.md          (today's monitored channel activity)
└── transcripts.md    (today's meeting transcripts, concatenated)
```

**Immutable.** Once written, never modified. Archive becomes the audit trail.

### 7.3 How the archive is used

- **Cortex auto-commit + entity-page updates (Gap 1)**: at end-of-day, read today's archive → triage what's commit-worthy → synthesize updates to project + entity pages.
- **`/brief` (Gap 2)**: NOT directly. The brief reads from synthesized entity pages, not archive. Archive is the raw material; synthesis is the surface.
- **Audit/review**: user can manually browse `<config-root>/archive/<date>/` if they want to retro-verify what happened on a day.

### 7.4 Privacy and storage

- Archive is gitignored by default in any user fork of the marketplace.
- Recommend `.gitignore` patterns for `<config-root>/archive/` and `<config-root>/daily-briefs/`.
- Consider optional encryption-at-rest for users who want it (out of scope for v1; users can use FileVault / disk-level encryption).
- Configurable retention: keep last 90 days by default; offer a `/archive-prune` skill that compresses or deletes older.

### 7.5 Plugins affected

- **claude-cortex:** add `/listen` skill OR
- **New plugin:** `archive-listener` (cleaner separation; cortex doesn't need to grow further)
- **core-ops/register-schedules:** add default schedule (weekday 11pm)
- **end-day chain (Gap 3):** if `/listen` is available, run it as step 1

### 7.6 Acceptance criteria

- `/listen` invoked manually pulls a complete archive folder for today. Files are sorted, structured, readable.
- Scheduled at 11pm, runs without user invocation.
- Archive folders never modify after creation (append-only at the day level, but each day-file is written once).
- `/end-day` chain (Gap 3) successfully reads today's archive when synthesizing.

### 7.7 Open questions

- Connector load — pulling 8 sources daily is significant API usage. Recommend: start with just calendar + transcripts (lightest); add inbox + slack later when proven useful.
- Slack history depth — read just today's messages or include thread context from prior days for active threads? Recommend: today's messages only; let the synthesis pass pull thread context from existing project nodes when needed.
- Multi-day archive aggregation — should there be a `<config-root>/archive/INDEX.md` that lists all archive folders with summaries? Useful for navigation. Build as a Gap-5b after the core pipeline is working.

---

## Part 8 — Implementation order and effort estimates

Rough sizing assuming Claude Code with the existing plugin source already cloned locally:

| Order | Gap | Effort | Why first/last |
|---|---|---|---|
| 0 | Step 0 Claude-Code-compatibility fix | ~30 min (5-min perl pass across 12 plugins + push) | Cheapest. Do this immediately. Unrelated to second-brain, but blocking. |
| 1 | Gap 1 — Entity wiki pages | 1-2 days | Highest retrieval-quality leverage. Foundation for Gap 2's contact-context section. |
| 2 | Gap 4 — Two-stage triage | ~half day | Quick cost win. Doesn't depend on Gap 1 but benefits from it (more node candidates to triage well). |
| 3 | Gap 2 — Daily brief | 1-2 days | Biggest behavioral change. Requires Gap 1 to populate contact context cleanly. |
| 4 | Gap 3 — `/end-day` orchestration | ~half day | Ties Gaps 1, 2, 4 together. Build after they exist. |
| 5 | Gap 5 — `/listen` archive | 1-2 days | Operationally nice; not blocking value of other gaps. Build last after validating user wants this depth of automation. |

**Total**: ~5-8 days of focused work to complete all five gaps. Could be split across 2-3 work sessions.

**Minimum viable second-brain**: Gap 1 (entity pages) + Gap 2 (daily brief) alone is ~80% of Omar's UX impact. Gaps 3-5 are quality-of-life and cost optimizations.

---

## Part 9 — What this spec doesn't address (and why)

1. **Memory location consolidation** — currently cortex memory pins to `~/Documents/Claude/memory/` regardless of config root choice. Could be moved to `<config-root>/memory/` for consistency. Tradeoff: breaks existing users' memory unless we run a migration. Decision: out of scope here. Tackle if a user explicitly complains about the split.

2. **Vector DB hybrid** — Omar argues against vector DBs. The spec follows his lead. If a future use case needs semantic search across many entity pages, an OPTIONAL vector index could be added (just as a search index, not as the source of truth). Don't build it preemptively.

3. **Obsidian integration** — Omar uses Obsidian as his viewer. The spec keeps markdown plain so any editor works. No reason to bake Obsidian-specific frontmatter unless a user requests it.

4. **Email-send automation** — Omar's `/process-brief` queues drafts in Gmail (not sends). The spec preserves this. NO automatic send. Always user-review.

5. **Mobile** — Omar's brief is read on phone (Obsidian sync). Markdown files in the config root sync via whatever the user uses (iCloud, Dropbox, etc.) — that's their concern.

6. **Sharing the brief with others** — a team-shared brief is a different system. This spec is single-user.

---

## Part 10 — Pre-flight checklist before starting

1. ✅ All 12 plugins at v0.2.1 / v4.1.1 / v1.4.1 with config-root refactor complete (already done as of 2026-05-11).
2. ✅ Marketplace at `BrightWayAI/claude-plugins` pushed and discoverable.
3. ⏳ Step 0 Claude Code compatibility fix (pre-cursor to this spec, but small).
4. ⏳ User has `~/Documents/.claude-plugin-config-root` populated and at least cortex's `/setup-identity` has run successfully.
5. ⏳ At least one of: HubSpot (or another CRM connector), Gmail, calendar connector available in the user's setup (otherwise the brief is thin and entity pages don't auto-populate).

---

## End of spec

When picking this up:

- Start with Gap 1. The entity-page schema is the foundation everything else builds on.
- Don't skip the cross-cutting concerns in Part 2 — Claude Code compatibility and config-root layout matter for every gap.
- Each gap section has its own Acceptance Criteria — use them as the test before moving to the next gap.
- Open questions in each gap are real decision points. Don't paper over them; decide explicitly and document in the relevant plugin's CHANGELOG.

Pair this brief with the existing `REFACTOR-BRIEF.md` in this directory — they're complementary. The refactor brief established the config-root convention; this brief builds the second-brain layer on top.

— End —
