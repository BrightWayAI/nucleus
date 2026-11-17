# Nucleus roadmap

_Last updated: 2026-11-16_

**Top-level `docs/proposals/*.md` = open specs.** Built specs are in `shipped/`.
Deferred specs are in `parked/` and are not on this roadmap. Past work is in
`docs/HISTORY.md` and each plugin's `CHANGELOG.md`.

## Direction

A 2026-11-16 audit measured Nucleus against current practice for running agents in
production. The conclusion: the durable asset is the shared context, not a roster of
named agents. Context is the strong part. Verification, review scaled to risk, and
event-driven starts are the weak parts. The refactor below fixes those in order. Each
item is its own branch and pull request in the repo it touches, and a phase does not
start until the one before it is merged.

## Active: signal-driven, self-verifying refactor

### Phase 0 — cleanup (merged 2026-11-16)

| Item | Where | State |
|---|---|---|
| Note-source adapter reference moved out of `agents/` so it stops registering as an agent | cortex 4.30.1 | merged |
| Regression tests for the hot-cache formats fixed in 4.28.1 | cortex 4.30.2 | merged |
| `autonomy.md` merged into `autonomy-policy.md`; retired commands removed | cortex 4.30.3 | merged |
| `/migrate-plugin-configs` for legacy files in `<config-root>/plugins/` | cortex 4.31.0 | merged; applied to the live root 2026-11-16 |
| Agent-log schema examples use current names | ops 0.14.2 | merged |
| Schedule library `Runs on` (`cloud` \| `local-device`); the local-device-only rule is gone | ops 0.15.0 + `contracts.md` | merged |
| This roadmap; history moved out of `CLAUDE.md` | nucleus | merged |
| Eval setup: fixture config root for the morning cases; routing cases carry a plugin catalog | cortex 4.31.1, ops 0.15.1 | merged |

Evals after the fix (3 runs per case, all runs must pass): cortex 3 of 5 cases, ops 5 of
9 with the default judge. Still failing: `draft-checkin-routing` (the router picks
growth `/draft-touchpoint`, the grader expects comms `/style`; an overlap to settle in
Phase 3), `catch-me-up` (asks whether Acme is a client or a prospect), and three cases
that pass 2 of 3. Run with `--judge-model sonnet`; see each repo's `evals/README.md`.

### Phase 1 — verification and risk tiers (merged 2026-11-16)

Plan approved 2026-11-16. Unattended memory merges stay off for this phase.

| Item | Where | State |
|---|---|---|
| 1. `verifier` agent, `check-citations`, `references/verification.md` | cortex 4.32.0 + `contracts.md` | merged |
| 2. `/listen` Step 4.5 runs the verifier on every proposal; `record-verification`; `/morning` shows the result | cortex 4.33.0 + `contracts.md` | merged |
| 3. Verifier on `/sow`, `/client-status`, `/invoices` | clients 0.9.0, admin 0.6.0, cortex 4.33.1 + `contracts.md` | merged |
| 4. Three risk tiers (policy 2.0.0) | cortex 4.34.0, ops 0.16.0 + `contracts.md` | merged |
| 5. `/morning` reviews failures and conflicts one at a time and the verified batch once; `triage-draft`; outcome log | cortex 4.35.0 + `contracts.md` | merged |
| 6. Actor ID in every run receipt (receipt schema 1.1.0); `write-receipt` | cortex 4.36.0, ops 0.17.0 + `contracts.md` | merged |
| 7. Tool limits on the eight agents that had none; a check that every agent declares them | cortex 4.36.1, ops 0.17.1, growth 0.6.6, comms 0.5.4, research 0.5.4, alignment 1.6.3 + `contracts.md` | merged |


- A verifier sub-agent: fresh context, a different model from the producer, read-only
  tools enforced by an allowlist, pass/fail with evidence per claim. First wired into
  `/listen` memory proposals, `clients:sow` and `client-status`, and `admin:invoices`.
