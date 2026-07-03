# Outreach Intelligence Platform

A portfolio demo for **AI-assisted outreach and workflow intelligence**. The platform turns organization profiles and interaction notes into structured knowledge about practical AI adoption opportunities, required knowledge sources, failure cases, human-review needs, and human-system adoption risks.

This project is intentionally safe: **it does not send real emails**. AI-assisted drafts are saved to a local **Demo Outbox** for human review and manual sending outside the app.

## Product Thesis

Successful AI adoption is not only a technical problem. Organizations also need to understand workflow pain points, knowledge sources, human-review requirements, failure cases, staff concerns, evaluation ambiguity, recognition gaps, and training needs.

The platform therefore treats **adoption risk as part of workflow intelligence**, not as a final afterthought. When interaction notes are entered, the system does not only look for possible AI-use opportunities. It also captures human-system risks that could affect whether an opportunity is realistic, trusted, and sustainable.

The core product idea is:

```text
Organization profile + interaction notes
  → AI-assisted note summary
  → workflow opportunities
  → knowledge sources
  → failure cases / exceptions
  → human-system and adoption-risk notes
  → workflow insights for future adoption planning
```

## What This Is

This is not meant to replace a CRM. It is an **AI intelligence layer** that can sit above different data sources.

Current data source:

- Local JSON demo CRM

Future data sources:

- Salesforce
- HubSpot
- Microsoft Dynamics
- Zoho CRM
- CSV import/export

## What Makes This Project Different

Many AI demos focus on prompt writing, generic productivity, or automated outreach. This project focuses on the earlier discovery stage of practical AI adoption:

- What workflow pain points are visible from real interactions?
- Which repeated tasks may be suitable for AI assistance?
- What knowledge sources would AI need before it could help safely?
- Where is human judgment still required?
- What could fail, and what exceptions need to be captured?
- Are there staff concerns around workload, trust, evaluation, or recognition?
- Which opportunities are low-risk enough to validate before broader planning?

The project is designed to show **human-reviewed AI adoption discovery**, not autonomous outreach or full automation.

## Current Feature Areas

### 1. CRM Workspace

The CRM Workspace provides the local organization directory and relationship context.

- Organization directory
- Contact name, general contact email, phone number, and website
- Outreach status
- Last interaction notes
- Editable contact fields
- Local JSON data storage
- Connector-agnostic service layer

### 2. Interaction Notes and AI Summaries

Interactions are the main source of workflow intelligence.

- Record interactions per organization: Meeting, Call, Email, Research Note, Follow-up, or Other
- Store date, title, notes, outcome, next action, follow-up date, and tags
- Run **AI Note Summary** on an interaction to extract structured knowledge
- Extract summary, discussion points, decisions, action items, risks, recommended follow-up, tags, and suggested follow-up tasks
- Use local mock AI logic only — no external API calls

### 3. Workflow Opportunities

Workflow Opportunities capture possible AI-use cases discovered from interaction notes.

Each opportunity may include:

- Current process
- Pain point
- Possible AI support
- Repetitive task pattern
- Human review requirement
- Required knowledge sources
- Known failure cases
- Staff impact
- Adoption risk level
- Next discovery questions
- Source interaction or note summary
- Status: `Identified`, `Needs Validation`, `Candidate for Pilot`, or `Not Suitable`

Workflow opportunities should behave as **organization-level accumulated knowledge**. If similar opportunities appear across multiple interactions, they should be merged or treated as stronger evidence rather than displayed as duplicates.

### 4. Knowledge Sources

Knowledge Sources record where required information lives.

Examples:

- FAQ documents
- Past meeting notes
- Past emails or drafts
- Policies
- Templates
- Q&A records
- Training materials
- Reports
- Public website content
- Staff expertise

Knowledge sources are metadata only. The app does not access external files or cloud storage.

### 5. Failure Cases and Exceptions

Failure cases capture what could go wrong before an AI-supported workflow is proposed too confidently.

Each failure case may include:

- What failed or may fail
- Why it failed
- Missing context
- Human review requirement
- Suggested prevention step
- Related workflow opportunity
- Source interaction

This supports the project’s human-in-the-loop design: failure cases define where review, safeguards, or more knowledge are required.

### 6. Human System and Adoption Risks

Human-system risks are part of the core product model.

Each organization can have **Adoption Risk Notes** that capture risks such as:

