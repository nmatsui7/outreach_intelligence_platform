# Outreach Intelligence Platform

A portfolio demo showing how AI can improve outreach planning, relationship intelligence, and practical AI adoption work while keeping humans in control.

This project is intentionally safe: **it does not send real emails**. Drafts are saved to a local Demo Outbox only.

## What This Is

This is not meant to replace a CRM. It is an AI layer that can sit above different data sources.

Current data source:

- Local JSON demo CRM

Future data sources:

- Salesforce
- HubSpot
- Microsoft Dynamics
- Zoho CRM
- CSV import/export

## Phase 1 — Foundation Features

### 1. Demo CRM

- Organization directory
- Contact name, general contact email, and phone number
- Outreach status
- Last interaction notes
- **Editable contact fields** — click "Edit Contact" in the detail panel to update name, email, phone number, or website after intake
- Local data storage

### 2. Outreach Intelligence

- AI-style organization summaries
- Outreach priority
- AI readiness score
- Suggested discovery questions
- AI Opportunity Analysis

### 3. AI Adoption Planning

The system suggests practical AI opportunities such as:

- Internal knowledge assistant
- Meeting summary workflow
- Workshop planning assistant
- Documentation support
- Follow-up preparation

Each opportunity includes:

- Expected benefit
- Estimated effort
- Human review requirement

### 4. Context-Aware Email Drafting ("Next Best Email")

- Generates the "Next Best Email" based on full organization context
- **Relationship stage detection** — email type is determined by outreach status and interaction history
- Context gathered includes: organization profile, status, interaction history (type, notes, outcome, next action, follow-up date), AI Summary / Readiness Score, and previous outbox drafts
- Displays "Context Used" panel and "Missing Context" warnings
- Editable subject, body, and recipient before saving
- Save to Demo Outbox only — no send button, no SMTP, no Gmail API

### 5. Meeting Support

- Meeting preparation brief
- Suggested discussion topics
- Desired meeting outcome
- Meeting notes summarization
- Action items
- Risks
- Follow-up recommendation

### 6. Research Intake

- Manually enter or paste researched organization information
- Save reviewed records directly to the Local JSON CRM
- Supports organization name, website, general contact email, organization type, program area, description, relevance notes, outreach angle, source URL, and notes
- No browsing, scraping, private personal email collection, or automated outreach

### 7. Organization Discovery

- Enter a research theme
- Review 5-10 mock candidate organizations
- Inspect organization type, website, general contact email, program area, fit score, relevance notes, outreach angle, and source note
- Approve, edit, or reject each candidate
- Save approved candidates to the Local JSON CRM only
- No browsing, scraping, private personal email collection, or automated outreach

### Organization Discovery vs AI Opportunity Analysis

These two features serve different stages of the research workflow:

- **Organization Discovery** (page at `/organization-discovery`): Find *new* candidate organizations based on a research theme. The user enters a theme, reviews 5–10 mock candidates, and approves/edits/rejects each one before saving to the CRM. This is a **top-of-funnel** research workflow — finding who to talk to.

- **AI Opportunity Analysis** (button in the CRM detail panel): Analyze a *specific saved organization* for practical AI adoption opportunities. The user selects an organization from the CRM list and clicks "AI Opportunity Analysis" to see suggested opportunities, benefits, effort estimates, and human review notes. This is a **deeper analysis** workflow — understanding what to propose to an organization already in the CRM.

In short: Organization Discovery finds organizations; AI Opportunity Analysis analyzes an organization that has already been found.

### 8. Interaction History

- Record interactions per organization: Meeting, Call, Email, Research Note, Follow-up, or Other
- Each interaction includes date, title, notes, outcome, next action, follow-up date, and tags
- Add, edit, and delete interactions directly from the organization detail page
- Interactions appear in reverse chronological order
- Stored locally in `backend/app/data/interactions.json`

### 9. AI Note Summary

