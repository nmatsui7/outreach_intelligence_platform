"""
Seed the project with realistic demo data for testing.

Usage:
    python backend/scripts/seed_demo_data.py

This script overwrites existing demo data files with fresh mock data.
Existing files are backed up with a .backup.json suffix before overwriting.

Uses local mock data only. No external systems are contacted.
No real customer data is included.
"""

import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA_DIR = ROOT / "app" / "data"
DATA_DIR = ROOT / "data"

FILES = {
    "organizations": APP_DATA_DIR / "organizations.json",
    "interactions": APP_DATA_DIR / "interactions.json",
    "interaction_summaries": APP_DATA_DIR / "interaction_summaries.json",
    "outbox": APP_DATA_DIR / "outbox.json",
    "tasks": APP_DATA_DIR / "tasks.json",
    "workflow_knowledge": APP_DATA_DIR / "workflow_knowledge.json",
}


def _now_iso(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(days_ago: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%d")


def backup(filepath: Path) -> None:
    if filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + ".backup.json")
        shutil.copy2(filepath, backup_path)
        print(f"  Backed up {filepath.name} -> {backup_path.name}")


def write_json(filepath: Path, data) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"  Wrote {len(data) if isinstance(data, list) else 'structured'} records to {filepath.name}")


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

ORGANIZATIONS = [
    {
        "id": 1,
        "name": "Waterloo Public Library",
        "category": "Public library",
        "website": "https://www.wpl.ca",
        "contact_name": "Sarah Chen",
        "contact_email": "sarah.chen@wpl.ca",
        "phone_number": "519-555-0147",
        "status": "Meeting Completed",
        "mission_notes": "Waterloo Public Library serves the community through public learning, digital literacy programs, newcomer support services, and public workshops. Runs multiple branches across Waterloo region with a focus on inclusive access to information and technology.",
        "pain_points": [
            "Manual documentation of community program outcomes",
            "Repetitive follow-up email preparation after workshops",
            "Inconsistent knowledge sharing between departments",
            "Limited staff digital literacy for emerging technologies"
        ],
        "last_interaction": _date(7),
        "program_area": "Public learning, digital literacy, newcomer support, public workshops",
        "created_at": _now_iso(90),
        "updated_at": _now_iso(7),
    },
    {
        "id": 2,
        "name": "Kitchener Community Food Centre",
        "category": "Nonprofit / Food security",
        "website": "https://www.kitchenerfoodcentre.ca",
        "contact_name": "Maria Santos",
        "contact_email": "maria.santos@kfc.ca",
        "phone_number": "519-555-0234",
        "status": "Draft Ready",
        "mission_notes": "Kitchener Community Food Centre provides food security programs, community meals, and nutrition education. Operates volunteer-driven food distribution, donation intake, and client support services across Kitchener.",
        "pain_points": [
            "Manual volunteer scheduling and coordination",
            "Donation intake tracking requires repetitive data entry",
            "Client communication is handled ad-hoc without templates",
            "Grant reporting requires manual data compilation from multiple spreadsheets"
        ],
        "last_interaction": _date(14),
        "program_area": "Volunteer coordination, donation intake, client communication, grant reporting",
        "created_at": _now_iso(85),
        "updated_at": _now_iso(14),
    },
    {
        "id": 3,
        "name": "GreenTech Startup Hub",
        "category": "Startup support / Innovation hub",
        "website": "https://www.greentechhub.ca",
        "contact_name": "James Okonkwo",
        "contact_email": "james.okonkwo@greentechhub.ca",
        "phone_number": "519-555-0369",
        "status": "Research Approved",
        "mission_notes": "GreenTech Startup Hub supports clean technology startups with mentorship, workspace, and grant navigation. Connects founders with industry mentors and provides programming for early-stage green technology ventures.",
        "pain_points": [
            "Founder intake information is scattered across forms and emails",
            "Mentor matching is done manually without structured profiles",
            "Event follow-up requires individual email tracking",
            "Grant and resource navigation is time-consuming for each startup"
        ],
        "last_interaction": _date(3),
        "program_area": "Founder intake, mentor matching, event follow-up, grant/resource navigation",
        "created_at": _now_iso(60),
        "updated_at": _now_iso(3),
    },
    {
        "id": 4,
        "name": "Grand River Arts Collective",
        "category": "Arts nonprofit / Community programming",
        "website": "https://www.grandriverarts.ca",
        "contact_name": "Priya Sharma",
        "contact_email": "priya.sharma@grandriverarts.ca",
        "phone_number": "519-555-0456",
        "status": "Meeting Completed",
        "mission_notes": "Grand River Arts Collective supports local artists and community arts programming. Coordinates workshops, exhibitions, and public art projects. Operates with a small core team and a large roster of contract artists and volunteers.",
        "pain_points": [
            "Workshop scheduling and instructor coordination is manual",
            "Artist communication uses individual emails without templates",
            "Grant documentation is scattered across multiple folders",
            "Newsletter drafting requires significant editing time each month"
        ],
        "last_interaction": _date(10),
        "program_area": "Workshop scheduling, artist communication, grant documentation, newsletter drafting",
        "created_at": _now_iso(75),
        "updated_at": _now_iso(10),
    },
    {
        "id": 5,
        "name": "Region Youth Employment Network",
        "category": "Workforce development / Youth services",
        "website": "https://www.ryen.ca",
        "contact_name": "Alex Thompson",
        "contact_email": "alex.thompson@ryen.ca",
        "phone_number": "519-555-0567",
        "status": "Research Intake",
        "mission_notes": "Region Youth Employment Network provides employment services for youth aged 15-29. Offers resume workshops, employer matching, job coaching, and career exploration programs across Waterloo Region.",
        "pain_points": [
            "Intake notes are handwritten and transcribed manually",
            "Employer outreach tracking is done in spreadsheets",
            "Workshop follow-up communications are inconsistent",
            "Program reporting requires compiling data from multiple sources"
        ],
        "last_interaction": _date(21),
        "program_area": "Intake notes, employer outreach, resume workshop follow-up, program reporting",
        "created_at": _now_iso(45),
        "updated_at": _now_iso(21),
    },
]

# ---------------------------------------------------------------------------
# Helper to create interaction notes with embedded workflow signals
# ---------------------------------------------------------------------------

def _wpl_notes():
    return [
        {
            "id": 1,
            "organization_id": 1,
            "interaction_type": "Meeting",
            "date": _date(30),
            "title": "Digital Literacy Program Planning",
            "notes": "Planning session for upcoming digital literacy programs this fall. Reviewed program calendar and discussed capacity. Staff spend significant time preparing follow-up emails after each workshop session. The program team manually drafts individual follow-up messages for 20+ participants per workshop, which takes approximately 2-3 hours per workshop cycle. Staff mentioned this is one of the most repetitive parts of their workflow. We discussed whether AI-assisted template drafting could reduce this time, but agreed that human review would be needed because follow-up messages sometimes need to reference sensitive community context or direct participants to specific resources. Staff also noted that they maintain a FAQ document for common digital literacy questions but it is not always easy to search.",
            "outcome": "Identified follow-up email drafting as a potential area for AI support with human review",
            "next_action": "Map current follow-up email workflow and identify template opportunities",
            "follow_up_date": _date(16),
            "tags": ["digital-literacy", "workflow", "follow-up"],
        },
        {
            "id": 2,
            "organization_id": 1,
            "interaction_type": "Meeting",
            "date": _date(21),
            "title": "Staff Workflow Pain Points",
            "notes": "Follow-up discussion with program leads about administrative workload. Post-workshop follow-up messages are repetitive and time-consuming. The team sends variations of the same thank-you message, resource list, and next-session reminder to each participant. Staff would like approved email templates but worry that automated messages may sound too generic and miss the personal connection they have built with participants. Program leads are also concerned about data privacy when using AI tools to draft messages that include participant details. They use a program calendar, past workshop notes, and a participant communication log as their main knowledge sources. Staff also mentioned that experienced program coordinators need to review any external communication before it is sent.",
            "outcome": "Confirmed follow-up email pain point is a recurring theme across multiple programs",
            "next_action": "Draft template options with human review checkpoints for review",
            "follow_up_date": _date(14),
            "tags": ["workflow", "follow-up", "staff-concern", "privacy"],
        },
        {
            "id": 3,
            "organization_id": 1,
            "interaction_type": "Follow-up",
            "date": _date(18),
            "title": "Follow-up Email Template Review",
            "notes": "Reviewed examples of current follow-up emails from three different programs. Program follow-up emails could use approved templates and human review before sending. Currently each program coordinator writes their own version from scratch. Even for standard updates like 'next session reminder' or 'program recap', the content varies significantly in tone and completeness. This creates inconsistency for participants who attend multiple programs. Staff agreed that having vetted templates with personalization fields would improve quality and save time, but emphasized that all AI-generated content must be reviewed by the program lead before sending. The team also has a growing library of past workshop notes that could serve as reference material for drafting more contextually accurate follow-ups.",
            "outcome": "Template approach agreed in principle, human review requirement confirmed",
            "next_action": "Create three template drafts for pilot testing",
            "follow_up_date": _date(7),
            "tags": ["follow-up", "templates", "human-review", "documentation"],
        },
        {
            "id": 4,
            "organization_id": 1,
            "interaction_type": "Call",
            "date": _date(12),
            "title": "Community Partner Outreach Call",
            "notes": "Called to discuss potential community partnership for digital literacy programs. Partner is interested in co-hosting a workshop series. Discussed scheduling, venue, and audience outreach. Partner wants to ensure content is accessible for newcomers and seniors with varying digital skills. We talked about how past workshop attendance data could help plan appropriate content levels, but this data is currently in a spreadsheet that requires manual analysis. Partner also mentioned they have internal policies about data sharing that would need to be reviewed before any joint program moves forward. Staff are concerned AI could create content mismatched for audience needs without human oversight.",
            "outcome": "Partnership interest confirmed, need to review data sharing policies",
            "next_action": "Share draft partnership agreement and schedule initial planning meeting",
            "follow_up_date": _date(5),
            "tags": ["partnership", "outreach", "community"],
        },
        {
            "id": 5,
            "organization_id": 1,
            "interaction_type": "Email",
            "date": _date(8),
            "title": "Grant Reporting Requirements",
            "notes": "Received updated grant reporting requirements from funder. New requirements include detailed outcome metrics and participant demographic data. Current reporting process involves manually pulling data from program registrations, workshop attendance sheets, and follow-up surveys. Program coordinator spends approximately 5 hours per quarter compiling these reports. The data lives in three separate spreadsheets that are not connected. Staff would like a more structured way to capture and report outcomes but are concerned that automation may introduce errors in data transcription. They also need to ensure privacy requirements are met when reporting participant data. Previous grant reports exist in a shared folder and could serve as templates for formatting.",
            "outcome": "Received new reporting requirements, identified data consolidation need",
            "next_action": "Audit current data sources and map reporting workflow",
            "follow_up_date": _date(21),
            "tags": ["reporting", "grants", "data", "workflow"],
        },
    ]


def _kfc_notes():
    return [
        {
            "id": 6,
            "organization_id": 2,
            "interaction_type": "Meeting",
            "date": _date(35),
            "title": "Volunteer Coordination Review",
            "notes": "Reviewed current volunteer coordination process. Volunteer scheduling is managed through a shared spreadsheet with 40+ active volunteers. The coordinator spends 4-6 hours per week on schedule matching, sending individual emails to confirm shifts, and managing last-minute changes. Staff expressed interest in a more automated scheduling system but worry volunteers may find technology changes difficult. There is no centralized volunteer manual - each program area has its own orientation document. Experienced volunteers train new volunteers informally, leading to inconsistent knowledge transfer.",
            "outcome": "Identified volunteer scheduling as potential area for process improvement",
            "next_action": "Document current scheduling workflow and volunteer communication patterns",
            "follow_up_date": _date(21),
            "tags": ["volunteer", "scheduling", "workflow"],
        },
        {
            "id": 7,
            "organization_id": 2,
            "interaction_type": "Call",
            "date": _date(28),
            "title": "Donation Intake Process Discussion",
            "notes": "Discussed donation intake process with operations lead. Food donations come from grocery partners, community food drives, and individual donors. Each donation is logged manually into a tracking spreadsheet. Staff estimate 8-10 hours per week is spent on donation data entry and receipt generation. Donors sometimes ask for tax receipts and staff have to look up past donation records manually. Staff are concerned that automating donation tracking may not capture important context about food quality or special handling requirements. They use a food safety policy document and donation intake forms as reference materials.",
            "outcome": "Donation intake identified as repetitive manual task",
            "next_action": "Review donation tracking requirements and explore structured input options",
            "follow_up_date": _date(14),
            "tags": ["donation", "data-entry", "workflow"],
        },
        {
            "id": 8,
            "organization_id": 2,
            "interaction_type": "Email",
            "date": _date(21),
            "title": "Client Communication Follow-up",
            "notes": "Reviewed client communication process. Clients are contacted individually about program availability, food distribution schedules, and special events. There are no standard email templates - each staff member writes their own messages. Staff worry that standardized templates may make communications feel impersonal, particularly for clients in vulnerable situations. The team uses a client intake form and a program calendar as their main reference sources. Staff mentioned that AI-generated communications would need careful human review to ensure they use appropriate language for diverse client needs.",
            "outcome": "Identified need for flexible communication templates with personalization options",
            "next_action": "Collect examples of effective client communications for template development",
            "follow_up_date": _date(10),
            "tags": ["communication", "templates", "client-services"],
        },
        {
            "id": 9,
            "organization_id": 2,
            "interaction_type": "Research Note",
            "date": _date(18),
            "title": "Grant Reporting Requirements Research",
            "notes": "Researched updated reporting requirements for three active grants. Each funder requires different metrics and reporting formats. Current process involves manually extracting data from donation logs, volunteer hours spreadsheets, and program attendance records. The program manager estimates 6-8 hours per quarter is spent on each grant report. Past grant reports are stored in a shared drive and could serve as reference templates. Staff are concerned that automation might miss important context about program impact that is not captured in structured data fields.",
            "outcome": "Mapped current reporting data sources and identified gaps",
            "next_action": "Create standardized data collection template aligned with common grant metrics",
            "follow_up_date": _date(4),
            "tags": ["reporting", "grants", "data"],
        },
        {
            "id": 10,
            "organization_id": 2,
            "interaction_type": "Follow-up",
            "date": _date(14),
            "title": "Reporting Template Follow-up",
            "notes": "Followed up on reporting template draft. Staff reviewed a proposed standardized data collection sheet but noted that each grant has unique requirements that may not fit a single template. They suggested creating a core template with funder-specific add-on sections. Staff also expressed that they want practical reporting examples tied to their own programs, not generic training materials. Evaluation criteria for staff performance does not currently account for improved reporting efficiency - staff are evaluated on program outcomes rather than administrative improvements.",
            "outcome": "Template approach refined, staff training needs identified",
            "next_action": "Develop core template and two funder-specific add-on sections",
            "follow_up_date": _date(0),
            "tags": ["reporting", "templates", "staff-training"],
        },
    ]


