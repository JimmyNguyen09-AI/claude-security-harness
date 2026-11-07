# Third-party sources and components

Original project code and documentation are MIT licensed; see [LICENSE](LICENSE).
This license does not relicense third-party tools, dependencies or documentation.

The native ZIP contains project-authored skills, role definitions, documentation,
schemas and a standard-library campaign checker. It does not bundle Claude Code,
the Claude Agent SDK, Semgrep, Gitleaks, OSV Scanner or their databases/rule packs.

The optional Python helper depends on Pydantic. Development tools and transitive
packages have their own license metadata; see `pyproject.toml` and
`requirements.lock.txt` for the tested dependency set. A requirements file is not
a redistribution of those packages. Check their licenses if you redistribute an
environment or image containing them.

[docs/sources.md](docs/sources.md) records the primary research references. Trail
of Bits and OWASP materials informed the workflow; their skill/document bodies were
not vendored. Referenced upstream content retains its original licensing. Future
copied/adapted content must retain provenance and comply with its license; do not
assume this project's MIT license overrides upstream terms.

Claude and Claude Code are names associated with Anthropic. This is an independent
community project and is not affiliated with, endorsed by or maintained by Anthropic,
Trail of Bits or OWASP.