- Click "AI Note Summary" on any interaction to extract structured knowledge
- Extracts: summary, key discussion points, decisions, action items, risks or concerns, recommended follow-up, suggested tags, and suggested follow-up tasks
- Uses local mock AI logic only — no external API calls

### 10. Organization Knowledge Summary

- Summarizes across all interactions for a given organization
- Shows: relationship status, main interests, known concerns, previous outreach attempts, current opportunities, and recommended next step
- Updates automatically when interactions are added, edited, or deleted
- Uses local mock AI logic only

### 11. AI Readiness Assessment

- Dedicated assessment of how ready an organization is for AI adoption
- **Six-category transparent scoring model** (each 0–20 or 0–10):
  - Workflow Repetition — does the org have repetitive tasks AI could help with?
  - Documentation Maturity — how much documentation/note-taking is part of their workflow?
  - Digital Maturity — existing comfort with digital tools and technology
  - Staff Capacity Benefit — would AI meaningfully reduce administrative burden?
  - Low-Risk Pilot Suitability — can they start with a small, contained pilot?
  - Human Oversight Clarity — is the need for human review understood?
- Total score maps to: **Low** (0–33), **Moderate** (34–66), **High** (67–100)
- Output includes: overall level, score, category breakdowns with explanations, best starting use case, why ready, gaps, risks, recommended pilot, human oversight requirements, and suggested questions for the next meeting
- Uses only existing organization profile + interaction data — no web scraping or external APIs
- Displays "Context Used" panel showing which fields influenced each score
- Requires human review before any outreach or implementation decisions

### 12. Demos, Data Tools, and Analytics

- **Demo Outbox** — save email drafts locally; no sending
- **CSV/JSON Import/Export** at `/data-tools` — import organizations from CSV with preview-then-confirm flow; export to CSV or JSON
- **Analytics Dashboard** at `/analytics` — overview metrics, outreach pipeline, organization breakdown by type/program area, AI readiness summary, follow-up workload, draft activity, and priority analytics

## Phase 2 — Outreach Intelligence

### 13. Outreach Recommendation

Each organization gets a structured recommendation accessed via `GET /api/organizations/{id}/outreach-recommendation` or the "Outreach Recommendation" button in the CRM workspace detail panel.

The recommendation includes:
- **outreach_priority**: High / Medium / Low (computed from priority score)
- **priority_score**: 0–100 composite score
- **recommended_next_action**: Status-derived action, adjusted for any open or overdue follow-up tasks
- **recommended_follow_up_date**: Inferred from last interaction and next action
- **recommended_email_type**: From context-aware draft analysis
- **recommended_collaboration_angles**: 1–3 practical ideas with title, description, effort, value, and human oversight
- **reasoning**: Explanation of the recommendation
- **risks_or_concerns**: Organization-specific risks (missing contact, low readiness, no pain points)
- **missing_information**: Gaps that would improve future recommendations
- **context_used**: All data that informed the recommendation

### Priority Score Calculation (0–100)

| Factor | Weight | Source |
|--------|--------|--------|
| AI Readiness Score | 0–30 | Readiness assessment total_score × 0.30 |
| Outreach Status | 0–20 | Status-based: Pilot Discussion (20), Draft Ready (18), Meeting Scheduled (16), etc. |
| Interaction Recency | 0–25 | Higher for recent interactions (within 7 days = 25, 30 days = 20, 90 days = 12) |
| Pain Points | 0–15 | 5 points per identified pain point (max 3) |
| Data Completeness | 0–10 | Points for contact email, name, phone, mission notes |

### Priority Queue

The `/priority-queue` page shows all organizations ranked by priority score descending. The queue supports filtering by:
- Priority level (High / Medium / Low)
- CRM status
- Readiness level
- Organization type

Sorting can be changed to name, readiness score, or priority score.

### 14. Meeting Intelligence and Follow-up Task Generation

When a user clicks "AI Note Summary" on any interaction, the system:

