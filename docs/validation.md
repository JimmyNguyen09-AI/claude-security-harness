# Validation

## Native v0.4 — 2026-11-08

- Local Python suite: **137 passed, 1 skipped** on Windows. The skipped case needs
  permission to create a symlink; it remains enabled on hosts that support it.
- Eleven skills and five roles checked; all local instruction links resolve.
- Claude Code's own plugin/marketplace validator passed. Non-blocking notices
  concern the maintainer-only root CLAUDE.md and a missing directory-listing icon.
- New tests exercise safe indirect authorization, tenant-admin boundaries,
  protected-field atomicity, valid edits and returned-object isolation.
- `doctor` rejects missing/malformed manifests, missing components, broken links,
  escaping references and invalid marketplace sources. Its diagnostics do not
  print file contents. Layout validity is not proof of model behavior.
- The native ZIP was extracted into a separate directory and its bundled doctor
  ran under Python isolated mode without installed third-party dependencies.
- Six manual Claude exercise cases, eight campaign scenarios and an unexecuted
  trial template are provided. No live Claude evaluation was run for this release.

## Native v0.3 — historical checks

The main deliverable is the local Claude Code plugin, not an SDK application.

- Claude Code's own `plugin validate .` accepted the native manifest/layout.
  The plugin now declares its public author and MIT license. Marketplace icon
  metadata is separate from local plugin validity; no marketplace submission is claimed.
- `python -m pytest -q`: **106 passed** in the SDK-free environment (Windows, Python 3.12).
- All nine native skills passed skill-creator validation; reference links and
  imported review/verifier evidence have automated tests.
- The helper is tested without importing Claude/Anthropic SDK packages.
- A fresh `.venv-native` environment without the Claude SDK verified the optional
  Python helper. `pip check` found no broken requirements.
- Native plugin ZIP is packaged separately from the optional Python wheel.
- Source and native ZIP passed the configured release-hygiene checks, including
  known token patterns, private-key blocks, personal Windows paths and excluded
  local/generated files. These limited patterns are not a comprehensive secret scan.
- Gitleaks 8.30.1 scanned the staged source export with default rules and reported
  no leaks. Its downloaded Windows archive was SHA-256 checked against the official
  release metadata. A false positive on a non-secret coverage tuple was resolved
  by clarifying its variable name; no scanner rule was disabled.
- CI is configured for Python 3.11/3.12 on Windows and Ubuntu; local test results
  do not establish that the hosted CI jobs have passed.
- Five agent-role definitions are checked for names and tool boundaries; no role
  overrides the session model or grants bypass permissions.
- Campaign tests cover stale scope/evidence, tampered hashes, traversal, missing or
  duplicate coverage, fake execution claims, missing positive/negative controls,
  inappropriate reproduced/fixed statuses and fail-closed malformed ledgers.
- The stdlib-only campaign CLI initializes 36 planned cells for two surfaces and
  returns INCOMPLETE before any review/test evidence is supplied.

No live model request was made. A real interactive Claude Code review has not been
behaviorally evaluated; login, subscription limits and model availability remain
those of the user's Claude Code session. Docker/scanner runtime integration remains
unverified from the earlier checks; it is not a prerequisite for native review.
The eight campaign scenarios are proposed behavioral evaluations, not executed
Claude benchmarks. No claim of exhaustive attack coverage or measured recall is made.
