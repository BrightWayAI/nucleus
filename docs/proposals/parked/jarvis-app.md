> **PARKED** — deferred indefinitely; NOT on the active roadmap. A standalone Tauri "Operator" desktop app is a separate product bet, revisited only if marketplace dogfooding produces strong demand. Kept here for reference, hidden from the active proposal list.

---

# JARVIS app — full build spec

_Created: 2026-05-16_
_For: Zach Wagner / BrightWayAI Nucleus_
_Status: Spec — not yet started. Estimated v1 ship: 8-12 weeks of focused work._
_Companion proposal: the productization plan (`shipped/productization.md`) defines positioning + services revenue. This proposal defines a new product surface that opens additional revenue paths._

---

## TL;DR

A standalone desktop app — voice-first, always-on, with a 3D circular orb that pulses while you and the AI speak. Reads and writes the same `<config-root>/` markdown substrate that Cowork plugins use, so it's a *third interaction surface* on top of Nucleus (alongside Cowork and Claude Code) rather than a replacement.

Built with Tauri (Rust shell, smaller than Electron), React + TypeScript frontend, the 21st.dev voice-powered orb (ogl + GLSL shaders), Anthropic SDK with prompt caching of cortex's CLAUDE.md + nucleus-router skill, browser SpeechRecognition for input (free) → upgradeable to Whisper, browser SpeechSynthesis for output → upgradeable to ElevenLabs.

The architectural insight that makes this work: Nucleus's "folder is the app" design means the JARVIS app doesn't replace anything. It's one more cockpit reading the same memory, voice, and identity files.

---

## Product positioning

**Nucleus marketplace today** = the engine. 14 plugins, markdown files, runs in Cowork (Claude Desktop) or Claude Code. Free OSS. Target: solo operators / fractional consultants who'll install plugins and configure them.

**JARVIS app** = the cockpit. A voice-first desktop app on top of the same engine. Target: same audience, but a *different mode of use* — when they want hands-free, ambient, always-on access to their AI staff. Free tier + paid Pro tier (see Monetization).

The two surfaces compose:
- 8am: open laptop → JARVIS orb in system tray; say "what's on my plate" → orb pulses, voice response.
- 10am: in Cowork doing a deep work session → same `<config-root>/`, same memory, same `/recall` mid-conversation.
- 2pm: on phone via Obsidian Sync → reading person pages on mobile.
- 5pm: back to JARVIS for "wrap up the day" while making dinner.

