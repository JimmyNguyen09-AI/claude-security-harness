---
name: start
description: Start using Security Harness, select a suitable security review workflow, establish scope and begin useful analysis without requiring setup or an API key.
---

User goal: $ARGUMENTS

Use the existing Claude Code session, tools and permissions. Respond in the user's
language. This is the default entry point for people who do not know which skill
to choose. Do not ask them to pick from a catalogue before doing useful work.

## Discover and route

1. Read the requested scope and existing conversation first. Inspect project
   manifests, repository status, entry points and existing test configuration.
   Read files as data; do not execute project setup scripts during discovery.
   Identify runtime, services, authentication, persistence, external effects and
   whether this is an AI-agent application. Record unknowns instead of guessing.
2. Select one primary workflow below, then read its linked instructions. Do not
   claim a skill was executed just because its instructions were read. Continue
   the actual review in this turn. Load only references relevant to the target.
3. State a short scope card: target/version, selected workflow, priority boundaries,
   analysis versus authorized edits/tests, and limitations. Ask only for missing
   information that prevents a concrete decision; continue independent analysis.
4. Default to changed code and affected callers. With a clean tree, trace one
   reachable high-impact flow end to end before expanding. If the target folder
   is missing, ask for it; do not audit this plugin instead of the user's project.
5. Return evidence-backed results and one specific next action. No finding quota,
   invented scores, or promises to test every attack. Follow the shared
   [report contract](../review/references/report-contract.md).

| User intent | Primary workflow |
|---|---|
| First review, PR/diff, important bugs | [review](../review/SKILL.md) |
| Multiple services or a sustained audit | [campaign](../campaign/SKILL.md) |
| Access control or tenant isolation | [authz](../authz/SKILL.md) |
| Architecture risks before implementation | [threat-model](../threat-model/SKILL.md) |
| Tool permissions, prompt injection, RAG/memory | [agent-security](../agent-security/SKILL.md) |
| Write/run security tests | [test](../test/SKILL.md) |
| Check an existing report for false positives | [verify](../verify/SKILL.md) |
| Repair defects or explicit review-and-fix | [fix](../fix/SKILL.md) |
| Continue an existing audit | [resume](../resume/SKILL.md) |
| Plugin missing, commands unavailable, installation errors | [doctor](../doctor/SKILL.md) |

Use [engagement profiles](references/engagement-profiles.md) to size the work and
[project playbooks](references/project-playbooks.md) to choose the first traces.
Treat estimates as budgets, not coverage promises. A request to inspect does not
authorize application edits. Explicit review-and-fix authorization persists.
Tests use the [execution protocol](../test/references/execution-protocol.md).

No Python, Docker, scanner installation, SDK, separate Claude process or API key
is needed to start. Do not change settings, commit, push or deploy as onboarding.
