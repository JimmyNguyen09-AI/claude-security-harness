---
name: doctor
description: Diagnose Security Harness installation, missing skills, version mismatches and local plugin packaging without changing user settings.
---

Diagnose: $ARGUMENTS

Use read-only inspection first. Do not request an API key or change plugin/global
settings automatically. Establish whether the user is in Desktop Code, VS Code,
terminal, or a cloud/remote session. Distinguish the plugin source directory from
the target application's workspace; never assume they are the same folder.

1. Locate this loaded skill and its plugin root. Read `.claude-plugin/plugin.json`.
   Expected plugin name is `security-harness`; marketplace name is
   `claude-security-harness`. Report the installed version, not a guessed latest.
2. Check `skills/*/SKILL.md`, `agents/` and referenced files. If Python is available,
   run the bundled `scripts/doctor.py` relative to this skill's directory, after
   inspecting it. It uses only the standard library and reads plugin files. It
   does not run target code, access the network, change settings or verify model
   behavior. Without Python, perform the same file checks manually.
3. For missing commands, check installation scope, enabled state, duplicate local
   versus marketplace copies and whether the session predates installation.
   Suggest opening the plugin manager and restarting the session if prompted.
   Do not disable or uninstall another copy without the user's authorization.
4. If Desktop/VS Code behavior is version-dependent, consult current official
   Claude Code documentation. Do not present CLI syntax as a GUI click path.
   The marketplace can be added using `JimmyNguyen09-AI/claude-security-harness`.
5. Return observed symptoms, checks performed, concrete cause if established,
   the smallest next action and anything not checked. A valid layout does not
   prove the plugin has loaded into the current Claude session.

If this skill cannot be invoked at all, the user can follow
[troubleshooting](../../docs/troubleshooting.md) from GitHub. Never inspect or
print login tokens, credential stores or complete environment dumps to diagnose
an installation. Report only relevant, redacted settings.
