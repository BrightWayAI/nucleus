# Multi-Agent Orchestration Patterns

Patterns for chaining subagents inside a single skill or slash command. Use this when a workflow needs research → analyze → synthesize → draft → review across multiple specialist agents.

This is a pattern doc for plugin authors, not a runtime artifact. The patterns here are already used implicitly in `news-curator/ai-roundup` (news-curator → user-pick → post-assembler) and `relationships` (relationship-ranker per bucket → optional contact-researcher per thin candidate). Documenting them so future plugins can use the same shape consistently.

---

## Why orchestration matters

Single-agent invocations work for narrow tasks: "research this contact," "synthesize across memory." Real workflows are chains: "find candidates → rank them → let the user pick → research the picks → draft from the research → review the draft."

Doing this inline in a skill bloats the parent's context with raw data at every step. Doing it as a chain of subagents keeps each step's context clean and produces structured handoffs the parent can render and gate.

---

## The canonical pattern

### Shape

```
Skill (parent context)
  ↓
  Step A: Delegate to Agent 1 (e.g., research / scan)
  ↓
  Returns structured output A
  ↓
  Step B: User gate (review, pick, edit) — OPTIONAL
  ↓
  Step C: Delegate to Agent 2 (e.g., synthesize / draft) with output A as input
  ↓
  Returns structured output B
  ↓
  Step D: User gate — OPTIONAL
  ↓
  Step E: Delegate to Agent 3 (e.g., review / verify) — OPTIONAL
  ↓
  Skill renders final result
```

### Rules

1. **The parent skill orchestrates. Agents don't know about each other.** Each agent is invoked independently with a self-contained brief. The parent passes Agent 1's output as input to Agent 2 — Agent 2 doesn't fetch it directly.

2. **User gates between agents are valuable.** Don't run the whole chain headless. Insert "show the user, ask for direction" between steps where editorial judgment matters. Examples: "which candidates to keep?" "is this the angle?" "ship it or iterate?"

3. **Each agent's return contract is fixed and parsed by the parent.** When Agent 1 returns a 10-item ranked list, the parent knows the shape (because Agent 1's spec defines it). The parent can render the list, let the user pick a subset, and pass only the subset to Agent 2.

4. **Confidence flows through the chain.** If Agent 1 returns Low confidence, the parent should consider whether to:
   - Pause and ask the user for context (re-run Agent 1 with a richer brief)
   - Skip Agent 2 and report the gap directly
   - Proceed with the chain but flag the limitation in the final output

   See "Confidence-aware delegation" pattern in any consumer skill (e.g., `relationships`, `lead-brief`, `client-status`).

5. **Don't re-invoke an agent for the same brief twice.** Cache outputs in the conversation context; reference them by structure rather than re-querying. Agents are expensive — re-running them in a chain step that already has the data is waste.

---

## Examples in the marketplace

### `news-curator/ai-roundup` — three-step chain

```
/ai-roundup
  ↓
  Step 2: news-curator agent → top 10 candidates with scores + themes
  ↓
  Step 3: USER GATE — show candidates, user picks 5-7
  ↓
  Step 4: post-assembler agent → drafted post + first-comment + alternate hook
  ↓
  Step 5: USER GATE — show draft, user iterates ("ship it" / "shorter" / "redo with X")
  ↓
  Step 6: Skill writes final to runs/[date].md
```

**Why this shape:** scanning is expensive (web fetches), drafting is voice-sensitive. The user gate after scanning lets editorial judgment shape the input to drafting. Without the gate, the post would draft from whatever the agent ranked highest — which is fine, but loses voice control.

### `relationships` — per-bucket fan-out with optional deepening

```
/relationships
  ↓
  Step 0-1: Read user-context, gate on time-budget
  ↓
  Step 2: For each bucket (new_biz, relationship, network):
            relationship-ranker agent → ranked candidates with score + why-now
            (For new_biz: optionally delegate to pipeline-analyst before ranking)
  ↓
  Step 3: Filter (cooling, DNE, "should we even send?") → top 3 per bucket
  ↓
  Step 4 (optional, per thin-data card): contact-researcher agent → fill missing context
  ↓
  Step 5: Parent picks channel + template, fills variables, drafts in voice
  ↓
  USER GATE — render brief, user copies / skips / snoozes per card
  ↓
  Step 6-8: Write today.md + today.json, optional person-page side-effects on "mark sent"
```

**Why this shape:** ranking + scoring is heavy context work (per-candidate signal aggregation across cortex + CRM + Gmail + hot.md) — the parent skill would bloat if it ran the math inline. Delegating per-bucket lets each ranking call load only what it needs. Drafting stays in the parent context because voice rules + templates + user-context all live there. Per-thin-card delegation to `contact-researcher` is opt-in and only fires for candidates with Low confidence from the ranker.

### `referral-engine` — single-agent parent-driven flow

```
Skill (referral-engine /referrals or /referral-ask)
  ↓
  Phase 1: contact-researcher agent → connector dossier (when needed)
  ↓
  Phase 2: Skill applies cooling-period rules + positive-moment triggers in parent context
  ↓
  Phase 3: Skill drafts ask in user's voice
```

**Why this shape:** drafting is voice-faithful and context-heavy; doing it in the parent context (which knows the user's voice rules from `~/Documents/Claude/voice.md`) avoids the round-trip of passing voice rules to a drafter agent. Single-agent chain.

---

## Anti-patterns

### Don't: chain agents that need each other's tools

If Agent 1 needs HubSpot and Agent 2 needs HubSpot, two separate invocations is fine. But don't construct a chain where Agent 2 needs Agent 1's specific tool *output*; instead, have one agent that does both, or have Agent 1 return data structured enough that Agent 2 doesn't need the tool.

### Don't: deep chains (4+ agents)

Two-agent chains are clean. Three-agent chains are workable. Four-agent chains are over-engineered — the orchestration overhead exceeds the per-agent value. If you're considering a 4-agent chain, it's usually a sign that one of the agents should be split into two skills or merged into a single more capable agent.

### Don't: silent chains

Always render intermediate results to the user, even if briefly. "Step 1 returned 10 candidates, top 3 were X, Y, Z. Now drafting." gives the user a chance to interrupt if something's off. Silent chains feel like black boxes and erode trust.

### Don't: agents that call agents

Agents inherit parent tools. They don't (currently) invoke other agents. If you find yourself wanting Agent 1 to invoke Agent 2 mid-flight, restructure: have the parent skill orchestrate both, or merge them into one agent with broader scope.

---

## Confidence handling in chains

When chaining, confidence compounds. Three agents at Medium confidence each → final output is *less* than Medium because errors stack.

Pattern:

```
After each agent returns:
  - If Confidence >= Medium: continue
  - If Confidence == Low AND critical sections empty: pause, surface gap, ask user
  - If Confidence == Low AND critical sections OK: continue but note limitation in final output
```

The "critical sections" depend on the agent. For contact-researcher, critical = Contact Snapshot + Relationship History + at least one talking point. For pipeline-analyst, critical = the top-10 priority items (not the risks or pipeline-health snapshot, which can be sparse without breaking the queue). Each parent skill defines what's critical for its workflow.

---

## When NOT to chain — just use one agent

If a workflow can be done with a single agent invocation followed by inline drafting/synthesis in the parent context, do that. Chains add coordination cost. The cost is worth paying when:

- Different specialist tools are involved (research vs. drafting vs. review)
- User gates between steps materially shape the output (editorial judgment)
- The chain produces a meaningfully better result than a single big agent

Otherwise: one agent, one skill, done.