- Workload increase risk
- Staff trust concerns
- Unclear evaluation criteria
- Lack of recognition for AI-enabled efficiency
- Role confusion
- Training gaps
- Knowledge-sharing gaps
- Quality or privacy concerns
- Missing adoption safeguards

Each risk note may include risk type, description, severity, related staff role, suggested mitigation, source interaction, and tags.

This section reflects the idea that AI adoption can fail if people, incentives, workflows, and leadership practices are not ready.

### 7. Workflow Insights

Workflow Insights aggregate the structured knowledge created from interactions.

Tracked patterns may include:

- Total searchable knowledge items
- Organizations with or without interaction history
- Workflow opportunities identified
- Opportunities requiring human review
- Organizations missing knowledge source notes
- Failure cases recorded
- Candidate pilot workflows
- Adoption risk notes recorded
- Staff concern notes
- Evaluation or recognition risk notes
- High-severity adoption risks

The UI should use product-facing labels such as **Workflow Insights** or **Workflow Intelligence** rather than user-facing “Phase 3” wording.

### 8. Knowledge Search

Route: `/knowledge-search`

Knowledge Search indexes local data including:

- Organizations
- Interactions
- Follow-up tasks
- Demo Outbox drafts
- Lessons learned
- Reusable insights
- Playbook candidates
- Workflow opportunities
- Knowledge sources
- Failure cases
- Human-system and adoption-risk notes

Search supports keyword search, organization filtering, and content-type filtering.

### 9. Demo Outbox

The Demo Outbox is a separate human-review queue for AI-assisted outreach drafts.

- Saves generated email drafts locally
- Does not send emails
- Does not use SMTP, Gmail, Outlook, or OAuth
- Allows review before a human manually sends outside the app
- Keeps draft review separate from CRM relationship tracking

Preferred product model:

```text
CRM Workspace = organization and relationship context
Demo Outbox = human-reviewed draft queue
```

### 10. Adoption Principles / Method Knowledge

The project can store reusable AI adoption principles derived from research notes. These principles guide how future interaction notes are interpreted into workflow opportunities, knowledge sources, failure cases, human-system risks, and future planning inputs.

Initial principles include:

- AI adoption should start with small, repeatable workflow-efficiency wins before larger revenue or automation projects.
- AI training should focus on changing real workflows, not only teaching tool usage.
- Effective AI workflows require structured, searchable, reliable knowledge sources.
- Failure cases and exceptions should be documented because they define where human review is needed.
- Experienced staff should guide AI workflow design because they can judge output quality.
- AI should support experienced workers by helping turn their knowledge into repeatable workflows.
- Workflows should be decomposed into smaller steps before deciding whether each step belongs to generative AI, browser automation, OCR, search, templates, or human judgment.
- Human review should remain explicit for externally visible, quality-sensitive, private, or judgment-heavy work.

## Demo Workflow

1. **Research Intake** → fill in organization details → save to CRM
2. **Organization Discovery** → enter a research theme → review mock candidates → approve one → it joins the CRM
3. Open **CRM Workspace** → select an organization → review summary, readiness, outreach recommendation, and interaction history
4. Add an **Interaction** with meeting or research notes
5. Run **AI Note Summary** → extract follow-up tasks and workflow intelligence
6. Review generated **Workflow Opportunities**, **Knowledge Sources**, **Failure Cases**, and **Human System / Adoption Risk Notes**
7. Use **Knowledge Search** to find relevant lessons, risks, sources, or opportunities across organizations
8. Use **Workflow Insights** to review patterns across the local dataset
9. Generate **Next Best Email** → review and edit the draft → save to **Demo Outbox**
10. Export data via CSV or JSON at the Data Tools page

## Safety Boundaries

- **No real email sending.** Drafts are saved locally to `backend/app/data/outbox.json`. No SMTP, Gmail API, or Outlook API is configured or called.
- **No SMS or phone automation.** Phone numbers are stored as informational strings only. No Twilio, no calling, no texting.
- **No web scraping.** Research Intake requires manual entry. Organization Discovery uses local mock data only.
- **No external API calls.** All AI responses are mocked locally. No OpenAI, no external CRM APIs, no cloud services.
- **No OAuth.** No OAuth flows are configured for any connector.
- **All Salesforce, HubSpot, Gmail, Outlook, Google Drive, Dropbox, SharePoint, OneDrive, and OpenText files are stubs only.** No credentials are stored, no tokens are requested, and no external systems are contacted.
- **Human review required before any action.** All recommendations, assessments, tasks, and drafts are informational. No auto-creation or auto-sending of any kind.
- **Attachments are stored locally only.** Uploaded files stay in `backend/data/attachments/`. No file is sent or shared externally.
- **Knowledge sources are metadata only.** No external files or cloud repositories are accessed.

