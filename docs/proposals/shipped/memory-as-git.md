> **SHIPPED.** Implemented across cortex v4.12.0 (`/setup-identity` Step 3.6 init · `/end-day` Step 5.8 commit · `/morning` Step 0.5 diff review · gitignore templates · write-lock) and completed in v4.13.0 (`/end-day` Step 5.8 init-offer when absent) + core-ops v0.3.2 (`/diagnose` Step 1D health line). The "NOT IMPLEMENTED" note below is the original draft state, retained for historical context. Privacy levels: local-only (default) + remote/`push_on_close` are wired; self-hosted works via any git remote.

---

# Memory-as-git — versioned vault with daily diff review

_Created: 2026-05-20_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Spec only. Implementation deferred._
_Inspiration: Jason Liu's "codex-maxxing" — "I review diffs when agents update the vault. Git diff is a review surface for memory."_

---

## Why this exists

Liu's load-bearing pattern: **the vault is version-controlled, and reviewing diffs is a daily ritual.** This forces agents to compress experience into durable, inspectable form, prevents threads from "quietly accumulating vibes in conversation history," and turns memory mutations into a thing you can audit.

Nucleus already has the substrate (`<config-root>/memory/` is plain markdown), the privacy gitignore (cortex v4.7.2), and a daily ritual (`/end-day` / `/morning`). The missing piece: actually commit those changes to git and surface the diff for review.

This proposal formalizes the pattern:

- `<config-root>/memory/` is a git repository (init on first run if not already).
- `/end-day` Step 5.8 (new) commits the day's changes with a structured message.
- `/morning` Step 0.5 (new) reads `git diff yesterday..HEAD` and shows the user what changed in memory overnight (from `/listen` mining + `/sweep` heartbeat-staged + drift-detected supersedes + auto-commits during sessions).
- Optional: push to a private GitHub repo (or self-hosted git) for off-machine backup + multi-device sync.

The user reads the diff each morning. Memory becomes a thing you *audit*, not just *recall from*.

---

## What this changes for the user

Before:
- Memory mutates throughout the day. No durable audit trail beyond per-node changelogs and `memory/log.md`.
- "What did Claude write to memory yesterday?" requires reading every changed file or running `find -newer`.
- Restoring a memory state ("undo last night's `/morning` merge") is impossible.

After:
- Each day's memory state is a git commit. `git log --oneline memory/` shows the history.
- `/morning` greets you with: "Here's what changed in memory since yesterday: 14 lines added, 3 modified, 1 demoted. Open the diff?"
- Memory mistakes are recoverable: `git revert HEAD` rolls back the last day's changes.
- If you push to a remote, your second brain has off-site backup. Cross-machine sync becomes a `git pull`.

---

## Architecture

### Repository layout

`<config-root>/memory/` becomes a git repository. Its working tree is the same files cortex already maintains — no migration required. Git metadata (`.git/`) sits at `memory/.git/`.

Cortex's existing `.gitignore` template stays in `<config-root>/.gitignore` (governs the parent directory; `archive/`, `briefs/`, `plugins/` are excluded). A **second, memory-specific** `.gitignore` lives at `memory/.gitignore` and governs what's tracked *within* memory:

```gitignore
# memory/.gitignore — what stays untracked even within the memory git repo

# Operational state (changes every tick; pollutes diffs)
.state.json
log.md                     # too noisy — operations log lives outside diffs

# Staged drafts (reviewed elsewhere; committed when accepted)
staged/

# Internal caches
hot.md                     # regenerated; would dirty every diff
index.md                   # auto-maintained; same reason
```

**Wait — is excluding `hot.md` and `index.md` right?** They're regenerated on every `/end-day`, so they'd appear in every diff and drown out signal. They're already deterministic re-renders of the rest of memory; if the underlying nodes are in the diff, the index/hot are derivable. **Yes, exclude them.** (Add a one-time `git rm --cached` step in the v4.9 migration if they were tracked before.)

`log.md` is the operations chronicle. It changes every command run. Excluding it from diffs keeps the daily-review surface focused on *knowledge* changes, not *operation* changes. The log still exists and is grep-able — just not in git.

### Init logic

New cortex command: `/snapshot-init` (or fold into `/setup-identity` Step 3.5 alongside `.gitignore` write).

```
Check whether <config-root>/memory/.git/ exists.
  If exists → log "memory repo already initialized; skipping init"; exit.
  If not exists:
    cd <config-root>/memory
    git init
    git config user.name "<from identity.md>"
    git config user.email "<from identity.md>"
    Write memory/.gitignore with the template above.
    git add .
    git commit -m "Initial memory snapshot"
```

Idempotent. Safe to re-run.

### Commit logic (within `/end-day`)

