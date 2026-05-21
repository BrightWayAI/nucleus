# /sweep — heartbeat for always-on activity and learning

_Created: 2026-05-20_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Spec only. Not started. Estimated ~1-2 weeks single-engineer to ship v1._
_Companion proposals: heartbeats general pattern (this proposal is the first concrete one), Operator app spec (eventually surfaces sweep output as toasts)._

---

## Why this exists

Today, Nucleus has two memory-write moments per day for the *user's actual work*:

- **`/end-day`** (5pm-ish) — runs mining agents against today's substrate; commits accepted proposals.
- **`/listen`** (overnight) — mines yesterday's full archive; stages `/morning` proposals for review.

That leaves an 8-hour gap where learnings happen, get said in conversations with Claude, get written in emails, get mentioned in meetings — and then evaporate by 5pm when `/end-day` finally fires. The user has to remember what was worth capturing, OR rely on `/end-day`'s mining to catch it (which is hit-or-miss across an 8-hour gap).

**`/sweep` fills the gap.** A new heartbeat fires every 3 hours during work hours, reviews recent work surfaces *and* in-progress Claude conversations, and stages proposed memory entries for review at the next `/end-day`. It never modifies active memory. It never sends anything. It just *notices* and stages.

This is Liu's "Chief of Staff" heartbeat pattern adapted to cortex's mining substrate: same agents (`transcript-reviewer`, `conversation-miner`, `activity-miner`), same write surface (`staged/heartbeat-drafts/<today>.md` mirroring `/listen`'s `.commit-drafts/<date>.md`), same review UX (walk-through merge at the closing ritual).

---

## The mirror to /listen + /morning

| Loop | Cadence | Sources | Drafts to | Reviewed at |
|---|---|---|---|---|
| `/sweep` (new) | every 3h, work hours | Today's surfaces + in-progress Claude conversations | `<config-root>/memory/staged/heartbeat-drafts/<today>.md` | `/end-day` |
| `/listen` (v4.7) | nightly | Yesterday's full archive (`archive/<yesterday>/`) | `<config-root>/memory/.commit-drafts/<yesterday>.md` | `/morning` |

`/sweep` catches the day in flight. `/listen` catches the previous full day at rest. Together they provide bidirectional mining coverage with one user-review event per period.

---

## Architecture

### File layout

```
<config-root>/
├── memory/
│   ├── staged/heartbeat-drafts/
│   │   ├── 2026-05-20.md           ← today's running pool (append-only across ticks)
│   │   ├── 2026-05-19.md           ← yesterday's (still pending if /end-day was skipped)
│   │   ├── archive/
│   │   │   ├── 2026-05-18-reviewed.md   ← reviewed at end-of-day; archived
│   │   │   └── 2026-05-17-merged-by-listen.md ← /listen rolled it into the overnight draft
│   │   └── .state.json             ← per-day tick log, dedup index, cadence state
│   ├── ...
```

### Heartbeat lifecycle

```
Every 3h work-hours (Cowork cron, or daemon fallback)
   │
   ▼
/sweep
   │
   ├──▶ Read identity.md → time zone + working hours
   │
   ├──▶ Check: in working hours? (with 30-min soft buffer either side)
   │      └─ No → log "skipped (outside work hours)" and exit
   │
   ├──▶ Check focus signal: did observe skill flag user as in deep work? (TODO v2 — skip in v1)
   │
   ├──▶ Read staged/heartbeat-drafts/.state.json
   │      ├─ last_run timestamp
   │      ├─ today's tick count
   │      └─ today's cumulative proposal list (for dedup)
   │
   ├──▶ Mine recent activity (since last_run, capped at last 4h):
   │      ├─ transcript-reviewer scope=today (in-progress Cowork sessions)
   │      ├─ conversation-miner scope=today (Cowork session-info MCP)
   │      └─ activity-miner scope=today (Gmail / Slack / Calendar / Drive)
   │
   ├──▶ Dedup proposals against:
   │      ├─ Active memory (semantic match via Haiku-tier classifier)
   │      ├─ staged/heartbeat-drafts/<today>.md (cumulative across ticks)
   │      ├─ triage-log.md entries for today (explicit /remember / /learn)
   │      └─ Yesterday's .commit-drafts/ (in case /listen already captured)
   │
   ├──▶ Append surviving proposals to staged/heartbeat-drafts/<today>.md
   │
   ├──▶ Update .state.json (last_run, tick count, proposal list)
   │
   ├──▶ Log one rolling-aggregated entry to memory/log.md:
   │      "## [<today HH:MM>] sweep | tick <N>: <P> proposals (<D> deduped). Cumulative today: <T>."
   │      (Update existing entry for today rather than appending a new H2 — one entry per day, updated in-place.)
   │
   └──▶ Exit silently. No user-facing output.
```

### What the mining agents see

In sweep mode, the existing mining agents (`transcript-reviewer`, `conversation-miner`, `activity-miner`) accept a new `scope: today` parameter (currently they default to yesterday for `/listen` and full-day for `/end-day`). Their behavior is otherwise identical — same proposal format, same confidence ratings, same node-routing rules.

**Cap per tick:** 5 proposals across all three agents combined. Higher volume = noise. Quality over quantity. Configurable via `cortex.user-context.md` `sweep.proposal_cap`.

---

## Dedup — the hard part

Most of the design pain is here. Without solid dedup, `/sweep` will re-propose the same fact every 3 hours and the user will reject duplicates 30 times before disabling the heartbeat.

### Three-layer dedup

For each candidate proposal, in order:

1. **Against active memory.** For each candidate, semantic-match (Haiku-tier classifier) against existing knowledge entries on the target node. Threshold: similarity ≥ 0.75. If match → skip with reason "already in memory."

2. **Against today's running pool.** Read `staged/heartbeat-drafts/<today>.md`. Same semantic-match. If match → skip with reason "already proposed this tick or earlier today."

3. **Against explicit captures.** Read `memory/triage-log.md` for entries today (last 12h). If a `/remember` / `/learn` / `/note` already wrote on the same node with the same content shape → skip with reason "user captured explicitly."

### Skip-log per tick

Track skipped proposals (with reason) in `.state.json` per tick. Surface aggregate dedup rate in `/diagnose` and in the `/end-day` review summary: "today's `/sweep` ran 3 ticks, found 18 candidates, deduped 11, staged 7 for review."

### Threshold tuning

The 0.75 similarity threshold is a v1 guess. Real usage will tell us if it's too tight (user sees duplicates) or too loose (good new content gets blocked as a "duplicate"). Make this configurable in v1, tune from real-world dedup rates in v2.

---

## Integration with existing pieces

| Piece | Change |
|---|---|
| **`/end-day` quick mode** | New **Step 3.5 — Review sweep drafts**. Walks `staged/heartbeat-drafts/<today>.md` proposal-by-proposal (accept/reject/edit/defer) — same UX as `/morning` walks `.commit-drafts/`. After walk, archives the file to `staged/heartbeat-drafts/archive/<today>-reviewed.md`. Step 3 (auto-commit) becomes a *final sweep* for whatever the heartbeat missed. |
| **`/end-day` full mode** | The original heavy mining steps (1, 2, 2a, 2b) still run, but with dedup against today's `staged/heartbeat-drafts/` file. They cover the gap between the last `/sweep` tick and `/end-day`, plus anything the heartbeat skipped or missed. |
| **`/listen` overnight** | When `/listen` mines yesterday's archive, it now also dedups against `staged/heartbeat-drafts/archive/<yesterday>-reviewed.md`. Entries the user already accepted via `/end-day` don't get re-proposed. Entries the user rejected during `/end-day` review get suppressed for 7 days. |
| **`/morning` walker** | If `/end-day` was skipped yesterday, today's `/morning` includes a section: "Yesterday's `/sweep` proposals still pending — review now alongside `/listen` draft?" Carries unmerged drafts forward. After 3 consecutive missed `/end-day`s, `/sweep` pauses for that user (clearly not reviewing). |
| **`memory/log.md`** | One aggregated entry per day, updated in-place each tick. Not one entry per tick (would flood the log). |
| **`memory/hot.md`** | Cumulative `staged/heartbeat-drafts/<today>.md` content participates in hot.md regeneration's "recent activity" section. Tomorrow's `/recall` auto-fire sees the staged-but-unreviewed pool as a "[pending end-of-day review]" tier. |
| **`memory-librarian`** | When responding to a `/recall` or `/search` query, includes pending-heartbeat proposals tagged as "[pending review — not yet committed]." Tier-ranks them below confirmed entries but above demoted ones. |
| **Autonomy slider** | New mapping: `autonomy: heartbeat.sweep: <mode>`. Values: `suggest` (default — heartbeat runs, stages drafts silently), `manual` (heartbeat disabled — explicit `/sweep` only), `confirm` (heartbeat asks before each tick — useful for testing, annoying for daily use). `auto` is meaningless here since sweep doesn't act. |
| **`/diagnose`** | Reports sweep health: last run timestamp, ticks/day average, proposals/tick average, dedup rate, drift between expected vs actual cadence (Cowork cron reliability check). |
| **`/cleanup`** | Adds a section that walks old `staged/heartbeat-drafts/archive/` files; offers to delete reviewed drafts > 60 days old. |
| **`core-ops` schedule library** | Adds row: `sweep-hourly` cron `0 */3 8-18 * *` (every 3h between 8am-6pm). Actual hours come from identity.md working hours — schedule entry is a hint, /sweep enforces. |
| **`/start-nucleus` walker** | Adds an offer in the post-foundational stage: "Want to enable the `/sweep` heartbeat? Fires every 3h during work hours; stages proposed memory entries for `/end-day` review. (y / skip)" |

---

## Cost model

Per tick at moderate activity:
- Input context: ~10K cached (cortex CLAUDE.md + nucleus-router + identity + voice + user.md + hot.md) + ~3K fresh (recent surfaces + conversations summary).
- Output: ~1-3K (5 proposals with reasoning).
- Mostly Haiku for triage + dedup; Sonnet only when ambiguity flags require it.

| Tier | Cost per tick | Cost per day (3 ticks) | Cost per month |
|---|---|---|---|
| Haiku only | $0.005 | $0.015 | $0.45 |
| Hybrid (Haiku triage + 1-2 Sonnet drafts) | $0.05 | $0.15 | $4.50 |
| Sonnet only | $0.20 | $0.60 | $18.00 |

**Default tier:** hybrid. ~$5/month per user at moderate activity.

Sensitive to:
- Number of active surfaces (more Slack channels watched → more dedup work)
- Conversation volume (busy Claude usage day → more mining)
- Identity working-hours (8h day = 3 ticks; 10h day = 4 ticks)

If cost spikes above $10/month for a user, surface a `/diagnose` warning and recommend reducing surfaces or extending cadence to 4h.

---

## Privacy considerations

The `/sweep` heartbeat reads **today's in-progress data**:

- Gmail metadata + snippets (same default-metadata-only policy as `/listen`)
- Slack messages where user authored or was @mentioned
- Calendar events that just ended
- Drive files modified since last tick (metadata only)
- Cowork session metadata for today's in-progress sessions (via session-info MCP)

All of this lands in `<config-root>/memory/staged/heartbeat-drafts/<today>.md` — same privacy posture as `.commit-drafts/`. Already covered by the cortex v4.7.2 gitignore template. Add `memory/staged/heartbeat-drafts/` to the explicit exclusion list (probably already implicit via `memory/.*`).

**One new concern:** Cowork conversation mining could surface sensitive content from in-progress sessions (e.g., a client confidential discussion the user is having with Claude). This was already a concern in `/end-day` mining but the smaller temporal window (hours, not a full day) made it less acute. With `/sweep` running every 3h, the proposals will frequently quote recent conversations.

**Mitigation:**
- `staged/heartbeat-drafts/` content is the most sensitive directory in `<config-root>/`. Hard-block from git via `.gitignore` (already done). Recommend symlinking to `~/.cache/nucleus/heartbeat-drafts/` for cloud-sync users (like `archive/`).
- The cortex CLAUDE.md should note this: conversation-mining of in-progress sessions writes summaries of *what was discussed*, not verbatim transcripts. Mining agents must paraphrase before writing to drafts.
- Add an explicit opt-out: `cortex.user-context.md` `sweep.mine_conversations: false` disables the conversation-miner inside `/sweep` (still surfaces / Slack / Gmail / Calendar). Default `true`.

---

## Cowork scheduler compatibility

`/sweep`'s cadence (every 3h during work hours) requires Cowork's scheduler to accept sub-daily crons. Three scenarios:

1. **Cowork accepts `0 */3 * * *` style crons:** Best case. Register via `/register-schedules`. Done.
2. **Cowork accepts daily-only:** Need a daemon. The Operator app (when built) becomes the natural home for the heartbeat tick. Until then, register a *daily* cron at the start of work hours that schedules N follow-up ticks via the macOS launchd / Linux systemd-user-timer / Windows Task Scheduler. Platform-specific, ugly.
3. **Unknown — verify before building:** First action in week 1 of the build is to confirm Cowork's scheduler granularity. The whole heartbeat pattern depends on it.

For v1, prefer scenario 1. If we discover scenario 2, defer `/sweep` until the Operator app's daemon ships (~2-3 months out).

---

## Build plan (1-2 weeks single-engineer)

### Days 1-2 — Cron + schema

- Verify Cowork sub-daily cron support (or document fallback to launchd/systemd).
- Add `sweep-hourly` row to `core-ops/references/schedules.template.md` (cron `0 */3 * * *`, narrowed to work hours by `/sweep` itself).
- Add `<config-root>/memory/staged/heartbeat-drafts/` directory creation to `/setup-identity` Step 3.5 (alongside `.gitignore` write).
- Write the heartbeat state schema (`.state.json` shape).

### Days 3-5 — /sweep command + skill

- New `commands/sweep.md` + `skills/sweep/SKILL.md` in cortex.
- Read identity → time zone + working hours. Bail if outside work hours.
- Read `.state.json` for last_run timestamp.
- Add `scope: today` parameter to `transcript-reviewer`, `conversation-miner`, `activity-miner` agents. Each agent's spec doc gets a new section explaining the today-scope behavior.
- Plumb the agents through a sweep-mode invocation.

### Days 6-8 — Dedup layer

- Implement three-layer dedup with semantic-match threshold (0.75 default).
- Write `<config-root>/memory/staged/heartbeat-drafts/<today>.md` as append-only across ticks.
- Update `.state.json` with cumulative proposal list for fast in-process dedup.
- Validate dedup against test fixtures (same fact mentioned in 3 different surfaces → only 1 proposal stages).

### Days 9-10 — Integration

- `/end-day` quick mode Step 3.5 (Review sweep drafts walker).
- `/listen` dedups against archived heartbeat drafts.
- `/morning` carries forward unreviewed sweep drafts when `/end-day` was skipped.
- `memory/log.md` aggregation pattern (one entry per day, updated in-place).
- `/diagnose` health report section.
- `/start-nucleus` offer for sweep enablement.

### Days 11-12 — Privacy + opt-outs

- Verify gitignore template covers `staged/heartbeat-drafts/`.
- Add `sweep.mine_conversations: false` opt-out to cortex.user-context.md.
- Add cost-spike detection: if proposals/tick > 10 or input tokens > 20K, surface a `/diagnose` warning.
- Update cortex CHANGELOG, plugin.json (v4.9.0 — minor for new command + agent param), router intent table (`"any new learnings from today" / "what should I capture from this session" / "sweep my work surfaces"` → `/sweep`).

### Days 13-14 — Soft launch + observation

- Run `/sweep` against your own substrate for 5+ days.
- Tune dedup threshold based on real proposal volume.
- Adjust cadence if 3h proves too noisy or too sparse.
- Document final v1 behavior in `references/sweep-heartbeat.md` (the formal post-build reference).

### Out of v1 (post-launch)

- Adaptive cadence based on observe-skill focus signals.
- Per-surface fine-grained cadence (e.g., conversations every 1h, surfaces every 3h).
- Real-time notifications when sweep flags something urgent (requires Operator app surface).
- Multi-user / team-shared `/sweep` proposals.
- Cost-tier auto-tuning based on observed proposal acceptance rate.

---

## Open decisions

Lock these before building:

1. **Cadence: 2h, 3h, 4h?** Recommend **3h**. Two ticks before lunch, one after; lighter dedup load than 2h; fresher than 4h.
2. **Cap per tick: 5 / 10 / 20?** Recommend **5** in v1. Higher means more dedup work. Tune from real volume.
3. **Mine in-progress conversations: yes/no default?** Recommend **yes** with opt-out flag. The conversation-mining is the highest-value capture path; defaulting it off cripples the heartbeat.
4. **Aggregation in log.md: per-tick or per-day?** Recommend **per-day, updated in-place**. Three ticks/day × 30 days = 90 log entries/month per user if per-tick; aggregating keeps the log readable.
5. **Cowork cron support — verified by week 1 or fallback to launchd?** Don't start the build until this is verified.
6. **Where does `/sweep` live — cortex or new heartbeats plugin?** Recommend **cortex**. Heartbeats are observation-shaped; same plugin owns observe, recall, the autonomy slider, the indexer. Don't fragment.

---

## Open question — the broader heartbeat pattern

This proposal is for ONE heartbeat (`/sweep`). The broader pattern from the earlier proposal (`docs/proposals/heartbeats.md` if you ever write it) includes inbox triage, pre-meeting brief, memory hygiene, etc. Recommendation: **ship `/sweep` first, dogfood for 2-4 weeks, then evaluate whether other heartbeats earn their cost.** Don't ship a whole heartbeat framework speculatively — let real usage prove which patterns are worth the architecture investment.

If `/sweep` works, the natural next heartbeats are:
- **`/coach`** (60-min cadence) — memory hygiene: reindex queue check, decay state recompute, rehearse-queue suggestions. Lower-cost than `/sweep` because it doesn't mine, just maintains.
- **`/brief-meeting`** (5-min cadence) — pre-meeting context surfacing. Highest demo value but requires the Operator app to surface usefully.
- **`/triage-inbox`** (15-min cadence work hours) — Chief-of-Staff style inbox drafting. Highest day-to-day operator value.

But none of those should be built until `/sweep` proves out.
