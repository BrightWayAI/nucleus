# Contributing to BrightWayAI Plugins

Thanks for considering a contribution. This guide covers contributing to any plugin in the [BrightWayAI marketplace](https://github.com/BrightWayAI/nucleus).

The marketplace itself (this repo) is a thin pointer file — almost no contributions land here. **Plugin contributions go to each plugin's individual repo.**

## Marketplace structure

```
BrightWayAI/nucleus/         ← this repo (marketplace catalog only)
  .claude-plugin/marketplace.json   ← lists each plugin and where to find it
  README.md                         ← marketplace overview, install guide
  docs/                             ← cross-cutting docs (e.g., multi-agent patterns)
  CONTRIBUTING.md                   ← this file

BrightWayAI/<plugin-name>/          ← each plugin lives in its own repo
  .claude-plugin/plugin.json        ← plugin manifest
  README.md                         ← plugin docs
  CHANGELOG.md                      ← version history
  SECURITY.md                       ← plugin-specific security policy
  LICENSE                           ← MIT
  commands/                         ← slash commands
  skills/                           ← auto-firing skills
  agents/                           ← subagents (some plugins)
  references/                       ← templates and user-editable content
```

## Where to send contributions

| Kind of change | Repo |
|---|---|
| Fix a typo in a plugin's README | the plugin's repo |
| Improve a slash command's behavior | the plugin's repo |
| Add a new subagent to a plugin | the plugin's repo |
| Update a starter template | the plugin's repo |
| Add a new plugin to the marketplace | open an issue in `nucleus` first to discuss; if accepted, you create the plugin repo and we add the entry to `marketplace.json` |
| Cross-cutting docs (e.g., orchestration patterns) | `nucleus/docs/` |
| Marketplace manifest fixes (broken plugin entry, etc.) | `nucleus` |

## Workflow

For changes to a specific plugin:

1. **Fork the plugin repo** (e.g., `BrightWayAI/lead-engine` → `yourname/lead-engine`).
2. **Create a feature branch** from `main`.
3. **Make your changes** following the conventions below.
4. **Open a PR** against `BrightWayAI/<plugin-name>:main`.
5. **Update the plugin's CHANGELOG.md** under `## [Unreleased]` describing what changed.
6. **Update the SECURITY.md** if your change affects what data the plugin reads or writes.

For new plugins: open an issue in `nucleus` first — we'd rather agree on scope before you build.

## Conventions across plugins

### Voice and writing style

Plugin docs (READMEs, command bodies, skill descriptions) use a consistent voice across the marketplace:

- **Direct, low-jargon, plainspoken.** Avoid corporate hedging ("leverage," "synergy," "delight").
- **Specific over generic.** "Drafts go for review" beats "outputs are produced."
- **Concrete examples over abstract claims.** Show what the plugin does with a real example, not just what it can do.
- **Honest about limitations.** Plugins say what they don't do as clearly as what they do.

If you're contributing copy, match this voice. If you're not sure, look at any existing plugin's README — they all share the same tone.

### Command and skill conventions

- **Slash command names use kebab-case.** `/setup-time` not `/setupTime`.
- **Setup commands populate a `references/user-context.md`** (gitignored). Other commands read from it.
- **Shared user-level config** lives at `~/Documents/Claude/identity.md` and `~/Documents/Claude/voice.md` (managed by cortex's `/setup-identity` and `/setup-voice`). Plugins **should** read these and skip duplicate questions in their own setup interviews.
- **Slash commands have matching auto-firing skills.** If you add a slash command, add a skill with the same name and trigger phrases.
- **No silent destructive actions.** Anything that writes externally (CRM, calendar, files) requires explicit user confirmation via a presented table or message.

### Subagent conventions

When adding a new subagent:

- **Tight tool allowlists.** Only the tools the agent genuinely needs.
- **Structured return contract.** Every agent's body documents the exact return shape (sections, format) parent skills depend on.
- **Confidence rating.** Every agent returns a Confidence assessment (High/Medium/Low) so consumers can route appropriately.
- **No conversational state.** Agents take a self-contained brief and return one shot. They don't ask the user clarifying questions.
- **Single responsibility.** If the description starts hedging ("also handles X, sometimes Y"), split it.

See [`docs/multi-agent-patterns.md`](docs/multi-agent-patterns.md) for chaining patterns when you need multiple agents in a workflow.

### Setup interview conventions

- **One section at a time.** Don't bombard with 25 questions; group by section, summarize after each.
- **Read shared identity and voice first.** If `~/Documents/Claude/identity.md` and `voice.md` exist, pre-fill from them and skip duplicate questions.
- **Idempotent.** Re-running a setup should let the user update specific sections without redoing everything.
- **Skip what doesn't apply.** "I don't have a CRM yet" is a valid answer; capture it as such.

### Templates and user-editable starters

- **Templates ship as starter content.** Each template file (e.g., `references/templates/invoice-template.md`) should make sense as a default but be editable by users.
- **Document customization.** Each template includes a "Customizing this template" section.

### Privacy and security

- **Never send data to a server outside Cowork's authorized connector framework.** All reads and writes go through user-authorized integrations.
- **Update the plugin's SECURITY.md** if your change affects the data surface (what the plugin reads or writes, where data lives, what it doesn't do).

## What to check before submitting a PR

- [ ] Plugin still passes `claude plugin validate .` (if you have it locally) or `/plugin validate .` inside Claude Code.
- [ ] CHANGELOG.md updated under `## [Unreleased]`.
- [ ] SECURITY.md updated if data surface changed.
- [ ] README.md updated if user-facing behavior or commands changed.
- [ ] Slash commands have matching auto-firing skills.
- [ ] No hardcoded user-specific values (company names, IDs, tools, brand specifics) in command bodies — those go in `references/user-context.md` and are read at runtime.
- [ ] If your change affects another plugin's behavior (e.g., a new subagent that another plugin should delegate to), updated that plugin's README + integration guide too.
- [ ] If the change is included in a coordinated Nucleus release, generated a pinned
      release candidate with `scripts/release_ecosystem.py` and validated its live
      connector evidence according to `docs/CONNECTOR_INTEGRATION_TESTING.md`.

## Style of writing in commands and skills

- **Frontmatter `description` is the routing signal.** Write it tightly so Claude (or Cowork) routes correctly. Bad descriptions cause wrong-skill firing or no-skill firing.
- **Trigger phrases in skill descriptions.** Include the natural-language phrases that should auto-fire the skill (e.g., "wrapping up", "calling it a day", "end of day" for `/end-day`).
- **Body uses Step 0 / Step 1 / etc. structure** for slash commands. Skills are thinner pointers to commands.

## Code of conduct

This is an open project; treat contributions and contributors with respect. There's no formal CoC across the marketplace right now (cortex has its own); the standing rule is: be specific in feedback, be kind in delivery, be patient with reviews.

## Questions?

If you're unsure how to contribute, open an issue in the relevant plugin repo or in `nucleus` (for marketplace-level questions). We'd rather have a conversation up front than reject a PR that took you a weekend to write.
