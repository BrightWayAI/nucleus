# Obsidian as the human UI for Nucleus

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus marketplace_
_Status: Spec ready. No work has started._
_Phase: 2 of the "Nucleus as JARVIS" initiative (Phase 1 = nucleus-router, Phase 3 = productization)._

---

## Why this exists

`<config-root>/` is already a folder of markdown files with wikilinks (`[[person/sarah-chen]]`, `[[client/acme]]`). It's *almost* an Obsidian vault — just missing the workspace config and a top-level entry point. Adding those turns the second brain into:

- A **graph view** of every person, company, topic, and client in cortex memory, with edges drawn from real wikilinks.
- A **mobile second brain** via Obsidian Sync or iCloud — read on phone, write from desktop or Claude.
- A **Dataview-powered dashboard** that replaces `/nucleus-dashboard` for users who prefer browsing to commanding.
- A **daily notes plugin integration** where today's daily-brief artifact becomes today's daily note.

Two interaction surfaces, one substrate: speak to Claude (router), browse in Obsidian.

The cost is small: a `.obsidian/` workspace config, a top-level `VAULT.md` map, and a single `/setup-obsidian` command in cortex that scaffolds it.

This phase complements but does not depend on cortex v4.5's `memory/index.md` (Phase 1) — if v4.5 ships, Obsidian users get the catalog as their home page for free.

---

## Decisions to make (flag before implementing)

1. **Where does `/setup-obsidian` live?** Cortex owns `<config-root>/` layout, so the natural home is cortex. Alternatives: new tiny `nucleus-obsidian` plugin (overkill for one command), or fold into nucleus-router (wrong — router is about routing).
2. **Opt-in or default?** Recommend opt-in via `/setup-obsidian`. Users who don't want Obsidian should not get a `.obsidian/` directory in their config root.
3. **Bundle plugins or just config?** Obsidian community plugins (Dataview, Tasks, Templater) are installed per-Obsidian-vault, not via Claude. Recommend: scaffold only the `workspace.json` + `app.json` + `core-plugins.json` files cortex can write; document the community plugins as a separate manual step in the setup doc.
4. **Daily Notes integration:** make daily-brief's markdown snapshot at `<config-root>/briefs/YYYY-MM-DD.md` *be* the Obsidian daily note? Recommend yes — set Obsidian's daily-notes folder to `briefs/` with format `YYYY-MM-DD`. Zero migration.

---

## Layout after `/setup-obsidian` runs

```
<config-root>/
├── VAULT.md                       ← top-level entry point (NEW)
├── .obsidian/                     ← workspace config (NEW)
│   ├── app.json
│   ├── workspace.json
│   ├── core-plugins.json
│   ├── community-plugins.json
│   └── plugins/                   ← (empty; user installs Dataview etc manually)
├── identity.md
├── voice.md
├── memory/                        ← already exists; now graph-visible
│   ├── index.md                   ← (added by cortex v4.5 Phase 1 — Obsidian home page)
│   ├── DASHBOARD.md
│   ├── user.md
│   ├── client/*.md
│   ├── person/*.md
│   ├── company/*.md
│   ├── topic/*.md
│   └── domain/*.md
├── plugins/                       ← per-plugin config; mostly read-only from Obsidian
├── briefs/                        ← daily-brief snapshots; ALSO Obsidian daily notes
└── ... (other plugin data)
```

The user opens `<config-root>/` in Obsidian. `VAULT.md` is their home page. From there, links to `memory/index.md` (the catalog), `DASHBOARD.md`, today's brief, active clients, etc.

---

## What `VAULT.md` looks like

```markdown
# Nucleus vault

> Your second brain + business OS. AI writes here. You write here. Same files.

## Today

- [[briefs/2026-05-16|Today's brief]]
- [[memory/DASHBOARD|Auto-recall dashboard]]
- [[memory/user|My profile]]

## Memory

- [[memory/index|Memory catalog]] — every node, grouped by type
- [[memory/.decay-config|Decay thresholds]] — hand-editable

## Active engagements

```dataview
TABLE confirmed AS "Last confirmed", status
FROM "memory/client"
WHERE !contains(file.name, "archive")
SORT confirmed DESC
```

## Active people

```dataview
TABLE confirmed AS "Last confirmed", role
FROM "memory/person"
WHERE !contains(file.name, "archive")
SORT confirmed DESC
LIMIT 20
```

## Capability map

The Nucleus router lives in your Claude session, not in this vault. To see every capability, ask Claude `/route`.

Common operations:
- "What's on my plate today" → `/brief`
- "I just met X" → `/remember`
- "Wrap up the day" → `/end-day`
- "Plan tomorrow" → `/plan-tomorrow`

## Pages I might want

- [[Onboarding|New to Nucleus? Start here]]
- [[Migration-from-flat-notes|Migrating from a flat notes app]]
```

