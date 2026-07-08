# Governance

## Purpose

This document defines how the project treats AI-generated outputs, human review, evidence, safety boundaries, and adoption risks. It is intended as practical project framing for a local portfolio demo, not as a legal policy.

## Core Principles

- Human review is required before any action or implementation decision.
- Workflow intelligence should be based on interaction evidence where practical.
- The demo stays local-first unless future integrations are explicitly added.
- Failure cases and exceptions must be captured before recommendations are treated as reliable.
- Adoption risks are part of workflow intelligence, not a separate afterthought.
- AI outputs are structured drafts, not validated truth.
- Staff workload, recognition, role clarity, and trust should be considered in adoption planning.

## Human Review Requirements

The following outputs require human review before use:

- Outreach drafts
- Workflow opportunities
- Adoption plans
- Pilot recommendations
- Success metrics
- Failure cases and adoption risk notes
- Any externally visible or implementation-related recommendation

## Evidence and Source Tracking

Interaction-derived records should preserve source references where practical, including:

- Source interaction IDs
- Note summary IDs
- Evidence excerpts
- Evidence counts
- Last-seen timestamps

Repeated similar findings should strengthen the evidence for an existing record rather than create unnecessary duplicates.

## Safety and Data Boundaries

The project uses local-demo safety boundaries:

- No real email sending
- No SMS or phone automation
- No web scraping
- No OAuth
- No external CRM or cloud connector access by default
- No external AI provider required by default
- Knowledge sources are metadata only unless future integrations are explicitly added

## Evaluation Limitations

AI adoption suggestions do not always have a stable ground truth. Outputs should be treated as reviewable working drafts whose quality depends on the available interaction notes, method knowledge, AI provider, and reviewer judgment.

Future improvements may include reviewer scoring, approval status, stale-date checks, regression tests, and human feedback records.

## Future Governance Improvements

- Approval workflow for AI-generated records
- Confidence or review status fields
- Stale knowledge review
- Reviewer comments
- Policy checks before draft export
- Governance dashboard
- Audit trail for generated outputs
