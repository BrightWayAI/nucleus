# Nucleus — Codex handoff

Nucleus is the master marketplace for 9 independently versioned plugins. It is not a
runtime plugin. Read `README.md` for the product map and `docs/contracts.md` before
changing cross-plugin behavior.

For release work, follow `docs/RELEASING.md`. `release.json` inside a versioned release
directory is the single host-neutral release decision. Do not create a Codex-only
release or hand-edit a generated pinned marketplace.

For connector certification, follow `docs/CONNECTOR_INTEGRATION_TESTING.md`. Live
connector calls are read-only, use designated sandbox data, and produce metadata-only
reports. Never commit connector payloads or credentials.

Before trusting a change, run:

```bash
python3 scripts/generate_openai_adapters.py --check
python3 scripts/check_openai_ecosystem.py
python3 scripts/smoke_codex_marketplace.py
python3 scripts/release_ecosystem.py check --all
```

Plugin behavior belongs in each plugin repository. Shared release coordination,
cross-plugin contracts, and connector certification policy belong here.