def _gtech_notes():
    return [
        {
            "id": 11,
            "organization_id": 3,
            "interaction_type": "Meeting",
            "date": _date(25),
            "title": "Founder Intake Process Review",
            "notes": "Reviewed founder intake process with program coordinator. New founder information comes through a web form, email inquiries, and in-person conversations. The coordinator manually enters information from these sources into a founder tracking spreadsheet. Information is often duplicated or inconsistent across sources. Staff spend 3-4 hours per week reconciling intake information. They use intake forms and past founder records as reference sources. Staff are concerned that AI-assisted intake could miss important nuances about founder readiness or specific challenges.",
            "outcome": "Founder intake identified as inefficient manual process",
            "next_action": "Map current intake data flow and identify consolidation opportunities",
            "follow_up_date": _date(11),
            "tags": ["intake", "data", "workflow"],
        },
        {
            "id": 12,
            "organization_id": 3,
            "interaction_type": "Call",
            "date": _date(20),
            "title": "Mentor Matching Discussion",
            "notes": "Discussed mentor matching process with hub director. Mentors are matched to founders based on the director's personal knowledge of both parties. There is no structured mentor profile database or matching criteria. When the director is unavailable, matching slows significantly. The team has discussed creating mentor profiles but has not had time to implement. Staff use a mentor interest form and past match records as references. Staff are also unsure how to evaluate whether a mentorship match is successful. There is an FAQ document with common mentor-mentee questions.",
            "outcome": "Mentor matching process identified as knowledge-dependent and not scalable",
            "next_action": "Draft mentor profile template and matching criteria framework",
            "follow_up_date": _date(6),
            "tags": ["mentoring", "matching", "scalability"],
        },
        {
            "id": 13,
            "organization_id": 3,
            "interaction_type": "Email",
            "date": _date(15),
            "title": "Event Follow-up Workflow",
            "notes": "Reviewed post-event follow-up process. After each event (workshops, networking sessions, demo days), the team sends follow-up emails to attendees. Currently each event requires individual email drafting for 20-100 attendees. The coordinator tracks attendance in a spreadsheet and manually composes messages. Staff expressed frustration that this takes 1-2 days per event. They would like follow-up templates but worry about impersonal messages. Staff also maintain a Q&A record from past events that could inform follow-up content. Experienced staff review all event communications before sending.",
            "outcome": "Event follow-up identified as high-effort repetitive task",
            "next_action": "Design event follow-up template with personalization fields and review workflow",
            "follow_up_date": _date(1),
            "tags": ["events", "follow-up", "templates"],
        },
        {
            "id": 14,
            "organization_id": 3,
            "interaction_type": "Research Note",
            "date": _date(10),
            "title": "Grant Navigation Research",
            "notes": "Researching how staff currently help founders navigate grant and resource opportunities. The process involves scanning funding websites, checking eligibility criteria, and matching founders to relevant opportunities. One staff member estimates spending 5 hours per week on this research. There is no centralized grant opportunity database. Information about past successful grants is shared informally. Staff have a list of frequently used funding websites but no structured way to track deadlines or eligibility changes. Browser automation could help monitor website updates but may break when site layouts change.",
            "outcome": "Grant navigation identified as time-intensive research task with no central system",
            "next_action": "Research grant tracking tools and explore structured opportunity database options",
            "follow_up_date": _date(24),
            "tags": ["grants", "research", "navigation"],
        },
        {
            "id": 15,
            "organization_id": 3,
            "interaction_type": "Follow-up",
            "date": _date(7),
            "title": "Resource Directory Follow-up",
            "notes": "Followed up on resource directory project. The hub maintains a list of recommended service providers, funding sources, and community partners. This directory is currently a shared document that is updated irregularly. Staff want a more structured resource directory that is easier to search and update. They also mentioned that when new founders join, staff spend time routing questions to the right person because there is no centralized knowledge base. Staff are open to AI-assisted resource matching but want to ensure recommendations are accurate and up to date. Staff are also worried that AI may overpromise services to founders.",
            "outcome": "Resource directory and question routing identified as knowledge management gaps",
            "next_action": "Evaluate resource directory platforms and draft knowledge base structure",
            "follow_up_date": _date(28),
            "tags": ["resources", "knowledge-base", "routing"],
        },
    ]


def _arts_notes():
    return [
        {
            "id": 16,
            "organization_id": 4,
            "interaction_type": "Meeting",
            "date": _date(40),
            "title": "Workshop Scheduling Workflow",
            "notes": "Reviewed workshop scheduling process with program lead. Workshops are scheduled based on artist availability, venue calendar, and seasonal program themes. The current process involves email chains with multiple artists, checking venue availability on a shared calendar, and manually confirming each session. Staff estimate 3-4 hours per workshop series is spent on scheduling coordination alone. Past workshop notes are stored in individual files rather than a central system. Staff are concerned that AI scheduling may not account for artist relationships and preferences that are currently managed through personal knowledge.",
            "outcome": "Workshop scheduling identified as coordination-heavy manual process",
            "next_action": "Document current scheduling workflow and identify automation-safe steps",
            "follow_up_date": _date(26),
            "tags": ["scheduling", "workshop", "coordination"],
        },
        {
            "id": 17,
            "organization_id": 4,
            "interaction_type": "Call",
            "date": _date(33),
            "title": "Artist Communication Review",
            "notes": "Discussed artist communication patterns with the team. Artist outreach, contract follow-up, and exhibition coordination are all handled through individual emails. There are no standard templates for common communications such as exhibition confirmations, payment notifications, or call-for-submissions responses. The team spends 5-6 hours per week on email communication with approximately 30 active artists. Staff are concerned that templated communications may feel impersonal to artists who value personal relationships. Staff also noted that experienced team members carry most of the relationship knowledge informally and there is no easy way to share this context with newer staff.",
            "outcome": "Artist communication identified as high-volume task with templating potential",
            "next_action": "Identify common communication patterns that could use flexible templates",
            "follow_up_date": _date(19),
            "tags": ["communication", "artists", "templates"],
        },
        {
            "id": 18,
            "organization_id": 4,
            "interaction_type": "Email",
            "date": _date(28),
            "title": "Grant Documentation Process",
            "notes": "Reviewed grant documentation workflow. Grant applications require narrative descriptions, artist bios, project budgets, and supporting materials. The team reuses content from previous successful grants but each application requires significant rewriting to match new funder priorities. Past grant documents are stored in a shared folder organized by year. Staff waste time searching for the right previous grant to adapt. They estimate 8-10 hours per grant application, with 40% of that time spent on formatting and adapting existing content. Staff are open to AI-assisted drafting but require human review to ensure the narrative aligns with funder priorities and accurately represents the organization.",
            "outcome": "Grant documentation identified as high-effort recurring task with reusable content",
            "next_action": "Create grant content library with tagged reusable sections",
            "follow_up_date": _date(14),
            "tags": ["grants", "documentation", "content-reuse"],
        },
        {
            "id": 19,
            "organization_id": 4,
            "interaction_type": "Research Note",
            "date": _date(22),
            "title": "Newsletter Content Research",
            "notes": "Researched current newsletter production process. The monthly newsletter includes program updates, artist spotlights, upcoming events, and community news. Content is gathered from multiple staff members via email and compiled by one editor. The editor estimates 6-8 hours per month on content gathering, formatting, and editing. Past newsletters are stored as PDFs and are not easily searchable. Staff are interested in AI-assisted drafting but are concerned the content may sound generic and miss the unique voice of the organization. Human review is required for all externally visible content.",
            "outcome": "Newsletter production identified as time-intensive with structured content patterns",
            "next_action": "Map newsletter content categories and identify template opportunities",
            "follow_up_date": _date(8),
            "tags": ["newsletter", "content", "editing"],
        },
        {
            "id": 20,
            "organization_id": 4,
            "interaction_type": "Follow-up",
            "date": _date(16),
            "title": "Exhibition Coordination Follow-up",
            "notes": "Followed up on upcoming exhibition coordination. The team manages artist contracts, artwork checklists, installation schedules, promotional materials, and opening event planning. Each exhibition requires approximately 15-20 individual email communications. Several staff noted that exhibition checklists exist but are not consistently used because they are in a shared document that is hard to update collaboratively. Staff also mentioned that past exhibition documentation could serve as valuable reference material for future planning. There is uncertainty about what information should be public vs internal-only when using AI tools to help draft promotional content.",
            "outcome": "Exhibition coordination identified as communication-heavy with process documentation gaps",
            "next_action": "Review exhibition checklist and explore collaborative documentation tools",
            "follow_up_date": _date(2),
            "tags": ["exhibition", "coordination", "documentation"],
        },
    ]


def _youth_notes():
    return [
        {
            "id": 21,
            "organization_id": 5,
            "interaction_type": "Meeting",
            "date": _date(45),
            "title": "Intake Process Review",
            "notes": "Reviewed youth intake process with program coordinator. Youth intake information is currently collected on paper forms during initial meetings and then transcribed into a digital spreadsheet by staff. Transcription is time-consuming and prone to errors. Staff spend 2-3 hours per week on data entry alone. The intake form collects employment history, education background, barriers to employment, and support needs. This information is referenced during follow-up sessions but is not easy to search. Staff use intake forms and a case notes binder as reference sources. Staff are concerned that digitizing intake may lose important contextual notes that case workers write in margins.",
            "outcome": "Intake transcription identified as inefficient manual process with error risk",
            "next_action": "Explore digital intake options that preserve contextual notes",
            "follow_up_date": _date(30),
            "tags": ["intake", "data-entry", "workflow"],
        },
        {
            "id": 22,
            "organization_id": 5,
            "interaction_type": "Call",
            "date": _date(35),
            "title": "Employer Outreach Discussion",
            "notes": "Discussed employer outreach tracking with employment specialist. The team maintains a spreadsheet of employer contacts, past outreach attempts, and placement outcomes. Outreach follow-up is done manually - staff check the spreadsheet and send individual emails. With 50+ active employer relationships, the specialist estimates 3-4 hours per week on follow-up coordination. There is no automated reminder system for check-in dates. Staff are open to AI-assisted reminders and template suggestions but want to maintain personal relationships with employers. Past outreach email templates exist in individual staff email folders but are not shared.",
            "outcome": "Employer outreach follow-up identified as manual tracking overhead",
            "next_action": "Design employer outreach tracking system with automated check-in reminders",
            "follow_up_date": _date(21),
            "tags": ["employer", "outreach", "tracking"],
        },
        {
            "id": 23,
            "organization_id": 5,
            "interaction_type": "Email",
            "date": _date(28),
            "title": "Resume Workshop Follow-up",
            "notes": "Reviewed post-workshop follow-up process for resume workshops. After each workshop, staff send follow-up emails with resources, next steps, and individual feedback. With 15-20 participants per workshop and multiple workshops per month, this is a significant time commitment. Staff currently compose each email individually. They use past workshop notes and a resource guide as reference materials. Staff are interested in template-assisted follow-ups but emphasize that each participant has unique needs that templates must accommodate. Staff also worry that AI-generated feedback may not be specific enough to be useful for job seekers.",
            "outcome": "Workshop follow-up identified as high-volume task with template potential and personalization needs",
            "next_action": "Design workshop follow-up template with structured personalization fields",
            "follow_up_date": _date(14),
            "tags": ["workshop", "follow-up", "templates"],
        },
        {
            "id": 24,
            "organization_id": 5,
            "interaction_type": "Research Note",
            "date": _date(21),
            "title": "Program Reporting Research",
            "notes": "Researched current program reporting process. The network reports outcomes to funders quarterly. Data is pulled from intake records, workshop attendance, placement tracking, and follow-up surveys. Each data source is in a different format, and staff spend 4-5 days per quarter compiling and cross-referencing data. Staff have expressed frustration that the current process does not capture the full impact of their work because qualitative outcomes (youth confidence, improved interview skills) are not included in required metrics. Past reports exist in a shared folder. Staff are unsure whether AI could help analyze qualitative notes without losing important context.",
            "outcome": "Program reporting identified as heavy manual compilation with data integration challenges",
            "next_action": "Audit data sources and explore integrated reporting approach",
            "follow_up_date": _date(7),
            "tags": ["reporting", "data", "workflow"],
        },
        {
            "id": 25,
            "organization_id": 5,
            "interaction_type": "Follow-up",
            "date": _date(14),
            "title": "Youth Check-in Follow-up",
            "notes": "Followed up with case worker about youth check-in process. Youth participants receive regular check-in calls or meetings to track progress toward employment goals. Case notes from these check-ins are entered into a shared document but there is no structured format. Information that could help match youth to opportunities (skills gained, schedule changes, new barriers) may be buried in free-text notes. Staff discussed whether structured check-in templates with standard fields could improve information capture without adding administrative burden. Staff are also concerned about privacy when recording sensitive youth information. Knowledge sharing between case workers is informal and mostly happens during team meetings.",
            "outcome": "Check-in documentation identified as unstructured with knowledge-sharing gaps",
            "next_action": "Draft structured check-in template with privacy-aware fields",
            "follow_up_date": _date(0),
            "tags": ["check-in", "documentation", "privacy", "knowledge-sharing"],
        },
    ]


