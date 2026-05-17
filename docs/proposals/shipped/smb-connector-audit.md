# Connector parity audit: Nucleus vs Claude for Small Business bundle

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus marketplace_
_Status: Audit complete. Recommendations ready for review._
_Related: Phase 3 of the Nucleus-as-JARVIS initiative._

---

## Why this exists

Anthropic's Claude for Small Business bundle (announced 2026-05) ships 15 SMB workflows + 15 skills on Cowork with first-class connectors for **QuickBooks, PayPal, HubSpot, Canva, DocuSign, Google Workspace, Microsoft 365**.

Nucleus targets the same platform (Cowork + Claude Code) and overlapping audience. This audit answers: where does Nucleus already use the same connectors? Where does Nucleus have gaps that Anthropic now covers natively? And where is Nucleus's *differentiation* — capabilities the SMB bundle doesn't touch?

The deliverable is not a "should we build feature X" list — it's a strategic positioning map. Phase 3's productization work depends on knowing the boundary between Nucleus and the SMB bundle.

---

## Connector usage by plugin

Method: grepped each plugin repo for HubSpot, QuickBooks, PayPal, Canva, DocuSign, Workspace, M365 / Outlook / Microsoft, plus Gmail and CRM. Cross-checked with each plugin's CONNECTORS.md / SECURITY.md / setup command.

| Plugin | HubSpot | QuickBooks | PayPal | Canva | DocuSign | Workspace (Gmail/Cal/Drive) | M365 / Outlook |
|---|---|---|---|---|---|---|---|
| **claude-cortex** | — | — | — | — | — | Gmail (mining adapter), Calendar (end-day) | Outlook (adapter, optional) |
| **daily-brief** | ✓ MCP, R+W | — | — | — | — | Gmail (R+W draft), Calendar (R) | — |
| **lead-engine** | ✓ MCP, R+W | — | — | — | — | Gmail (R, optional) | — |
| **bizdev-outreach** | ✓ MCP, R+W (via `~~crm` abstraction; also Salesforce/Pipedrive/Close) | — | — | — | — | Gmail (R, via `~~email`) | ✓ Outlook (R, via `~~email`) |
| **weekly-outreach** | ✓ MCP, R+W | — | — | — | — | Gmail (R), Calendar (R) | — |
| **referral-engine** | ✓ MCP, R | — | — | — | — | Gmail (R, optional) | — |
| **news-curator** | — | — | — | — | — | — | — |
| **client-status** | ✓ MCP, R | — | — | — | — | Calendar (R), Drive (R, optional) | — |
| **project-setup** | — | — | — | — | — | Drive (W) | — |
| **time-tracking** | — | mentioned as a *manual destination*; no native integration | — | — | — | Calendar (R) | — |
| **weekly-alignment** | — | — | — | — | — | — | — |
| **writing-style** | — | — | — | — | — | — | — |
| **core-ops** | ✓ MCP, R (pipeline-analyst subagent) | — | — | — | — | — | — |
| **nucleus-router** | — (pure routing layer) | — | — | — | — | — | — |

**Read+Write to HubSpot:** daily-brief, lead-engine, bizdev-outreach, weekly-outreach.
**Read-only HubSpot:** referral-engine, client-status, core-ops/pipeline-analyst.
**Drafts-only to Gmail (never sends):** bizdev-outreach, daily-brief, lead-engine, weekly-outreach.

---

## Where Nucleus already has connector parity

These connectors are first-class in both Nucleus and Anthropic's SMB bundle. Nucleus uses Cowork's MCP system, which is the same substrate Anthropic uses for the SMB connectors — so we don't need to "migrate" anything; we just need to make sure plugins use the *latest* MCP server versions when Anthropic refreshes them.

### HubSpot (and other CRMs)

**Parity:** Strong. Nucleus uses HubSpot MCP throughout the BD layer (lead-engine, weekly-outreach, daily-brief, client-status, bizdev-outreach, referral-engine, core-ops/pipeline-analyst). Bizdev-outreach goes further with a `~~crm` connector abstraction supporting HubSpot / Salesforce / Pipedrive / Close.

**Anthropic SMB**: HubSpot for campaign analysis, lead triage, content strategy.

**Differentiation:** Nucleus's HubSpot use is **relationship-layer** (warm pipeline, weekly cadence, per-contact research, referral tracking). Anthropic's is **marketing-funnel** (campaign attribution, lead triage). Different value props on the same connector.