New Step 5.8 in `/end-day` (after Step 5.7 log):

```
Check whether <config-root>/memory/.git/ exists.
  If not → skip (memory-as-git not enabled; nothing to do).
  Else:
    cd <config-root>/memory
    git add .
    git diff --cached --stat   ← compute the day's diff summary
    If staged changes is empty → exit (nothing to commit).
    Compose commit message:
      "<today_local> day close — <N> nodes touched, <K> entries added, <D> demoted, <A> archived. Commit: <commit-source-summary>."
      where commit-source-summary lists what touched memory today:
        e.g., "1 /listen merge via /morning, 3 /remember runs, 1 /research-gaps merge, /cleanup section H archive."
    git commit -m "<message>"
```

The commit-source summary derives from `memory/log.md` entries for today — read which commands wrote, count occurrences. No new tracking needed.

**Optional push** (configurable per user-context):
- `memory_as_git.remote: <url>` set → after commit, run `git push origin main`.
- Default: no remote configured; commits are local-only.

### Diff review (within `/morning`)

New Step 0.5 in `/morning` (before Step 0 — runs even when no `/listen` draft exists):

```
Check whether <config-root>/memory/.git/ exists.
  If not → skip (memory-as-git not enabled).
  Else:
    cd <config-root>/memory
    Read the date of HEAD~1 commit.
    If HEAD~1 is from today (so no overnight commit happened) → skip with a one-liner: "No memory commit since today's last close."
    Else:
      Compute git diff HEAD~1..HEAD:
        - Files changed (count by directory: client/, person/, topic/, etc.)
        - Insertions / deletions per file
      Surface:
        "Memory changed overnight:
          - 3 client nodes updated (acme, contoso, initrode)
          - 2 person pages added (sarah-chen, jamie-park)
          - 1 topic node demoted entry (ai-governance)
          Open the diff? (y / skim / skip)"
      On `y`: display `git diff HEAD~1..HEAD` paginated.
      On `skim`: display file-level summary only.
      On `skip`: continue to Step 1.
```

The diff IS the review surface. The user can spot bad commits before they compound into wrong context for tomorrow's sessions.

### Optional: per-commit `/morning` integration

If `/listen` ran overnight, the commit message includes `/listen` as a source. After review of the diff, `/morning` proceeds to its existing flow (walk `.commit-drafts/`). The diff review is *additional* to the proposal review, not a replacement — proposals stage *before* commit; the diff captures *after* commit.

---

## Privacy decisions

Memory contains personal information: people you've met, things you've learned, your relationships, your work. Pushing to a remote means it's stored off-machine.

Three configurable levels:

| Level | Description | Privacy posture |
|---|---|---|
| **local-only** (default) | Git repo lives only on your machine. No remote. | Highest — never leaves disk. |
| **private GitHub** | Push to a private GitHub repo. | Moderate — stored on Microsoft servers; subject to GitHub's data policy; encrypted at rest but accessible to GitHub. |
| **self-hosted** | Push to user's Gitea / Forgejo / GitLab instance. | High — user controls the storage. |

Configured in `cortex.user-context.md`:

```yaml
memory_as_git:
  enabled: true
  remote: "git@github.com:yourname/my-memory.git"   # leave blank for local-only
  push_on_close: true                                # if remote set, push after each /end-day commit
```

**What the gitignore template covers (already done in v4.7.2):**
- `archive/` (raw email/Slack/transcripts) — never in memory repo.
- `briefs/` — out of scope; daily snapshots not knowledge.
- `plugins/` — config; sensitive (API keys via referenced files), excluded.

**What the memory-level gitignore adds (new):**
- `staged/` (proposals pending review)
- `log.md`, `hot.md`, `index.md`, `.state.json` (operational/derived)

The combination means a git push only contains:
- User profile (`user.md`)
- DASHBOARD.md
- Node files (people, clients, topics, domains) — knowledge content
- Decay config + research-skip-log
- Per-node changelogs

Sensitive? Yes — these are your relationships and what you know. But less sensitive than raw archives. Most consultants would be comfortable with a private GitHub repo for this.

---

## Integration with existing pieces

| Piece | Effect |
|---|---|
| `/end-day` | New Step 5.8 — commit memory after Step 5.7 log. Idempotent: empty commit is a no-op. |
| `/morning` | New Step 0.5 — surface overnight diff. Runs even when no `/listen` draft exists. |
| `/setup-identity` | Step 3.6 (new) — offer to init memory-as-git on first run. Default: yes for local-only; remote is opt-in via prompt. |
| `/start-nucleus` | Surfaces memory-as-git enablement as a step. Default-on for local-only. |
| `/cleanup` | Adds a `git gc` step at the end of long runs (optional — keeps the repo lean). |
| `/diagnose` | Reports memory-as-git status: enabled? last commit when? remote configured? last successful push? |
| `memory/log.md` | Excluded from git tracking (covered above). Stays as the operations chronicle outside the diff stream. |
| cortex `.gitignore` template | Adds memory/.gitignore template alongside the parent-level one. |
| `/setup-obsidian` | The `.obsidian/workspace.json` and friends already go in the parent gitignore. Obsidian users see git history within Obsidian's "Source Control" view if they install the Git plugin. |