# ---------------------------------------------------------------------------
# Interaction Summaries (pre-generated AI Note Summary results)
# ---------------------------------------------------------------------------

def _build_summaries():
    out = []
    all_interaction_notes = _wpl_notes() + _kfc_notes() + _gtech_notes() + _arts_notes() + _youth_notes()
    for i, note in enumerate(all_interaction_notes):
        nid = note["id"]
        oid = note["organization_id"]
        org_name = {o["id"]: o["name"] for o in ORGANIZATIONS}[oid]
        summary = _summary_for_interaction(nid, oid, org_name, note)
        out.append(summary)
    return out


def _summary_for_interaction(nid, oid, org_name, note):
    notes_text = note["notes"]
    base = {
        "summary_id": nid,
        "interaction_id": nid,
        "organization_id": oid,
        "created_at": _now_iso(30) if nid <= 5 else _now_iso(20) if nid <= 10 else _now_iso(10),
        "updated_at": _now_iso(7) if nid <= 5 else _now_iso(3) if nid <= 10 else _now_iso(1),
        "summary": f"Summary of {note['title']} at {org_name}. Key themes identified.",
        "key_discussion_points": [f"Discussed {note['title'].lower()}", "Reviewed current workflow", "Identified pain points and potential improvements"],
        "decisions": [note["outcome"]],
        "action_items": [note["next_action"]],
        "risks_or_concerns": [],
        "lessons_learned": [],
        "reusable_insights": [],
        "staff_concerns_or_adoption_concerns": [],
        "human_judgment_points": [],
        "knowledge_sharing_opportunities": [],
        "playbook_candidates": [],
        "recommended_follow_up": note["next_action"],
        "suggested_follow_up_date": note["follow_up_date"],
        "suggested_next_email_type": "follow_up",
        "suggested_tags": note["tags"],
        "follow_up_tasks": [],
        "current_workflow": f"Current workflow involves manual processes as described in the interaction notes.",
        "workflow_pain_points": [],
        "repetitive_tasks_identified": [],
        "information_or_documents_used": [],
        "possible_ai_insertion_points": [],
        "required_human_review": [],
        "missing_knowledge_or_data": [],
        "failure_cases_or_exceptions": [],
        "reusable_workflow_insights": [],
        "workflow_tags": note["tags"],
    }

    # Extract workflow pain points from notes
    pain_point_keywords = {
        "repetitive": "repetitive",
        "manual": "manual",
        "time": "time-consuming",
        "hours": "time-consuming",
        "inconsisten": "inconsistent",
        "scattered": "information scattered",
        "ad-hoc": "ad-hoc process",
        "ad hoc": "ad-hoc process",
    }
    for kw, label in pain_point_keywords.items():
        if kw.lower() in notes_text.lower():
            base["workflow_pain_points"].append(label)
    base["workflow_pain_points"] = list(set(base["workflow_pain_points"]))

    # Extract repetitive tasks from notes  
    rep_keywords = {
        "follow-up": "Follow-up email composition",
        "data entry": "Manual data entry",
        "transcription": "Manual transcription",
        "transcribing": "Manual transcription",
        "email": "Email drafting",
        "scheduling": "Manual scheduling",
        "reporting": "Report compilation",
        "data compilation": "Data compilation",
        "composing": "Email composition",
    }
    for kw, label in rep_keywords.items():
        if kw.lower() in notes_text.lower():
            base["repetitive_tasks_identified"].append(label)
    base["repetitive_tasks_identified"] = list(set(base["repetitive_tasks_identified"]))

    # Extract knowledge sources mentioned
    ks_keywords = {
        "FAQ": "FAQ documents",
        "faq": "FAQ documents",
        "workshop notes": "Past workshop notes",
        "program calendar": "Program calendars",
        "calendar": "Program calendars",
        "email template": "Approved email templates",
        "template": "Template documents",
        "intake form": "Intake forms",
        "intake forms": "Intake forms",
        "Q&A": "Q&A records",
        "qa record": "Q&A records",
        "policy": "Policy documents",
        "grant report": "Previous grant reports",
        "previous grant": "Previous grant reports",
        "past grant": "Previous grant reports",
        "volunteer manual": "Volunteer manuals",
        "resource guide": "Resource guides",
        "website": "Public website pages",
        "spreadsheet": "Spreadsheet trackers",
        "data sheet": "Spreadsheet trackers",
    }
    for kw, label in ks_keywords.items():
        if kw.lower() in notes_text.lower():
            base["information_or_documents_used"].append(label)
    base["information_or_documents_used"] = list(set(base["information_or_documents_used"]))

    # Extract human review requirements
    hr_keywords = {
        "human review": "All AI-generated content requires human review before external use",
        "review": "AI-generated content requires human review",
        "privacy": "Privacy and data handling requires human judgment",
        "personal": "Personalized content requires human review for tone and accuracy",
        "context": "Community context awareness requires human oversight",
    }
    for kw, label in hr_keywords.items():
        if kw.lower() in notes_text.lower():
            base["required_human_review"].append(label)
    base["required_human_review"] = list(set(base["required_human_review"]))

    # Extract staff concerns
    concern_keywords = {
        "generic": "AI-generated content may sound generic",
        "worry": "Staff worry about increased expectations with AI",
        "concern": "Staff expressed concerns about AI impact",
        "privacy": "Privacy concerns about AI data handling",
        "personal connection": "Concern about losing personal connection with AI templates",
    }
    for kw, label in concern_keywords.items():
        if kw.lower() in notes_text.lower():
            base["staff_concerns_or_adoption_concerns"].append(label)

    # Extract human judgment points
    hjp_keywords = {
        "experienced staff": "Experienced staff must review AI outputs before external sharing",
        "experience": "Experienced staff judgment required for quality assurance",
        "human oversight": "Human oversight required for sensitive content",
        "human review": "Human review required for externally visible content",
    }
    for kw, label in hjp_keywords.items():
        if kw.lower() in notes_text.lower():
            base["human_judgment_points"].append(label)

    # Extract failure cases
    fc_keywords = {
        "generic": {"what": "AI output may sound too generic", "why": "Template lacks personalization for specific context", "prevention": "Include personalization fields and human review step"},
        "privacy": {"what": "AI may mishandle private or sensitive information", "why": "AI cannot distinguish public vs internal-only information", "prevention": "Define data handling rules and require human review for privacy-sensitive content"},
        "overpromise": {"what": "AI-generated follow-up may overpromise services", "why": "AI lacks awareness of actual service capacity and eligibility", "prevention": "Include capacity constraints in AI context and require human review"},
        "outdated": {"what": "AI may use outdated program information", "why": "AI training data or reference materials may not reflect current programs", "prevention": "Ensure reference materials are current and include review checkpoint"},
        "eligibility": {"what": "AI summary may miss eligibility exceptions", "why": "Edge cases may not be documented in training or reference data", "prevention": "Document eligibility rules explicitly and require human verification for exceptions"},
    }
    for kw, info in fc_keywords.items():
        if kw.lower() in notes_text.lower():
            base["failure_cases_or_exceptions"].append({
                "what_failed": info["what"],
                "why": info["why"],
                "missing_context": "AI lacks organization-specific operational context and edge-case knowledge",
                "human_review_required": "Human must verify AI output before use or sharing",
                "suggested_prevention": info["prevention"],
            })

    # Extract lessons learned
    if "spreadsheet" in notes_text.lower() or "data" in notes_text.lower():
        base["lessons_learned"].append({
            "title": "Data fragmentation increases reporting effort",
            "description": "When program data lives in disconnected spreadsheets, reporting requires significant manual compilation time."
        })
    if "template" in notes_text.lower():
        base["lessons_learned"].append({
            "title": "Templates with human review balance efficiency and quality",
            "description": "Approved templates with personalization fields reduce drafting time while maintaining quality through human review."
        })
    if "experience" in notes_text.lower() or "experienced" in notes_text.lower():
        base["lessons_learned"].append({
            "title": "Experienced staff carry undocumented process knowledge",
            "description": "Key workflow knowledge resides with experienced staff and is not systematically captured or shared."
        })

    # Extract reusable insights
    if "follow-up" in notes_text.lower() or "follow_up" in notes_text.lower():
        base["reusable_insights"].append("Follow-up communication is a common high-effort pattern across programs that benefits from template support.")
    if "reporting" in notes_text.lower() or "grant" in notes_text.lower():
        base["reusable_insights"].append("Grant reporting effort can be reduced through standardized data collection aligned with common metrics.")
    if "scheduling" in notes_text.lower():
        base["reusable_insights"].append("Manual scheduling coordination is a predictable time sink that can be partially automated.")

    # Extract playbook candidates
    if "follow-up" in notes_text.lower() or "follow_up" in notes_text.lower():
        base["playbook_candidates"].append({
            "title": "Follow-up Communication Workflow",
            "when_to_use": "After any workshop, event, or meeting that requires participant follow-up",
            "suggested_process": "1. Identify follow-up type (thank-you, resource share, next steps) 2. Select approved template 3. Personalize with participant-specific details 4. Human review 5. Send"
        })
    if "reporting" in notes_text.lower():
        base["playbook_candidates"].append({
            "title": "Grant Reporting Pipeline",
            "when_to_use": "At the end of each reporting period or when grant report is due",
            "suggested_process": "1. Extract data from program sources 2. Map to funder metrics 3. Draft narrative from structured inputs 4. Human review for context and accuracy 5. Submit"
        })

    # Fill risks/concerns from staff concerns
    if base["staff_concerns_or_adoption_concerns"]:
        base["risks_or_concerns"] = base["staff_concerns_or_adoption_concerns"][:]

    return base


# ---------------------------------------------------------------------------
# Workflow Knowledge (pre-generated from interaction notes)
# ---------------------------------------------------------------------------