**Recommendation:** No migration. When Anthropic refreshes the HubSpot MCP, smoke-test the plugins. Document that Nucleus's BD layer composes with Anthropic's marketing layer — they can run on the same HubSpot instance side by side.

### Google Workspace (Gmail, Calendar, Drive)

**Parity:** Strong. Nucleus uses Gmail MCP (read + draft) across daily-brief, lead-engine, bizdev-outreach, weekly-outreach; Calendar MCP across daily-brief, client-status, weekly-outreach, time-tracking, cortex; Drive MCP for project-setup folder creation and client-status reference reads.

**Anthropic SMB**: Workspace for "agentic workflows across …".

**Recommendation:** No migration. Drafts-only Gmail discipline is a key Nucleus security promise (every email is a Gmail draft, never sends). Keep that explicit.

### Microsoft 365 / Outlook

**Partial parity.** Only `bizdev-outreach` lists Outlook in its `~~email` connector abstraction; the rest of the BD layer is Gmail-first. Cortex's note-source adapters mention Outlook as a generic-Gmail-style adapter.

**Anthropic SMB**: Microsoft 365 is first-class on their bundle.

**Recommendation:** Generalize the `~~email` abstraction beyond bizdev-outreach. Lead-engine, weekly-outreach, daily-brief, client-status, referral-engine should all be email-platform-agnostic. Two ways: (a) lift bizdev-outreach's `~~email` connector convention into a shared cortex reference like `references/email-adapters.md`, then have other plugins reference it; (b) write a small migration that updates each plugin's setup command to ask "Gmail or Outlook?" and route accordingly. This is a real gap for Outlook-first SMB customers.

---

## Where Anthropic's SMB bundle covers what Nucleus doesn't

These are the connectors Nucleus has **no native integration** with. Anthropic's bundle now provides first-class workflows here. The right move is **defer to Anthropic** — don't build a parallel layer that competes.

### QuickBooks (finance, payroll, cash flow)

**Nucleus today:** time-tracking has no QuickBooks integration. Its `/generate-invoices` command outputs structured markdown for the user to copy into "QuickBooks, Wave, Stripe, or manual emails."

**Anthropic SMB:** QuickBooks-native payroll planning, cash forecasting, monthly close, reconciliation.

**Recommendation:** **Defer to Anthropic for accounting workflows.** But add a *handoff* in time-tracking: if the user has QuickBooks installed via Anthropic's SMB bundle, `/generate-invoices` should output in a QuickBooks-importable format (CSV with the right column mapping) and surface a one-line note: "These rows are formatted for QuickBooks import. Drop into Anthropic's QuickBooks workflow to push them in." That makes Nucleus *compose* with the SMB bundle instead of duplicating it.

### PayPal (payments, invoicing, disputes)

**Nucleus today:** Not used anywhere.

**Anthropic SMB:** PayPal-native settlements, invoicing, dispute resolution.

**Recommendation:** **Defer entirely.** No need for Nucleus to touch PayPal. If a user mentions invoicing or payments and PayPal is involved, the router should suggest the user run Anthropic's SMB PayPal workflow.

### Canva (content / design)

**Nucleus today:** Not used. News-curator and writing-style produce text content; visual design is out of scope.

**Anthropic SMB:** Canva-native content generation.

**Recommendation:** **Defer entirely.** Nucleus's content layer (news-curator + writing-style + core-ops/review-deliverable) is text-and-voice-focused. Canva is the right tool for visual design and Anthropic now owns that integration.

### DocuSign (contracts)

**Nucleus today:** Not used. Project-setup creates engagement scaffolding (Drive folders, system prompts, project plans) but never touches contract workflows.

**Anthropic SMB:** DocuSign-native contract review.

**Recommendation:** **Defer entirely**, with one composition point: project-setup could optionally surface "Contracts handled by Anthropic SMB / DocuSign — link your contract templates here" in its setup interview. Pure pointer; no integration.

---

## Where Nucleus differentiates — capabilities Anthropic's SMB bundle does NOT cover

This is the strategic moat. Anthropic's SMB bundle is **finance + payments + content + contracts** glued onto generic CRM/Workspace workflows. Nucleus's value sits in places the SMB bundle does not touch:

### 1. Bidirectional, typed, decaying second-brain memory (claude-cortex)

Anthropic's bundle has no equivalent. Cortex's typed nodes (INSIGHT / MODEL / GOTCHA / LESSON / RECIPE / CORRECTION), decay states (Fresh / Stale / Dormant / Cold), `[confirmed:...]` substrate, mining layer (v4.3), decay layer (v4.4), legibility layer (v4.5 — index + research-gaps + Obsidian) — none of this exists in the SMB bundle.

