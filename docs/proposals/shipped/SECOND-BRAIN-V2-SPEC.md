# Second-Brain v2 — Tech Spec for the BrightWayAI Plugin Marketplace

_Created: 2026-05-11_
_For: Zach Wagner / BrightWayAI marketplace_
_Supersedes: `second-brain-extension.md` (Claude Code's first pass)_
_Inspiration: Omar Ismail's second-brain setup — https://omarismail.com/projects/second-brain — adapted, not copied, for a solo-founder context_
_Status: Ready to execute. Scheduling configuration is deferred — Cowork scheduled tasks get wired up after the foundation lands._

---

## Part 1 — Why this spec replaces the earlier one

The first pass (`second-brain-extension.md`) is a faithful read of Omar Ismail's post but extrapolates in three ways that don't fit a solo-founder context:

1. **It puts entity pages before the daily brief.** The brief is Omar's single most valuable surface. It's the thing that converts memory into action. Shipping entity pages first delivers infrastructure no human is yet asking for. The brief should ship first against current cortex memory.

2. **It invents a Company page schema Omar doesn't have.** Omar uses Person + Topic only. The current cortex `client/` and `bizdev/` nodes already absorb company-level state. A third schema adds maintenance burden without proportional value.

3. **It defaults the annotation mechanism to plain-markdown `[action]:` markers.** Omar's annotation loop only works because Obsidian has native commenting. Plain markdown markers are a UX downgrade. Cowork artifacts provide a better-fit primitive (interactive HTML, persistent across sessions, mobile-readable in the Cowork app).

Other changes from the first pass:

- Graduation rule for people is usage-based, not mention-count
- Listen pipeline is narrowed to one source (inbox triage) for v1; the full 6-source nightly archive is deferred until volume justifies it
- Two cheap, high-value guardrails added (orphan detection, duplicate-topic surfacing) that Omar's post mentions and the first pass missed
- A real success metric named (90% of time in planning + review) borrowed from Omar
- The 5-day effort estimate replaced with a realistic 10-15 days including smoke testing

The first pass remains a useful reference for the gaps it enumerated. This spec is the build order.

### What stays from the first pass

- Step 0 Claude Code compatibility fix (Part 2.1 below — same fix, cleaner framing)
- Config-root convention from the v0.2 refactor (no change)
- Two-stage triage cost discipline (preserved, scoped to one phase)
- Append-additive-never-destructive writes from downstream plugins (preserved)
- Privacy posture (preserved)
- Pre-flight checklist as a discipline (preserved, updated)

---

## Part 2 — Cross-cutting concerns

### 2.1 Platform compatibility (Cowork and Claude Code)

Every plugin must work in both Cowork and Claude Code. Current marketplace plugins mostly do. Step 0 in each setup command currently says "Call `request_cowork_directory(<path>)`" which is Cowork-specific.

Rewrite the directory-access language to be platform-agnostic. Replace:

> "Call `request_cowork_directory(<path>)` to mount it."

With:

> "Ensure access to `<path>`. If running in Cowork and the folder isn't already mounted in this session, call `request_cowork_directory(<path>)`. If running in Claude Code or another environment with direct filesystem access, no mount call is needed — proceed to read or write the file."

Apply across all 12 plugins. Realistic effort: 30-60 min (every setup command AND every main skill that does directory reads — both need the audit, not just setups). Single perl pass plus one verification run per plugin.

### 2.2 Config-root convention (from v0.2 refactor, unchanged)

- Pointer file: `~/Documents/.claude-plugin-config-root` (single-line text, contains absolute path of user-chosen config root)
- Layout extending the existing structure:

```
<config-root>/
├── identity.md
├── voice.md
├── memory/
│   ├── DASHBOARD.md
│   ├── user.md
│   ├── client/*.md
│   ├── bizdev/*.md
│   ├── infra/*.md
│   ├── strategy/*.md
│   ├── person/*.md           ← NEW (Phase 3)
│   └── triage-log.md         ← NEW (Phase 4 — audit log for skipped commits)
├── plugins/
│   └── *.user-context.md
├── briefs/                   ← NEW (Phase 1 — daily brief markdown archive)
│   └── YYYY-MM-DD.md
└── time-log.csv
```

Note: NO `archive/` directory in v1. The full nightly Listen pipeline is deferred. The `briefs/` directory holds markdown snapshots of each day's brief for audit, not raw source archive.

### 2.3 The brief lives as a live Cowork artifact, not a static markdown file

This is the biggest architectural change from the first pass.

**Why an artifact:**
- Cowork artifacts persist across sessions (created via `mcp__cowork__create_artifact`, listed via `mcp__cowork__list_artifacts`)
- Re-render on open with fresh data from connectors (HubSpot, Gmail, Calendar, cortex memory)
- Interactive HTML: real input fields, real buttons, no parsing of markdown markers
- Mobile-readable through the Cowork app
- No editor dependency (no Obsidian, no Google Docs adapter, no plain-markdown compromise)

**Two-file pattern per day:**

| File | Purpose | Lifecycle |
|---|---|---|
| Cowork artifact titled "Today's Brief" | The live working surface — the thing the user opens, annotates, processes | Single artifact, updated daily by `/brief` |
| `<config-root>/briefs/YYYY-MM-DD.md` | Markdown snapshot of the day's brief content, written when the artifact is regenerated | Append-only audit trail; one file per day |

When the user runs `/brief` (or it's scheduled later), the skill:
1. Pulls today's data from connectors
2. Generates the markdown snapshot at `briefs/YYYY-MM-DD.md`
3. Calls `mcp__cowork__update_artifact` on the existing "Today's Brief" artifact with the new content (or `create_artifact` if first run)

Yesterday's markdown is preserved at `briefs/<yesterday>.md`. The artifact always shows "today."

### 2.4 Cost discipline

- Synthesized state lives in Claude's context. Raw source data does not enter context except during synthesis passes.
- Haiku-class for routing and classification (Phase 4 triage, inbox triage classification).
- Sonnet for synthesis and drafting.
- Hard caps on agent file reads. Memory-librarian's 20-file cap stays.

### 2.5 Backward compatibility

- Existing cortex project nodes (`client/`, `bizdev/`, `strategy/`, `infra/`) keep working unchanged.
- `person/` directory added alongside, not in place of.
- No automatic migration of existing project nodes. New person mentions going forward.
- If a user is running the marketplace today and never installs v2 capabilities, nothing breaks.

### 2.6 Privacy

- `<config-root>/briefs/` markdown archive contains email snippets and contact context. Recommend gitignored.
- Person pages may contain personal relationship info. Same treatment as cortex memory today.
- No email or message is sent without explicit user approval. All drafting plugins remain draft-only.

### 2.7 Naming note

"Second-brain" is Omar's term. For your marketplace branding, consider naming the extension after a BrightWay concept once the build is settled. Candidates: "compounding memory," "operator brain," "the loop." For this spec, "second-brain v2" is the working title.

---

## Part 3 — Phase 1: Daily Brief (live Cowork artifact)

### 3.1 Why this ships first

The brief is the surface that turns memory into action. Every other phase below either feeds the brief (Phase 2 inbox triage) or extends what the brief can do (Phase 3 person pages). Without the brief, the rest is plumbing with no faucet.

Build it against current cortex memory. Don't gate on entity pages. The brief works today with what cortex knows today.

### 3.2 New plugin: `daily-brief`

New GitHub repo: `BrightWayAI/daily-brief`

```
daily-brief/
├── .claude-plugin/plugin.json
├── commands/
│   ├── brief.md
│   ├── process-brief.md
│   └── setup-brief.md
├── skills/
│   ├── brief/SKILL.md
│   ├── process-brief/SKILL.md
│   └── setup/SKILL.md
└── references/
    ├── user-context.template.md
    └── brief-artifact-template.html
```

### 3.3 What `/brief` does

1. Reads `<config-root>/identity.md`, `voice.md`, and relevant `plugins/*.user-context.md` files.
2. Reads `<config-root>/memory/DASHBOARD.md` for active project context.
3. Pulls today's calendar via the connected calendar MCP. For each external meeting, cross-references attendees against existing cortex nodes for context.
4. Pulls inbox action items via the inbox-triage skill (Phase 2) if installed. If not, falls back to "Gmail threads with messages received in last 24h where you're the recipient and haven't replied."
5. Pulls today's priority tasks from CRM via HubSpot MCP, filtered by owner and due-today / overdue.
6. Pulls today's outreach queue if `weekly-outreach` is installed.
7. Reads yesterday's `briefs/<yesterday>.md` for the previous end-of-day reflection.
8. Writes today's markdown snapshot to `<config-root>/briefs/YYYY-MM-DD.md`.
9. Creates or updates the Cowork artifact titled "Today's Brief" with the rendered HTML.
10. Notifies user: "Brief ready. Open 'Today's Brief' artifact, annotate sections, then run /process-brief when done."

### 3.4 Brief artifact structure

The artifact is HTML, not markdown. Each section is a card with a fixed shape. Each card has a text input for annotations.

Sections (in order):

| Section | Source | Annotation type |
|---|---|---|
| 1. Today's meetings | Calendar + cortex contact context | One annotation field per meeting |
| 2. Inbox action items | Phase 2 inbox-triage (or fallback) | One annotation field per thread |
| 3. Today's priority tasks | HubSpot CRM (owner = you, due today/overdue) | One annotation field per task |
| 4. Outreach queue | weekly-outreach (if installed) | One annotation field for the group |
| 5. Drafted replies awaiting approval | Populated by /process-brief | Read-only display |
| 6. Yesterday's reflection | briefs/<yesterday>.md | Read-only display |
| 7. End-of-day prompts | Filled by /end-day | Three text inputs |

Each annotation field is a `<textarea>` with placeholder text showing example instructions. A single "Process all annotations" button at the bottom of the artifact calls `sendPrompt("Process the annotations in Today's Brief")` which triggers `/process-brief` in chat.

### 3.5 What `/process-brief` does

1. Reads the Cowork artifact's current state via `mcp__cowork__read_widget_context` (the artifact reports its annotation field values).
2. For each non-empty annotation:
   - "draft reply" → invoke `bizdev-outreach` skill to draft, save to Gmail drafts via Gmail MCP
   - "move to tomorrow" / "move to [date]" → update CRM task due date via HubSpot MCP
   - "add talking point: X" → append to the meeting's prep section in the markdown snapshot, regenerate artifact
   - "skip" / "I'll handle this" → log as dismissed in triage-log.md, no action
   - Free-form / ambiguous → ask user a follow-up clarification in chat before acting
3. After all annotations processed, update section 5 of the brief artifact with the list of drafts queued in Gmail.
4. Report to user: "Processed [N] annotations. [M] drafts in Gmail. [K] tasks updated. Section 5 of the brief shows details."

### 3.6 `/setup-brief` captures

- Annotation preview text (placeholders shown in each input)
- Which sections to enable (defaults: all 7)
- Default sort within each section (e.g., meetings by start time, tasks by priority then due date)
- Whether outreach section appears if no weekly-outreach queue exists (default: hide)

Identity, voice, and other shared context come from the config root automatically.

### 3.7 Acceptance criteria

- User runs `/brief` → an artifact titled "Today's Brief" appears in the Cowork artifacts list → user opens it → sees all 7 sections populated → annotates 3-4 inputs → clicks "Process all annotations" → `/process-brief` runs → drafts appear in Gmail within 2 minutes; CRM tasks update; brief's section 5 lists the queued drafts.
- The markdown snapshot at `briefs/YYYY-MM-DD.md` matches the artifact content.
- Re-running `/brief` on the same day updates the existing artifact (doesn't create duplicates).
- Yesterday's brief is preserved at `briefs/<yesterday>.md` even after today's brief regenerates.

### 3.8 Open questions

- Should the artifact support marking sections as "handled manually" (a checkbox per item that doesn't require an annotation)? Recommend: yes, simple checkbox-per-item that closes the loop without invoking Claude. Adds minor complexity, big UX win.
- Should the brief artifact persist permanently or rotate at end-of-day? Recommend: persist permanently. Each day's snapshot exists in `briefs/`; the artifact is "the live one." Simpler mental model.
- What happens if a user runs `/brief` twice in one day? Recommend: regenerate, but preserve any user annotations in fields that still apply (match by section + item ID). The artifact tool supports update; preserving annotation state across updates is a real engineering decision worth getting right in v1.

---

## Part 4 — Phase 2: Inbox triage skill

### 4.1 Why this ships second

The brief's section 2 ("Inbox action items") is its weakest content source without intelligent triage. Gmail's "unread or flagged" is noise. Most real action items live in threads where conversation already exists. A small focused skill solves this without building the full Listen pipeline.

### 4.2 New skill in cortex (or new tiny plugin `inbox-triage`)

Recommendation: new plugin `inbox-triage`. Keeps cortex focused on memory infrastructure.

```
inbox-triage/
├── .claude-plugin/plugin.json
├── commands/
│   └── triage-inbox.md
├── skills/
│   └── triage-inbox/SKILL.md
└── references/
    └── user-context.template.md
```

### 4.3 What `/triage-inbox` does

Pulls Gmail threads matching the following heuristic:

- Message received in the last 48 hours
- User is in the To or CC line
- One of:
  - Last message in thread is from someone other than the user
  - User's last message in the thread contains an open question or commitment to the other party
  - Thread is marked starred or important by Gmail

Uses Haiku-tier classification on subject + first 500 chars of each candidate to assign one of:

| Class | Definition |
|---|---|
| Needs-reply-today | Direct question, decision request, time-sensitive ask |
| Needs-reply-this-week | FYI requiring acknowledgment, less urgent question |
| Read-only | Update for awareness, no reply needed |
| Drop | Newsletter, automated notification, spam-adjacent |

Returns top 5-7 Needs-reply-today threads as the brief's section 2 content. Each item includes:

- Sender + their cortex context (if person page exists)
- Subject + snippet (first 200 chars)
- Suggested response framing in 1-2 sentences
- Annotation field for user instruction

### 4.4 Acceptance criteria

- `/triage-inbox` returns 3-7 prioritized threads (not 20). Quality filtered, not quantity.
- Classification accuracy spot-checked: of 20 random items classified Needs-reply-today over a week, at least 17 are genuinely things the user would have flagged manually.
- Token cost per run stays under ~$0.10 (Haiku, narrow context per item).

### 4.5 Open questions

- Should the triage learn from user dismissals? If user annotates "skip" on threads from a particular sender repeatedly, should the classifier learn to demote that sender? Recommend: out of scope for v1. Adds complexity. Revisit after 30 days of usage data.
- Slack triage as a sibling skill? Recommend: deferred. Slack is mostly handled by weekly-alignment today, and the inbox case is more universal.

---

## Part 5 — Phase 3: Person pages

### 5.1 Why this ships third

Once the brief is in daily use, the gap that surfaces fastest is "I need to remember who this person is in 5 seconds before this meeting." Cortex currently knows people only inside project nodes. A person mentioned across three clients lives across three nodes with no canonical view.

Person pages give the brief a clean place to pull contact context for section 1 (meetings) and section 2 (inbox). They also give `contact-researcher` a place to write dossiers that get reused.

### 5.2 New directory under cortex memory

```
memory/
└── person/
    ├── sarah-chen.md
    ├── tom-reyes.md
    └── ...
```

Only `person/`. No `company/`. No `topic/`. Existing `client/`, `bizdev/`, `infra/`, `strategy/` nodes continue to handle company and topic-level state.

### 5.3 Page schema (`person/firstname-lastname.md`)

```markdown
# person:firstname-lastname

> Last updated: YYYY-MM-DD

## Identity
- **Full name:** ...
- **Title / role:** ...
- **Company:** ... (free-text; link to cortex node if relevant, e.g., [client/acme-corp])
- **Email:** ...
- **LinkedIn / other:** ...
- **First mentioned:** YYYY-MM-DD (which conversation/source)

## Relationship
- **How we know each other:** ...
- **Relationship temperature:** [Cold | Warm | Active | Dormant]
- **Last meaningful contact:** YYYY-MM-DD ([type: email / meeting / DM])
- **Relationship owner:** [you, or someone else]

## Recent interactions (last 90 days, append-only)
- YYYY-MM-DD — [type] — one-line summary

## Open threads
- [WAITING:them] — ...
- [WAITING:you] — ...
- [P0] — ...

## Notes
- [Free-form context]

## Linked entities
- Projects: [client/...], [bizdev/...]
```

### 5.4 Graduation rule (usage-based, not mention-count)

A person becomes a page when ANY of:

1. `contact-researcher` produces a dossier on them (the dossier IS the initial page content)
2. `/recall person:X` is invoked 3+ times for them
3. `project-setup` names them as the primary contact for a new engagement
4. They appear in `time-log.csv` with a billing contact role
5. Explicit `[ENTITY:person]` tag in a `/remember` commit
6. They're the attendee of 3+ meetings on the calendar

Casual mentions in conversation stay in the relevant project node and DO NOT auto-create a person page. Mention-count alone is too noisy. Usage signals real interest.

### 5.5 Plugins affected

| Plugin | Change |
|---|---|
| cortex | Add `person/` directory schema to CLAUDE.md. Update `/remember` to detect graduation triggers and create pages. Update `/recall` to recognize `person:slug` query prefix. Update memory-librarian to check person pages first for person-shaped queries. Add per-recall counter to track graduation rule #2. |
| lead-engine | `contact-researcher` agent: when producing a dossier, write/update `person/<slug>.md` if cortex is installed. Subsequent runs UPDATE, don't re-synthesize. |
| bizdev-outreach | After drafting outreach, append one-line entry to the contact's Recent interactions section. |
| weekly-outreach | When generating the queue, update Recent interactions on each queued contact's page. |
| client-status | When generating status drafts, update Recent interactions for the primary contact. |
| referral-engine | When `/referral-ask` sends, log Recent interaction on the connector's page. |
| project-setup | When initializing a new client, create the primary contact's person page (if not yet graduated). |
| daily-brief | When pulling section 1 (meetings), read each attendee's person page if it exists. |

All cross-plugin writes are additive. Plugins append to Recent interactions; they never overwrite existing page content.

### 5.6 DASHBOARD.md change

Add an "Active people" section listing graduated person pages sorted by Last updated. Cap at top 10 to keep dashboard readable.

### 5.7 Acceptance criteria

- After 2 weeks of usage, person pages exist only for people the user actually interacted with deliberately (no flood of incidental mentions).
- `/recall person:sarah-chen` reads the single file and returns context.
- Memory-librarian, asked "what do we know about Sarah Chen," reads her person page first.
- `contact-researcher` second run on same person is faster (updates rather than synthesizes from scratch).
- DASHBOARD.md shows the Active people section populated.

### 5.8 Open questions

- Name disambiguation (two Sarah Chens): include company in slug — `sarah-chen-acme.md`. Document the convention in cortex CLAUDE.md. Auto-detect when two stubs would collide and prompt the user.
- Should person pages ever be "demoted"? If a person hasn't been touched in 12+ months, archive them. Recommend: out of scope for v1. Add a `/person-prune` skill later.

---

## Part 6 — Phase 4: Cheap-tier triage for memory commits

### 6.1 Why this ships fourth

The first three phases create more commit volume (the brief generates daily artifacts, person pages get updated, inbox triage runs). Without cost discipline, memory commits balloon. This phase preserves cortex's responsiveness and keeps subscription costs predictable.

### 6.2 Architecture

Add Step 0 to `/remember` and `/observe` in cortex.

**Step 0 — Haiku triage:**

> "Read the last N exchanges of this conversation. Decide:
> 1. Is this commit-worthy? Did decisions get made, knowledge shared, corrections given, or entities mentioned in a way that should update existing nodes?
> 2. If yes, list the nodes affected: `{commit: true, nodes: ['client:acme', 'person:sarah-chen']}`.
> 3. If no, return `{commit: false, reason: '...'}` (1-line reason).
> 4. Only list nodes that need updating. Don't over-attribute."

**Step 1 (existing, but scoped):**

- If `commit: false` → log to `<config-root>/memory/triage-log.md` and return silently
- If `commit: true` → run synthesis only on listed nodes, passing the node list to the Sonnet-tier call

### 6.3 Triage log format

Append-only log at `<config-root>/memory/triage-log.md`:

```markdown
# Triage Log

_Auto-appended by cortex's two-stage commit triage. Audit weekly._

## 2026-05-12 14:23
- Decision: skip
- Reason: greeting / scheduling check-in, no decisions or knowledge
- Conversation context: 4 turns about meeting time

## 2026-05-12 16:08
- Decision: commit
- Nodes: [client:cureate, person:kim-bryden]
- Reason: pricing discussion + scope change
```

The user reviews this weekly. If false-negatives accumulate (real decisions skipped), the triage prompt needs tuning. Cheap mitigation against the silent-loss failure mode.

### 6.4 Plugins affected

- cortex: edit `commands/remember.md` and the auto-commit logic in `skills/observe/SKILL.md`

### 6.5 Acceptance criteria

- Trivial conversations produce `commit: false`, log a line, run no synthesis
- Substantive conversations produce a targeted node list; synthesis runs only on those
- Average token usage on commits drops 30-50% measured over a week (Haiku triage replaces full-context synthesis on many conversations)
- Weekly review of triage-log shows <5% false-negative rate (subjective spot-check)

### 6.6 Open questions

- Surfacing triage decisions to the user: silent by default; expose via `/remember --verbose` or in a weekly summary.
- Triage model: Haiku for cost. Sonnet acceptable if cost isn't a constraint. Test both during phase build.

---

## Part 7 — Phase 5: `/end-day` orchestration

### 7.1 Why this ships fifth

By this point, the brief is in use, person pages are populating, inbox triage runs, and commit triage is in place. `/end-day` becomes the ritual that ties them together — read the day, capture commitments, update memory, pre-stage tomorrow.

### 7.2 Chain (with user gates)

Rewrite `cortex/commands/end-day.md`:

1. **Inbox triage for tomorrow:** call `/triage-inbox` to surface threads that need attention. Queue results into tomorrow's brief stub.
2. **Transcript-reviewer agent (existing):** surface uncaptured commitments from today's Granola transcripts. User gates: convert which to CRM tasks?
3. **Cortex auto-commit with Phase 4 triage:** classify the day's conversation history, synthesize updates to affected project nodes and person pages.
4. **Reflective prompts (existing):** biggest thing done today, what blocked you, one thing to move tomorrow.
5. **Pre-stage tomorrow's brief artifact:** call `/brief` to generate tomorrow's snapshot. Yesterday's reflection (just captured in step 4) populates section 6 of tomorrow's brief.

### 7.3 User gates

- After step 1: "Tomorrow's inbox triage shows [N] threads. Review now or wait until morning?"
- After step 2: "Convert [N] uncaptured commitments to CRM tasks?" (Y/N per item)
- After step 5: "Tomorrow's brief is staged. Want to review it now or wait until morning?"

Default to "wait" if no response. Don't block the ritual.

### 7.4 Plugins affected

- cortex: rewrite `commands/end-day.md`
- daily-brief: expose a `pre-stage` invocation that generates tomorrow's brief with optional reflection-injection from cortex

### 7.5 Acceptance criteria

- User runs `/end-day` at 5pm. Within 10-15 min: inbox triaged for tomorrow, today's transcripts reviewed, memory updated, tomorrow's brief staged. Next morning the brief is waiting.
- If any phase isn't installed (e.g., `/triage-inbox` not built yet), the chain skips that step silently and continues.

---

## Part 8 — Phase 6: Guardrails

### 8.1 Why this ships sixth

Two cheap, high-value guardrails from Omar's actual post that the first-pass spec missed. Both run inside cortex. Both prevent the system from quietly drifting into noise.

### 8.2 Orphan detection

At end-of-week (or run on demand via `/cortex-cleanup`), scan all memory nodes for files with:
- No incoming links from other nodes
- No outgoing links to other nodes
- Last updated > 30 days ago

Flag these as "isolated" in DASHBOARD.md's existing maintenance section. User reviews weekly and decides: archive (move to `archive/`), merge into another node, or annotate as intentionally standalone.

This catches notes that drift off the map. Cheap to implement, easy to maintain.

### 8.3 Duplicate-topic surfacing

When `/recall` is invoked on a topic-shaped query, first scan existing nodes for similar topics (using Haiku-tier semantic match on node summaries, not vector search). If a similar node exists, surface it:

> "Note: `infra/content-writing.md` may cover this. Read that first?"

Prevents the user from re-discovering ideas they already wrote about months ago. The Haiku scan keeps cost low.

### 8.4 Plugins affected

- cortex: add to existing `skills/cleanup/SKILL.md` (orphan detection) and `skills/recall/SKILL.md` (duplicate-topic check)

### 8.5 Acceptance criteria

- Orphan detection runs weekly via `/cortex-cleanup`, returns 0-5 candidates with suggested actions
- Duplicate-topic surfacing fires on `/recall` queries that overlap with existing nodes, ~80% precision
- Both guardrails cost <$0.05 per invocation in Haiku tokens

---

## Part 9 — Deferred (with rationale)

These were in the first-pass spec but are deliberately deferred from v1.

### 9.1 Full nightly Listen pipeline (6 sources)

Omar pulls Granola, Fireflies, Gmail, Slack, WhatsApp, and Calendar nightly into an immutable archive. At his volume (15-25 meetings/week) the automation pays back. At your volume (5-10 client engagements, fewer meetings) the inbox-triage skill (Phase 2) captures the highest-value source. Granola already files transcripts. Slack is read-only via weekly-alignment. The remaining sources don't have proven ROI yet.

Build only if Phase 1-6 are in daily use and the gap becomes felt.

### 9.2 Company pages

Existing `client/<name>.md` and `bizdev/<name>.md` nodes already handle company-level state for engaged companies. A separate `company/` directory duplicates this. If the gap surfaces (a company appears across multiple clients/bizdev nodes and needs a unified view), add then.

### 9.3 Topic pages

Existing `infra/<topic>.md` and `strategy/<topic>.md` nodes handle cross-cutting topics. A separate `topic/` directory duplicates. Same logic: add if a real gap surfaces.

### 9.4 Obsidian integration

The Cowork artifact replaces the need for Obsidian as the brief surface. Markdown files in `<config-root>/` are still readable in any markdown editor, but no Obsidian-specific frontmatter or sync is built in.

### 9.5 Email-send automation

Stays explicitly out of scope. Every email is drafted to Gmail drafts. User reviews and sends manually. This is non-negotiable per Omar's hard rule and your own existing posture across drafting plugins.

### 9.6 Scheduled task wiring

The spec describes triggering points (morning brief, end-of-day) but does not configure Cowork's scheduled-task system. User wires schedules once the foundation is in place, using Cowork's `mcp__scheduled-tasks__create_scheduled_task` tool (which `core-ops/register-schedules` already abstracts).

Default schedule recommendations (configure later):
- Weekday 7:30am: run `/brief`
- Weekday 5:00pm: run `/end-day`
- Weekday 11:00pm: (deferred — `/listen` not yet built)
- Sunday 6:00pm: run `/cortex-cleanup` for orphan detection

---

## Part 10 — Implementation order, effort, success criteria

### 10.1 Build order

| Phase | Component | Realistic effort | Why this order |
|---|---|---|---|
| 0 | Step 0 Claude Code compatibility fix | 30-60 min | Cheap, unblocks every other phase, no design risk |
| 1 | Daily Brief plugin (artifact + markdown snapshot) | 3-4 days | Highest behavioral leverage; the surface that turns memory into action |
| 2 | Inbox-triage plugin | 1-2 days | Quality boost for Brief section 2; narrow scope |
| 3 | Person pages in cortex + cross-plugin writes | 2-3 days | Foundation for richer Brief content; touches many plugins |
| 4 | Two-stage triage for cortex commits | 1 day | Cost discipline as commit volume grows |
| 5 | `/end-day` orchestration chain | 1 day | Ties Phases 1-4 together |
| 6 | Orphan + duplicate-topic guardrails | 1 day | Cheap quality additions |

**Realistic total: 10-15 days of focused work** including smoke testing across affected plugins. Could be split across 3-4 sessions of 3-4 days each.

The first-pass estimate of 5-8 days assumed clean compilation and no integration debugging. Plan for the longer number.

### 10.2 Success metrics

Borrowed from Omar's framing, translated to your context. Measured at week 4 of using the system.

| Metric | Target | How measured |
|---|---|---|
| Brief opened daily | >5 of 7 days | Self-tracked in DASHBOARD.md or via artifact-view-count if Cowork exposes it |
| Annotations written | Average 2+ per opening | Count of non-empty annotation fields in artifacts |
| Drafted-to-sent ratio | >70% of Claude-drafted replies sent (with edits OK) | Manual review in Gmail Drafts |
| Time in planning + review | Subjective: >60% of work time | Self-assessment journal entry in cortex weekly |
| Memory commits skipped by triage | 30-50% of conversations | `triage-log.md` line count |
| Person pages graduated meaningfully | >80% of pages get queried or referenced 2+ times within 30 days of creation | Manual audit |

These are not vanity metrics. Each maps to a behavioral question: am I using this, and is it changing how I work?

### 10.3 Rollback / off-switch

Each phase's plugin reads a per-feature toggle in its user-context file:

```yaml
brief_enabled: true
inbox_triage_enabled: true
person_pages_enabled: true
commit_triage_enabled: true
end_day_chain_enabled: true
guardrails_enabled: true
```

If any feature creates more friction than value, the user sets the toggle to `false` and that phase stops writing or reading. No uninstall required.

---

## Part 11 — Pre-flight checklist

Before any code lands:

1. ✅ All 12 plugins at post-refactor versions with config-root convention in place
2. ✅ Marketplace at `BrightWayAI/claude-plugins` pushed and discoverable
3. ✅ User has `~/Documents/.claude-plugin-config-root` populated and `identity.md`, `voice.md` in place
4. ✅ At least one of: HubSpot, Gmail, Calendar MCP available in the user's Cowork setup
5. ⏳ Phase 0 Step 0 platform-agnostic fix applied to all 12 plugins
6. ⏳ Run agent-metrics for 1-2 weeks first to establish baseline (which subagents already work, where confidence routinely lands Low). This data informs whether Phase 4 triage actually saves cost or just adds latency
7. ⏳ Decide naming: stick with "second-brain v2" or rename to BrightWay-native concept

Items 1-4 are already true as of 2026-05-11. Items 5-7 are pre-work for this spec.

---

## Part 12 — What to hand to Claude Code

When picking this up, the kickoff prompt:

> "Read `~/Documents/Claude/plugin-configs/SECOND-BRAIN-V2-SPEC.md` and execute it phase by phase. Use the `REFACTOR-BRIEF.md` in the same folder for context on the v0.2 config-root convention; that work is done. Start with Phase 0 (the Step 0 platform-agnostic fix across all 12 plugins). Then Phase 1 (Daily Brief plugin). Get Phase 1 working end-to-end and ask me to verify before proceeding to Phase 2. Don't batch all six phases without check-ins."

Pair this spec with the existing `REFACTOR-BRIEF.md` in this directory. They're complementary: the refactor brief established the config-root convention; this spec builds the second-brain layer on top.

Open questions in each phase are real decision points. Don't paper over them. Decide explicitly and document the choice in the relevant plugin's CHANGELOG when you push.

— End —
