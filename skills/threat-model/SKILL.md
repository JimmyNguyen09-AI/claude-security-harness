---
name: threat-model
description: Build an evidence-backed threat model and abuse-case backlog across service, identity, data and infrastructure boundaries.
---

Model threats for: $ARGUMENTS
Use the existing session and relevant source/configuration. Read
[orchestration](../campaign/references/orchestration.md) and the
[domain catalogue](../test/references/security-catalogue.md).

Map assets, principals, entry points, data flows, dependencies and trust boundaries.
Distinguish observed configuration from assumptions about deployment and intended
product rules. Include anonymous, compromised user, tenant admin, service identity,
malicious dependency and untrusted retrieved content where relevant.

For each threat record actor/preconditions -> boundary crossed -> abuse sequence ->
asset/invariant affected -> existing defenses -> evidence -> proposed verification.
Assess impact and feasibility separately; do not manufacture a numeric risk score.
Use spoofing, tampering, repudiation, disclosure, denial and privilege escalation
as prompts, then add business-specific abuse chains and multi-service interactions.

Return a prioritized threat register linked to surfaces and test cases, assumptions,
unresolved policy questions and the coverage matrix. Threats are hypotheses, not
findings, until source/runtime evidence supports them. Route AI-agent surfaces to
the agent-security workflow. Keep threat modeling useful without blocking source
review while missing deployment information is requested.