The dataview blocks render natively once the user installs the Dataview plugin. Without Dataview, they render as code blocks — degraded but not broken.

---

## What `.obsidian/app.json` contains

Minimal, opinionated config. Cortex writes this:

```json
{
  "alwaysUpdateLinks": true,
  "newLinkFormat": "shortest",
  "useMarkdownLinks": false,
  "defaultViewMode": "preview",
  "showLineNumber": false,
  "spellcheck": false,
  "promptDelete": true,
  "newFileLocation": "folder",
  "newFileFolderPath": "memory",
  "attachmentFolderPath": "attachments"
}
```

Rationale:
- `useMarkdownLinks: false` keeps cortex's existing `[[wikilink]]` syntax working.
- `newLinkFormat: shortest` lets the user type `[[sarah-chen]]` and have it resolve to `[[person/sarah-chen]]`.
- `defaultViewMode: preview` — read-first, edit-on-click.
- `newFileFolderPath: memory` — new notes go where the second brain lives.
- `attachmentFolderPath: attachments` — keeps any pasted images out of `memory/`.

---

## `.obsidian/core-plugins.json` — what to enable

```json
[
  "file-explorer",
  "global-search",
  "switcher",
  "graph",
  "backlink",
  "outgoing-link",
  "tag-pane",
  "page-preview",
  "daily-notes",
  "templates",
  "outline",
  "starred",
  "command-palette",
  "markdown-importer",
  "random-note",
  "note-composer",
  "format-converter"
]
```

Daily-notes is the load-bearing one for the brief integration.

---

## Daily-notes integration

In `.obsidian/daily-notes.json` (written by `/setup-obsidian`):

```json
{
  "format": "YYYY-MM-DD",
  "folder": "briefs",
  "template": "",
  "autorun": false
}
```