def _workflow_opportunities():
    return [
        {
            "id": 1,
            "organization_id": 1,
            "source_interaction_id": 1,
            "source_interaction_title": "Digital Literacy Program Planning",
            "title": "Follow-up Email Drafting for Workshop Participants",
            "canonical_title": "Follow-up email drafting for program participants",
            "normalized_key": "follow up email drafting program participants",
            "current_process": "Staff manually draft individual follow-up emails for each workshop participant (20+ per workshop). Takes 2-3 hours per workshop cycle.",
            "pain_point": "Repetitive manual drafting of similar follow-up emails after each workshop session",
            "possible_ai_support": "AI-assisted template drafting with personalization fields for participant name, session date, resources, and next steps",
            "knowledge_sources_needed": ["Approved email templates", "Past workshop notes", "Participant communication log", "FAQ documents"],
            "human_review_points": ["All AI-generated content must be reviewed by program lead before sending", "Community context and sensitive participant situations require human judgment"],
            "risks_or_exceptions": ["AI draft may sound too generic for participants with specific needs", "Participant privacy information must be handled carefully"],
            "tags": ["follow-up", "templates", "email", "workshop", "WPL"],
            "status": "Candidate for Pilot",
            "staff_impact": "Reduces 2-3 hours per workshop cycle to 30 minutes of review time",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["Which workshop types have the most consistent follow-up patterns?", "What personalization fields do staff need?", "How do staff currently handle exceptions?"],
            "source_interaction_ids": [1, 2, 3],
            "evidence_count": 3,
            "evidence_excerpts": [
                "Staff spend significant time preparing follow-up emails after each workshop session",
                "Post-workshop follow-up messages are repetitive and time-consuming",
                "Program follow-up emails could use approved templates and human review"
            ],
            "last_seen_at": _now_iso(7),
            "required_human_review": "Program lead review required for all AI-generated content before sending",
            "known_failure_cases": ["Generic-sounding messages may lose personal connection", "Outdated program dates or resource links may be included"],
            "created_at": _now_iso(25),
            "updated_at": _now_iso(7),
        },
        {
            "id": 2,
            "organization_id": 1,
            "source_interaction_id": 5,
            "source_interaction_title": "Grant Reporting Requirements",
            "title": "Grant Report Data Compilation and Drafting",
            "canonical_title": "Grant report data compilation and drafting",
            "normalized_key": "grant report data compilation drafting",
            "current_process": "Staff manually compile data from three separate spreadsheets (registrations, attendance, surveys) into grant reports. Takes approximately 5 hours per quarter.",
            "pain_point": "Manual data compilation from disconnected spreadsheets for quarterly grant reports",
            "possible_ai_support": "Structured data collection with AI-assisted report drafting from standardized inputs",
            "knowledge_sources_needed": ["Previous grant reports", "Program registration data", "Attendance records", "Participant surveys"],
            "human_review_points": ["AI-generated narrative must be reviewed for accuracy and context", "Privacy requirements must be met when reporting participant data"],
            "risks_or_exceptions": ["AI transcription errors could introduce data inaccuracies", "Qualitative program impact may be missed in structured data"],
            "tags": ["reporting", "grants", "data", "WPL"],
            "status": "Needs Validation",
            "staff_impact": "Reduces 5 hours per quarter to 1-2 hours of review and validation",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What metrics are most commonly requested by funders?", "Can qualitative outcomes be captured in structured format?", "What privacy rules apply to participant data?"],
            "source_interaction_ids": [5],
            "evidence_count": 1,
            "evidence_excerpts": ["Program coordinator spends approximately 5 hours per quarter compiling grant reports from three separate spreadsheets"],
            "last_seen_at": _now_iso(8),
            "required_human_review": "Program manager review required for narrative accuracy and context",
            "known_failure_cases": ["AI may miss important qualitative context not captured in structured data fields"],
            "created_at": _now_iso(15),
            "updated_at": _now_iso(8),
        },
        {
            "id": 3,
            "organization_id": 1,
            "source_interaction_id": 4,
            "source_interaction_title": "Community Partner Outreach Call",
            "title": "Workshop Attendance Data Analysis",
            "canonical_title": "Workshop attendance data analysis for program planning",
            "normalized_key": "workshop attendance data analysis program planning",
            "current_process": "Past workshop attendance data is in a spreadsheet and requires manual analysis to inform content planning for future sessions.",
            "pain_point": "No automated way to analyze past attendance patterns to plan appropriate content levels",
            "possible_ai_support": "AI-assisted data analysis to identify attendance patterns and suggest content levels for different audience segments",
            "knowledge_sources_needed": ["Past workshop attendance data", "Program calendars", "Participant feedback forms"],
            "human_review_points": ["Content recommendations must be reviewed by program lead who knows audience needs"],
            "risks_or_exceptions": ["Data may not capture all relevant factors affecting attendance"],
            "tags": ["data-analysis", "planning", "attendance", "WPL"],
            "status": "Identified",
            "staff_impact": "Reduces manual analysis time and improves data-informed program planning",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["What attendance patterns would be most useful for planning?", "How is attendance data currently structured?", "What else affects content level decisions beyond attendance data?"],
            "source_interaction_ids": [4],
            "evidence_count": 1,
            "evidence_excerpts": ["Past workshop attendance data could help plan appropriate content levels but requires manual analysis"],
            "last_seen_at": _now_iso(12),
            "required_human_review": "Program lead review of data-driven recommendations",
            "known_failure_cases": [],
            "created_at": _now_iso(18),
            "updated_at": _now_iso(12),
        },
        {
            "id": 4,
            "organization_id": 2,
            "source_interaction_id": 6,
            "source_interaction_title": "Volunteer Coordination Review",
            "title": "Volunteer Schedule Matching and Communication",
            "canonical_title": "Volunteer schedule matching and communication",
            "normalized_key": "volunteer schedule matching communication",
            "current_process": "Volunteer scheduling managed through shared spreadsheet. Coordinator spends 4-6 hours per week on schedule matching and email confirmations.",
            "pain_point": "Manual schedule matching and individual confirmation emails for 40+ active volunteers",
            "possible_ai_support": "AI-assisted schedule matching based on availability, skills, and program needs with automated confirmation draft generation",
            "knowledge_sources_needed": ["Volunteer availability records", "Program schedules", "Volunteer skill profiles"],
            "human_review_points": ["Schedule changes and volunteer preference exceptions require human handling"],
            "risks_or_exceptions": ["Some volunteers may struggle with technology changes"],
            "tags": ["volunteer", "scheduling", "KFC"],
            "status": "Needs Validation",
            "staff_impact": "Reduces 4-6 hours per week to 1-2 hours of review and exception handling",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What percentage of scheduling is routine vs exception?", "How technology-comfortable are the volunteers?", "What information is needed for effective schedule matching?"],
            "source_interaction_ids": [6],
            "evidence_count": 1,
            "evidence_excerpts": ["Coordinator spends 4-6 hours per week on schedule matching and sending individual emails"],
            "last_seen_at": _now_iso(21),
            "required_human_review": "Coordinator review for schedule exceptions and volunteer preferences",
            "known_failure_cases": ["Volunteers may find automated scheduling difficult to adapt to"],
            "created_at": _now_iso(30),
            "updated_at": _now_iso(21),
        },
        {
            "id": 5,
            "organization_id": 2,
            "source_interaction_id": 7,
            "source_interaction_title": "Donation Intake Process Discussion",
            "title": "Donation Intake Logging and Receipt Generation",
            "canonical_title": "Donation intake logging and receipt generation",
            "normalized_key": "donation intake logging receipt generation",
            "current_process": "Donations logged manually into a tracking spreadsheet. Staff spend 8-10 hours per week on data entry and receipt generation.",
            "pain_point": "Time-consuming manual data entry for donation tracking and tax receipt lookups",
            "possible_ai_support": "Structured donation intake form with automated logging and receipt generation, OCR for handwritten donation notes",
            "knowledge_sources_needed": ["Donation intake forms", "Food safety policy documents", "Donor records"],
            "human_review_points": ["Food quality notes and special handling requirements need human review"],
            "risks_or_exceptions": ["OCR may inaccurately capture handwritten donation details", "Food quality context may be lost in structured fields"],
            "tags": ["donation", "data-entry", "KFC"],
            "status": "Identified",
            "staff_impact": "Reduces 8-10 hours per week to 2-3 hours of review and handling exceptions",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What donation information is most commonly needed for receipts?", "How are food quality notes currently captured?", "What are the most common data entry errors?"],
            "source_interaction_ids": [7],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff estimate 8-10 hours per week on donation data entry and receipt generation"],
            "last_seen_at": _now_iso(14),
            "required_human_review": "Staff review for food quality context and special handling notes",
            "known_failure_cases": ["OCR may inaccurately capture handwritten information", "Structured fields may miss important food quality context"],
            "created_at": _now_iso(28),
            "updated_at": _now_iso(14),
        },
        {
            "id": 6,
            "organization_id": 2,
            "source_interaction_id": 9,
            "source_interaction_title": "Grant Reporting Requirements Research",
            "title": "Multi-Funder Grant Report Compilation",
            "canonical_title": "Multi-funder grant report compilation",
            "normalized_key": "multi funder grant report compilation",
            "current_process": "Data extracted manually from donation logs, volunteer hours, and attendance records for each funder's specific format. 6-8 hours per quarter per grant.",
            "pain_point": "Each funder requires different metrics and formats, requiring manual data extraction from multiple sources",
            "possible_ai_support": "Standardized data collection with AI-assisted report drafting that adapts content to each funder's required format and metrics",
            "knowledge_sources_needed": ["Donation logs", "Volunteer hours records", "Program attendance records", "Past grant reports"],
            "human_review_points": ["Program impact context requires human narrative input that structured data may not capture"],
            "risks_or_exceptions": ["AI may miss important program impact context not in structured data"],
            "tags": ["reporting", "grants", "KFC"],
            "status": "Identified",
            "staff_impact": "Reduces compilation time while improving consistency across funder reports",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What common metrics exist across funders?", "Can qualitative impact data be captured structurally?", "What is the biggest time sink in current reporting?"],
            "source_interaction_ids": [9, 10],
            "evidence_count": 2,
            "evidence_excerpts": [
                "Program manager estimates 6-8 hours per quarter on each grant report",
                "Each funder requires different metrics and reporting formats"
            ],
            "last_seen_at": _now_iso(4),
            "required_human_review": "Program manager review for narrative context and impact description",
            "known_failure_cases": ["Automation may miss important qualitative program impact context"],
            "created_at": _now_iso(20),
            "updated_at": _now_iso(4),
        },
        {
            "id": 7,
            "organization_id": 3,
            "source_interaction_id": 11,
            "source_interaction_title": "Founder Intake Process Review",
            "title": "Founder Intake Information Consolidation",
            "canonical_title": "Founder intake information consolidation",
            "normalized_key": "founder intake information consolidation",
            "current_process": "Founder information comes through web forms, emails, and in-person conversations. Coordinator manually enters and reconciles data from all sources.",
            "pain_point": "Founder intake data scattered across multiple sources requiring manual reconciliation",
            "possible_ai_support": "AI-assisted intake information extraction and consolidation from multiple sources into structured founder profiles",
            "knowledge_sources_needed": ["Intake forms", "Past founder records", "Email inquiries"],
            "human_review_points": ["Founder readiness assessment and nuanced challenges require human judgment"],
            "risks_or_exceptions": ["AI may miss important nuances about founder readiness or specific challenges"],
            "tags": ["intake", "data", "GTH"],
            "status": "Identified",
            "staff_impact": "Reduces 3-4 hours per week of reconciliation to 30 minutes of review",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["What information is most commonly duplicated across sources?", "What founder readiness signals are hardest to capture?"],
            "source_interaction_ids": [11],
            "evidence_count": 1,
            "evidence_excerpts": ["Coordinator spends 3-4 hours per week reconciling intake information from multiple sources"],
            "last_seen_at": _now_iso(11),
            "required_human_review": "Coordinator review for nuanced founder context",
            "known_failure_cases": ["AI may miss subtle signals about founder readiness that are apparent in conversation"],
            "created_at": _now_iso(25),
            "updated_at": _now_iso(11),
        },
        {
            "id": 8,
            "organization_id": 3,
            "source_interaction_id": 12,
            "source_interaction_title": "Mentor Matching Discussion",
            "title": "Structured Mentor Matching with Profiles",
            "canonical_title": "Structured mentor matching with profiles",
            "normalized_key": "structured mentor matching profiles",
            "current_process": "Mentors matched to founders based on hub director's personal knowledge. No structured database or criteria. Matching slows when director is unavailable.",
            "pain_point": "Mentor matching depends on one person's knowledge with no structured backup",
            "possible_ai_support": "AI-assisted matching based on structured mentor profiles (industry, expertise, availability) and founder needs",
            "knowledge_sources_needed": ["Mentor interest forms", "Past match records", "Founder profiles"],
            "human_review_points": ["Match quality and relationship dynamics require human judgment that AI cannot assess"],
            "risks_or_exceptions": ["AI matching may miss important interpersonal dynamics that affect mentorship success"],
            "tags": ["mentoring", "matching", "GTH"],
            "status": "Identified",
            "staff_impact": "Reduces dependency on single person's knowledge and speeds initial matching",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What criteria define a successful mentorship match?", "How should mentor profiles be structured?", "What is the current match success rate?"],
            "source_interaction_ids": [12],
            "evidence_count": 1,
            "evidence_excerpts": ["Mentor matching relies on director's personal knowledge with no structured backup system"],
            "last_seen_at": _now_iso(6),
            "required_human_review": "Director review of AI-suggested matches before confirmation",
            "known_failure_cases": ["AI may suggest matches that look good on paper but miss important interpersonal dynamics"],
            "created_at": _now_iso(20),
            "updated_at": _now_iso(6),
        },
        {
            "id": 9,
            "organization_id": 3,
            "source_interaction_id": 13,
            "source_interaction_title": "Event Follow-up Workflow",
            "title": "Post-Event Follow-up Email Generation",
            "canonical_title": "Post-event follow-up email generation",
            "normalized_key": "post event follow up email generation",
            "current_process": "After each event, coordinator drafts individual follow-up emails for 20-100 attendees. Takes 1-2 days per event.",
            "pain_point": "Time-consuming individual email drafting after each event for large attendee lists",
            "possible_ai_support": "Template-based follow-up generation with event-specific content and attendee personalization",
            "knowledge_sources_needed": ["Past Q&A records", "Event attendance lists", "Approved email templates"],
            "human_review_points": ["Experienced staff must review event communications before sending", "Personalization must not sound impersonal"],
            "risks_or_exceptions": ["Generic-sounding follow-ups may reduce attendee engagement"],
            "tags": ["events", "follow-up", "GTH"],
            "status": "Candidate for Pilot",
            "staff_impact": "Reduces 1-2 days per event to 1-2 hours of template customization and review",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["What follow-up content categories are most common?", "Which events have the most standardized follow-up patterns?"],
            "source_interaction_ids": [13],
            "evidence_count": 1,
            "evidence_excerpts": ["Coordinator spends 1-2 days per event composing individual follow-up emails"],
            "last_seen_at": _now_iso(1),
            "required_human_review": "Experienced staff review all event communications before sending",
            "known_failure_cases": ["Templated messages may feel impersonal if not properly customized"],
            "created_at": _now_iso(15),
            "updated_at": _now_iso(1),
        },
        {
            "id": 10,
            "organization_id": 3,
            "source_interaction_id": 14,
            "source_interaction_title": "Grant Navigation Research",
            "title": "Grant Opportunity Monitoring and Matching",
            "canonical_title": "Grant opportunity monitoring and matching",
            "normalized_key": "grant opportunity monitoring matching",
            "current_process": "Staff manually scan funding websites, check eligibility, and match founders to opportunities. Estimated 5 hours per week.",
            "pain_point": "Time-intensive manual research to find and match relevant grant opportunities for founders",
            "possible_ai_support": "Automated grant opportunity monitoring with eligibility matching and deadline tracking. Browser automation for website monitoring.",
            "knowledge_sources_needed": ["Frequently used funding websites", "Founder profiles and eligibility", "Past successful grant records"],
            "human_review_points": ["Grant eligibility nuances and founder-fit assessment require human judgment"],
            "risks_or_exceptions": ["Browser automation may break when website layouts change", "AI may miss subtle eligibility requirements"],
            "tags": ["grants", "research", "GTH"],
            "status": "Identified",
            "staff_impact": "Reduces 5 hours per week of scanning to 1 hour of review and matching refinement",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["Which funding sources are most frequently used?", "What eligibility criteria are most commonly checked?"],
            "source_interaction_ids": [14],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff member estimates spending 5 hours per week scanning funding websites and checking eligibility"],
            "last_seen_at": _now_iso(10),
            "required_human_review": "Staff review of AI-matched opportunities before presenting to founders",
            "known_failure_cases": ["Browser automation may fail on website layout changes", "AI may not catch subtle eligibility exceptions"],
            "created_at": _now_iso(18),
            "updated_at": _now_iso(10),
        },
        {
            "id": 11,
            "organization_id": 4,
            "source_interaction_id": 16,
            "source_interaction_title": "Workshop Scheduling Workflow",
            "title": "Workshop Scheduling Coordination",
            "canonical_title": "Workshop scheduling coordination",
            "normalized_key": "workshop scheduling coordination",
            "current_process": "Workshop scheduling involves email chains with multiple artists, venue calendar checks, and manual confirmations. 3-4 hours per workshop series.",
            "pain_point": "Coordination-heavy manual scheduling with multiple stakeholders",
            "possible_ai_support": "AI-assisted scheduling that checks artist availability, venue calendar, and program themes against past patterns",
            "knowledge_sources_needed": ["Artist availability records", "Venue calendars", "Past workshop schedules"],
            "human_review_points": ["Artist relationships and preferences require human judgment that AI cannot assess"],
            "risks_or_exceptions": ["AI scheduling may not account for artist relationship nuances and personal preferences"],
            "tags": ["scheduling", "workshop", "GRAC"],
            "status": "Identified",
            "staff_impact": "Reduces 3-4 hours per series to 1 hour of review and exception handling",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What scheduling decisions are routine vs relationship-dependent?", "How are artist preferences currently tracked?"],
            "source_interaction_ids": [16],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff estimate 3-4 hours per workshop series on scheduling coordination alone"],
            "last_seen_at": _now_iso(26),
            "required_human_review": "Program lead review for artist relationship considerations",
            "known_failure_cases": ["AI may not understand artist availability nuances and relationship dynamics"],
            "created_at": _now_iso(35),
            "updated_at": _now_iso(26),
        },
        {
            "id": 12,
            "organization_id": 4,
            "source_interaction_id": 17,
            "source_interaction_title": "Artist Communication Review",
            "title": "Artist Communication Template System",
            "canonical_title": "Artist communication template system",
            "normalized_key": "artist communication template system",
            "current_process": "Artist outreach, contracts, and coordination handled through individual emails. No standard templates. 5-6 hours per week on email with 30 artists.",
            "pain_point": "High-volume email communication with no templates for common scenarios",
            "possible_ai_support": "Flexible communication templates for common scenarios (exhibition confirmations, payment notifications, call-for-submissions) with personalization fields",
            "knowledge_sources_needed": ["Past email examples", "Artist contact records", "Contract templates"],
            "human_review_points": ["Personal artist relationships require human tone judgment", "Experienced staff knowledge must be preserved in templates"],
            "risks_or_exceptions": ["Templated communications may feel impersonal to artists who value direct relationships"],
            "tags": ["communication", "artists", "GRAC"],
            "status": "Needs Validation",
            "staff_impact": "Reduces 5-6 hours per week to 2-3 hours of personalization and review",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What are the most common communication scenarios?", "Which templates would benefit most from AI assistance?"],
            "source_interaction_ids": [17],
            "evidence_count": 1,
            "evidence_excerpts": ["Team spends 5-6 hours per week on email communication with approximately 30 active artists"],
            "last_seen_at": _now_iso(19),
            "required_human_review": "Experienced staff review for tone and relationship appropriateness",
            "known_failure_cases": ["Templated messages may feel impersonal to artists"],
            "created_at": _now_iso(30),
            "updated_at": _now_iso(19),
        },
        {
            "id": 13,
            "organization_id": 4,
            "source_interaction_id": 18,
            "source_interaction_title": "Grant Documentation Process",
            "title": "Grant Application Content Reuse System",
            "canonical_title": "Grant application content reuse system",
            "normalized_key": "grant application content reuse system",
            "current_process": "Grant applications require rewriting content from past successful grants to match new funder priorities. 8-10 hours per application, 40% on adapting existing content.",
            "pain_point": "Significant time spent reformatting and adapting content from previous successful grants",
            "possible_ai_support": "Tagged content library with AI-assisted adaptation to match funder priorities and requirements",
            "knowledge_sources_needed": ["Previous grant documents", "Funder guidelines", "Artist bios and project budgets"],
            "human_review_points": ["Narrative alignment with funder priorities requires human strategic judgment"],
            "risks_or_exceptions": ["AI adaptation may misrepresent organizational priorities or program details"],
            "tags": ["grants", "documentation", "GRAC"],
            "status": "Candidate for Pilot",
            "staff_impact": "Reduces 8-10 hours per application to 4-5 hours of content selection and review",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What content sections are most commonly reused?", "How do funder priorities change between applications?"],
            "source_interaction_ids": [18],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff estimate 40% of grant application time is spent formatting and adapting existing content"],
            "last_seen_at": _now_iso(14),
            "required_human_review": "Program lead review for narrative accuracy and funder alignment",
            "known_failure_cases": ["AI may misrepresent organizational priorities when adapting content"],
            "created_at": _now_iso(25),
            "updated_at": _now_iso(14),
        },
        {
            "id": 14,
            "organization_id": 4,
            "source_interaction_id": 19,
            "source_interaction_title": "Newsletter Content Research",
            "title": "Newsletter Content Assembly and Drafting",
            "canonical_title": "Newsletter content assembly and drafting",
            "normalized_key": "newsletter content assembly drafting",
            "current_process": "Content gathered from multiple staff via email and compiled by one editor. 6-8 hours per month on content gathering, formatting, and editing.",
            "pain_point": "Manual content gathering from multiple contributors with significant editing time",
            "possible_ai_support": "Structured content submission with AI-assisted drafting of recurring sections (program updates, artist spotlights, event listings)",
            "knowledge_sources_needed": ["Past newsletters (PDF)", "Program calendars", "Event listings"],
            "human_review_points": ["Organizational voice and quality require human editorial review"],
            "risks_or_exceptions": ["AI-generated content may sound generic and lose organizational voice"],
            "tags": ["newsletter", "content", "GRAC"],
            "status": "Identified",
            "staff_impact": "Reduces 6-8 hours per month to 3-4 hours of editorial review",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What newsletter sections have the most predictable content patterns?", "How can organizational voice be preserved in templates?"],
            "source_interaction_ids": [19],
            "evidence_count": 1,
            "evidence_excerpts": ["Editor estimates 6-8 hours per month on content gathering, formatting, and editing"],
            "last_seen_at": _now_iso(8),
            "required_human_review": "Editor review for voice, accuracy, and quality",
            "known_failure_cases": ["AI-generated content may lose organizational voice and sound generic"],
            "created_at": _now_iso(22),
            "updated_at": _now_iso(8),
        },
        {
            "id": 15,
            "organization_id": 5,
            "source_interaction_id": 21,
            "source_interaction_title": "Intake Process Review",
            "title": "Youth Intake Transcription and Digitization",
            "canonical_title": "Youth intake transcription and digitization",
            "normalized_key": "youth intake transcription digitization",
            "current_process": "Youth intake information collected on paper forms and transcribed to digital spreadsheet. 2-3 hours per week on data entry.",
            "pain_point": "Manual transcription of paper intake forms prone to errors and time-consuming",
            "possible_ai_support": "Digital intake form with structured fields and optional AI-assisted transcription from handwritten notes",
            "knowledge_sources_needed": ["Intake forms", "Case notes"],
            "human_review_points": ["Contextual notes written in margins of paper forms may be lost in digitization"],
            "risks_or_exceptions": ["OCR error risk for handwritten notes", "Important contextual notes may be lost in structured fields"],
            "tags": ["intake", "data-entry", "RYEN"],
            "status": "Identified",
            "staff_impact": "Reduces 2-3 hours per week of transcription to 30 minutes of validation",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["What intake fields are most essential for follow-up?", "How are margin notes currently used?"],
            "source_interaction_ids": [21],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff spend 2-3 hours per week transcribing paper intake forms into digital spreadsheet"],
            "last_seen_at": _now_iso(30),
            "required_human_review": "Case worker review for contextual notes preservation",
            "known_failure_cases": ["OCR may inaccurately capture handwritten margin notes that contain important context"],
            "created_at": _now_iso(40),
            "updated_at": _now_iso(30),
        },
        {
            "id": 16,
            "organization_id": 5,
            "source_interaction_id": 22,
            "source_interaction_title": "Employer Outreach Discussion",
            "title": "Employer Outreach Follow-up Tracking",
            "canonical_title": "Employer outreach follow-up tracking",
            "normalized_key": "employer outreach follow up tracking",
            "current_process": "Employer contacts and outreach tracked in spreadsheet. Specialist sends individual follow-up emails manually. 3-4 hours per week for 50+ employer relationships.",
            "pain_point": "Manual follow-up tracking and email composition for a large employer network",
            "possible_ai_support": "Automated check-in reminders with AI-assisted draft follow-up emails based on last interaction context",
            "knowledge_sources_needed": ["Employer contact records", "Past outreach email templates", "Placement outcome data"],
            "human_review_points": ["Personal employer relationships require careful tone management in AI-generated communications"],
            "risks_or_exceptions": ["Automated reminders may feel impersonal to long-standing employer partners"],
            "tags": ["employer", "outreach", "RYEN"],
            "status": "Identified",
            "staff_impact": "Reduces 3-4 hours per week to 1 hour of review and personalization",
            "adoption_risk_level": "Low",
            "next_discovery_questions": ["What is the optimal check-in frequency for different employer types?", "What employer information is most important for follow-up context?"],
            "source_interaction_ids": [22],
            "evidence_count": 1,
            "evidence_excerpts": ["Specialist spends 3-4 hours per week on employer follow-up coordination with 50+ active relationships"],
            "last_seen_at": _now_iso(21),
            "required_human_review": "Specialist review for tone and relationship appropriateness",
            "known_failure_cases": ["Automated follow-ups may feel impersonal to established employer partners"],
            "created_at": _now_iso(35),
            "updated_at": _now_iso(21),
        },
        {
            "id": 17,
            "organization_id": 5,
            "source_interaction_id": 23,
            "source_interaction_title": "Resume Workshop Follow-up",
            "title": "Workshop Follow-up with Personalized Feedback",
            "canonical_title": "Workshop follow-up with personalized feedback",
            "normalized_key": "workshop follow up personalized feedback",
            "current_process": "Staff compose individual follow-up emails for 15-20 participants per workshop with resources, next steps, and feedback.",
            "pain_point": "High-volume personalized follow-up for workshop participants is time-intensive",
            "possible_ai_support": "Template-assisted follow-ups with structured personalization fields for participant-specific resources and feedback sections",
            "knowledge_sources_needed": ["Past workshop notes", "Resource guides", "Participant records"],
            "human_review_points": ["Each participant has unique needs that templates must accommodate", "AI-generated feedback may not be specific enough to be useful"],
            "risks_or_exceptions": ["AI-generated feedback may be too generic to be helpful for job seekers"],
            "tags": ["workshop", "follow-up", "RYEN"],
            "status": "Needs Validation",
            "staff_impact": "Reduces email composition time while maintaining personalization quality",
            "adoption_risk_level": "Medium",
            "next_discovery_questions": ["What personalization fields are most important for useful follow-ups?", "How specific does feedback need to be to be helpful?"],
            "source_interaction_ids": [23],
            "evidence_count": 1,
            "evidence_excerpts": ["Staff compose individual follow-up emails for 15-20 participants per workshop with resources and feedback"],
            "last_seen_at": _now_iso(14),
            "required_human_review": "Staff review for feedback specificity and accuracy",
            "known_failure_cases": ["AI-generated feedback may be too generic to address individual participant needs"],
            "created_at": _now_iso(25),
            "updated_at": _now_iso(14),
        },
    ]


