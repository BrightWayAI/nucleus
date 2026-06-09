# Nucleus End-Day Routine — Improvement Spec

**Author:** Zach Wagner (BrightWay AI)
**Drafted:** 2026-06-08
**Status:** Proposed — for review
**Owners (skills to change):** `cortex/end-day`, `daily-brief/brief`, `daily-brief/process-brief`, `cortex/remember`
**Related memory:** `memory/meta/nucleus-improvements.md`, `memory/workstream/nucleus-improvements.md`, `memory/surfacing-prefs.md`

---

## 1. Why this exists

The end-day routine works, but three things hold it back today:

1. **The "Today's Brief" artifact is inconsistent and under-interactive.** Formatting drifts between `/brief` and `/end-day` pre-staging, and the only real interaction is a checkbox. The brief is the user's most explicit daily signal, yet it is the one artifact the routine never mines.
2. **The routine over-indexes on noise.** Repeat-ignored items (e.g., subscription-card dunning, certification nudges) resurface forever because nothing learns from what the user skips or dismisses.
3. **The flow is opaque on cost and consent.** It reaches into transcripts, email, Slack, and CRM without asking first or saying what it will cost, and the memory-vs-forget proposal step is not as intuitive as it should be.

This spec defines the target state for (A) the brief artifact and (B) the end-day flow.

---

## PART A — "Today's Brief" artifact

### A.0 Principles

- **One artifact, stable id.** Always `id: todays-brief`. `/end-day` and `/brief` both `update_artifact` it; never create a parallel one. Formatting must be identical regardless of which command produced it.
- **The brief is a working surface, not a read-only snapshot.** Every interactive action writes to `localStorage` under `brief-YYYY-MM-DD` and is mined by `/end-day`.
- **Section order is fixed** (below). A markdown twin is always written to `briefs/YYYY-MM-DD.md` as the canonical text record.

### A.1 Sections (in order)

**1. Center of Gravity**
The single most important thing for the day, one or two sentences. Pulled from yesterday's "one thing that has to move" + the top P0. Visually distinct (accent banner). Not interactive.

**2. Calendar Block — visual + written**
Two coordinated views:
- **Visual timeline strip** — a horizontal day-at-a-glance (e.g., 8a–6p) with blocks positioned by time, color-coded (meeting / focus / personal / open). At-a-glance density read.
- **Written block list** — each event as a row: time, title, attendees, and **notes where available** (meeting context pulled from the linked CRM/cortex node, prior meeting notes, or the event description). Where a meeting maps to a known person/client node, surface one line of "why this matters / last touch."

**3. Priority Tasks**
P0/P1 items only (no clutter). Each row supports richer actions (see A.2). Progress bar on `done`. Tasks are filtered against `surfacing-prefs.md` before render (suppressed items never appear).

**4. Outreach Queue**
Each contact row supports richer actions **and** category tagging (see A.3). Sourced from the relationships/lead-engine pipeline, tiered (today / this week / backlog).

**5. Yesterday's Reflection**
Read from the prior day's `briefs/YYYY-MM-DD.md` `## Reflection`. Shows at minimum **the biggest thing done** and **the one thing that has to move today** (the latter feeds section 1). Read-only.

### A.2 Priority Task actions (richer than a checkbox)

Each task row exposes:

| Action | Meaning | Detail prompt | What `/end-day` does with it |
|---|---|---|---|
| ✓ **Done** | completed | — | Mark source node action COMPLETED; candidate "biggest thing done" |
| 👉 **Delegate** | handed off | "to whom?" (default Erica) | Reassign in source node; if CRM connected, create task for delegatee |
| ⏭ **Skip** | not today | "how long?" (1d/3d/next week) | Defer; increment per-task skip counter (feeds repeat-ignore rule) |
| 🚫 **Not important** | stop surfacing | confirm | Append to `surfacing-prefs` do-not-resurface; demote/close source action |
| 📝 **Annotate** | free-text note | inline text | Route via `/process-brief` (draft reply / move date / add talking point) |

`localStorage`: `brief-DATE.tasks[id] = { action, detail, ts, name }`.

### A.3 Outreach Queue actions + categories

**Per-contact actions:** Sent ✓ · Skip · Nudge · Let go · (Booked 📅 · Dead ✕ optional).

