# Coordinated Nucleus releases

Nucleus has two catalog channels:

- The root marketplace is the rolling development catalog.
- `releases/<release-id>/` is an immutable coordinated snapshot. Its native
  OpenAI marketplace pins every plugin to a full Git commit SHA.

The release contract is `release.json`. It records the version and commit for all
9 plugins plus the live-connector evidence required before promotion. OpenAI's
GitHub marketplace format supports full commit SHA pins. Claude consumes the same
plugin versions and shared release contract; do not maintain a separate release
decision in Claude instructions.

## Prepare a candidate

1. Merge and push every participating plugin change.
2. Confirm all 9 sibling checkouts are clean and on their intended release commits.
3. Run the ecosystem checks:

   ```bash
   python3 scripts/generate_openai_adapters.py --check
   python3 scripts/check_openai_ecosystem.py
   python3 scripts/smoke_codex_marketplace.py
   ```

4. Create the coordinated snapshot from the published heads:

   ```bash
   python3 scripts/release_ecosystem.py snapshot \
     --release 2026.09.0-rc.1 \
     --revision origin/main \
     --write
   ```

   The command refuses dirty sibling repositories unless `--allow-dirty` is supplied
   explicitly. That override is appropriate only when snapshotting a different,
   already-published revision; it never includes uncommitted work.

5. Run `$ops:test-connectors` or `/test-connectors` in each required host against
   designated sandbox accounts. Save only the sanitized JSON reports under the
   candidate directory and list their relative paths in `connectorEvidence`.
6. Validate the candidate:

   ```bash
   python3 scripts/release_ecosystem.py check \
     --release 2026.09.0-rc.1 \
     --verify-checkouts \
     --require-live
   ```

7. Review the diff, change `status` from `candidate` to `released`, and create the
   matching Nucleus Git tag only after the strict check passes.

## Install a coordinated release

For ChatGPT workspace import, use the Nucleus repository URL and set **Path** to the
release directory, for example `releases/2026.09.0`. For Codex, register that directory
as the marketplace source. The rolling root remains available for development.

## Versioning rule

Plugin versions remain independent semantic versions. The Nucleus release ID uses
`YYYY.MM.PATCH`, with optional `-rc.N`. A coordinated release changes whenever any
plugin commit pin changes. A breaking shared-file contract requires compatible plugin
updates in the same candidate and a documented migration in `docs/contracts.md`.
