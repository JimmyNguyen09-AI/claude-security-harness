# Sources

The primary integration is now native Claude Code skills, following the user's
clarification. The earlier SDK-based architecture was removed from executable code.

- [Claude Code skills](https://code.claude.com/docs/en/skills): SKILL.md discovery,
  supporting references and plugin command names.
- [Claude Code plugins](https://code.claude.com/docs/en/plugins): local plugin layout
  and loading a folder into an existing Claude Code workflow.
- [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference):
  .claude-plugin/plugin.json and component locations.
- [Trail of Bits skills](https://github.com/trailofbits/skills): security audit
  workflow inspiration, including differential review and counterevidence.
  No third-party skill text was copied or installed. Review licensing before
  adapting upstream CC-BY-SA-4.0 content.
- [Anthropic security review](https://github.com/anthropics/claude-code-security-review):
  workflow reference; its prompt-injection limitations remain relevant.
- [OWASP ASVS](https://asvs.owasp.org/): framework for verification requirements;
  this harness makes no ASVS compliance claim.
- [Semgrep](https://github.com/semgrep/semgrep),
  [Gitleaks](https://github.com/gitleaks/gitleaks),
  [OSV](https://github.com/google/osv-scanner): optional scanner integrations.
- [OSV offline database](https://github.com/google/osv-scanner/blob/main/docs/offline-mode.md):
  optional runner's cached database contract.

v0.3 additionally consulted:

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents): role files,
  tool boundaries and inherited session model/permissions.
- [OWASP WSTG](https://owasp.org/projects/web-security-testing-guide): security
  testing categories and test methodology. Pin the reference version when mapping
  requirements; the current stable/development distinction matters.
- [OWASP GenAI security project](https://owasp.org/projects/top-10-for-large-language-model-applications):
  LLM and agent-system risks. The custom catalogue is not an official compliance
  mapping or an exhaustive reproduction of the OWASP documents.