- Tool allowlists for the eight agent files that have none today.
- Three risk tiers replacing the flat autonomy policy: low runs unattended and is
  reversible, medium is batched for one review, high keeps per-item approval. Sends,
  SOWs, invoices and CRM stage changes stay high.
- `/morning` shows only verifier failures, conflicts and medium-risk items.
- Every run receipt records the accountable actor ID.
- **Open decision (owner):** exact criteria for unattended memory merges. Nothing
  merges unattended until that is approved.

Carried out of Phase 1, not yet proven in real use:

- No real overnight draft has been through `/listen` Step 4.5 or the new `/morning`
  review. The first scheduled run on cortex 4.33.0 or later is that test.
- The verifier steps in `/sow`, `/client-status` and `/invoices` have only been run as
  scenario walk-throughs, not end to end with a live verifier.
- Agent tool limits were confirmed in Claude Code only. Cowork's handling of `tools:` and
  `disallowedTools:` for plugin agents is undocumented.
- Open decisions (owner): whether `relationships-director` should stop writing person
  pages directly; whether growth `/draft-touchpoint` or comms `/style` owns "draft a
  check-in"; unattended memory merges, to revisit once
  `memory/staged/verifier-outcomes.md` has two weeks of data.

### Phase 2 — nudges (merged 2026-11-16)

Plan approved 2026-11-16. The owner chose two triggers: a deal that has gone quiet
(15 days) and a follow-up that went blank. The second is built as two checks: no reply
to something sent (5 business days), and something owed that was never sent (past its
date, or 7 days undated). A daily check replaces the always-on dispatcher first
proposed; the reasons are in `sweep-heartbeat.md`.

| Item | Where | State |
|---|---|---|
| 1. Spec and file formats | `sweep-heartbeat.md`, `contracts.md` | merged |
| 2. Date math and "do not flag twice" script, with tests | growth 0.6.7 | merged |
| 3. `/nudges` command and the user-owned thresholds file | growth 0.7.0 | merged |
| 4. `daily-nudges` schedule row (cloud); two `--verify` fixes | ops 0.18.0 | merged |
| 5. `/morning` shows **Needs a nudge** with snooze and dismiss; `open-nudges` | cortex 4.37.0 | merged |

Not yet proven in real use: `/nudges` has not run against the live CRM, mailbox, or
memory, and `daily-nudges` is not registered. The first run should be by hand
("what's gone quiet?") before the schedule is turned on.

Not built unless asked for: triggers that react to an event (contract signed, meeting
ended, email received, invoice overdue).

### Phase 3 — orchestration and framing (merged 2026-11-16)

Plan approved 2026-11-16. Decisions: plugins are shown by their plain names (Ops,
Clients, Comms, Growth, Briefing, Admin, Research, Alignment); `/cos` keeps its name;
the agents `chief-of-staff` and `relationships-director` keep their names for now and
get descriptions with no role framing. Renaming them waits for another reason to touch
those files, or for the adapter freeze to lift.

The adapter freeze was crossed once, by owner decision on 2026-11-16: the display names
live in `scripts/generate_openai_adapters.py`, so plain names required changing them
there and regenerating. Only display names and one description sentence changed; no
adapter behavior was added or altered. In ChatGPT the mentions are now `@Ops`,
`@Clients`, `@Comms`, `@Growth`, `@Briefing`, `@Alignment`.

| Item | Where | State |
|---|---|---|
| 1. `/cos` parallel plans and `then` steps | ops 0.19.0 + `contracts.md` | merged |
| 2. Routing by what a request is about, not by role name | ops 0.20.0 + `contracts.md` | merged |
| 3. Plain plugin names everywhere, including the ChatGPT/Codex display names (owner decision); descriptions say what each plugin covers | all nine plugins, the adapter generator, `marketplace.json`, READMEs | merged |

Not yet proven in real use: a parallel plan has only been exercised as a plan. No run
has yet started several workers at once and assembled their results.

Eval harness gap, closed in Phase 4 item 3: the growth, clients, and briefing suites
now run against a copy of cortex's fixture config folder.

### Phase 4 — context coverage and self-improvement (in progress)