## Frontend Pages

```text
/                         CRM workspace with organization list, organization detail, AI actions,
                          interaction history, knowledge summary, meeting notes, and follow-up tasks
/research-intake          Manual research intake form for saving reviewed organizations to the Local CRM
/organization-discovery   Mock candidate discovery workflow with Approve, Edit, and Reject review actions
/knowledge-search         Search across organizations, interactions, tasks, drafts, workflow opportunities,
                          knowledge sources, failure cases, and adoption risk notes
/demo-outbox              Separate local draft review queue; no sending
/integrations             Read-only architecture overview with connector stubs and import/export notes
/data-tools               CSV import with preview-then-confirm flow, CSV export, and JSON export
/analytics                Workflow Insights and analytics: overview metrics, outreach pipeline,
                          readiness summary, follow-up workload, draft activity, and workflow intelligence
/priority-queue           All organizations ranked by outreach priority score with filtering
/follow-ups               Global follow-up task list with filters by status, priority, and organization
```

## Organization Detail Tabs

The organization detail view should keep organization-specific data separated into readable tabs:

```text
Overview
Interactions
Workflow Opportunities
Knowledge Sources
Failure Cases
Human System
Insights
```

This reinforces the product flow: interactions are the raw source, while the other tabs show structured workflow-transformation knowledge derived from those interactions.

## Development Roadmap

The app currently includes features that correspond to three internal development stages. These stage labels are useful for the README and developer planning, but the app UI should use product-facing labels such as **Workflow Intelligence** and **Workflow Insights**.

### Foundation Features

- Local demo CRM
- Research Intake
- Organization Discovery
- Organization summaries
- AI Opportunity Analysis
- Context-aware email drafting
- Demo Outbox
- Meeting support
- Interaction history
- Organization Knowledge Summary
- AI Readiness Assessment
- CSV/JSON import and export
- Analytics dashboard

### Outreach Intelligence

- Outreach Recommendation
- Priority Queue
- Meeting Intelligence
- Suggested follow-up task generation
- Follow-up Tasks page
- Outreach Recommendation with task awareness
- Analytics with task statistics

### Workflow Transformation Knowledge

This layer captures structured knowledge about workflows, human systems, and adoption readiness from interactions. It prepares the information needed for future AI adoption planning, but does not generate final adoption plans.

Implemented or planned items include:

- Organization Timeline
- Lessons Learned
- Reusable Insights
- Playbook Candidates
- Global Knowledge Search
- Enhanced Knowledge Summary
- Workflow Opportunity Records
- Knowledge Source Tracking
- Failure Case / Exception Tracking
- Human System / Adoption Risk Notes
- Workflow Insights analytics
- Optional Adoption Principles / Method Knowledge
- Source-aware links back to the interaction or note summary that produced each record

## Source-Aware Interaction-Derived Data

Workflow intelligence should be evidence-based. Records created from AI Note Summary should preserve source references where practical:

```text
source_interaction_id or source_interaction_ids
source_note_summary_id or source_note_summary_ids
evidence_excerpt or evidence_excerpts
evidence_count
last_seen_at
```

This allows the app to show why a workflow opportunity, knowledge source, failure case, or adoption risk exists.

## Duplicate Handling

Workflow opportunities, knowledge sources, failure cases, and adoption risk notes should avoid unnecessary duplicates.

For example, if three Waterloo Public Library interactions mention variants of “follow-up email drafting,” the app should show one accumulated opportunity with stronger evidence, not three duplicate cards.

Suggested deduplication fields:

```text
canonical_title
normalized_key
evidence_count
source_interaction_ids
source_note_summary_ids
evidence_excerpts
last_seen_at
```

Deduplication should be organization-specific, not global.

## Project Structure

