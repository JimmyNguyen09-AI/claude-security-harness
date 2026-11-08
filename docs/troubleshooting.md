# Troubleshooting

| Symptom | Check | Next action |
|---|---|---|
| No `security-harness` in catalogue | Marketplace source and fetch result | Add `JimmyNguyen09-AI/claude-security-harness`, refresh the marketplace |
| Installed but no slash commands | Enabled state, install scope, current project/session | Enable in plugin manager; start a new session if requested |
| Old commands after updating | Installed version versus repo manifest; duplicate local/plugin-dir copies | Refresh marketplace, update plugin, reopen session; review duplicate scopes before removing anything |
| Desktop has no plugin browser | Code session type and app version | Check current official Desktop docs; use a supported local/SSH session |
| Review is auditing the harness itself | Open workspace and requested target | Open the application repository, then invoke `/security-harness:start` |
| Python/Docker missing | Native versus optional helper workflow | Continue native review; only helper/scanner execution needs those dependencies |
| Tests cannot connect to DB | Fixture setup and actual target | Record blocked; repair local test setup before making a vulnerability claim |
| Campaign reports stale evidence | Source/config/fixture fingerprints | Re-run impacted checks; do not relabel old evidence with a new fingerprint |
| Too many speculative findings | Reachability, invariant, counterevidence | Run `/security-harness:verify`; retain one disposition per candidate |

When the skill loads, `/security-harness:doctor` performs read-only diagnosis.
From a local plugin directory, an optional offline layout check is:

```sh
python skills/doctor/scripts/doctor.py
```

It returns JSON and exit code 0 for a valid layout, 2 for errors. This does not
check credentials, network access, session loading or review effectiveness. No
Python packages are required. Standalone ZIPs need no marketplace manifest.

For a public issue include plugin version, Claude Code version, UI/session type,
redacted error and minimal reproduction. Do not attach credentials, private
source or full environment dumps. Use the security policy for sensitive reports.

Official product behavior changes: verify [Desktop](https://code.claude.com/docs/en/desktop)
and [VS Code](https://code.claude.com/docs/en/vs-code) docs when UI labels differ.