**Plus category tagging** — when an action is logged, capture *what kind of outreach it was*, drawn from existing taxonomy so the log is analyzable and feeds the pipeline:

- **Outreach bucket** (from the relationships plugin): `new business` · `relationship building` · `network expansion`.
- **Signal type** (from lead-engine's 7 signals, when applicable): Engagement · Job change · Funding · Hiring · Growth/expansion · Tech-stack change · Direct intent.
- **Value-add used** (from bizdev value-add approaches): article/framework · intro · diagnostic tool/free sample · case study/result · domain observation.

UI: the action button row plus a small dropdown (or chips) for bucket + value-add; signal type auto-fills from the pipeline entry if present.

`localStorage`: `brief-DATE.outreach_actions[id] = { name, action, bucket, signal, value_add, detail, ts }`.

`/end-day` mining: `sent` → log touch + value-add on the person/bizdev node; `booked` → advance stage + create prep task; `nudge` → log follow-up touch; `let go`/`dead` → mark dead, remove from active queue; bucket/value-add roll up into outreach analytics over time.

### A.4 localStorage contract (canonical)

```json
{
  "tasks":            { "<task-id>":   { "action": "done|delegate|skip|not_important", "detail": "", "ts": "", "name": "" } },
  "annotations":      { "<item-id>":   "free text" },
  "outreach_actions": { "<contact-id>":{ "name": "", "action": "sent|skip|nudge|let_go|booked|dead", "bucket": "", "signal": "", "value_add": "", "detail": "", "ts": "" } },
  "last_interaction_at": "ISO8601"
}
```

---

## PART B — End-Day flow (prompting + actions)

Target sequence. Each numbered step is a discrete, intuitive beat.

### B.1 Review sources — with per-source consent + cost estimate

Before reading anything, present a **review menu**: the sources to be reviewed, each with a checkbox (default on/off per config) and an **approximate cost** shown *before* running.

Sources, in priority order:
1. **Today's Brief responses** — *required input, always first.* Read the `todays-brief` widget context (tasks, annotations, outreach actions). This is the cheapest and highest-signal source and must never be skipped.
2. **Transcripts** (Granola/Gemini) — today's meetings.
3. **Email** (Gmail) — today's threads where the user is a participant.
4. **Slack** — configured channels/DMs since yesterday.
5. **CRM** (HubSpot) — today's deal/task/activity changes.

**Cost estimate model:** before each source, show an estimate derived from volume × per-unit token cost, e.g. *"Transcripts: 2 meetings (~14k tokens) ≈ $0.05"*, *"Email: 23 threads, 4 likely-relevant ≈ $0.03"*. Provide a **running total** and a single "review all" vs. "let me choose" control. Ask permission per source (or batch-approve). Skipped sources are logged so the summary is honest about what was and wasn't reviewed.

> Design note: keep the gate lightweight — one card with checkboxes + costs + a confirm, not five sequential yes/no prompts.

### B.2 Share learnings → propose memories & forgettings

After the approved sources are read:
1. **Surface the main learnings of the day** in plain language first (a short narrative, not raw proposals) — "here's what today was about."
2. Then propose **memories** (new/updated knowledge, decisions, relationship context) **and forgettings** (stale facts to demote/archive, items to suppress) side by side. Forgettings are first-class, not an afterthought.
3. Each proposal shows type, confidence, target node, and source citation.

### B.3 Memory taxonomy consolidation

Current knowledge types are: Model, Gotcha, Insight, Lesson, Recipe, Correction, Decision. Proposed leaner set (consolidate unless a type earns its keep):

| Keep | Rationale |
|---|---|
| **Insight** | the workhorse — observations, mental models, "how X works" (absorbs **Model** and **Lesson**) |
| **Decision** | distinct and auditable — what was chosen and why |
| **Gotcha** | earns its keep — an actionable *warning* ("do NOT…", "watch out for…"); different intent from an insight |
| **Correction** | distinct — overturns a prior belief; needed for trust |

| Fold / retire | Into | Rationale |
|---|---|---|
| **Model** | Insight (tag `mental-model`) | rarely distinct from insight in practice |
| **Lesson** | Insight | overlaps with insight |
| **Recipe** | Insight (tag `recipe`) *or* keep only if a true step-by-step procedure | most "recipes" are really insights; keep the label only for genuine repeatable procedures |

Net: **Insight, Decision, Gotcha, Correction**, with optional `mental-model` / `recipe` tags. (Open for your call — see §D.)

### B.4 Walk proposals — intuitive, batchable

Move through proposed memories/forgettings in an intuitive experience:
- **Default:** grouped by node, accept-all / pick / edit per group.
- **High-confidence fast path:** "accept all high-confidence" in one tap; only medium/low get individual attention.
- Keep per-item accept/edit/skip available but never force one-at-a-time when a batch is obviously fine.

### B.5 Propose tomorrow's priorities & outreach — individually, batchable

After memory is settled, propose **tomorrow's priority tasks and outreach log**:
- Walk each proposed priority and outreach item individually (this is where deliberateness matters most).
- Offer a batch path when sensible ("these 3 carry over unchanged — keep all?").
- Respect `surfacing-prefs` (don't propose suppressed/noise items).
- Output writes straight into tomorrow's `todays-brief` (sections 3 & 4) so the morning surface is ready.

### B.6 Ask for anything else

Explicitly ask: **"Any other priorities or outreach for tomorrow?"** — free-form capture appended to tomorrow's brief.

### B.7 Reflect — and store over time

Finally, ask the day's reflection: **biggest thing done**, **what blocked you** (optional), **the one thing tomorrow has to move**. Pre-fill candidates from the brief actions (done tasks → biggest-thing candidate). Write to `briefs/YYYY-MM-DD.md` `## Reflection`.

**Store reflections over time:** in addition to the per-day file, append to a rolling `memory/reflections.md` (or a `reflections/` log) so reflections become a longitudinal, queryable record — "what have my biggest wins been this month," "what keeps blocking me." This longitudinal store is itself a future input to weekly review and to surfacing decisions.

---

## PART C — New / changed data stores

| Store | Purpose | Status |
|---|---|---|
| `memory/surfacing-prefs.md` | do-not-resurface list, noise rules, repeat-ignore rule, action taxonomy | **created 2026-06-08** |
| `memory/reflections.md` (or `reflections/`) | longitudinal reflection log | new |
| `brief-YYYY-MM-DD` localStorage | full action contract in §A.4 | extend existing |
| Cost model (in `end-day` skill) | per-source token→$ estimates for B.1 | new |

---

## PART D — Open questions for Zach

1. **Taxonomy:** OK to collapse to **Insight / Decision / Gotcha / Correction** (with `mental-model`/`recipe` tags), or keep Recipe as a full type?
2. **Cost gate granularity:** one batch-approval card with per-source costs (recommended), or a hard per-source yes/no every time?
3. **Outreach category capture:** require bucket + value-add on every `sent`, or make it optional/quick-tag?
4. **Reflection store:** single `reflections.md` rolling file, or dated `reflections/` folder mirroring `briefs/`?
5. **Batch threshold:** what counts as "obviously fine to batch" for B.4/B.5 — high-confidence only, or also unchanged carryovers?

---

## PART E — Implementation checklist

- [ ] `daily-brief/brief`: render the 5 sections in fixed order; add visual calendar strip; richer task actions; outreach category tagging; filter against `surfacing-prefs`.
- [ ] `daily-brief/brief` + `cortex/end-day`: always `update_artifact id=todays-brief`; write markdown twin.
- [ ] `cortex/end-day`: add **B.1 source-review consent + cost** card (Today's Brief required & first).
- [ ] `cortex/end-day`: add **mine-the-brief** step (read widget context → write-backs per §A.2/A.3).
- [ ] `cortex/end-day`: learnings-first narrative, then memories **and** forgettings (B.2).
- [ ] `cortex/remember` + nodes: taxonomy consolidation per B.3 (pending §D.1).
- [ ] `cortex/end-day`: propose tomorrow's priorities/outreach individually w/ batch path (B.5); ask "anything else" (B.6).
- [ ] `cortex/end-day`: reflection capture + append to longitudinal `reflections` store (B.7).
- [ ] `daily-brief/process-brief`: handle new action types (delegate/skip/not_important + outreach categories).
