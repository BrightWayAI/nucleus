# Nucleus roadmap

_Last updated: 2026-06-08_

This is the active roadmap. **Top-level `docs/proposals/*.md` = open / not-yet-built.** Shipped specs live in `shipped/` (archived with a SHIPPED banner). Deferred-indefinitely specs live in `parked/` (not on this roadmap).

## 🟢 Active / next up

| Proposal | Status | Notes |
|---|---|---|
| `sweep-heartbeat.md` | Not started (~1–2 wk) | `/sweep` heartbeat every ~3h: mines the day's surfaces into staged proposals reviewed at `/end-day`. **Gated on** dogfooding `/listen` + `/morning` first. |

### Loose follow-ups (no standalone spec yet)
- **cleanup-pass-1 items E–G** (deferred from cortex v4.8.1): mining-agent consolidation, `/end-day` decomposition, autonomy-slider coverage across all gated commands. See `shipped/cleanup-pass-1.md`.

## ✅ Recently shipped (see `shipped/`)

| Shipped as | Spec |
|---|---|
| daily-brief v0.5.0 + cortex v4.13.0 + core-ops v0.3.2 | `shipped/end-day-routine-improvement.md` |
| cortex v4.12.0 + v4.13.0 + core-ops v0.3.2 (memory-as-git) | `shipped/memory-as-git.md` |
| nucleus-router v0.2.0 + cortex v4.9.0 | `shipped/chief-of-staff-evolution.md` |
| relationships v0.1.0 → v0.2.3 | `shipped/relationships-plugin.md` |
| cortex v4.10.0 (wikilinks) | `shipped/wikilink-density.md` |
| cortex v4.8.1 (items A–D) | `shipped/cleanup-pass-1.md` |
| (earlier) cortex v4.5–4.7, nucleus-router v0.1, Obsidian, productization | other files in `shipped/` |

## ⏸️ Parked (see `parked/` — NOT on the roadmap)

| Proposal | Why parked |
|---|---|
| `parked/jarvis-app.md` | Standalone Tauri desktop app — separate product bet; revisit only on strong marketplace-demand signal. |

## Current plugin versions

Authoritative source is each plugin's `plugin.json`; mirrored in `.claude-plugin/marketplace.json` and the README table for at-a-glance reference. See the README "Plugin versions" table.