def _knowledge_sources():
    return [
        {"id": 1, "organization_id": 1, "source_type": "FAQ documents", "name": "Digital Literacy FAQ", "description": "FAQ document for common digital literacy questions asked by workshop participants", "location_note": "Local - shared drive", "created_at": _now_iso(60), "updated_at": _now_iso(30), "normalized_key": "faq documents digital literacy faq", "evidence_count": 1, "last_seen_at": _now_iso(30)},
        {"id": 2, "organization_id": 1, "source_type": "Past meeting notes", "name": "Workshop Program Notes Archive", "description": "Past workshop planning notes and program documentation", "location_note": "Local - program team shared folder", "created_at": _now_iso(50), "updated_at": _now_iso(21), "normalized_key": "past meeting notes workshop program notes archive", "evidence_count": 2, "last_seen_at": _now_iso(18)},
        {"id": 3, "organization_id": 1, "source_type": "Approved email templates", "name": "Follow-up Email Draft Templates", "description": "Approved follow-up email templates for workshop communications under development", "location_note": "Local - program team workspace", "created_at": _now_iso(18), "updated_at": _now_iso(7), "normalized_key": "approved email templates follow up email draft templates", "evidence_count": 3, "last_seen_at": _now_iso(7)},
        {"id": 4, "organization_id": 1, "source_type": "Program calendars", "name": "Program Calendar and Schedule", "description": "Workshop schedule and program calendar used for content planning", "location_note": "Local - shared calendar", "created_at": _now_iso(60), "updated_at": _now_iso(12), "normalized_key": "program calendars program calendar and schedule", "evidence_count": 1, "last_seen_at": _now_iso(12)},
        {"id": 5, "organization_id": 1, "source_type": "Previous grant reports", "name": "Past Grant Report Library", "description": "Previous grant reports in shared folder that could serve as templates for formatting", "location_note": "Local - grants shared drive", "created_at": _now_iso(90), "updated_at": _now_iso(8), "normalized_key": "previous grant reports past grant report library", "evidence_count": 1, "last_seen_at": _now_iso(8)},
        {"id": 6, "organization_id": 2, "source_type": "Intake forms", "name": "Donation Intake Forms", "description": "Standard forms used for logging incoming food donations", "location_note": "Local - operations binder", "created_at": _now_iso(80), "updated_at": _now_iso(14), "normalized_key": "intake forms donation intake forms", "evidence_count": 1, "last_seen_at": _now_iso(14)},
        {"id": 7, "organization_id": 2, "source_type": "Policy documents", "name": "Food Safety Policy Document", "description": "Policy document outlining food safety and special handling requirements", "location_note": "Local - shared drive", "created_at": _now_iso(80), "updated_at": _now_iso(14), "normalized_key": "policy documents food safety policy document", "evidence_count": 1, "last_seen_at": _now_iso(14)},
        {"id": 8, "organization_id": 2, "source_type": "Spreadsheet trackers", "name": "Volunteer Hours and Donation Logs", "description": "Spreadsheets tracking volunteer hours and incoming donations for reporting", "location_note": "Local - operations team workspace", "created_at": _now_iso(70), "updated_at": _now_iso(4), "normalized_key": "spreadsheet trackers volunteer hours and donation logs", "evidence_count": 2, "last_seen_at": _now_iso(4)},
        {"id": 9, "organization_id": 2, "source_type": "Previous grant reports", "name": "Past Grant Reports", "description": "Previous grant reports stored in shared drive used as reference for formatting and metrics", "location_note": "Local - grants shared drive", "created_at": _now_iso(60), "updated_at": _now_iso(4), "normalized_key": "previous grant reports past grant reports", "evidence_count": 2, "last_seen_at": _now_iso(4)},
        {"id": 10, "organization_id": 3, "source_type": "Intake forms", "name": "Founder Intake Forms and Records", "description": "Web forms and structured records for founder intake information", "location_note": "Local - intake system", "created_at": _now_iso(50), "updated_at": _now_iso(11), "normalized_key": "intake forms founder intake forms and records", "evidence_count": 1, "last_seen_at": _now_iso(11)},
        {"id": 11, "organization_id": 3, "source_type": "Q&A records", "name": "Event Q&A Records", "description": "Q&A records from past events used to inform follow-up content", "location_note": "Local - event team folder", "created_at": _now_iso(30), "updated_at": _now_iso(1), "normalized_key": "qa records event qa records", "evidence_count": 1, "last_seen_at": _now_iso(1)},
        {"id": 12, "organization_id": 3, "source_type": "Past meeting notes", "name": "Past Match Records", "description": "Historical records of mentor-founder matches and outcomes", "location_note": "Local - program team shared folder", "created_at": _now_iso(45), "updated_at": _now_iso(6), "normalized_key": "past meeting notes past match records", "evidence_count": 1, "last_seen_at": _now_iso(6)},
        {"id": 13, "organization_id": 4, "source_type": "Past meeting notes", "name": "Past Workshop Notes", "description": "Individual workshop notes stored in program files", "location_note": "Local - program team files", "created_at": _now_iso(60), "updated_at": _now_iso(26), "normalized_key": "past meeting notes past workshop notes", "evidence_count": 1, "last_seen_at": _now_iso(26)},
        {"id": 14, "organization_id": 4, "source_type": "Previous grant reports", "name": "Past Grant Documents", "description": "Previous grant applications and supporting materials organized by year", "location_note": "Local - grants shared folder", "created_at": _now_iso(50), "updated_at": _now_iso(14), "normalized_key": "previous grant reports past grant documents", "evidence_count": 2, "last_seen_at": _now_iso(14)},
        {"id": 15, "organization_id": 5, "source_type": "Intake forms", "name": "Youth Intake Forms", "description": "Paper and digital intake forms for youth participant information", "location_note": "Local - intake binder and digital records", "created_at": _now_iso(50), "updated_at": _now_iso(30), "normalized_key": "intake forms youth intake forms", "evidence_count": 1, "last_seen_at": _now_iso(30)},
        {"id": 16, "organization_id": 5, "source_type": "Spreadsheet trackers", "name": "Employer Contact Spreadsheet", "description": "Spreadsheet tracking employer contacts, outreach history, and placement outcomes", "location_note": "Local - employment team workspace", "created_at": _now_iso(50), "updated_at": _now_iso(21), "normalized_key": "spreadsheet trackers employer contact spreadsheet", "evidence_count": 1, "last_seen_at": _now_iso(21)},
    ]