---

## What this is NOT

- **Not a substitute for `.commit-drafts/` review.** Staged proposals are reviewed *before* commit (via `/morning` walk). The diff is the safety net *after* commit.
- **Not multi-device sync.** Pushing to a remote enables cross-machine pull, but conflict resolution is manual (you'd `git pull --rebase` and resolve any merge conflicts). True real-time sync would need CRDTs or a sync service. Out of scope.
- **Not undo for individual commands.** `git revert` rolls back a *day's worth* of changes. Granular undo (per-`/remember`) would require commit-per-command, which floods the log. Day-granularity is the right trade-off.
- **Not telemetry.** Local-only mode means BrightWay never sees your memory.

---

## Build plan (~half a day)

1. **Spec the `.gitignore` template** for memory level (in `cortex/references/memory-gitignore-template.md`).
2. **New `/snapshot-init` command** (or fold into `/setup-identity` Step 3.6).
3. **`/end-day` Step 5.8** — commit after log step.
4. **`/morning` Step 0.5** — surface diff.
5. **`/setup-identity` Step 3.6** — first-run init prompt.
6. **Config schema** — add `memory_as_git:` section to user-context template.
7. **Migration** — for existing cortex installs, the next `/end-day` after upgrade runs init if memory/ isn't a repo yet.
8. **`/diagnose` integration** — health line.
9. **Bump cortex to v4.9.0** (minor — new commands + new chain step).
10. **Update CHANGELOG, CLAUDE.md, router intent table** (`"show me the memory diff" / "what changed in memory" / "memory history"` → `git diff` invocation).

Total: ~4-6 hours single-engineer.

---

## Open decisions

1. **Default to enabled or opt-in?** Recommend **default-on for local-only**. Pushing is opt-in. Most users gain audit without privacy risk.
2. **Commit cadence — only `/end-day`, or after every memory mutation?** Recommend **only `/end-day` (plus `/morning` after merge).** Per-mutation commits would flood the log; daily-granularity matches the review cadence.
3. **What about Cowork running `/remember` mid-day — should those commit too?** Recommend **no**. Mid-day commits would create a noisy log. `/end-day` rolls everything up into one commit per day.
4. **What if `/end-day` is skipped for several days?** The accumulated changes commit on the next `/end-day` as one big day-rollup. Or `/morning` could detect "no commit since N days" and offer to commit current state.
5. **Should `.research-drafts/` be tracked too, or just `staged/`?** Recommend **exclude staged entirely** (they're transient). Once a research draft is merged via `/merge-research-draft`, the merge writes to memory nodes which DO get committed.
6. **Optional `git commit -S` (signed commits)?** Useful for some users who want cryptographic audit. Out of v1; surface as an advanced config later.

---

## Karpathy alignment

This proposal is the direct implementation of Liu's "git diff as review surface for memory" pattern. Specifically:

- ✅ Vault-as-app (already true)
- ✅ AGENTS.md / CLAUDE.md as schema (already true)
- ✅ **Git diff as review surface (this proposal makes it real)**
- ✅ Inspection over generation — the diff is the inspection moment
- ✅ Memory mutations have somewhere to live and somewhere to be reviewed

This is one of the highest-leverage Karpathy patterns Nucleus is missing. Once shipped, the daily flow becomes:

```
Overnight: /listen mines → drafts staged
Morning:   /morning → review diff (what changed) + walk staged proposals
Day:       use Nucleus normally; memory mutates as you /remember, etc.
Evening:   /end-day → commit the day; optional push
```

Each day produces one commit. Over a year: 250-300 commits. A real history of how the second brain evolved.

---

## Why this is worth doing

Three reasons:

1. **The user explicitly asked for it.** "We should be committing the memory files to GitHub and reading the diff each day like that article proposed." Direct request.
2. **It's a cheap unlock for a load-bearing pattern.** ~half a day of work; produces a daily ritual that compounds.
3. **It addresses the hardest mistrust failure mode in any memory system: "Claude wrote something to memory I didn't see."** With this, every mutation is visible the next morning.

The honest counter-case: if you're not going to actually *read* the diff each morning, this just adds steps. The review only works if the human shows up. So commit to the ritual before the ritual ships.
