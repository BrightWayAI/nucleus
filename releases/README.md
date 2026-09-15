# Nucleus release snapshots

Each child directory is a coordinated, immutable catalog candidate. `release.json`
pins all 13 plugin versions and Git commits. The OpenAI marketplace inside the same
directory carries those full SHA pins so workspace sync cannot silently advance one
plugin ahead of its peers.

`2026.09.15-baseline` records the last published heads before release coordination was
introduced. It is intentionally a candidate with no live connector evidence and must
not be promoted as a certified release.

Follow `../docs/RELEASING.md` to create, test, and promote the next candidate.