def _failure_cases():
    return [
        {"id": 1, "organization_id": 1, "source_interaction_id": 2, "source_interaction_title": "Staff Workflow Pain Points", "what_failed": "AI-generated follow-up email may sound too generic for community context", "why_it_failed": "AI lacks understanding of the personal relationships staff build with program participants", "missing_context": "Participant-specific context and relationship history are not available to AI", "human_review_required": "Program lead must review all AI-generated communications before sending", "suggested_prevention": "Include participant context fields in templates and require human review for tone and personalization", "tags": ["follow-up", "tone", "community-context"], "status": "Identified", "created_at": _now_iso(25), "updated_at": _now_iso(7), "source_interaction_ids": [1, 2, 3], "evidence_count": 3, "evidence_excerpts": ["Staff worry automated messages may sound too generic and miss personal connection", "Templated messages need to accommodate participant-specific situations", "Staff emphasized human review for all external communications"], "last_seen_at": _now_iso(7), "normalized_key": "ai generated follow up email may sound too generic for community context"},
        {"id": 2, "organization_id": 1, "source_interaction_id": 5, "source_interaction_title": "Grant Reporting Requirements", "what_failed": "AI may introduce data errors when transcribing or compiling reporting data", "why_it_failed": "AI transcription may not accurately capture data from disconnected spreadsheet sources", "missing_context": "Data sources are not standardized and contain inconsistent formats", "human_review_required": "Program manager must verify all AI-compiled data before submission", "suggested_prevention": "Standardize data collection formats and implement validation checks before AI processing", "tags": ["data", "reporting", "accuracy"], "status": "Identified", "created_at": _now_iso(15), "updated_at": _now_iso(8), "source_interaction_ids": [5], "evidence_count": 1, "evidence_excerpts": ["Staff concerned that automation may introduce errors in data transcription"], "last_seen_at": _now_iso(8), "normalized_key": "ai may introduce data errors when transcribing or compiling reporting data"},
        {"id": 3, "organization_id": 2, "source_interaction_id": 7, "source_interaction_title": "Donation Intake Process Discussion", "what_failed": "Automated donation tracking may miss important food quality context", "why_it_failed": "Structured fields cannot capture nuanced quality observations that staff currently note", "missing_context": "Food quality notes and special handling requirements are context-dependent", "human_review_required": "Staff must review automated entries for quality and special handling context", "suggested_prevention": "Include free-text quality notes field and require staff sign-off on each donation entry", "tags": ["donation", "quality", "context"], "status": "Identified", "created_at": _now_iso(28), "updated_at": _now_iso(14), "source_interaction_ids": [7], "evidence_count": 1, "evidence_excerpts": ["Staff concerned that automating donation tracking may not capture important food quality context"], "last_seen_at": _now_iso(14), "normalized_key": "automated donation tracking may miss important food quality context"},
        {"id": 4, "organization_id": 2, "source_interaction_id": 8, "source_interaction_title": "Client Communication Follow-up", "what_failed": "AI-generated client communications may use inappropriate language for vulnerable situations", "why_it_failed": "AI cannot fully understand the diverse needs and circumstances of clients in vulnerable situations", "missing_context": "Client vulnerability context and appropriate communication tone are not fully documented", "human_review_required": "Staff with client knowledge must review all AI-generated communications", "suggested_prevention": "Develop communication tone guidelines and require staff review before sending to clients", "tags": ["communication", "client-services", "tone"], "status": "Identified", "created_at": _now_iso(25), "updated_at": _now_iso(10), "source_interaction_ids": [8], "evidence_count": 1, "evidence_excerpts": ["Staff worry standardized templates may make communications feel impersonal for vulnerable clients"], "last_seen_at": _now_iso(10), "normalized_key": "ai generated client communications may use inappropriate language for vulnerable situations"},
        {"id": 5, "organization_id": 3, "source_interaction_id": 14, "source_interaction_title": "Grant Navigation Research", "what_failed": "Browser automation for grant website monitoring may break on layout changes", "why_it_failed": "Websites frequently update their layouts, breaking automated scraping or monitoring scripts", "missing_context": "AI/browser automation cannot predict or adapt to website layout changes without human intervention", "human_review_required": "Staff must periodically verify automation is still working correctly", "suggested_prevention": "Implement monitoring alerts for automation failures and maintain manual fallback process", "tags": ["automation", "grants", "website"], "status": "Identified", "created_at": _now_iso(18), "updated_at": _now_iso(10), "source_interaction_ids": [14], "evidence_count": 1, "evidence_excerpts": ["Browser automation may help monitor funding website updates but may break when layouts change"], "last_seen_at": _now_iso(10), "normalized_key": "browser automation for grant website monitoring may break on layout changes"},
        {"id": 6, "organization_id": 3, "source_interaction_id": 15, "source_interaction_title": "Resource Directory Follow-up", "what_failed": "AI-generated follow-up may overpromise services to founders", "why_it_failed": "AI lacks awareness of actual service capacity, eligibility criteria, and current availability", "missing_context": "Real-time capacity and eligibility status are not available to AI systems", "human_review_required": "Staff must review AI-generated commitments before communication with founders", "suggested_prevention": "Include capacity constraints in AI context and require staff approval before any service commitment communication", "tags": ["overpromise", "founders", "accuracy"], "status": "Identified", "created_at": _now_iso(14), "updated_at": _now_iso(7), "source_interaction_ids": [15], "evidence_count": 1, "evidence_excerpts": ["Staff are worried that AI may overpromise services to founders"], "last_seen_at": _now_iso(7), "normalized_key": "ai generated follow up may overpromise services to founders"},
        {"id": 7, "organization_id": 4, "source_interaction_id": 20, "source_interaction_title": "Exhibition Coordination Follow-up", "what_failed": "AI may not distinguish between public information and internal-only notes", "why_it_failed": "AI lacks context about what content is appropriate for public vs internal use", "missing_context": "Content classification rules and organizational privacy policies are not systematically documented", "human_review_required": "Staff must review AI-generated promotional content for public vs internal appropriateness", "suggested_prevention": "Define content classification guidelines and include in AI system context, require staff review for all external content", "tags": ["privacy", "content", "public-vs-internal"], "status": "Identified", "created_at": _now_iso(18), "updated_at": _now_iso(2), "source_interaction_ids": [20], "evidence_count": 1, "evidence_excerpts": ["Uncertainty about what information should be public vs internal-only when using AI to draft promotional content"], "last_seen_at": _now_iso(2), "normalized_key": "ai may not distinguish between public information and internal only notes"},
        {"id": 8, "organization_id": 5, "source_interaction_id": 21, "source_interaction_title": "Intake Process Review", "what_failed": "OCR may inaccurately capture handwritten intake notes with important context", "why_it_failed": "Handwritten margin notes contain nuanced observations that OCR may miss or misinterpret", "missing_context": "Case worker observations written in margins of intake forms are not structured", "human_review_required": "Case worker must review AI-transcribed intake notes for accuracy", "suggested_prevention": "Implement human-in-the-loop validation for all OCR-processed intake notes, with special attention to margin annotations", "tags": ["intake", "ocr", "accuracy"], "status": "Identified", "created_at": _now_iso(40), "updated_at": _now_iso(30), "source_interaction_ids": [21], "evidence_count": 1, "evidence_excerpts": ["Staff concerned that digitization may lose important contextual notes that case workers write in margins"], "last_seen_at": _now_iso(30), "normalized_key": "ocr may inaccurately capture handwritten intake notes with important context"},
    ]


