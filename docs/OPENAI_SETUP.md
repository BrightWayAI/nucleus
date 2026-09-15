# Nucleus on ChatGPT and Codex

Nucleus is the master marketplace, not a fourteenth runtime plugin. Importing the
Nucleus repository makes its 13 catalog entries available; users or workspace admins
still choose which entries to install. `nucleus-router` is the conversational front
door. `cortex` owns shared memory, identity, and voice. The other plugins are
independent specialists that compose through the same config root.

## Supported surfaces

| Surface | Skills | Shared local files | Connector-dependent workflows |
|---|---|---|---|
| ChatGPT desktop Local Work | Supported | Supported after folder permission | Supported when the required app/MCP connector is installed |
| Codex | Supported | Supported when the config root is a readable/writable sandbox root | Supported when the required tool/MCP connector is available |
| ChatGPT web/cloud | Supported | Unavailable without an approved remote MCP bridge | Supported only through workspace apps/connectors |

The GitHub repositories contain workflow code and templates. They do not contain,
upload, or synchronize anyone's memory. Each member should use a private config root;
do not point multiple people at one shared folder as a collaboration database.

## Import the marketplace in a ChatGPT workspace

A workspace administrator:

1. Opens workspace plugin management and chooses **Import from GitHub**.
2. Enters `https://github.com/BrightWayAI/nucleus` and leaves the path blank.
3. Pins a reviewed release tag or commit when the UI offers a revision selector.
4. Reviews all 13 referenced repositories.
5. Marks the desired plugins Available or Installed for the intended roles.

The native catalog is `.agents/plugins/marketplace.json`. GitHub import does not make
every entry active automatically and does not grant filesystem or connector access.
Plugins with local MCP servers—Cortex in particular—are desktop-only unless an
approved remote bridge is configured.

Start a new ChatGPT desktop Local Work chat after installation. Enable at least:

- `nucleus-router` — natural-language routing;
- `cortex` — shared memory, identity, and voice;
- `core-ops` — diagnostics and operational utilities.

Then add specialists for the user's actual work. Installing all 13 is supported but
not required.

## Install from Codex

From a trusted checkout or the GitHub marketplace:

```bash
codex plugin marketplace add https://github.com/BrightWayAI/nucleus
codex plugin add nucleus-router@nucleus
codex plugin add cortex@nucleus
codex plugin add core-ops@nucleus
```

Install other entries with `codex plugin add <plugin-name>@nucleus`, then start a new
thread so the newly installed skills and role bindings are loaded. A local checkout
can be registered by replacing the GitHub URL with the absolute path to the Nucleus
repository.

## Choose the shared memory location once

Existing Claude users should not create another memory store. Cortex resolves the
same path in this order:

1. explicit workflow/project override;
2. `CORTEX_CONFIG_ROOT`;
3. `~/.cortex/config-root`;
4. legacy `~/Documents/.claude-plugin-config-root`;
5. `~/Documents/Claude`.

For a new user, enable Cortex and ask:

```text
@Cortex configure my memory at ~/Documents/Cortex. Show the exact path and ask
before creating anything.
```

Or, from a trusted Cortex checkout:

```bash
python3 scripts/configure_cortex.py --config-root "$HOME/Documents/Cortex"
```

This writes the vendor-neutral pointer `~/.cortex/config-root` and initializes only
missing starter files. It does not migrate or delete an old root. There is no separate
GPT config file. In Codex, also grant the resolved absolute root as a sandbox writable
root for mutating workflows. In ChatGPT desktop, grant Local Work access to that same
folder.

Identity and voice are not separate plugins:

- `@Cortex set up my identity` writes `<config-root>/identity.md` after review.
- `@Cortex set up my voice` writes `<config-root>/voice.md` after review.

Every specialist reads those same files. Per-plugin setup writes settings under
`<config-root>/plugins/`.

## Essential first-run prompts

| Goal | ChatGPT prompt | Codex skill form |
|---|---|---|
| Check the resolved root | `@Cortex report status only; do not read memory` | `$cortex:recall` only after checking the root with the Cortex hook/helper |
| Set identity | `@Cortex set up my identity` | `$cortex:setup-identity` |
| Set voice | `@Cortex set up my voice` | `$cortex:setup-voice` |
| Recall | `@Cortex recall what we know about Acme` | `$cortex:recall Acme` |
| Save this conversation | `@Cortex show what you would remember, then ask before saving` | `$cortex:remember` |
| See the stack | `@Core Ops diagnose my Nucleus setup` | `$core-ops:diagnose` |
| Route naturally | `@Nucleus Router what should handle this request?` | `$nucleus-router:route` |

Claude slash-command names remain useful aliases in documentation. ChatGPT users can
ask naturally or mention a plugin with `@`; Codex exposes namespaced skills. The
underlying workflow remains the same.

## Agents and degradation

The six non-Cortex role definitions have read-only Codex bindings. When the host can
delegate, they return research/ranking output to the parent workflow. When it cannot,
the parent follows the same role inline. Agents never receive independent authority to
write files, mutate CRM, send mail, or register schedules.

Each plugin includes `references/openai-portability.md`, which maps Claude/Cowork
examples capability by capability. Important fallbacks include:

- Cowork HTML artifacts become Markdown or supported document artifacts.
- Missing Slack, CRM, mail, calendar, Apollo, or Drive connectors are reported and
  skipped; the model never invents their data.
- Scheduling is performed only when the active host exposes a scheduler and the user
  confirms the registrations.
- Outbound messages, invoices, and status updates remain drafts unless a separate
  confirmed send action is explicitly requested.

## Validate a checkout without real user data

Place the 13 repositories as siblings under one parent directory, then run:

```bash
python3 scripts/generate_openai_adapters.py --check
python3 scripts/check_openai_ecosystem.py
python3 scripts/smoke_codex_marketplace.py
python3 scripts/release_ecosystem.py check --all
```

The ecosystem check validates manifests, marketplace ordering, versions, command-to-
skill coverage, role bindings, and config-root precedence using a temporary home. It
does not resolve or read the operator's real config root. Cortex has an additional
fixture-only suite:

```bash
python3 ../claude-cortex/scripts/check_repo.py
```

Connector behavior still requires the corresponding test workspace/account. Static
validation can prove honest degradation and binding coverage; it cannot prove access
to Slack, CRM, mail, calendar, or Drive credentials that were not supplied.

Before promoting a coordinated release, run Core Ops `test-connectors` in each required
host and validate the sanitized reports as described in
`docs/CONNECTOR_INTEGRATION_TESTING.md`. A real tool call is required for a pass.