1. Extracts structured knowledge (summary, discussion points, decisions, action items)
2. Suggests a follow-up date (typically 14 days out)
3. Suggests a next email type based on keywords in the notes
4. Generates 2–3 **suggested follow-up tasks** based on keyword matching:
   - "pilot" or "proposal" → "Prepare pilot proposal document"
   - "follow-up" or "next steps" → "Send follow-up summary"
   - "documentation" or "records" → "Review documentation workflow"
   - "meeting" or "schedule" → "Schedule follow-up meeting"
   - "training" or "workshop" → "Prepare AI literacy workshop materials"
   - "grant" or "funding" → "Research grant opportunities"
   - "staff" or "capacity" → "Assess staff readiness for AI tools"
   - "outreach" or "community" → "Plan community outreach strategy"

Suggested tasks appear in the **Follow-up Tasks** section of the organization detail panel with Save, Edit, and Reject actions. Tasks are not auto-created — the user must click "Save" to create them.

### 15. Follow-up Tasks

- **CRUD via REST API**: `GET /api/tasks`, `POST /api/tasks`, `PATCH /api/tasks/{task_id}`, `DELETE /api/tasks/{task_id}`
- Tasks stored in `backend/app/data/tasks.json`
- Each task has: `task_id`, `organization_id`, `source_interaction_id`, `title`, `description`, `due_date`, `priority`, `status` (Open/Completed), `created_at`, `updated_at`
- The organization detail panel shows open tasks (with Complete/Delete actions), overdue tasks highlighted in red, and completed tasks in a collapsible section
- The global **Follow-ups page** at `/follow-ups` shows all tasks across organizations with filters by status (Open/Completed/Overdue/Due This Week), priority (High/Medium/Low), and organization

### 16. Outreach Recommendation with Task Awareness

The Outreach Recommendation checks for open and overdue follow-up tasks for the organization:

- If **overdue tasks** exist, the recommended next action starts with "Attention needed: [task title] is overdue."
- If **open tasks** exist (but none overdue), the next action starts with "Complete open task: [task title]."
- Task counts (open and overdue) appear in the `context_used` section of the recommendation

### 17. Analytics with Task Stats

The analytics dashboard includes task statistics in the "Follow-up Workload" section:
- `open_tasks`, `completed_tasks`, `overdue_tasks`, `tasks_due_this_week`, `high_priority_open_tasks`

## Demo Workflow

1. **Research Intake** → fill in organization details → save to CRM
2. **Organization Discovery** → enter a research theme → review candidates → approve one → it joins the CRM
3. Open **CRM Workspace** → select the organization → click "AI Summary" → "AI Opportunity Analysis" → "AI Readiness Assessment" → "Outreach Recommendation"
4. Click **Next Best Email** → review the generated draft → edit if needed → "Save to Demo Outbox"
5. Add an **Interaction** (e.g., Meeting with notes containing "pilot") → click "AI Note Summary" → review suggested tasks → "Save Task"
6. Open the **Priority Queue** to see all organizations ranked by priority
7. Open the **Follow-ups page** to see all tasks across organizations
8. Open the **Analytics Dashboard** to see metrics updated with task data
9. Open the **Demo Outbox** to see saved drafts with attachments
10. Export data via **CSV or JSON** at the Data Tools page

## Safety Boundaries

- **No real email sending.** Drafts are saved locally to `backend/app/data/outbox.json`. No SMTP, Gmail API, or Outlook API is configured or called.
- **No SMS or phone automation.** Phone numbers are stored as informational strings only. No Twilio, no calling, no texting.
- **No web scraping.** Research Intake requires manual entry. Organization Discovery uses local mock data only.
- **No external API calls.** All AI responses are mocked locally. No OpenAI, no external CRM APIs, no cloud services.
- **No OAuth.** No OAuth flows are configured for any connector.
- **All Salesforce, HubSpot, Gmail, Outlook, Google Drive, Dropbox, SharePoint, OneDrive, and OpenText files are stubs only.** No credentials are stored, no tokens are requested, and no external systems are contacted.
- **Human review required before any action.** All recommendations, assessments, and tasks are informational. No auto-creation or auto-sending of any kind.
- **Attachments are stored locally only.** Uploaded files stay in `backend/data/attachments/`. No file is sent or shared externally.