```text
outreach_intelligence_platform/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── models.py
│       ├── connectors/
│       │   ├── base.py
│       │   ├── local_json.py
│       │   ├── salesforce_stub.py
│       │   └── hubspot_stub.py
│       ├── services/
│       │   ├── ai_mock.py
│       │   ├── analytics.py
│       │   ├── attachments.py
│       │   ├── data_tools.py
│       │   ├── field_mapper.py
│       │   ├── interaction_summaries.py
│       │   ├── interactions.py
│       │   ├── knowledge.py
│       │   ├── outbox.py
│       │   ├── outreach_recommendation.py
│       │   ├── research_mock.py
│       │   ├── tasks.py
│       │   └── workflow.py
│       └── data/
│           ├── interactions.json
│           ├── organizations.json
│           ├── outbox.json
│           └── tasks.json
└── frontend/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Setup

From the project root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Notes:

- Python 3.13 is recommended for the current pinned dependencies. Python 3.14 may fail to install `pydantic-core` for these versions.
- The frontend is served by FastAPI from the `frontend/` directory, so no separate JavaScript package install or frontend dev server is required.
- Phone numbers are stored as optional contact information (simple string, no strict format enforcement) and are **not used for SMS, automated calling, or any outbound communication**.
- The platform uses a connector-agnostic service layer — AI features never depend on a specific CRM backend.
- Draft email attachments are saved locally in `backend/data/attachments/`. Supported file types: PDF, DOCX, TXT, PNG, JPG, CSV. Maximum file size: 5 MB.
- **Field mapping:** The MVP uses a lightweight local data model. Some internal field names differ from user-facing CSV/API labels and are mapped at import/export boundaries. See `backend/app/services/field_mapper.py` for the full mapping table. In short: `organization_type` (external) ↔ `category` (internal), and free-text fields (description, notes, program_area, etc.) are concatenated into `mission_notes` (internal). `program_area` is stored as a separate key on CSV import but embedded in `mission_notes` for Research Intake and Discovery — a known limitation of the lightweight model.
- **Timestamps:** `created_at` and `updated_at` are automatically set on organization creation and updates by `LocalJsonCRMConnector` (`backend/app/connectors/local_json.py`). Existing records missing these fields are handled gracefully — they appear as empty in exports. A `backfill_timestamps()` helper function is available to assign fallback values (marked `(backfilled)`) to legacy records.

## API Endpoints

```text
GET    /api/health
GET    /api/organizations
GET    /api/organizations/{id}
PATCH  /api/organizations/{id}/status
PATCH  /api/organizations/{id}  (update contact name, email, phone number, website)
GET    /api/organizations/{id}/summary
GET    /api/organizations/{id}/opportunities
POST   /api/organizations/{id}/readiness-assessment
GET    /api/organizations/{id}/outreach-recommendation  (internal roadmap: outreach intelligence)
GET    /api/organizations/{id}/knowledge-summary
GET    /api/organizations/{id}/meeting-brief
GET    /api/organizations/{id}/interactions
POST   /api/organizations/{id}/interactions
PATCH  /api/organizations/{id}/interactions/{interaction_id}
DELETE /api/organizations/{id}/interactions/{interaction_id}
POST   /api/organizations/{id}/interactions/{interaction_id}/summarize  (internal roadmap: outreach intelligence)
POST   /api/drafts/generate
POST   /api/outbox
GET    /api/outbox
POST   /api/outbox/{draft_id}/attachments
GET    /api/outbox/{draft_id}/attachments
DELETE /api/outbox/{draft_id}/attachments/{attachment_id}
POST   /api/meeting-notes/summarize
POST   /api/research/intake
POST   /api/research/discover
POST   /api/research/approve
POST   /api/data/import/csv
POST   /api/data/import/csv/confirm
GET    /api/data/export/csv
GET    /api/data/export/json
GET    /api/analytics/summary
GET    /api/analytics/priority-queue  (internal roadmap: outreach intelligence)
GET    /api/tasks  (internal roadmap: outreach intelligence)
POST   /api/tasks  (internal roadmap: outreach intelligence)
PATCH  /api/tasks/{task_id}  (internal roadmap: outreach intelligence)
DELETE /api/tasks/{task_id}  (internal roadmap: outreach intelligence)
GET    /api/organizations/{id}/workflow-opportunities  (internal roadmap: workflow transformation knowledge)
POST   /api/organizations/{id}/workflow-opportunities  (internal roadmap: workflow transformation knowledge)
PATCH  /api/organizations/{id}/workflow-opportunities/{opp_id}  (internal roadmap: workflow transformation knowledge)
GET    /api/organizations/{id}/knowledge-sources  (internal roadmap: workflow transformation knowledge)
POST   /api/organizations/{id}/knowledge-sources  (internal roadmap: workflow transformation knowledge)
PATCH  /api/organizations/{id}/knowledge-sources/{ks_id}  (internal roadmap: workflow transformation knowledge)
DELETE /api/organizations/{id}/knowledge-sources/{ks_id}  (internal roadmap: workflow transformation knowledge)
GET    /api/organizations/{id}/failure-cases  (internal roadmap: workflow transformation knowledge)
POST   /api/organizations/{id}/failure-cases  (internal roadmap: workflow transformation knowledge)
PATCH  /api/organizations/{id}/failure-cases/{fc_id}  (internal roadmap: workflow transformation knowledge)
GET    /api/organizations/{id}/adoption-risk-notes  (internal roadmap: workflow transformation knowledge)
POST   /api/organizations/{id}/adoption-risk-notes  (internal roadmap: workflow transformation knowledge)
PATCH  /api/organizations/{id}/adoption-risk-notes/{ar_id}  (internal roadmap: workflow transformation knowledge)
DELETE /api/organizations/{id}/adoption-risk-notes/{ar_id}  (internal roadmap: workflow transformation knowledge)
```

## Verification Checklist

After setup, these checks should pass:

```bash
python -m compileall backend
python -m pip check
node --check frontend/app.js
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/organizations
curl http://127.0.0.1:8000/api/organizations/1
curl http://127.0.0.1:8000/api/organizations/1/summary
curl http://127.0.0.1:8000/api/organizations/1/opportunities
curl http://127.0.0.1:8000/api/organizations/1/meeting-brief
curl -X POST http://127.0.0.1:8000/api/research/intake \
  -H "Content-Type: application/json" \
  -d '{"organization_name":"Example Community Org","organization_type":"Community nonprofit","program_area":"Digital literacy"}'