Same data, three cockpits, picked by context.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  JARVIS desktop app  (Tauri shell, ~10MB binary)            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React + TypeScript frontend                         │   │
│  │  ┌─────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  Voice orb      │  │  Conversation panel      │   │   │
│  │  │  (21st.dev)     │  │  (chat history,          │   │   │
│  │  │  ogl + GLSL     │  │   suggestions, status)   │   │   │
│  │  └─────────────────┘  └──────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  Settings, autonomy slider, voice config     │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tauri backend (Rust)                                │   │
│  │  - File watcher on <config-root>/                    │   │
│  │  - Anthropic SDK (with prompt caching)               │   │
│  │  - System tray + global hotkey                       │   │
│  │  - Voice provider abstraction (browser / external)   │   │
│  │  - MCP client (to call user's existing MCP servers)  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────────┐
            │  <config-root>/  (~/Documents/Claude/)│
            │  ├── identity.md, voice.md          │
            │  ├── memory/  (cortex)              │
            │  ├── archive/  (raw substrate)      │
            │  ├── briefs/  (daily-brief)         │
            │  ├── plugins/  (per-plugin config)  │
            │  └── log.md, hot.md, index.md       │
            └─────────────────────────────────────┘
                    ▲                  ▲
                    │                  │
              Cowork plugins      Claude Code
              (existing today)    (existing today)
```

### Tech stack (locked decisions)

| Layer | Choice | Rationale |
|---|---|---|
| **Desktop shell** | **Tauri** (Rust + WebView) | ~10MB binary vs Electron's 100+MB. Single-binary distribution. Better security model (allowlist-based capabilities). Cross-platform: macOS, Windows, Linux. |
| **Frontend** | **React + TypeScript** + Vite | Standard. 21st.dev components are React. TypeScript catches integration bugs early. |
| **Voice orb** | **21st.dev voice-powered-orb** by Isaiah | ogl + GLSL shaders, audio-reactive via Web Audio API. Already exists. Free MIT-style use. |
| **AI** | **Anthropic SDK (`@anthropic-ai/sdk`)** | Direct API access. Prompt caching is critical (see below). Claude Opus 4 or Sonnet 4 default. |
| **Voice input (v1)** | **Browser `SpeechRecognition` API** | Free, decent latency, works offline-ish (browser dependent). Upgradeable to Whisper later. |
| **Voice output (v1)** | **Browser `SpeechSynthesis` API** | Free, sounds robotic but functional. Upgradeable to ElevenLabs later. |
| **State** | **Zustand** or built-in React state | No Redux ceremony. Conversation state is mostly linear. |
| **File watching** | **Tauri's fs watch + notify-rs** | Native, no Node deps. |
| **MCP client** | **Custom MCP client in Rust** (or use existing one) | The app needs to invoke the user's existing MCP servers (Gmail, Calendar, HubSpot, etc.) — same ones Cowork uses. |

### Tech stack (open decisions — flag for user)

| Layer | Choice | Decision needed? |
|---|---|---|
| Voice input premium | Whisper (OpenAI API or local whisper.cpp) | Wait for Pro tier — v1 ships with browser SpeechRecognition only |
| Voice output premium | ElevenLabs / OpenAI TTS / Cartesia | Wait for Pro tier — v1 ships with browser SpeechSynthesis |
| Wake-word | "Hey JARVIS" via Porcupine or Picovoice | Not v1 — global hotkey first |
| Multi-modal | Camera input for visual context | Not v1 |
| Mobile companion app | iOS / Android via Tauri Mobile (alpha) | v3+ |

---

## The voice orb (21st.dev)

URL: https://21st.dev/community/components/isaiahbjork/voice-powered-orb/default

**What it is:** A React component rendering an audio-reactive 3D orb using ogl (lightweight WebGL wrapper) + GLSL shaders. Procedural noise generation, color shifting, lighting effects. The orb's rotation speed and visual intensity modulate in real-time based on microphone audio levels.

**Dependency:** Just `ogl` (single npm package). No Three.js, no react-three-fiber, no heavy 3D framework.

**State driver:** Microphone audio amplitude. The component captures audio internally via Web Audio API and modulates shader uniforms.

**Caveats:**
- Requires HTTPS context for microphone permissions (Tauri's webview should grant this since it's local).
- The 21st.dev page says "Might not work in sandbox due to browser restrictions but will work in your codebase" — confirms it works in production-shipped contexts, just not in iframe previews.
- The component appears to drive its own audio analysis. We'll want to *also* drive the orb from TTS output (so it pulses while the AI is speaking back), which means either:
  - Forking the component to accept an external audio source
  - Routing the TTS audio through a Web Audio destination the orb can analyze
  - Maintaining two animation modes: "listening to user" (mic-driven) and "speaking to user" (TTS-driven)

**Adaptations needed:**
1. **Speaking mode.** During TTS output, the orb should pulse with the AI's speech, not the user's mic. Implement a state machine: idle / listening / thinking / speaking. Each state has different visual parameters (color, intensity, rotation).
2. **Thinking mode.** While Claude is generating (no audio yet), the orb should *think* — slower rotation, dimmer, no audio-reactivity.
3. **Color theming.** Match cortex's identity (BrightWay color palette?). User-customizable in settings.

### Other 21st.dev components worth using

(Browse https://21st.dev/community to find current options; below are categories, not specific component names — the catalog changes.)

| Component need | What to look for at 21st.dev |
|---|---|
| **Command menu** | cmdk-style spotlight for explicit command invocation (mirrors `/route` cheat sheet) |
| **Conversation bubble / message** | Chat-style message component for the conversation history panel |
| **Animated status pill** | "Thinking..." / "Listening..." / "Speaking..." indicator near the orb |
| **Toast notifications** | For background events ("/listen finished; 14 proposals ready", "/morning waiting for review") |
| **Glassmorphism panel** | Background panel for the conversation area (modern, slightly transparent over desktop wallpaper) |
| **Settings tree** | Hierarchical settings panel for autonomy slider, voice config, file paths, plugin toggles |
| **Animated icons / loaders** | Subtle loading states for tool calls |

Each is a 1-2 hour drop-in if 21st.dev has a good one. Otherwise roll custom — none are load-bearing.

---

## Integration with Nucleus

### What the JARVIS app reads at startup

1. **`~/Documents/.claude-plugin-config-root`** → resolves the config root path.
2. **`<config-root>/identity.md`** → user's name, role, company, time zone.
3. **`<config-root>/voice.md`** → voice descriptors, banned phrases.
4. **`<config-root>/memory/user.md`** → user profile (preferences, corrections, patterns).
5. **`<config-root>/memory/hot.md`** → 7-day rolling cache (warm start).
6. **`<config-root>/memory/DASHBOARD.md`** → active nodes + P0 list.
7. **`<config-root>/memory/index.md`** → catalog (so the app can suggest entity lookups).
8. **`<config-root>/plugins/cortex.user-context.md`** → autonomy mode mappings.

### What the JARVIS app sends to Anthropic on each turn

```
[cached] System prompt:
  - Cortex CLAUDE.md (the memory schema + always-on behaviors)
  - Nucleus-router skill (the natural-language → command intent table)
  - User identity.md + voice.md
  - memory/user.md (preferences)
  - memory/hot.md (recent context)

[fresh] Current turn:
  - Voice transcript: "<user utterance>"
  - Conversation history (last N turns; ≤ 5K tokens)
```

**Prompt caching** is critical. The cached system prompt is ~30-50K tokens of cortex + router context. With caching, each turn costs only the fresh portion (~1-3K tokens). Without caching, each turn is ~30-50K tokens — costs 10-30x more.

Anthropic's prompt-cache breakpoints: cortex CLAUDE.md (stable across sessions), then nucleus-router (stable), then identity+voice+user (stable per user), then hot.md (refreshes daily). Four cache breakpoints maximize hit rate.

### What the JARVIS app writes to `<config-root>/`

Same as cortex commands today. The app invokes the same cortex skills (loaded via cached system prompt) which tell Claude how to:
- Append a `/note` to a project node's changelog
- Update `memory/user.md` with new observations
- Add a person to `memory/person/`
- Write today's brief in `<config-root>/briefs/`
- Append to `memory/log.md` via the log-writer skill
- Refresh `memory/hot.md` via the indexer skill

The app is **not** re-implementing these behaviors. It's loading the skills as instructions and letting Claude execute them with file-system tools.

### MCP servers

The app needs to call the same MCP servers the user has configured for Cowork — Gmail MCP, Calendar MCP, HubSpot MCP, Slack MCP, etc. Two options:

**Option A: Custom MCP client in the Tauri backend.** Implements the MCP protocol (JSON-RPC over stdio or HTTP). Calls the same MCP servers the user has installed. Requires ~1-2 weeks of implementation.

**Option B: Reuse Cowork's MCP runtime via IPC.** If Cowork exposes an MCP gateway, the app proxies through it. Probably easier but ties the app to Cowork being installed.

**Recommendation:** Option A. Independence from Cowork is a feature — the app should work whether or not Cowork is installed. Use the existing Anthropic MCP SDK (`@modelcontextprotocol/sdk` for Rust if it exists; otherwise port).

### File-watcher integration

A `notify-rs` file watcher on `<config-root>/` lets the app react when Cowork or Claude Code writes new memory:

- User runs `/end-day` in Cowork at 5pm → cortex writes `## Reflection` to today's brief → JARVIS app sees the file change → suggests "Want me to read your reflection back?" in the conversation panel.
- Nightly `/listen` writes `.commit-drafts/2026-05-17.md` → next morning, the orb shows a notification badge → user says "good morning" → app routes to `/morning`.
- User edits `voice.md` manually → app reloads the cached system prompt on next turn (cache breakpoint busts cleanly).

---

## MVP scope (v1)

What ships in the first release. Everything else is post-v1.

### Must-have

- [ ] Tauri shell with macOS-first build (Windows + Linux as fast-follow).
- [ ] System tray icon. Click to expand/collapse the orb window.
- [ ] Global hotkey (default: ⌃Space) to invoke the app from anywhere.
- [ ] Voice orb (21st.dev) with 4-state animation: idle / listening / thinking / speaking.
- [ ] Browser SpeechRecognition for voice input. Browser SpeechSynthesis for voice output.
- [ ] Anthropic SDK integration with prompt caching of cortex + router + user context.
- [ ] Conversation panel showing transcript + responses.
- [ ] File-system tool access for reading/writing `<config-root>/`.
- [ ] Settings panel: config-root path, voice provider, autonomy mode mappings (mirror cortex's `autonomy:` config), API key entry.
- [ ] File watcher on `<config-root>/` with notification toasts for relevant events.
- [ ] Onboarding flow: first run detects no config-root → walks `/start-nucleus` via voice.

### Nice-to-have for v1

- [ ] MCP client in Rust (or use Cowork proxy if simpler).
- [ ] Per-conversation memory (the conversation panel can scroll back; not persisted long-term yet).
- [ ] Quick-action buttons below the orb (the "Top 5 utterances" from your usage).
- [ ] Visual feedback during tool calls ("Reading memory/client/acme.md..." etc.).

### Explicitly OUT of v1

- ❌ Whisper or ElevenLabs integration (Pro tier feature).
- ❌ Wake-word ("Hey JARVIS") — global hotkey only.
- ❌ Mobile companion app.
- ❌ Camera / visual input.
- ❌ Multi-user / team features.
- ❌ Cloud sync.
- ❌ Auto-update infrastructure (manual download for v1).
- ❌ App Store distribution (direct download from `brightwayai.com` for v1).
- ❌ Telemetry beyond the existing `memory/log.md` chronicle.

---

## Build plan (12 weeks, single-engineer)

### Weeks 1-2: Foundation

- Tauri project scaffold. Choose between Tauri 2.x and stable 1.x (default: 2.x for active development).
- React + TypeScript + Vite frontend wired into the Tauri shell.
- macOS code signing + entitlements (microphone permission).
- Basic window: system tray icon + togglable main window.
- Anthropic SDK integration. Hardcoded "hello world" message to verify auth.
- Config-root resolution from `~/Documents/.claude-plugin-config-root`.

**Milestone:** Empty window opens via tray click. Successfully sends one Anthropic API call.

### Weeks 3-4: Voice loop

- Integrate 21st.dev voice-powered-orb component.
- Browser SpeechRecognition wired to mic input. User can speak, see transcript.
- Browser SpeechSynthesis wired to AI response. AI speaks back.
- Orb state machine: idle (low pulse) / listening (mic amplitude) / thinking (slow rotation) / speaking (TTS amplitude).
- Fork or extend the orb to accept external audio source (the TTS output stream).

**Milestone:** Press hotkey, speak "hello," AI responds with audible voice while orb pulses.

### Weeks 5-6: Nucleus integration

- Load cortex CLAUDE.md, nucleus-router skill, identity.md, voice.md, user.md, hot.md as cached system prompt.
- Implement prompt caching with 4 cache breakpoints.
- File-system tools (read, write, append) for `<config-root>/`.
- Test: "what's in my memory about Acme" should read `memory/client/acme.md` and respond verbally.
- Test: "remember Sarah Chen is VP Eng at Acme" should write to `memory/person/sarah-chen.md`.

**Milestone:** Real conversations against real cortex memory. Writes back correctly.

### Weeks 7-8: MCP + intent routing

- Custom MCP client in Tauri backend (or Cowork proxy).
- Wire Gmail MCP, Calendar MCP, HubSpot MCP from the user's existing config.
- Test: "what's on my plate today" routes through nucleus-router to `/brief` → reads Calendar + Gmail + HubSpot via MCP → responds verbally.
- Test: "draft a reply to Sarah's email" goes through lead-engine / bizdev-outreach skills, drafts to Gmail.

**Milestone:** The router intent table works end-to-end through voice.

### Weeks 9-10: File watcher + ambient UX

- File watcher on `<config-root>/`. Toast notifications for `.commit-drafts/` writes, `briefs/` updates, etc.
- Quick-action buttons inferred from time of day + recent log entries (e.g., 5pm → "wrap up the day").
- Settings panel: config-root path, autonomy mode, API key entry, voice provider selection.
- Onboarding flow: first run with empty config-root → routes to `/start-nucleus` via voice.
- Error handling: API failures, MCP failures, mic-permission denied.

**Milestone:** Polish pass. App feels alive even when idle.

### Weeks 11-12: Packaging + ship

- macOS code signing + notarization.
- Auto-update via Tauri's updater (or manual download for v1).
- Build a one-page landing on `brightwayai.com` with a demo video.
- Soft launch to ~10 operators in Zach's network.
- Bug-fix sprint based on initial usage.

**Milestone:** v1 is downloadable, signed, runs on a clean Mac without dev tools, makes Zach's existing Nucleus install work as a voice-first cockpit.

### Post-v1 (separate cycles)

- **v1.1:** Windows + Linux builds.
- **v1.2:** Whisper integration for premium voice input (Pro tier).
- **v1.3:** ElevenLabs / OpenAI TTS for premium voice output (Pro tier).
- **v1.4:** Wake-word ("Hey JARVIS").
- **v2.0:** Mobile companion app via Tauri Mobile.
- **v2.5:** Multi-user / team features (multi-tenant).

---

## Privacy, security, and trust

### Local-first by default

The app runs entirely on the user's machine. The only outbound network calls are:
- Anthropic API (user's own API key)
- Whatever MCP servers the user has authorized
- Voice provider (browser SpeechRecognition/Synthesis is local; external Whisper/ElevenLabs are user-opt-in)

No BrightWay telemetry. No usage data leaves the device.

### Microphone permission

macOS will prompt for microphone access on first run. App must declare `NSMicrophoneUsageDescription` in `Info.plist`. UI explicitly explains why the mic is needed and how to revoke.

### API key handling

- Stored in macOS Keychain (or platform equivalent). Never written to plain files.
- Rotatable via settings panel.
- Optionally: BrightWay-hosted proxy for users who don't want to manage their own API key (this is a paid-tier feature).

### Config-root privacy

The app respects the privacy defaults written by cortex `/setup-identity` (`.gitignore`). Doesn't override or weaken them. If user has the recommended symlink for `archive/` → local-only, app reads through the symlink transparently.

### "What the AI heard" log

Every voice transcript is logged to `<config-root>/memory/log.md` via the log-writer skill — same chronicle the rest of Nucleus uses. Users can grep their own history. No off-device storage.

---

## Monetization (revisits productization.md)

The JARVIS app opens a SaaS revenue path the marketplace alone doesn't have. Three tiers, in addition to existing services revenue:

### Free

- Full Tauri app, MIT-licensed (mostly — the app shell stays open-source).
- Browser SpeechRecognition for input, browser SpeechSynthesis for output.
- User brings their own Anthropic API key.
- All Nucleus plugins fully functional.
- Single-machine.

This tier is the lead magnet. People should *want* to share it.

### Pro ($30-49/month or $300-499/year)

- Premium voice in: Whisper via OpenAI (high accuracy, low latency).
- Premium voice out: ElevenLabs (custom voice clone trained on the user's `voice.md` reference samples) or OpenAI TTS HD.
- BrightWay-hosted Anthropic proxy (user doesn't manage their own key; BrightWay handles rate limits and billing).
- Cloud sync of `<config-root>/` across machines (optional; user opt-in).
- Priority support via the existing BrightWay retainer model.
- Update channel: stable + beta.

**Compute cost reality check** (rough):
- Anthropic Sonnet 4 with prompt caching: ~$0.50-2.00/day for a heavy user.
- Whisper: ~$0.006/minute × 30-60 minutes/day = $0.18-0.36/day.
- ElevenLabs voice cloning: ~$22-99/month flat depending on tier.
- Total cost-of-goods: ~$30-60/month per Pro user at heavy usage.

So $49/month gross is $-10 to $+20/month net at heavy usage. Pricing needs to be tuned to expected usage. **Recommended pricing for v1 Pro: $39/month, $399/year.** Tune from real usage data.

### Team ($199-499/month per firm)

- Multi-user JARVIS for consulting firms (2-10 operators sharing a workspace).
- Shared memory pool (per-operator + shared firm memory).
- Admin console for adding/removing operators, viewing aggregate telemetry, managing shared MCP credentials.
- Single Anthropic billing for the firm.
- Requires the multi-tenant work specced separately.

This is the bigger ARR opportunity once Pro is validated.

### Revenue ladder (12-month projection, hypothetical)

| Month | Free users | Pro users | Team firms | MRR |
|---|---|---|---|---|
| 1 (v1 launch) | 50 | 0 | 0 | $0 |
| 3 | 300 | 10 | 0 | $390 |
| 6 | 1,500 | 75 | 1 | $3,125 |
| 9 | 5,000 | 250 | 5 | $11,500 |
| 12 | 10,000 | 600 | 15 | $26,400 |

These numbers are speculative. Real growth depends on TikTok / LinkedIn / content marketing performance. The Free → Pro conversion rate above is ~5-6%, which is reasonable for a productivity SaaS. Team firms come from BrightWay's services pipeline naturally.

Plus continued BrightWay services revenue (setup-in-a-day, custom plugins, training). Those compound on top.

---

## Distribution & marketing

### Channels (in order of expected lead quality)

1. **TikTok / LinkedIn build-in-public.** Daily 15-60 second clips showing the orb doing real operator work. The visual hook is the orb itself. Use Nucleus's existing news-curator + writing-style to draft commentary.
2. **Direct outreach from Zach's network.** BrightWay's existing services pipeline. Solo operators who'd use Pro from day 1.
3. **Product Hunt + Hacker News launch** at v1 ship. Single-day burst; lasting effect depends on whether the demo lands.
4. **Anthropic ecosystem visibility.** Mention in Anthropic's developer community if Nucleus + JARVIS app become a reference implementation of "what you can build on Anthropic API."
5. **Operator community Slacks / Substacks.** Indie consultants, fractional CXOs. Drop demos selectively.

### Marketing assets (build alongside the app)

- A 60-second demo video showing the orb + voice loop + real workflow (drafting outreach, reading brief, ending day).
- A landing page at `brightwayai.com/jarvis` (or similar) — single page, one CTA (download).
- A behind-the-scenes "How I built JARVIS" series for LinkedIn/TikTok.
- The build-log itself becomes content. Don't separate "building" and "marketing" — they're the same flow.

---

## What this proposal does NOT cover (open questions for future iterations)

1. **Wake-word.** "Hey JARVIS" via Porcupine or Picovoice. Requires always-on mic, more battery, more privacy concerns. v1 uses global hotkey instead.
2. **Multi-modal / vision.** Camera input for visual context (e.g., "what's on my screen"). Real but post-v1.
3. **Mobile companion app.** Read-only on phone is achievable via Obsidian mobile today. A full mobile JARVIS app is v2+.
4. **Offline mode.** Anthropic API requires internet. A local-only fallback via Ollama + Llama would be a different product entirely.
5. **Persistent personality / character.** The "voice" of JARVIS itself (vs the user's writing voice). Subtle but matters for delight.
6. **App Store distribution.** macOS App Store has stricter sandbox; might not be feasible for v1's microphone + file-system needs.
7. **Enterprise / SSO.** Team tier needs SSO eventually. Out of v1 and v2.

---

## Decisions to lock before starting

These are the open choices that should be locked before week 1, in order of importance:

1. **Tauri 2.x or 1.x?** Recommend 2.x (active development, mobile support roadmap).
2. **macOS-first or cross-platform from day one?** Recommend macOS-first; Windows + Linux as fast-follow once v1 is validated.
3. **MCP client custom or Cowork-proxy?** Recommend custom (independence from Cowork).
4. **System prompt size — full cortex CLAUDE.md or trimmed?** Recommend full — prompt caching makes this affordable, and the model performs better with the full schema.
5. **Voice provider lock-in or pluggable?** Pluggable (abstract via interface; v1 ships with browser; Pro adds OpenAI/ElevenLabs).
6. **Pricing for Pro tier.** Recommend $39/month ($399/year). Tune from real usage data.
7. **Brand for the app — "JARVIS" or something else?** "JARVIS" is iconic but Marvel/Disney-owned; trademark risk. Pick a Nucleus-aligned name: "Core," "Nucleus Cockpit," "Operator," "Atlas," etc. **Recommend "Operator"** — fits the audience, owns the category, free of IP entanglement.

---

## Estimated cost to ship v1

- **Engineering:** ~12 weeks × $0 (Zach builds it) OR ~$30-60K if hired.
- **Design:** $2-5K for icon set, landing page, demo video editing.
- **Code signing:** $99/year (Apple Developer Program).
- **Anthropic API for development/testing:** ~$200-500.
- **Voice provider setup (testing):** ~$50 (OpenAI/ElevenLabs trial).
- **Distribution infrastructure (auto-update server, etc.):** ~$20/month if hosted; $0 if just direct downloads.

**Total cash outlay for a single-engineer 12-week build to v1: ~$3-5K** (excluding engineering time). Comparatively cheap for a product that opens recurring SaaS revenue.
