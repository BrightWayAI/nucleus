# Nudges: a daily check for things that went quiet

_Rewritten 2026-11-16. Status: approved by the owner; build in progress (Phase 2)._
_This file previously held the 2026-05-20 `/sweep` proposal: a heartbeat every three
hours that mined in-progress work into memory. That design was not built. Its text is in
this file's git history._

## What this is

Once a day, Nucleus looks for two kinds of thing that slipped because nothing prompted
the owner, and prepares the next step for each:

| Trigger | Fires when | Prepared |
|---|---|---|
| `stale-deal` | An open CRM deal has had no email, meeting, note, task, or stage change for 15 days | The deal, its last activity, and a drafted check-in |
| `no-reply` | An email the owner sent to a client or prospect has had no reply for 5 business days | The thread and a drafted follow-up |
| `owed-follow-up` | Something the owner committed to is past its date, or is 7 days old with no date | The commitment, where it came from, and a draft if it is a message |

`no-reply` and `owed-follow-up` are the two halves of "a follow-up that went blank":
one where the other person went quiet, one where the owner did.

The results appear in `/morning` under **Needs a nudge**.

## Why daily, and why not a dispatcher

The audit behind this refactor proposed an always-on dispatcher polling for business
events. All three triggers here detect that something did *not* happen. Absence does not
arrive as an event; it is found by looking. A daily look finds it as well as a
five-minute poll would, with one scheduled run a day and no event plumbing. If a trigger
is added later that reacts to something happening (a contract signed, a meeting ended),
revisit this.

## Rules

1. **It only prepares.** A nudge is a staged item with a draft. Drafting is low risk
   under the autonomy policy. Sending the draft, or changing a deal, is high risk and
   needs the owner's approval for that item.
2. **It does not flag twice.** Each nudge has a key: trigger plus the deal, thread, or
   commitment ID. A key that has been flagged is not flagged again until there is new
   activity on it, or the trigger's threshold has passed again since the last flag.
3. **The owner can silence it.** Snooze (until a date) or dismiss (never again for this
   key) from `/morning`. Both are recorded in the ledger.
4. **Thresholds belong to the owner.** They live in a settings file the owner edits,
   not in the plugin.
5. **Date math is done by a script,** not by the model: which items cross a threshold,
   business-day counting, and the "do not flag twice" check.
6. **Missing sources degrade, they do not fail.** No CRM connector means no
   `stale-deal` check that day; the run says so and does the rest.
7. **No judgment about the deal.** A nudge says a deal has been quiet. It does not
   propose closing it as lost. That is the owner's call.

## Pieces

| Piece | Where | Owner |
|---|---|---|
| Thresholds and on/off per trigger | `<config-root>/plugins/growth/triggers.md` | user |
| Starter for that file | growth `references/triggers.template.md` | plugin |
| Date math and dedup | growth `scripts/nudge_check.py` | plugin |
| The daily run | growth `/nudges` | plugin |
| Staged results | `<config-root>/memory/staged/nudges/<date>.md` | written by `/nudges` through `cortex_cli.py` |
| Ledger (flagged, snoozed, dismissed) | `<config-root>/memory/staged/nudges/ledger.jsonl` | appended through `cortex_cli.py` |
| Schedule | `daily-nudges` row in the ops schedule library, `cloud` | registered by the user |
| Review | cortex `/morning`, **Needs a nudge** | user |

The staged files sit under `memory/staged/` because that location syncs through the
private repository, so a cloud run's results reach the owner's computer.
`<config-root>/relationships/` does not sync.

## What a run does

1. Read the thresholds. A missing settings file means the defaults in the table above.
2. Gather, read-only: open deals with their last-activity date (CRM); threads the owner
   sent to a client or prospect with no later inbound message (mail); open items the
   owner owes, with their dates (memory open threads tagged as owed by the owner).
3. Hand those lists, the ledger, and today's date to `nudge_check.py`. It returns the
   items to flag and the ledger lines to add.
4. For each flagged item, draft the check-in or follow-up in the owner's voice.
5. Stage the day's file and append the ledger lines.
6. Write a run receipt (schema 1.1.0, with the actor).

## Open

- Whether `/brief` should also show the nudges. Not in the first version.
- Whether a dismissed deal should come back if its stage later changes.