Started 2026-11-16 on the owner's instruction to keep going. Assumption, because the
question went unanswered: the owner is the only person writing to memory, so none of the
collaborative-proposals machinery is being built. Trello was dropped from the adapter
list earlier.

| Item | Where | State |
|---|---|---|
| 1. Every sub-agent call logged automatically inside the config root | ops 0.21.0, briefing 0.12.5 + `contracts.md` | merged |
| 2. A decision-record node type; `/morning` and `/remember` route decisions to it | cortex 4.38.0 + `contracts.md` | merged |
| 3. Fixture config root for the growth, clients, and briefing eval suites; output-quality evals for `/morning`, `/listen`, `/brief`, `/relationships`, `/client-status` | cortex 4.38.1, growth 0.7.2, clients 0.9.2, briefing 0.12.6; fixture-copy check in nucleus | merged |
| 4. Command files under 2,500 words, deterministic steps in `cortex_cli.py`, behavior confirmed by evals | 4a `/morning` 4,422 → 2,500 (cortex 4.39.0) merged. 4b `/listen` 5,226 → 2,411 (cortex 4.40.0) merged. 4c baseline evals for the remaining four (cortex 4.40.1) in review. Still over: `/end-day` 8,913, `/remember` 7,019, `/cleanup` 3,230, `/recall` 3,105 | in progress |
| 5. `/listen` adapters for HubSpot, QuickBooks, GitHub, and Airtable, metadata-first | cortex | not started |
| 6. A weekly agent that reads the run log and verifier results and opens improvement pull requests | to be decided | not started |

Found while reading the four remaining long commands (2026-11-17). These are places
where a command disagrees with itself or with another command. A trim has to pick one
side, so each needs an owner decision or an explicit choice in the trim PR:

- `/end-day`: the quick-mode step list omits brief mining, which "ALWAYS runs, both
  modes"; quick mode says CRM activity is in scope while the activity-mining step says it
  is full mode only; a step cites a section "B.4" that does not exist; "the chain ends
  after Step 4" without briefing conflicts with "this step always runs" for the index
  refresh.
- `/remember`: "append" in the text where the tool named is `prepend-section` (twice);
  memory hygiene says "remove outdated entries" while the conflict step says move them
  to Demoted knowledge; knowledge mode still points at the pre-4.38 inline decision
  format.
- `/recall`: hard-codes `~/Documents/Claude` in one call while everything else uses the
  resolved config root; says "no new file writes" yet creates two files; names no write
  tool or lock for its tag updates.
- `/cleanup`: "never auto-execute" against an `auto` mode that executes without the
  gate; "default to archive over delete" against three steps that delete; its decision
  step edits a decision's status, where 4.38 says a changed decision is superseded, not
  edited; it cites a `/recall --unarchive` flag that `/recall` does not define.

## Open specs

| Proposal | Status |
|---|---|
| `sweep-heartbeat.md` | Rewritten 2026-11-16 as the Phase 2 nudges spec. The `/sweep` heartbeat it used to describe was not built. |

## Known loose ends (not scheduled)

- All nine entries in `releases/index.json` are `candidate`. None has been promoted;
  promotion needs live connector evidence and a tag.
- `/end-day` does not read the hosted brief's shared state before asking for a paste
  (`/brief` and `/listen` do).
- cleanup-pass-1 item F (`/end-day` decomposition) is folded into the Phase 4 command
  cut. Item E (mining-agent consolidation) shipped 2026-09-15. Item G (autonomy-slider
  coverage) is superseded by the Phase 1 risk tiers.
- About 30 files still mention retired commands or agents; many are legitimate
  migration notes. Sweep them during the Phase 4 command cut.
- Frozen: Codex and ChatGPT Work portability. Adapters are kept passing, not extended.

## Parked (see `parked/`)

| Proposal | Why parked |
|---|---|
| `parked/jarvis-app.md` | Standalone desktop app. A separate product bet; revisit only on strong demand. |

## Current plugin versions

The source of truth is each plugin's `plugin.json`, mirrored in
`.claude-plugin/marketplace.json` and the README "Plugin versions" table.
