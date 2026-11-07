# Contributing

Thanks for helping improve Security Harness. This is an experimental community
plugin for Claude Code, maintained independently of Anthropic.

## Scope

The native skills and agent roles are the main product. Keep them usable with the
user's existing Claude Code session, without API keys, SDK orchestration or mandatory
Python/Docker dependencies. Local helpers are optional. Do not broaden tool grants
or override the user's model to make a workflow easier to run.

Use [SECURITY.md](SECURITY.md) for vulnerabilities in this project. Ordinary issues
should include the plugin version, Claude Code version, OS, expected/observed
behavior and a small synthetic reproduction. Never attach private source, tokens,
customer data or unredacted model/tool transcripts.

## Development

Python 3.11+ is needed only for helper development and automated tests:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python -m pip check
python scripts/export_schemas.py
python scripts/package_plugin.py
python scripts/check_release.py
```

If Claude Code is installed, also run `claude plugin validate .`. It may report
marketplace-specific metadata notices; local plugin validity is a different check.
Build optional Python distributions with `python scripts/build_release.py` to avoid
carrying stale generated files into a wheel.

## Pull requests

- Explain the concrete problem, resulting behavior and evidence for the change.
- Keep scope focused. Preserve explicit user authorization and existing edits.
- Test security invariants and failure cases, not only implementation details.
- For skills, verify relative links and realistic tasks. Distinguish a behavioral
  Claude Code evaluation from structural validation and unit tests.
- Include coverage gaps, unexecuted tests and environment limitations honestly.
- Avoid copied third-party skill/rule text unless provenance, license and required
  notices are supplied and compatible. Discuss new dependencies first.
- Do not commit `.env` files, local profiles, artifacts, virtual environments or
  real audit reports. Fixtures must be synthetic and clearly labeled.

The test suite does not require a Claude login or network scanner targets. CI must
not receive production credentials or run live attack tests. Changes to workflows
and execution permissions deserve particular scrutiny.

Contributions are submitted under this repository's MIT license. Ensure you have
the right to contribute the code and documentation you submit. AI-assisted changes
are welcome with the same review, attribution and test requirements; generated
test results must never be presented as observed execution.