curl -X POST http://127.0.0.1:8000/api/research/discover \
  -H "Content-Type: application/json" \
  -d '{"research_theme":"public AI literacy workshops"}'
curl http://127.0.0.1:8000/api/analytics/summary
curl http://127.0.0.1:8000/api/analytics/priority-queue
curl http://127.0.0.1:8000/api/organizations/1/outreach-recommendation
curl http://127.0.0.1:8000/api/tasks
```

The browser UI should load all frontend pages at their respective routes. The CRM workspace should preserve all Phase 1 and Phase 2 features.


## Future Development

Future work should use the workflow transformation knowledge already captured by the app.

### AI Adoption Planning

Future planning features may use workflow opportunities, failure cases, knowledge sources, adoption risk notes, and adoption principles to create:

- Adoption roadmaps
- Pilot recommendations
- Training suggestions
- Success metrics
- Human-review models
- Change-management checklists

These should remain editable planning drafts, not final automated recommendations.

### Production and Integration Work

Possible later upgrades:

- Replace mock AI with OpenAI API calls
- Add SQLite or PostgreSQL database
- Add authentication and user management
- Add real Salesforce connector
- Add real HubSpot connector
- Add Gmail draft-only integration, with no sending
- Add Google Calendar integration
- Add Kanban outreach board
- Add dashboard charts and visualizations
- Replace mock Organization Discovery with an approved research integration
- Add team collaboration features such as shared notes and task assignment

Avoid adding email delivery tracking or automated sending unless the project scope changes substantially. The current product principle is human-reviewed drafting, not outreach automation.

## Portfolio Framing

Suggested title:

**Outreach Intelligence Platform: Human-reviewed workflow intelligence for practical AI adoption**

Suggested description:

A local portfolio demo that combines lightweight CRM functions with AI-assisted outreach preparation, interaction summarization, workflow opportunity discovery, knowledge-source mapping, failure-case tracking, and human-system adoption-risk awareness. The system is designed as an intelligence layer that can eventually connect to Salesforce, HubSpot, or other CRM systems while preserving human review before external communication or implementation decisions.

## License

Recommended license: **Apache License 2.0**.

```text
Copyright © 2026 Nobuki Matsui
```

This portfolio project is provided for demonstration, learning, and review purposes. Reuse, modification, and distribution are permitted under the terms of the Apache License 2.0.

## References

The AI adoption principles used in this portfolio project were informed by notes taken from public videos by 株式会社AX.

株式会社AX YouTube Channel: https://youtube.com/@ax_channel?si=jzQT6Rl-OVVY1sdU

These references were used as learning material for developing the project’s workflow-intelligence concepts, including practical AI adoption, workflow transformation, human review, adoption risks, incentives, and organizational change. This project is independent and is not affiliated with or endorsed by 株式会社AX.