## Frontend Pages

```text
/                         CRM workspace with organization list, details, AI actions, Interaction History,
                          Knowledge Summary, meeting notes, Follow-up Tasks, and Demo Outbox
/research-intake          Manual research intake form for saving reviewed organizations to the Local CRM
/organization-discovery   Mock candidate discovery workflow with Approve, Edit, and Reject review actions
/integrations             Read-only architecture overview with Active Local Connector, CRM Connectors,
                          Document/Content Connectors, Communication Connectors, and Data Import/Export
/data-tools               CSV import with preview-then-confirm flow, CSV export, and JSON export
/analytics                Analytics dashboard with overview metrics, pipeline breakdowns,
                          AI readiness summary, follow-up workload, draft activity, priority analytics,
                          and task statistics
/priority-queue           All organizations ranked by outreach priority score with filtering
                          by priority level, status, readiness level, and organization type
/follow-ups               Global follow-up task list with filters by status, priority, and organization
```

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
│   │   ├── ai_mock.py
│   │   ├── analytics.py
│   │   ├── attachments.py
│   │   ├── data_tools.py
│   │   ├── field_mapper.py
│   │   ├── interaction_summaries.py
│   │   ├── interactions.py
│   │   ├── knowledge.py
│   │   ├── outbox.py
│   │   ├── outreach_recommendation.py
│   │   ├── research_mock.py
│   │   ├── tasks.py
│   │   └── workflow.py
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
GET    /api/organizations/{id}/outreach-recommendation  (Phase 2)
GET    /api/organizations/{id}/knowledge-summary
GET    /api/organizations/{id}/meeting-brief
GET    /api/organizations/{id}/interactions
POST   /api/organizations/{id}/interactions
PATCH  /api/organizations/{id}/interactions/{interaction_id}
DELETE /api/organizations/{id}/interactions/{interaction_id}
POST   /api/organizations/{id}/interactions/{interaction_id}/summarize  (Phase 2)
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
GET    /api/analytics/priority-queue  (Phase 2)
GET    /api/tasks  (Phase 2)
POST   /api/tasks  (Phase 2)
PATCH  /api/tasks/{task_id}  (Phase 2)
DELETE /api/tasks/{task_id}  (Phase 2)
GET    /api/organizations/{id}/workflow-opportunities  (Phase 3)
POST   /api/organizations/{id}/workflow-opportunities  (Phase 3)
PATCH  /api/organizations/{id}/workflow-opportunities/{opp_id}  (Phase 3)
GET    /api/organizations/{id}/knowledge-sources  (Phase 3)
POST   /api/organizations/{id}/knowledge-sources  (Phase 3)
PATCH  /api/organizations/{id}/knowledge-sources/{ks_id}  (Phase 3)
DELETE /api/organizations/{id}/knowledge-sources/{ks_id}  (Phase 3)
GET    /api/organizations/{id}/failure-cases  (Phase 3)
POST   /api/organizations/{id}/failure-cases  (Phase 3)
PATCH  /api/organizations/{id}/failure-cases/{fc_id}  (Phase 3)
GET    /api/organizations/{id}/adoption-risk-notes  (Phase 3)
POST   /api/organizations/{id}/adoption-risk-notes  (Phase 3)
PATCH  /api/organizations/{id}/adoption-risk-notes/{ar_id}  (Phase 3)
DELETE /api/organizations/{id}/adoption-risk-notes/{ar_id}  (Phase 3)
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

## Phase 3 — Workflow Transformation Knowledge

Phase 3 captures structured knowledge about workflows, human-systems, and adoption readiness from interactions — storing it for future Phase 4 adoption plan generation. All data stays local.

### 1. Organization Timeline

Each organization detail page includes a **Timeline** section that combines events in chronological order:

- Organization created (from `created_at` timestamp)
- Interactions added (from interaction dates)
- Follow-up tasks created and completed (from task timestamps)
- Drafts saved to Demo Outbox (from draft timestamps)

Each event shows the date/time, event type badge, a short title, and a description excerpt.

### 2. Lessons Learned, Reusable Insights, and Playbook Candidates

When a user runs **AI Note Summary** on an interaction, the system extracts organizational knowledge beyond immediate follow-up tasks.

**Lessons Learned** — Practically useful takeaways from each interaction:
- Displayed in a dedicated **Lessons Learned** section on each organization detail page
- Each lesson shows: title, description, source interaction, date, and tags
- Stored persistently in `backend/app/data/interaction_summaries.json`

**Reusable Insights** — Generalizable observations that apply across organizations:
- Indexed and searchable via Knowledge Search
- Included in the Knowledge Summary

**Playbook Candidates** — Repeatable processes extracted from interaction notes:
- Displayed in a dedicated **Playbook Candidates** section on each org detail page
- Each playbook includes: title, when to use it, suggested process, source interaction, and tags
- Filterable in Knowledge Search by content type "playbook" or "lesson"

**Additional fields extracted per interaction:**
- Staff concerns or adoption concerns
- Human judgment / human review points
- Knowledge-sharing opportunities
- Suggested tags from a controlled vocabulary: `workflow-improvement`, `staff-concern`, `human-review`, `knowledge-sharing`, `training-need`, `evaluation-concern`, `pilot-idea`, `documentation`, `follow-up`

### 3. Global Knowledge Search

Route: `/knowledge-search`

Navigation label: **Knowledge Search**

Allows keyword search across local project data including:

- Organization names, descriptions (mission_notes), category, status
- Interaction titles, notes, outcomes, next actions
- Follow-up task titles and descriptions
- Draft subjects and bodies
- Lessons learned, reusable insights, playbook candidates
- Staff concerns, human judgment points, knowledge-sharing opportunities
- Workflow opportunities, knowledge sources, failure cases
- Current workflows and reusable workflow insights
- Adoption risk notes

Search supports:
- **Keyword search** (required)
- **Organization filter** — limit results to a specific org
- **Content type filter** — narrow by organizations, interactions, tasks, drafts, lessons, insights, playbooks, workflow opportunities, knowledge sources, failure cases, or adoption risk notes

Results appear as cards showing content type, organization name, a matching excerpt, date, and a "View Organization" button that navigates to the CRM workspace and selects the organization.

### 4. Enhanced Knowledge Summary

The Knowledge Summary section (on each org detail page) now includes:

- Relationship status, main interests, known concerns
- Previous outreach attempts (interaction history)
- Active opportunities (open tasks), completed follow-ups count
- Interaction history (last 5), follow-up task history, draft history
- Timeline events summary
- Main lessons learned, recurring concerns, reusable outreach insights
- Knowledge-sharing opportunities, recommended knowledge item to preserve
- **Workflow transformation fields:** main workflow opportunities, repeated workflow pain points, important knowledge sources, known failure cases, human review requirements, best candidate workflow for AI
- **Human-system fields:** staff concerns, evaluation or recognition risks, training or follow-up needs, adoption safeguards, human system notes

### 5. Phase 3 Analytics

The Analytics dashboard now includes a **Workflow Transformation Knowledge** section:

- Total searchable knowledge items (orgs + interactions + tasks + drafts)
- Organizations with/without interaction history
- Most common tags from interactions
- Recent knowledge activity (last 5 events)
- **Workflow opportunities identified** — count of workflow opportunities across all orgs
- **Workflow opps with human review** — opportunities that explicitly require human review
- **Organizations with workflow opportunities** — unique orgs that have at least one
- **Organizations missing knowledge source notes** — orgs without knowledge source records
- **Failure cases recorded** — total failure cases across all orgs
- **Candidate pilot workflows** — workflow opportunities with status "Candidate for Pilot" or "Needs Validation"
- **Adoption risk notes recorded** — total adoption risk notes across all orgs
- **Organizations with adoption risk notes** — unique orgs that have risk notes
- **Staff concern notes** — risk notes categorized as staff concerns
- **Evaluation risk notes** — risk notes categorized as evaluation risks
- **High-severity adoption risks** — risk notes with Medium or High severity

