# Codex cloud readiness — 2026-10-30

## Latest review after Claude's fixes

Cortex is now 4.30.0 (`d857c001251fd675d079d063bb4409c396cd027c`), with
read-only `root-status` and unreachable-root handling. Claude also added companion
workflow guards and created release candidate `2026.10.30-rc.5`.

The remaining generated OpenAI instruction gap has now been fixed locally: the
Nucleus generator and all eight companion portability references include the full
resolution order, reachability check, cloud bootstrap/sync rules, private-repo
boundary, and per-job verification. Ecosystem checks now cover materialized versus
unmaterialized cloud roots, pointer precedence, and invalid-pointer rejection.
All four required Nucleus checks pass. Existing release pins are unchanged.

The eight companion patch versions are now committed and pushed, and coordinated
candidate `2026.10.30-rc.6` pins their published commits. Fresh ChatGPT operator
evidence passes for rc.6; Claude evidence is still required before promotion.
Do not reuse rc.3 connector evidence as proof for rc.6. The actual cloud read/write test and schedule migration remain
unverified; no real memory was edited.

## Earlier local verification (historical)

- Cortex `main` is 4.29.4 (`1c1cd13f6e57097de26fa70b8595e72c7d60c2ca`).
- `codex plugin list --marketplace nucleus --json` reports all nine plugins enabled,
  including Cortex 4.29.4. The existing conversation loaded 4.28.2 wrappers; start a
  new conversation to load the current installed version.
- The local pointer resolves to `/Users/zachwagner/cortex-root`. Both org and
  private checkouts have `.cortex-role` markers and were clean at inspection.
- The latest observed local sync receipt reported success for both checkouts.
  This is a local receipt, not proof of cloud authorization.
- All 35 tests in `tests.test_repo_sync` and `tests.test_config_root` passed using
  disposable fixtures, including detached HEADs, convergence, and private-path
  protection. No real memory writes or remote pushes were used for those tests.
- The current session does not grant write access to that root. The user config
  inspected contains no `sandbox_workspace_write.writable_roots` setting.
- Release rc.3 connector evidence validates, but calendar/mail/CRM evidence does
  not certify GitHub memory access or cloud writes.

## Ecosystem follow-up status

1. Implemented locally: updated `scripts/generate_openai_adapters.py:portability_md`
   and regenerated all eight companion references against Cortex's root and sync
   contract. Published in the companion versions pinned by rc.6.
2. Distinguish filesystem-capable Codex cloud sessions from MCP-only ChatGPT
   sessions. Cortex's ChatGPT setup documentation says to bootstrap/sync through
   the bridge, but `adapters/chatgpt_work/server.py` currently exposes neither
   operation. Such a bridge needs host-side lifecycle orchestration or explicit,
   bounded tools before that route can be certified. Codex with shell access can
   use the existing CLI; it does not need those MCP additions.
3. Coordinate resulting plugin versions through a new host-neutral release;
   do not replace the rc.3 plugin pins or hand-edit generated marketplaces.

Only the shared OpenAI instructions and validation changed; no release was promoted.

## Cloud setup and read test

Use a private Codex Cloud environment with the Cortex code repository plus the
user's org and private memory repositories attached. Keep sharing set to Only me.
The local Mac path is not a cloud mount. Use the root resolved inside the cloud
environment and grant only that root the necessary filesystem access.

Paste this into the environment setup task:

```text
Verify Cortex cloud memory using Cortex 4.30.0 or a reviewed later release.
Read the Cortex repository AGENTS.md, core-contract.md sections 1 and 11B,
and capability-matrix.md. Discover the two attached memory repositories by
their .cortex-role markers. Do not display memory contents, secrets, credential
helpers, or raw connector payloads.

First inspect both checkouts for local changes and verify that the org/private
roles are unambiguous. If either is dirty, stop before bootstrap. If credentials
or repository attachments are missing, report the exact missing capability;
do not copy credentials from another machine or invent a replacement root.

Run the existing cortex_cli.py bootstrap --skip-derived with an explicit cloud
root, adopting the designated checkouts. Report only success/failure, role
markers, resolved path, clean/dirty status, and whether private symlinks resolve
inside the private checkout. Bootstrap may create local layout links and ignore
rules; do not edit durable memory, commit, or push during this first stage.

Then prepare a synthetic private staged note with no business data and show its
exact path and contents for approval. Before a real sync, inspect both checkouts
again: sync commits all outstanding changes in both, so do not run it if it would
include unrelated changes. After approval, use the shared CLI for the test write,
sync through cortex_cli.py, and verify the exact resulting file through an
independent remote read. Report cloud read and cloud write results separately.
Do not mark the round trip passed from a local commit or fixture test alone.
```

The real cloud test remains unperformed. The legacy CLI returned no tasks, which
does not establish whether current cloud environments exist. Native app inspection
was blocked by the computer-use tool, so no environment was selected or modified.

Official setup reference:
https://learn.chatgpt.com/docs/environments/cloud-environments