def _adoption_risk_notes():
    return [
        {"id": 1, "organization_id": 1, "source_interaction_id": 2, "source_interaction_title": "Staff Workflow Pain Points", "risk_type": "Staff Concern", "description": "Staff worry AI will increase output expectations without reducing overall workload", "severity": "Medium", "related_staff_role": "Program coordinators and facilitators", "suggested_mitigation": "Set clear expectations that AI is for reducing repetitive work, not increasing output volume without recognition", "tags": ["staff-concern", "workload"], "created_at": _now_iso(25), "updated_at": _now_iso(7), "source_interaction_ids": [1, 2], "normalized_key": "staff worry ai will increase output expectations without reducing workload", "evidence_count": 2, "evidence_excerpts": ["Staff spend significant time on repetitive follow-up emails", "Team worried that efficiency gains may not reduce overall workload"], "last_seen_at": _now_iso(7)},
        {"id": 2, "organization_id": 1, "source_interaction_id": 4, "source_interaction_title": "Community Partner Outreach Call", "risk_type": "Staff Concern", "description": "Staff concerned AI may create content mismatched for audience needs without human oversight", "severity": "Low", "related_staff_role": "Program leads", "suggested_mitigation": "Require human review for all audience-facing content and maintain staff authority over final content decisions", "tags": ["staff-concern", "quality"], "created_at": _now_iso(18), "updated_at": _now_iso(12), "source_interaction_ids": [4], "normalized_key": "staff concerned ai may create content mismatched for audience needs", "evidence_count": 1, "evidence_excerpts": ["Staff are concerned AI could create content mismatched for audience needs without human oversight"], "last_seen_at": _now_iso(12)},
        {"id": 3, "organization_id": 1, "source_interaction_id": 2, "source_interaction_title": "Staff Workflow Pain Points", "risk_type": "Staff Concern", "description": "Data privacy concerns when using AI tools to draft messages containing participant details", "severity": "High", "related_staff_role": "All staff handling participant data", "suggested_mitigation": "Define data privacy guidelines for AI tool use and establish which participant data can be processed through AI systems", "tags": ["privacy", "data-protection"], "created_at": _now_iso(21), "updated_at": _now_iso(7), "source_interaction_ids": [2], "normalized_key": "data privacy concerns when using ai tools with participant details", "evidence_count": 1, "evidence_excerpts": ["Program leads concerned about data privacy when using AI tools to draft messages with participant details"], "last_seen_at": _now_iso(7)},
        {"id": 4, "organization_id": 2, "source_interaction_id": 8, "source_interaction_title": "Client Communication Follow-up", "risk_type": "Staff Concern", "description": "Staff worry AI-generated communications may feel impersonal for clients in vulnerable situations", "severity": "Medium", "related_staff_role": "Client services staff", "suggested_mitigation": "Develop flexible templates with tone options and require staff personalization review before sending to clients", "tags": ["staff-concern", "client-services"], "created_at": _now_iso(25), "updated_at": _now_iso(10), "source_interaction_ids": [8], "normalized_key": "staff worry ai communication may feel impersonal for vulnerable clients", "evidence_count": 1, "evidence_excerpts": ["Staff worry standardized templates may make communications feel impersonal for clients in vulnerable situations"], "last_seen_at": _now_iso(10)},
        {"id": 5, "organization_id": 2, "source_interaction_id": 10, "source_interaction_title": "Reporting Template Follow-up", "risk_type": "Evaluation Risk", "description": "Staff evaluation criteria do not account for improved reporting efficiency, only program outcomes", "severity": "Medium", "related_staff_role": "Program managers and coordinators", "suggested_mitigation": "Update evaluation criteria to recognize administrative improvements and efficiency gains from AI-assisted workflows", "tags": ["evaluation", "recognition"], "created_at": _now_iso(18), "updated_at": _now_iso(0), "source_interaction_ids": [10], "normalized_key": "staff evaluation criteria do not account for reporting efficiency improvements", "evidence_count": 1, "evidence_excerpts": ["Staff are evaluated on program outcomes rather than administrative improvements"], "last_seen_at": _now_iso(0)},
        {"id": 6, "organization_id": 3, "source_interaction_id": 15, "source_interaction_title": "Resource Directory Follow-up", "risk_type": "Staff Concern", "description": "Staff worried AI may provide inaccurate or outdated resource recommendations to founders", "severity": "Medium", "related_staff_role": "Program coordinators", "suggested_mitigation": "Implement regular review cycles for AI resource recommendations and maintain human verification step before sharing with founders", "tags": ["staff-concern", "accuracy"], "created_at": _now_iso(14), "updated_at": _now_iso(7), "source_interaction_ids": [15], "normalized_key": "staff worried ai may provide inaccurate resource recommendations", "evidence_count": 1, "evidence_excerpts": ["Staff want to ensure AI-assisted resource recommendations are accurate and up to date"], "last_seen_at": _now_iso(7)},
        {"id": 7, "organization_id": 3, "source_interaction_id": 12, "source_interaction_title": "Mentor Matching Discussion", "risk_type": "Staff Concern", "description": "No structured way to evaluate mentorship match success, making AI improvement measurement difficult", "severity": "Low", "related_staff_role": "Hub director and coordinators", "suggested_mitigation": "Define success criteria for mentorship matches before implementing AI-assisted matching", "tags": ["evaluation", "mentoring"], "created_at": _now_iso(20), "updated_at": _now_iso(6), "source_interaction_ids": [12], "normalized_key": "no structured way to evaluate mentorship match success", "evidence_count": 1, "evidence_excerpts": ["Staff unsure how to evaluate whether a mentorship match is successful"], "last_seen_at": _now_iso(6)},
        {"id": 8, "organization_id": 4, "source_interaction_id": 17, "source_interaction_title": "Artist Communication Review", "risk_type": "Knowledge Gap", "description": "Experienced staff carry most relationship knowledge informally, no system to share context with newer staff", "severity": "Medium", "related_staff_role": "All team members", "suggested_mitigation": "Document key artist relationships, communication preferences, and historical context in a shared knowledge base", "tags": ["knowledge-sharing", "onboarding"], "created_at": _now_iso(30), "updated_at": _now_iso(19), "source_interaction_ids": [17], "normalized_key": "experienced staff carry relationship knowledge informally no sharing system", "evidence_count": 1, "evidence_excerpts": ["Experienced team members carry most of the relationship knowledge informally with no easy way to share"], "last_seen_at": _now_iso(19)},
        {"id": 9, "organization_id": 4, "source_interaction_id": 19, "source_interaction_title": "Newsletter Content Research", "risk_type": "Staff Concern", "description": "Staff concerned AI-generated content may sound generic and lose organizational voice", "severity": "Medium", "related_staff_role": "Communications team", "suggested_mitigation": "Develop voice and tone guidelines for AI-assisted content, require human editorial review for all published content", "tags": ["staff-concern", "voice", "quality"], "created_at": _now_iso(22), "updated_at": _now_iso(8), "source_interaction_ids": [19], "normalized_key": "staff concerned ai content may sound generic lose organizational voice", "evidence_count": 1, "evidence_excerpts": ["Staff are concerned AI-assisted drafting may produce content that sounds generic and misses the unique organizational voice"], "last_seen_at": _now_iso(8)},
        {"id": 10, "organization_id": 5, "source_interaction_id": 21, "source_interaction_title": "Intake Process Review", "risk_type": "Staff Concern", "description": "Concern that digitizing intake may lose important contextual notes written in margins", "severity": "Low", "related_staff_role": "Case workers", "suggested_mitigation": "Design intake system that preserves free-text case worker observations alongside structured fields", "tags": ["staff-concern", "intake", "context"], "created_at": _now_iso(40), "updated_at": _now_iso(30), "source_interaction_ids": [21], "normalized_key": "concern digitizing intake may lose contextual margin notes", "evidence_count": 1, "evidence_excerpts": ["Staff concerned digitization may lose important contextual notes that case workers write in margins"], "last_seen_at": _now_iso(30)},
        {"id": 11, "organization_id": 5, "source_interaction_id": 23, "source_interaction_title": "Resume Workshop Follow-up", "risk_type": "Staff Concern", "description": "AI-generated feedback may not be specific enough to be useful for job seekers", "severity": "Medium", "related_staff_role": "Employment specialists", "suggested_mitigation": "Design feedback templates with structured specificity fields and require staff review for usefulness before sending", "tags": ["staff-concern", "feedback", "quality"], "created_at": _now_iso(25), "updated_at": _now_iso(14), "source_interaction_ids": [23], "normalized_key": "ai feedback may not be specific enough for job seekers", "evidence_count": 1, "evidence_excerpts": ["Staff worry AI-generated feedback may not be specific enough to be useful for job seekers"], "last_seen_at": _now_iso(14)},
        {"id": 12, "organization_id": 5, "source_interaction_id": 25, "source_interaction_title": "Youth Check-in Follow-up", "risk_type": "Privacy Risk", "description": "Privacy concerns when recording sensitive youth information in structured or AI-processed systems", "severity": "High", "related_staff_role": "Case workers and program staff", "suggested_mitigation": "Define privacy-aware data handling protocols for youth information and establish clear access controls", "tags": ["privacy", "youth", "data-protection"], "created_at": _now_iso(18), "updated_at": _now_iso(0), "source_interaction_ids": [25], "normalized_key": "privacy concerns recording sensitive youth information", "evidence_count": 1, "evidence_excerpts": ["Staff concerned about privacy when recording sensitive youth information in shared or AI-processed systems"], "last_seen_at": _now_iso(0)},
    ]


# ---------------------------------------------------------------------------
# Outbox Drafts
# ---------------------------------------------------------------------------