### 6. Extended AI Note Summary — Workflow & Human-System Fields

When a user runs **AI Note Summary**, the following workflow-specific and human-system fields are extracted from the notes:

**Workflow fields:**
- **Current workflow described** — description of the organization's current process
- **Workflow pain points** — specific friction points identified
- **Repetitive tasks identified** — tasks that recur and could be automated or assisted
- **Information or documents used** — documents, records, or knowledge sources referenced in the workflow
- **Possible AI insertion point** — where AI could meaningfully assist
- **Required human review** — points where human judgment is essential
- **Missing knowledge or data** — gaps that would need to be filled for AI adoption
- **Failure cases / exceptions** — what has failed or could fail, why, missing context, human review requirement, and suggested prevention steps
- **Reusable workflow insights** — generalizable observations across organizations
- **Workflow tags** — controlled vocabulary tags for workflow analysis

**Human-system fields:**
- **Staff concerns** — staff fears, capacity constraints, and data privacy concerns around AI adoption
- **Evaluation or recognition risks** — risks around unclear evaluation criteria, lack of recognition for AI-assisted work
- **Knowledge-sharing opportunities** — insights and materials that could be shared across organizations
- **Training or follow-up needs** — AI literacy training needs, digital skill assessments, pilot preparation
- **Adoption safeguards** — human oversight measures, staff consultation requirements, responsible deployment practices
- **Human system notes** — overall assessment of the human system around workload, evaluation, recognition, and staff confidence

All fields are optional — no breaking changes to existing data or interfaces.

### 7. Workflow Opportunity Records

Each organization can have **Workflow Opportunity** records that capture structured opportunities:

- **Title** — descriptive name for the opportunity
- **Current process** — how the work is done today
- **Pain point** — the specific problem or friction
- **Possible AI support** — how AI could address the pain point
- **Knowledge sources needed** — documents or data required
- **Human review points** — steps requiring human judgment
- **Risks or exceptions** — what could go wrong
- **Staff impact** — how the opportunity affects staff workload and confidence
- **Adoption risk level** — Unknown, Low, or Medium based on staff concerns and evaluation risks
- **Next discovery questions** — open questions to explore before adoption planning
- **Human review required** — specific human oversight requirements
- **Required knowledge sources** — knowledge sources needed for this opportunity
- **Known failure cases** — failure cases linked to this opportunity
- **Source interaction** — which interaction identified this opportunity
- **Status** — `Identified`, `Needs Validation`, `Candidate for Pilot`, or `Not Suitable`
- **Tags** — categorization tags

Workflow opportunities are **auto-created** when a user runs AI Note Summary (one per AI insertion point). They can also be manually created or edited.

CRUD endpoints:
```
GET    /api/organizations/{id}/workflow-opportunities
POST   /api/organizations/{id}/workflow-opportunities
PATCH  /api/organizations/{id}/workflow-opportunities/{opp_id}
```

### 8. Knowledge Source Tracking

For each organization, the platform records **Knowledge Sources** — metadata about where information lives:

- **FAQ documents, Past meeting notes, Past emails or drafts, Policies, Templates, Q&A records, Training materials, Reports, Public website content, Other**

Each source stores: type, name, description, and a location note. Knowledge sources are **auto-created** from the "Information or documents used" field during AI Note Summary. Manual CRUD is also available.

```
GET    /api/organizations/{id}/knowledge-sources
POST   /api/organizations/{id}/knowledge-sources
PATCH  /api/organizations/{id}/knowledge-sources/{ks_id}
DELETE /api/organizations/{id}/knowledge-sources/{ks_id}
```

No external files or cloud storage are accessed — this is local metadata only.

### 9. Failure Case / Exception Tracking

Each organization can record **Failure Cases or Exceptions** from interactions:

