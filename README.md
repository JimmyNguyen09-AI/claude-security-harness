# Security Harness for Claude Code

[Tiếng Việt](README.vi.md) · [MIT license](LICENSE) · [Security policy](SECURITY.md)

**Security review, threat modeling and adversarial testing inside your existing
Claude Code session.** Nine skills and five specialist roles help review code,
verify findings, test security boundaries and fix confirmed defects.

No separate Anthropic API key or Agent SDK is required. Python and Docker are
optional helper dependencies, not prerequisites for the native workflows.

**Status: experimental.** Structural/unit tests are available; real Claude Code
behavioral benchmarks and scanner-container integration have not been completed.
This is an independent community project, not an official Anthropic product.

## Quick start

### Install from the graphical interface

This repository is also a community marketplace. Add this GitHub source in your
plugin manager's **Marketplaces** tab:

```text
JimmyNguyen09-AI/claude-security-harness
```

- **Claude Desktop, Code tab:** start a local session, click **+** beside the
  prompt, then **Add plugins** (or **Plugins → Browse plugins**).
- **VS Code:** type `/plugins` in the Claude Code chat box to open the graphical
  plugin manager.

After adding the marketplace, find **security-harness** under **Plugins**, click
**Install**, and choose your installation scope. Start a new session if prompted.
Enter `/security-harness:review` in the chat box to use it.

Marketplace name: `claude-security-harness`. Plugin name: `security-harness`.
This is a self-hosted community catalog, not a listing in Anthropic's official
marketplace. Desktop's plugin browser requires a local or SSH session; it is not
available in cloud or WSL sessions.

See the official [Desktop instructions](https://code.claude.com/docs/en/desktop#install-plugins)
and [VS Code instructions](https://code.claude.com/docs/en/vs-code#manage-plugins).

### Load a local checkout

Clone this repository into a tools directory:

```sh
git clone https://github.com/JimmyNguyen09-AI/claude-security-harness.git
```

From the project you want to review, launch Claude Code with the plugin path:

```sh
cd /path/to/your-project
claude --plugin-dir /path/to/claude-security-harness
```

Windows PowerShell example:

```powershell
cd C:\projects\your-project
claude --plugin-dir C:\tools\claude-security-harness
```

Use your normal Claude Code login. The plugin loads for this session; it does not
edit global settings or replace the target project's `CLAUDE.md`.

Inside Claude Code:

```text
/security-harness:review review this project, prioritizing authorization and failure paths
/security-harness:verify challenge the findings and check for false positives
/security-harness:test implement and run local regression tests for confirmed defects
/security-harness:fix fix the confirmed issues and preserve legitimate behavior
```

Review is read-only with respect to application behavior unless fixes are requested.
You can ask for review-and-fix in one instruction. Existing user edits are preserved.

## Large repositories and AI-agent applications

```text
/security-harness:campaign audit this monorepo; split work by trust boundary and save checkpoints outside the repository
/security-harness:threat-model map API, worker, database and external-service abuse paths
/security-harness:authz check ownership, field permissions and cross-tenant access
/security-harness:agent-security test prompt injection, tool authorization, memory/RAG isolation and approval replay
/security-harness:resume continue the campaign saved at /path/to/audit-run
```

| Skill | Purpose |
|---|---|
| `review` | Evidence-backed source review and explicit coverage limits |
| `authz` | Subject/action/resource/tenant/context authorization checks |
| `verify` | Counterevidence and one verdict per candidate |
| `fix` | Scoped remediation and positive/negative regressions |
| `campaign` | Risk-based work packages, role coordination and checkpoints |
| `threat-model` | Assets, actors, boundaries and abuse-case backlog |
| `test` | Test design, implementation, execution and actual observations |
| `agent-security` | AI-agent-specific attack surfaces and enforcement checks |
| `resume` | Restore context and invalidate evidence after source/configuration drift |

The architect, reviewer and verifier roles expose read/search tools. Tester and
fixer roles use normal session permissions. No role overrides your selected model
or grants bypass permissions. Delegation depends on the session and task; roles can
run sequentially when delegation is unavailable or outside scope.

Coverage is tracked by **surface × 18 security domains**, including authentication,
authorization, tenant isolation, injection, browser/network/file boundaries,
crypto/secrets, privacy, business logic, concurrency, resilience, API protocols,
infrastructure, supply chain, detection, AI-agent security and memory safety.

Read the [campaign design](docs/scalable-campaigns.md) and
[architecture](docs/architecture.md) for work-package contracts and trust boundaries.
Some detailed design documents are currently in Vietnamese; skill instructions are
in English and can be used with requests in either language.

## Evidence and testing

- Testers distinguish planned, executed, failed and blocked cases.
- Negative cases are paired with legitimate positive controls and side-effect checks.
- Repository, tool and retrieved text do not authorize new actions.
- Scope changes invalidate evidence; old results must not be relabeled as current.
- Same-session verification is not presented as independent verification.
- Skills are workflow guidance, **not a sandbox or proof of comprehensive security**.

The optional stdlib-only campaign checker ships with the plugin:

```sh
python skills/campaign/scripts/campaign_state.py init \
  --out /path/to/new-audit-run --scope CURRENT_INPUT_FINGERPRINT --surfaces api worker
python skills/campaign/scripts/campaign_state.py check \
  /path/to/new-audit-run --scope CURRENT_INPUT_FINGERPRINT
```

These commands run from this harness repository. The fingerprint must reflect
actual source, dirty content, effective configuration and fixtures. The checker
verifies ledger structure, references and hashes; it does not compute the complete
fingerprint, execute tests or prove that artifact contents are true.

## Optional Python helpers

The source repository also contains commit-snapshot, restricted container-scanner
and JSON evidence-checking helpers. They never call a model:

```sh
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
python -m pytest -q
```

See [local helper documentation](docs/local-helpers.md). Scanner images must be
reviewed and pinned by digest. Missing required tools yield incomplete coverage;
they do not prevent native source review in Claude Code.

`requirements.lock.txt` records the tested development environment. It is not a
hash-locked supply-chain guarantee. Scanner binaries, databases and virtual
environments are not bundled with the plugin.

## Build and contribute

```sh
claude plugin validate .
python scripts/package_plugin.py
python scripts/check_release.py
```

The native archive is written to `dist/security-harness-native-0.3.0.zip`.
Extract it and point `--plugin-dir` at the directory containing `.claude-plugin/`.
Generated archives are not committed; maintainers can attach checked builds to a
GitHub release when publishing one.

[Contributing](CONTRIBUTING.md) · [Validation record](docs/validation.md) ·
[Changelog](CHANGELOG.md) · [Sources](docs/sources.md) ·
[Third-party notices](THIRD_PARTY_NOTICES.md)

## License

MIT © 2026 JimmyNguyen09-AI. See [LICENSE](LICENSE). Third-party tools and referenced
materials retain their own licenses. Claude and Claude Code are associated with
Anthropic; this project is not affiliated with or endorsed by Anthropic.