def _outbox_drafts():
    return [
        {
            "id": 1,
            "to": "sarah.chen@wpl.ca",
            "subject": "Follow-up on Digital Literacy Program Planning",
            "body": "Hello Sarah,\n\nThank you for the productive discussion about the digital literacy program planning.\n\nAs discussed, I will map the current follow-up email workflow and identify template opportunities. I will share the draft template options for your review once they are ready.\n\nPlease let me know if there are any specific program areas you would like me to prioritize.\n\nBest regards,\nNobuki Matsui",
            "organization_id": 1,
            "status": "draft",
            "recipient_name": "Sarah Chen",
            "recipient_role": "Program Coordinator",
            "recipient_email_optional": "sarah.chen@wpl.ca",
            "draft_type": "follow_up",
            "source_interaction_id": 1,
            "source_note_summary_id": 1,
            "human_review_notes": "",
            "created_at": _now_iso(15),
            "updated_at": _now_iso(15),
        },
        {
            "id": 2,
            "to": "maria.santos@kfc.ca",
            "subject": "Exploring Volunteer Coordination Support",
            "body": "Hello Maria,\n\nI am reaching out to explore how we might support Kitchener Community Food Centre with volunteer coordination.\n\nBased on our initial discussion, I understand that volunteer scheduling and communication represents a significant time commitment for your team. I would be happy to explore structured scheduling approaches that could reduce manual coordination time while preserving the personal touch your volunteers value.\n\nWould you be available for a brief follow-up conversation?\n\nBest regards,\nNobuki Matsui",
            "organization_id": 2,
            "status": "needs_review",
            "recipient_name": "Maria Santos",
            "recipient_role": "Program Director",
            "recipient_email_optional": "maria.santos@kfc.ca",
            "draft_type": "intro_outreach",
            "source_interaction_id": 6,
            "source_note_summary_id": 6,
            "human_review_notes": "Add specific reference to volunteer scheduling pain point mentioned in our meeting",
            "created_at": _now_iso(20),
            "updated_at": _now_iso(20),
        },
        {
            "id": 3,
            "to": "james.okonkwo@greentechhub.ca",
            "subject": "Thank You for the Founder Intake Discussion",
            "body": "Hello James,\n\nThank you for taking the time to walk me through the founder intake process at GreenTech Startup Hub. It was very helpful to understand the current workflow.\n\nI will follow up with a summary of the intake consolidation opportunities we discussed, along with some initial ideas for structured intake approaches that could reduce manual reconciliation time.\n\nLooking forward to continuing the conversation.\n\nBest regards,\nNobuki Matsui",
            "organization_id": 3,
            "status": "approved",
            "recipient_name": "James Okonkwo",
            "recipient_role": "Hub Director",
            "recipient_email_optional": "james.okonkwo@greentechhub.ca",
            "draft_type": "thank_you",
            "source_interaction_id": 11,
            "source_note_summary_id": 11,
            "human_review_notes": "Ready to send",
            "created_at": _now_iso(12),
            "updated_at": _now_iso(5),
        },
        {
            "id": 4,
            "to": "priya.sharma@grandriverarts.ca",
            "subject": "Meeting Request: Workshop Scheduling Workflow",
            "body": "Hello Priya,\n\nI would like to schedule a meeting to discuss the workshop scheduling workflow at Grand River Arts Collective.\n\nBased on initial information, I understand that workshop scheduling coordination involves multiple artists and venue calendars. I believe there may be opportunities to streamline parts of this process.\n\nWould you be available for a 30-minute call next week?\n\nBest regards,\nNobuki Matsui",
            "organization_id": 4,
            "status": "needs_review",
            "recipient_name": "Priya Sharma",
            "recipient_role": "Program Manager",
            "recipient_email_optional": "priya.sharma@grandriverarts.ca",
            "draft_type": "meeting_request",
            "source_interaction_id": 16,
            "source_note_summary_id": 16,
            "human_review_notes": "",
            "created_at": _now_iso(25),
            "updated_at": _now_iso(25),
        },
        {
            "id": 5,
            "to": "alex.thompson@ryen.ca",
            "subject": "Information Request: Youth Intake Process",
            "body": "Hello Alex,\n\nI am hoping you could share some additional information about the youth intake process at Region Youth Employment Network.\n\nSpecifically, I would like to understand:\n1. What information is currently collected on the paper intake forms\n2. How case workers use the contextual notes from intake in follow-up sessions\n3. What the current data entry workflow looks like from paper to digital\n\nThis will help me better understand where structured intake support could be most useful.\n\nThank you for your time.\n\nBest regards,\nNobuki Matsui",
            "organization_id": 5,
            "status": "draft",
            "recipient_name": "Alex Thompson",
            "recipient_role": "Program Coordinator",
            "recipient_email_optional": "alex.thompson@ryen.ca",
            "draft_type": "information_request",
            "source_interaction_id": 21,
            "source_note_summary_id": 21,
            "human_review_notes": "",
            "created_at": _now_iso(30),
            "updated_at": _now_iso(30),
        },
        {
            "id": 6,
            "to": "sarah.chen@wpl.ca",
            "subject": "Recap - Staff Workflow Review - Waterloo Public Library",
            "body": "Hello Sarah,\n\nThank you for the productive conversation during our meeting regarding 'Staff Workflow Pain Points'.\n\nKey outcome: Confirmed follow-up email pain point is a recurring theme across multiple programs.\n\nAs agreed, next steps include: Draft template options with human review checkpoints for review.\n\nI have noted the follow-up date of " + _date(14) + ".\n\nPlease let me know if anything was missed or if priorities have shifted.\n\nBest regards,\nNobuki Matsui",
            "organization_id": 1,
            "status": "sent_manually",
            "recipient_name": "Sarah Chen",
            "recipient_role": "Program Coordinator",
            "recipient_email_optional": "sarah.chen@wpl.ca",
            "draft_type": "follow_up",
            "source_interaction_id": 2,
            "source_note_summary_id": 2,
            "human_review_notes": "Reviewed and sent manually by Nobuki",
            "created_at": _now_iso(10),
            "updated_at": _now_iso(8),
            "email_type": "Meeting Recap and Next Steps",
            "tone": "professional",
        },
        {
            "id": 7,
            "to": "james.okonkwo@greentechhub.ca",
            "subject": "Event Follow-up: GreenTech Demo Day",
            "body": "Hello James,\n\nAttached is a draft follow-up message for attendees of the recent Demo Day event.\n\nAs discussed during our 'Event Follow-up Workflow' review, I have created a template-based follow-up that can be customized for each attendee segment.\n\nPlease review the draft and let me know if any adjustments are needed before sending.\n\nBest regards,\nNobuki Matsui",
            "organization_id": 3,
            "status": "archived",
            "recipient_name": "James Okonkwo",
            "recipient_role": "Hub Director",
            "recipient_email_optional": "james.okonkwo@greentechhub.ca",
            "draft_type": "follow_up",
            "source_interaction_id": 13,
            "source_note_summary_id": 13,
            "human_review_notes": "Superseded by newer template version",
            "created_at": _now_iso(8),
            "updated_at": _now_iso(3),
        },
        {
            "id": 8,
            "to": "priya.sharma@grandriverarts.ca",
            "subject": "Grant Application Support - Grand River Arts Collective",
            "body": "Hello Priya,\n\nI have reviewed the grant documentation process we discussed in our last meeting.\n\nBased on the content reuse patterns I observed, I believe a tagged content library with section-level templates could significantly reduce the time spent adapting content for different funders.\n\nWould you be interested in a pilot project to develop this approach for your next grant application?\n\nBest regards,\nNobuki Matsui",
            "organization_id": 4,
            "status": "needs_review",
            "recipient_name": "Priya Sharma",
            "recipient_role": "Program Manager",
            "recipient_email_optional": "priya.sharma@grandriverarts.ca",
            "draft_type": "follow_up",
            "source_interaction_id": 18,
            "source_note_summary_id": 18,
            "human_review_notes": "Check if there is an upcoming grant deadline to reference",
            "created_at": _now_iso(5),
            "updated_at": _now_iso(5),
        },
    ]


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def _tasks():
    return [
        {"id": 1, "organization_id": 1, "title": "Map current follow-up email workflow", "description": "Document current process for follow-up emails after digital literacy workshops at Waterloo Public Library", "status": "open", "priority": "High", "due_date": _date(14), "created_at": _now_iso(25), "updated_at": _now_iso(25), "source_interaction_id": 1},
        {"id": 2, "organization_id": 1, "title": "Draft template options for program follow-ups", "description": "Create three template drafts for pilot testing with human review checkpoints", "status": "open", "priority": "High", "due_date": _date(7), "created_at": _now_iso(21), "updated_at": _now_iso(21), "source_interaction_id": 2},
        {"id": 3, "organization_id": 1, "title": "Audit grant reporting data sources", "description": "Audit current data sources and map reporting workflow for grant requirements at Waterloo Public Library", "status": "open", "priority": "Medium", "due_date": _date(21), "created_at": _now_iso(15), "updated_at": _now_iso(15), "source_interaction_id": 5},
        {"id": 4, "organization_id": 2, "title": "Document volunteer scheduling workflow", "description": "Document current scheduling workflow and volunteer communication patterns at Kitchener Community Food Centre", "status": "open", "priority": "Medium", "due_date": _date(10), "created_at": _now_iso(28), "updated_at": _now_iso(28), "source_interaction_id": 6},
        {"id": 5, "organization_id": 2, "title": "Review donation tracking requirements", "description": "Review donation tracking requirements and explore structured input options for intake process", "status": "open", "priority": "Medium", "due_date": _date(3), "created_at": _now_iso(21), "updated_at": _now_iso(21), "source_interaction_id": 7},
        {"id": 6, "organization_id": 2, "title": "Create standardized data collection template", "description": "Create standardized data collection template aligned with common grant metrics for reporting", "status": "completed", "priority": "High", "due_date": _date(4), "created_at": _now_iso(18), "updated_at": _now_iso(2), "source_interaction_id": 9},
        {"id": 7, "organization_id": 3, "title": "Draft mentor profile template", "description": "Draft mentor profile template and matching criteria framework for GreenTech Startup Hub", "status": "open", "priority": "Medium", "due_date": _date(6), "created_at": _now_iso(20), "updated_at": _now_iso(20), "source_interaction_id": 12},
        {"id": 8, "organization_id": 3, "title": "Design event follow-up template", "description": "Design event follow-up template with personalization fields and review workflow", "status": "open", "priority": "High", "due_date": _date(-3), "created_at": _now_iso(15), "updated_at": _now_iso(15), "source_interaction_id": 13},
        {"id": 9, "organization_id": 4, "title": "Create grant content library", "description": "Create grant content library with tagged reusable sections for Grand River Arts Collective", "status": "open", "priority": "Medium", "due_date": _date(14), "created_at": _now_iso(25), "updated_at": _now_iso(25), "source_interaction_id": 18},
        {"id": 10, "organization_id": 4, "title": "Map newsletter content categories", "description": "Map newsletter content categories and identify template opportunities", "status": "open", "priority": "Low", "due_date": _date(8), "created_at": _now_iso(22), "updated_at": _now_iso(22), "source_interaction_id": 19},
        {"id": 11, "organization_id": 5, "title": "Explore digital intake options", "description": "Explore digital intake options that preserve contextual notes for youth services", "status": "open", "priority": "Medium", "due_date": _date(30), "created_at": _now_iso(40), "updated_at": _now_iso(40), "source_interaction_id": 21},
        {"id": 12, "organization_id": 5, "title": "Design workshop follow-up template", "description": "Design workshop follow-up template with structured personalization fields for resume workshop participants", "status": "open", "priority": "Medium", "due_date": _date(14), "created_at": _now_iso(28), "updated_at": _now_iso(28), "source_interaction_id": 23},
        {"id": 13, "organization_id": 5, "title": "Audit program reporting data sources", "description": "Audit data sources and explore integrated reporting approach for youth program outcomes", "status": "open", "priority": "Low", "due_date": _date(7), "created_at": _now_iso(21), "updated_at": _now_iso(21), "source_interaction_id": 24},
        {"id": 14, "organization_id": 5, "title": "Draft structured check-in template", "description": "Draft structured check-in template with privacy-aware fields for youth follow-ups", "status": "open", "priority": "Medium", "due_date": _date(-5), "created_at": _now_iso(18), "updated_at": _now_iso(18), "source_interaction_id": 25},
        {"id": 15, "organization_id": 1, "title": "Review partnership data sharing policies", "description": "Review data sharing policies before proceeding with community partnership for digital literacy programs", "status": "completed", "priority": "High", "due_date": _date(5), "created_at": _now_iso(15), "updated_at": _now_iso(3), "source_interaction_id": 4},
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Seeding demo data...")
    print()

    for name, path in FILES.items():
        print(f"  Processing {name}...")
        backup(path)

    print()

    write_json(FILES["organizations"], ORGANIZATIONS)
    all_interactions = _wpl_notes() + _kfc_notes() + _gtech_notes() + _arts_notes() + _youth_notes()
    write_json(FILES["interactions"], all_interactions)
    write_json(FILES["interaction_summaries"], _build_summaries())
    write_json(FILES["outbox"], _outbox_drafts())
    write_json(FILES["tasks"], _tasks())
    write_json(FILES["workflow_knowledge"], {
        "workflow_opportunities": _workflow_opportunities(),
        "knowledge_sources": _knowledge_sources(),
        "failure_cases": _failure_cases(),
        "adoption_risk_notes": _adoption_risk_notes(),
    })

    print()
    print("Done. Demo data seeded successfully.")
    print()
    print("Organizations:   5 realistic org profiles")
    print("Interactions:    25 mock interaction notes across 5 orgs")
    print("Summaries:       25 pre-generated AI Note Summary results")
    print("Workflow Opps:   17 pre-generated workflow opportunities (3 merged for WPL dedup test)")
    print("Knowledge Srcs:  16 pre-generated knowledge sources")
    print("Failure Cases:   8 pre-generated failure cases")
    print("Adoption Risks:  12 pre-generated human-system risk notes")
    print("Outbox Drafts:   8 drafts with varied statuses and types")
    print("Tasks:           15 follow-up tasks (open, completed, overdue, high-priority)")
    print()
    print("Dedup test:      Waterloo Public Library interactions 1, 2, 3 mention similar")
    print("                 follow-up email pain points with different wording.")
    print("                 Expected: 1 merged opportunity with evidence_count=3.")
    print()
    print("To start the server:")
    print("  cd backend && ../.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000")
    print()
    print("Safety: Local mock data only. No external systems contacted.")
    print("        No real customer data included.")


if __name__ == "__main__":
    main()
