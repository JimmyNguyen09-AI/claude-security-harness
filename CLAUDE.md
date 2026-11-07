# Project context

This repository is a native Claude Code security-review plugin. Its main entry
points are `.claude-plugin/plugin.json`, `skills/` and the specialist `agents/`.
The user intends Claude Code to read, review and fix code in its existing session.
Do not reintroduce an API-key requirement or an SDK-based model orchestrator.

`src/security_harness` contains optional local helpers for snapshots, container
scanners and evidence validation. Helpers do not call any model. Native workflows
must remain usable without Python, Docker or those helper dependencies.

For plugin changes, validate the manifest with `claude plugin validate .`, verify
reference links and run the relevant tests. Package with `python scripts/package_plugin.py`.
For helper changes run the Python test suite in `.venv-native` (or a fresh dev env).
Skill instructions are workflow guidance, not a security sandbox. Never claim
runtime or model-behavior verification based only on schema/unit tests.

Campaigns use explicit scope fingerprints and a surface-by-domain coverage ledger.
Tester roles must distinguish planned, executed, failed and blocked checks and
preserve negative/positive controls. The optional campaign checker is stdlib-only
and ships with the plugin; it does not execute tests or prove evidence semantics.
