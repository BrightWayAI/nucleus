# Live connector integration testing

Static validation cannot prove that a real workspace can read its calendar, mail,
CRM, Slack, Drive, enrichment provider, or transcript source. Nucleus therefore has a
host-run live probe workflow plus a deterministic, privacy-preserving report validator.

## Safety boundary

- Use designated sandbox accounts, test channels, folders, contacts, and records.
- V1 probes are read-only. They never send mail, modify CRM, create calendar events,
  post to Slack, upload files, or change source data.
- Bound every query to one result or a narrow empty query.
- Reports contain only tool identifiers, latency, record counts, content block types,
  and response key names. Never copy raw connector content into a release repository.
- A missing or unauthorized connector is `fail` or `skip`, never `pass`.

## Run the probes

Install Core Ops in the host being certified and invoke `test-connectors` naturally,
with `/test-connectors` in Claude, or `$core-ops:test-connectors` in Codex. Select a
profile from `connector-tests/plan.json`:

- `operator`: calendar, mail, and CRM;
- `collaboration`: Slack and Drive;
- `research`: contact enrichment and transcripts;
- `full`: every connector above.

The workflow performs actual connector calls through the host's authorized tools. It
does not accept a user's statement that a connector is configured as proof. Run it
separately in Claude and ChatGPT because authorization, tool schemas, and availability
are host-specific even though the test plan is shared.

## Validate evidence

Copy `connector-tests/report.template.json`, replace the placeholders with the
metadata-only results emitted by the workflow, then run:

```bash
python3 scripts/validate_connector_report.py /path/to/report.json \
  --release 2026.09.0-rc.1 \
  --profile operator
```

The validator rejects unknown connectors, missing required passes, duplicate results,
and raw-payload fields. A coordinated release can require evidence with:

```bash
python3 scripts/release_ecosystem.py check \
  --release 2026.09.0-rc.1 \
  --require-live
```

The default candidate contract requires one `operator` report from Claude and one from
ChatGPT. Change that requirement explicitly in `release.json` when the release targets
a different supported-host set; do not silently waive a failed connector.