This makes `<config-root>/briefs/YYYY-MM-DD.md` (produced by daily-brief's `/brief`) the canonical Obsidian daily note. The Calendar plugin lights up. Cmd+D in Obsidian jumps to today.

No work needed in daily-brief itself — it already writes `briefs/YYYY-MM-DD.md`. The Obsidian config just points at the right folder.

---

## Recommended community plugins (manual install via Obsidian)

Documented in the setup doc, not bundled (Obsidian community plugins aren't installable from outside Obsidian).

| Plugin | Why |
|---|---|
| **Dataview** | Renders the queries in `VAULT.md` and lets the user write their own. |
| **Tasks** | Pulls actionable items from anywhere in the vault into a daily TODO surface. |
| **Calendar** | Sidebar calendar with hot-keys to today's brief. |
| **Templater** | Optional: lets the user define their own daily note template if they want to overlay structure on top of daily-brief's output. |
| **Periodic Notes** | Optional: extends daily-notes to weekly/monthly notes if the user wants to mirror cortex's `/end-week`. |
| **Mobile (built-in)** | Free with Obsidian. Activates the same vault on iOS/Android. |

The setup command prints these as a suggested list and links to install instructions.

---

## `/setup-obsidian` command flow (cortex side)

1. **Check `<config-root>/.obsidian/` doesn't already exist.** If it does, ask: overwrite, merge, or abort.
2. **Print the plan.** "I'll create `<config-root>/.obsidian/` with workspace settings, a `VAULT.md` home page, and configure daily-notes to use `briefs/`. Continue?"
3. **Write files** on confirm:
   - `<config-root>/.obsidian/app.json`
   - `<config-root>/.obsidian/core-plugins.json`
   - `<config-root>/.obsidian/daily-notes.json`
   - `<config-root>/VAULT.md`
4. **Print next steps.** "Open `<config-root>/` in Obsidian (File → Open vault → select this folder). Then install Dataview from Settings → Community plugins so the queries in VAULT.md render. Mobile: install Obsidian on phone and sync via iCloud or Obsidian Sync."

### Failure modes

- **User doesn't have Obsidian installed.** Setup writes files anyway — they're inert without Obsidian, and the user might install later.
- **`<config-root>/.obsidian/` exists from a previous Obsidian setup.** Don't clobber the user's existing workspace. Offer merge mode (write only files that don't exist) or skip.
- **Cortex memory/index.md not yet generated.** `VAULT.md` links to it preemptively; the link will resolve as soon as v4.5's indexer runs. Until then, it's a broken link — acceptable since the user clearly opted into Obsidian and presumably knows the index is forthcoming.

---

## Daily-brief integration (no code change)

daily-brief already writes `<config-root>/briefs/YYYY-MM-DD.md`. Once Obsidian's daily-notes folder is set to `briefs/`, that markdown *is* the daily note. Two consequences:

1. **The brief is now mobile-readable.** Open Obsidian on phone, tap today's date, read the brief. Annotations on the Cowork artifact still work; the markdown is read-only on phone.
2. **The brief participates in the graph.** If today's brief mentions `[[person/sarah-chen]]` (which it should once Phase 3 person-page integration lands), the link shows up in Sarah's backlinks pane.

No daily-brief plugin code changes needed. The integration is config-only.

---

## Acceptance criteria

- [ ] `commands/setup-obsidian.md` added to cortex.
- [ ] `skills/setup-obsidian/SKILL.md` added to cortex with trigger conditions ("set up Obsidian," "enable graph view," "make this work on mobile").
- [ ] `VAULT.md` template stored at `references/obsidian-vault-template.md` in cortex; rendered (with light substitution) by setup-obsidian.
- [ ] `references/obsidian-config-templates/` directory in cortex with `app.json`, `core-plugins.json`, `daily-notes.json` templates.
- [ ] Setup command does not clobber an existing `.obsidian/` directory.
- [ ] Nucleus root README gains an "Obsidian (optional)" section pointing at this proposal once shipped.
- [ ] Cortex CLAUDE.md updated with the `/setup-obsidian` command and a "Obsidian vault layout" reference.
- [ ] Nucleus-router's intent table adds rows for "set up Obsidian," "enable graph view," "make this work on mobile" → `/setup-obsidian`.

---

## Productization angle

This is the cheapest "wow" demo Nucleus has. A 5-minute install path that ends with the user seeing their own knowledge graph in Obsidian feels like JARVIS the moment they look at it.

Recommended SMB-tour-style demo flow:
1. Run `/setup-identity` (cortex) — answer 8 questions about who you are.
2. Run `/setup-voice` — paste two sample emails.
3. Run `/setup-obsidian` (cortex v4.5+) — scaffolds the vault.
4. Open the vault in Obsidian. Graph view shows you as the center node with edges to all your initial identity context.
5. Run `/brief` (daily-brief). Open today's date in Obsidian. The brief is your daily note.
6. Run `/recall acme` (cortex). See it surfaced both in the Claude chat *and* visible in Obsidian as you click into the Acme node.

The demo is the product: same data, two views, AI keeps it in sync. Productization is mostly about polishing this flow.

---

## Out of scope (future work)

- **Obsidian plugin (true bidirectional sync).** A real Obsidian-side plugin that surfaces cortex actions inside Obsidian (e.g., a button on a person page that says "ask Claude to draft outreach"). Big lift. Worth doing after the markdown-only path is validated.
- **Obsidian publish integration.** Use Obsidian Publish to expose a curated subset of the vault as a public knowledge site (e.g., for thought leadership). Out of scope for v0.1.
- **Logseq / Foam / Dendron alternatives.** Same wikilink substrate; setup commands for other tools could be added later as `/setup-logseq`, etc. Not v0.1.
- **Auto-installing community plugins.** Obsidian's plugin API doesn't expose external install from cortex's side. The setup doc lists recommended plugins; the user installs.
- **Encrypted vault for shared/team use.** If multiple operators share a `<config-root>`, vault-level encryption (e.g., Obsidian's Sync end-to-end encryption) is a manual configuration. Not a Nucleus concern.
