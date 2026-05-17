# Productization plan: Nucleus for solo operators

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Strategy locked. Implementation choices below._
_Related: smb-connector-audit.md (internal-only context on competitive landscape)._

---

## Strategic decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Monetization | **Free OSS, monetize via services** | Nucleus is the lead magnet. BrightWay AI sells consulting, setup, customization, training on top. MIT-licensed across every plugin. Matches Zach's existing consulting model. Lowest commitment, fastest distribution. |
| Audience | **Solo operators / fractional consultants** | Tightest message-market fit. The plugins (lead-engine, weekly-outreach, time-tracking, client-status, referral-engine) were built for this profile. Avoids overlap with general-SMB workflow products. |
| Public positioning vs Anthropic SMB bundle | **Don't mention it** | Position purely on Nucleus's own merits. The competitive lens stays in `smb-connector-audit.md` as internal context. No comparison tables, no callouts, no antagonism. |
| Phase 3 outputs | **Rewritten README + this plan** | README.md is the public artifact (already shipped in this proposal cycle). This doc is the internal strategy reference. |

---

## Who Nucleus is for (the ICP)

| Trait | Detail |
|---|---|
| **Role** | Solo / near-solo operator. Fractional CTO / COO / CMO; independent consultant; founder of a 1-3-person firm; agency owner who still does delivery. |
| **Workflow** | Client work billable by the hour or project. Pipeline of 5-30 active prospects. 3-10 active engagements. Regular outbound (BD, content, referrals). Calendar-heavy. Email-heavy. |
| **Tools they already use** | Claude (Cowork Desktop or Code), Gmail or Outlook, HubSpot or Salesforce or Pipedrive or Close, Drive or OneDrive, Slack or Teams, LinkedIn. |
| **What they want from AI** | Less context-switching. Better recall. Drafted-in-their-voice writing. A daily working surface that doesn't require clicking through five tabs. A system that compounds — gets sharper the longer they use it. |
| **What they explicitly don't want** | Another CRM. Another SaaS subscription. Another tool that needs prompting from scratch every time. Generic AI that sounds like ChatGPT. |

**Not** for: enterprise teams, marketing departments at scale, sales orgs with 50+ reps, general SMBs running e-commerce / restaurants / brick-and-mortar.

---

## How Nucleus monetizes (free OSS + services)

### What's free, forever
- All 14 plugins, MIT-licensed.
- The marketplace manifest, contribution docs, references, templates.
- The router, the memory system (cortex), the BD layer, the daily-flow layer.
- Updates pushed to GitHub; users pull automatically through Cowork's marketplace mechanism.

### What BrightWay AI sells on top
Five service offers, in order of expected demand:

1. **Setup-in-a-day** — 4-hour remote install + onboarding for a solo operator. Walks identity / voice / tooling setup; runs `/setup-identity`, `/setup-voice`, `/setup-obsidian`; configures the user's CRM / email / calendar connectors; runs through first `/brief`, first `/end-day`; trains them on the router. Flat fee. Aimed at non-technical operators who want it just working.

2. **Custom plugin development** — build a new plugin specific to the customer's vertical (e.g., a research firm's research-tracker, a fractional CFO's monthly-close ritual, a healthcare consultant's compliance checklist). Pricing per project.

3. **Memory and voice training intensive** — one-week engagement where BrightWay observes the operator working with Nucleus, then tunes cortex's decay thresholds, tunes the writing-style patterns, builds custom person-page schemas, and codifies the operator's working playbook into memory. Fixed price.

4. **Multi-operator team rollout** — for 2-10-person firms that want a shared memory layer and cross-user routing. Requires customizations Nucleus doesn't ship out of the box (shared `<config-root>`, admin patterns, multi-tenant identity). Engagement pricing.

5. **Office hours / retainer support** — monthly retainer for operators who want a Slack / call channel into BrightWay for help, customization tweaks, new-plugin requests.