- **What failed or may fail** — description of the failure
- **Why it failed** — root cause
- **Missing context** — what information was lacking
- **Human review required** — why human judgment is needed
- **Suggested prevention step** — how to avoid in the future

Failure cases are **auto-created** from AI Note Summary. They can also be manually managed.

```
GET    /api/organizations/{id}/failure-cases
POST   /api/organizations/{id}/failure-cases
PATCH  /api/organizations/{id}/failure-cases/{fc_id}
```

### 10. Adoption Risk Notes

Each organization can have **Adoption Risk Notes** — structured records of human-system risks that could affect AI adoption success.

**Risk types:**
- **Staff Concern** — staff fears, capacity constraints, data privacy concerns
- **Evaluation Risk** — unclear evaluation criteria, lack of recognition
- **Adoption Safeguard** — protective measures needed for responsible adoption

Each risk note stores: risk type, description, severity (Low/Medium/High), related staff role, suggested mitigation, source interaction, and tags.

Adoption Risk Notes are **auto-created** from AI Note Summary from the new human-system fields. Manual CRUD is also available.

```
GET    /api/organizations/{id}/adoption-risk-notes
POST   /api/organizations/{id}/adoption-risk-notes
PATCH  /api/organizations/{id}/adoption-risk-notes/{ar_id}
DELETE /api/organizations/{id}/adoption-risk-notes/{ar_id}
```

### 11. Knowledge Search Extensions

The Knowledge Search indexes the following content types:
- `workflow-opportunity` — workflow opportunity titles, pain points, and AI support
- `knowledge-source` — knowledge source names, types, descriptions
- `failure-case` — failure case descriptions and root causes
- `adoption-risk` — adoption risk descriptions and mitigations

Search results show appropriate content-type badges (⚙️, 📚, ⚠️, 🛡️).

### 12. How This Supports Phase 4 Adoption Planning

Workflow transformation knowledge connects interaction-level data to organizational-level insights for future adoption planning:
- Running AI Note Summary auto-creates structured workflow opportunities, knowledge sources, failure cases, and adoption risk notes
- All knowledge is immediately searchable across all organizations via Knowledge Search
- The Knowledge Summary surfaces the most important workflow and human-system insights per organization
- Analytics tracks overall workflow knowledge maturity and human-system risk posture
- This knowledge directly feeds **Phase 4 AI Adoption Planning**, which will use workflow opportunities, failure cases, knowledge sources, and adoption risk notes to create adoption roadmaps, pilot plans, and readiness recommendations

### 13. Safety

- No external APIs called
- No web scraping
- No credentials stored
- Local search only — no external search services
- Knowledge sources are metadata only — no external files accessed
- All workflow recommendations require human review
- No automated outreach, email sending, or external communication

## Future Development (Phase 4)

Phase 4 features are not yet implemented. The workflow transformation knowledge captured in Phase 3 will directly inform Phase 4:

- **AI Adoption Planning** — use workflow opportunities, failure cases, knowledge sources, and adoption risk notes to create adoption roadmaps, pilot plans, and readiness recommendations for each organization
- Replace mock AI with OpenAI API calls
- Add SQLite or PostgreSQL database
- Add authentication and user management
- Add real Salesforce connector
- Add real HubSpot connector
- Add Gmail draft-only integration (no sending)
- Add Google Calendar integration
- Add Kanban outreach board
- Add dashboard charts and visualizations
- Replace mock Organization Discovery with an approved research integration
- Add email delivery tracking (read receipts, click tracking)
- Add team collaboration features (shared notes, task assignment)

## Portfolio Framing

Suggested title:

**Outreach Intelligence Platform: AI-assisted outreach and adoption planning with human review**

Suggested description:

A demo platform that combines lightweight CRM functions with AI-assisted opportunity discovery, outreach preparation, meeting support, and responsible AI adoption planning. The system is designed as an intelligence layer that can eventually connect to Salesforce, HubSpot, or other CRM systems while preserving human review before external communication.
