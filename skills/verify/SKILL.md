---
name: verify
description: Verify existing security findings against source, real enforcement layers and reproducible tests; reject false positives with evidence.
---

Verify the findings/report specified by the user: $ARGUMENTS

Work inside this Claude Code session. Read the supplied report and relevant code,
then the shared [report contract](../review/references/report-contract.md).
If no report is specified, use the findings already in the conversation. If neither
exists, identify that missing input; do not manufacture findings to verify.

For every finding, independently check the premises: actual reachable entry point,
attacker privileges, data flow, middleware/service/database controls and deployment
conditions. Search for the strongest refutation rather than merely restating the
original narrative. Re-read source; do not trust line references blindly.

Return exactly one supported/rejected/inconclusive verdict for each input ID, with
source evidence and reasoning. Never omit a candidate to lower noise. If tests are
authorized and available, inspect and run relevant tests, distinguish setup failure
from behavioral failure, and record actual commands and results. Claim reproduction
only when observed behavior establishes the defect and controls rule out a broken
test environment. Preserve raw secrets in neither test output nor reports.

State whether this was same-session verification or a separate session. This skill
does not automatically create an independent agent. Code changes require an
existing request to fix; otherwise return concrete remediation without edits.