**Positioning line:** "Anthropic's SMB bundle remembers your *workflows*. Cortex remembers your *world*."

### 2. Adaptive voice (writing-style)

Anthropic's content workflows are template-driven. Writing-style learns the operator's voice from real edits over time, with two-stage triage and pattern-based style-guide refinement.

**Positioning line:** "Generic AI writes generically. Writing-style writes in your voice — and gets sharper every week."

### 3. The relationship layer (lead-engine, weekly-outreach, referral-engine, bizdev-outreach)

Anthropic's HubSpot integration is marketing-funnel (campaigns, lead triage). Nucleus's HubSpot use is relationship-layer:
- **lead-engine** turns LinkedIn signals into warm DMs in your voice with a 3-touch cadence.
- **weekly-outreach** builds a prioritized 10-12-contact plan every Monday with per-contact research.
- **referral-engine** surfaces latent revenue from connectors who've gone quiet.
- **bizdev-outreach** does per-contact deep research and drafts personalized outreach.

**Positioning line:** "Anthropic's SMB triages your leads. Nucleus runs your relationships."

### 4. The daily flow loop (daily-brief, cortex's `/end-day`)

Anthropic's bundle is workflow-shaped (run this workflow when you need this output). Nucleus is rhythm-shaped (a daily/weekly rhythm of recap → reflect → commit → plan). No equivalent in the SMB bundle.

**Positioning line:** "Anthropic runs your workflows. Nucleus runs your day."

### 5. JARVIS-style natural-language router (nucleus-router)

No equivalent. Anthropic's bundle still requires the user to know which workflow to invoke. Nucleus's router maps natural-language utterances to the right capability.

**Positioning line:** "Don't memorize workflow names. Just talk."

### 6. Cross-team Slack alignment (weekly-alignment)

No equivalent in the SMB bundle.

### 7. Operator-tailored client engagements (project-setup, client-status, time-tracking)

The consulting / agency / fractional-operator vertical. Anthropic's bundle is built for "general SMBs"; Nucleus has a tighter operator playbook (project initialization, weekly client status drafts, calendar-to-invoice loop).

---

## Recommended actions

### High-value (do)

1. **Generalize the `~~email` connector** (lift from bizdev-outreach into a shared cortex reference) so Outlook-first SMB users can adopt Nucleus's BD layer without Gmail dependency. Update lead-engine, weekly-outreach, daily-brief, client-status, referral-engine setup commands accordingly.

2. **Add QuickBooks-compatible output to time-tracking's `/generate-invoices`.** No native QuickBooks integration; just emit CSV with the right column mapping and a "drop this into Anthropic's QuickBooks workflow" pointer. Lets Nucleus compose with the SMB bundle.

3. **Document composition explicitly in the README.** A "Nucleus + Anthropic SMB" section showing how the two stacks compose: Anthropic does finance/contracts/content/payments; Nucleus does memory/voice/relationships/daily-flow.

### Medium-value (consider)

4. **In the nucleus-router intent table**, add fallback rules for utterances that map to Anthropic SMB workflows. Example: user says "run payroll" → router suggests "this is an Anthropic SMB workflow — see your QuickBooks integration." Pure pointer; no built-in capability.

5. **In `/project-setup`**, surface a one-line "Contracts handled separately via DocuSign + Anthropic SMB" item in the engagement-initialization output. Don't build the integration; just acknowledge the handoff.

### Low-value / skip

- Building native QuickBooks / PayPal / DocuSign / Canva integrations. Anthropic now owns these; competing is wasted effort.
- Building a "Nucleus deliverable design" Canva integration. Out of scope.
- A unified payments layer. Anthropic owns this.

---

## Strategic summary (carries into positioning doc)

The SMB bundle is **finance + contracts + content + payments** — verticals that depend on tight connector integrations Anthropic now ships natively.

Nucleus is **memory + voice + relationships + daily flow** — verticals that depend on always-on observation, adaptive learning, and a multi-plugin rhythm. The connector layer matters but is secondary; the value is in the *behavior*, not the integration.

Together: a small business owner runs Anthropic's SMB bundle for their books, their contracts, their content, and their payments. They run Nucleus for their second brain, their voice, their daily working rhythm, and their relationship engine. The two stacks are complements, not competitors. **That is the productization story.**