### What BrightWay doesn't sell
- Hosted infrastructure (Nucleus runs on the user's Cowork or Claude Code; no hosting needed).
- Per-seat or per-user licensing (everything is OSS).
- Enterprise volume deals (not the target audience).

---

## Onboarding flow for new users

The README is the entry point. After they install via Cowork, they hit this sequence:

```
1. /plugin marketplace add BrightWayAI/nucleus           (marketplace install)
2. Install cortex + router as a minimum                  (2 plugins required)
3. /setup-identity                                       (8 questions, 5 min)
4. /setup-voice                                          (paste 2 emails, 5 min)
5. /setup-obsidian                                       (optional — scaffolds vault)
6. Install the install-combo for their archetype          (consultant / agency / content / cross-team)
7. /setup-* for each installed plugin                    (5 min per plugin)
8. /diagnose                                             (verify wiring)
9. /register-schedules                                   (daily/weekly automation)
10. Open Obsidian → File → Open vault → <config-root>/    (graph view live)
```

**Total time:** 30-45 minutes for a full install. 10 minutes for the minimum viable setup (cortex + router + core-ops).

A guided `/onboarding` slash command could collapse steps 3-9 into a single chained flow. **Future work.** Not blocking for Phase 3.

---

## The share / demo story

When Zach (or any BrightWay-services customer) is showing Nucleus to another operator, this is the demo script. ~8 minutes, designed to fit a coffee chat.

### Demo flow

1. **Open Claude Desktop with Nucleus already installed.** (Don't waste the demo on install — pretend they're using a colleague's setup.)
2. **Talk to it.** *"What's on my plate today?"* → router runs `/brief`. Show the Cowork artifact with calendar / inbox / CRM / outreach / yesterday's reflection. Annotate one item: "draft a short reply." Run `/process-brief`. Show the Gmail draft. **Beat:** "I never had to type a slash command."
3. **Add a memory.** *"I just met Sarah Chen from Acme — VP Eng, sharp on agentic systems, mentioned they're evaluating ops platforms."* → router runs `/remember`. Show the new person page. Show how it links to client/acme. **Beat:** "It captured the relationship without me telling it the schema."
4. **Open Obsidian.** Show the graph view. The operator + their clients + their people + their topics, all connected by real edges. Tap into `person/sarah-chen`. **Beat:** "Same files. Two interaction surfaces."
5. **Wrap up the day.** *"Wrap up the day."* → router runs `/end-day`. Walk through the chain: inbox triage → transcript review (skip if no transcripts) → cheap-tier commit triage → reflective prompts → memory index refresh → pre-stage tomorrow. **Beat:** "It runs the rhythm so I don't have to remember to."
6. **Hand-wave the rest.** Don't try to demo every plugin. Mention the BD layer (lead-engine, weekly-outreach, referral-engine), the content layer (news-curator, writing-style), the engagement layer (project-setup, client-status, time-tracking). Show `/route` so they see the catalog scrolls past.
7. **Close.** "It's free, MIT-licensed, install via Cowork. I sell setup-in-a-day and custom plugin development if you want it tuned for your firm. Want the link?"

The demo is the product. Nothing about it requires polish work — it just works. The strongest signal is the absence of friction.

### Recording the demo

A 6-minute screen recording of this flow makes the strongest landing-page asset Nucleus could have. **Future work** for BrightWay AI marketing. Recording it sells better than any README rewrite.

---

## Distribution channels

In order of expected lead quality:

1. **Direct outbound from Zach's network.** The first 10-30 users come from Zach's existing operator network. The setup-in-a-day service rides on this.
2. **Content marketing through news-curator and writing-style itself.** Zach uses his own product to draft a weekly LinkedIn post about agentic operator workflows. The product *is* the marketing.
3. **Anthropic / Cowork ecosystem visibility.** Nucleus shows up as an installable marketplace at `BrightWayAI/nucleus`. Discoverability depends on Anthropic's marketplace UX evolving — wait and see, no work needed from BrightWay.
4. **GitHub topics / search.** Tag the marketplace and each plugin repo with `claude-plugin`, `agentic-operator`, `second-brain`, `nucleus`. Free distribution.
5. **Operator communities.** Indie consultant Slacks, fractional CXO communities, On Deck-style networks. Drop demo videos when ready.

**Not** investing in:
- Paid ads (audience is too narrow; word-of-mouth wins).
- Product Hunt launch (audience doesn't live there).
- General SMB marketing channels (wrong audience).

---

## Polishing pass: marketplace.json descriptions

The marketplace catalog descriptions are the first thing a Cowork user sees when browsing plugins. The current ones are functional but vary in tone and density. A polishing pass would bring them to the same marketing-quality level as the new README.

**Future work** — small but valuable, ~30 min. Not blocking.

Proposed pattern: **one-sentence value prop + one-clause "for whom."**

Example: cortex's current description:
> Always-on learning system — Claude gets smarter about you with every conversation. Passively observes preferences, captures knowledge, and adapts.

Proposed:
> Your second brain. Typed memory that learns and forgets, auto-maintained catalog, autonomous gap-fill, Obsidian-ready. For operators who hate explaining themselves to AI twice.

This is a low-priority pass. Do it once the README has been live and tested with real users.

---

## What's NOT in Phase 3

- **Multi-tenant features** — Shared memory, cross-user identity, team admin console. Phase 4+. Required for the multi-operator team rollout service but not for the free OSS product.
- **Hosted Nucleus** — A managed install. No. Stays self-host.
- **Per-plugin paid tiers** — Considered and rejected. Open-core fragments the audience; service-led monetization is cleaner.
- **A "Pro" plugin pack** — Same reason. Everything stays free.
- **Anthropic SMB bundle integration** — Per the user decision, don't mention it publicly. The composition story is real but stays in `smb-connector-audit.md` as internal context. If a customer asks, the answer is "they compose well; install both."
- **Pricing pages, billing infrastructure, paywalls** — None of this is needed. BrightWay's services are sold on the existing brightwayai.com site.
- **Landing page rewrite** — The README is the landing page for Nucleus itself. `brightwayai.com` is the landing page for services. No third surface needed.

---

## Acceptance criteria (for Phase 3 completion)

- [x] `smb-connector-audit.md` written — internal competitive context locked.
- [x] `README.md` rewritten — positions Nucleus for solo operators, no Anthropic mention, JARVIS-forward.
- [x] `productization.md` (this doc) written — monetization model, audience, demo script, distribution channels documented.
- [ ] `README.md` reviewed in dogfooding for at least one week before any further marketing investment.
- [ ] (Optional, future) `/onboarding` chained command added to nucleus-router or cortex.
- [ ] (Optional, future) Marketplace.json description polishing pass.
- [ ] (Optional, future) 6-minute demo screen recording.

The mandatory deliverables are the three docs. Everything else is future polishing once real usage data is in.

---

## Open questions for future sessions

1. **Should `/onboarding` exist?** A single command that chains setup-identity → setup-voice → install-combo selection → per-plugin setup → diagnose → register-schedules. Would shrink onboarding from 30 minutes to one prompt. Decision: defer until at least 3 real users have done manual onboarding and reported friction.
2. **How visible should BrightWay AI services be from the README?** Current rewrite has one paragraph at the bottom. Could be more prominent (a dedicated section under "Help") or less (just a contact line). Decision: let real users react to v1; tune in v2.
3. **Is there a 15th plugin worth shipping for the Solo-operator-running-BD combo?** Something around contract-tracking or proposal-drafting. Decision: wait for user signal. Don't ship plugins on speculation.
4. **Does the team-rollout service need its own minimal-product?** A "Nucleus Teams" SKU that's still OSS but adds shared-memory primitives. Bigger question. Decision: defer until at least one paying customer asks.
