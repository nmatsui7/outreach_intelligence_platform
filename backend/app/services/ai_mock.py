from datetime import datetime, timezone
from typing import Dict, Any, List


def summarize_organization(org: Dict[str, Any]) -> Dict[str, Any]:
    readiness_score = min(95, 60 + len(org.get("pain_points", [])) * 8)
    return {
        "summary": f"{org['name']} is a {org['category']} organization. {org['mission_notes']}",
        "outreach_priority": "High" if readiness_score >= 75 else "Medium",
        "ai_readiness_score": readiness_score,
        "why_it_matters": [
            "The organization appears to serve people through information-heavy programs.",
            "AI could support staff preparation, documentation, and follow-up work.",
            "A small pilot would be safer than broad automation."
        ],
        "recommended_questions": [
            "Which repetitive administrative tasks take the most staff time?",
            "Where do staff search for information during service delivery?",
            "What communication or documentation steps require human review?"
        ]
    }


def discover_opportunities(org: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "organization": org["name"],
        "opportunities": [
            {
                "name": "Internal Knowledge Assistant",
                "benefit": "Help staff find approved information faster.",
                "effort": "Medium",
                "human_review": "Required for policy, public-facing, or sensitive answers."
            },
            {
                "name": "Meeting Summary Workflow",
                "benefit": "Convert rough notes into action items and follow-up tasks.",
                "effort": "Low",
                "human_review": "Coordinator reviews before saving or sharing."
            },
            {
                "name": "Workshop Planning Assistant",
                "benefit": "Draft outlines, checklists, and outreach materials for programs.",
                "effort": "Low",
                "human_review": "Program owner approves final materials."
            }
        ]
    }


def generate_next_best_email(
    org: Dict[str, Any],
    interactions: List[Dict[str, Any]],
    ai_summary: Dict[str, Any] | None,
    outbox_entries: List[Dict[str, Any]],
) -> Dict[str, Any]:
    org_name = org.get("name", "")
    contact_name = org.get("contact_name", "there")
    contact_email = org.get("contact_email", "")
    phone_number = org.get("phone_number", "")
    status = org.get("status", "")
    org_id = org.get("id", 0)

    missing_context = []
    if not contact_email:
        missing_context.append("No contact email on file — using placeholder.")
    if not interactions:
        missing_context.append("No interaction history recorded yet.")
    if not ai_summary:
        missing_context.append("AI Summary has not been generated yet.")

    email_type, reason, detected_stage = _determine_email_type(org, interactions)

    recent = _most_recent_interaction(interactions)
    context_used = {
        "Organization Name": org_name,
        "Category": org.get("category", ""),
        "Contact Email": contact_email,
        "Phone Number": phone_number or "Not available",
        "CRM Status": status,
        "Detected Relationship Stage": detected_stage,
        "Total Interactions": len(interactions),
        "Interaction Types": list({i.get("interaction_type", "") for i in interactions}) if interactions else [],
        "Most Recent Interaction": f"{recent.get('date','')} — {recent.get('title','')}" if recent else "None",
        "Recent Outcome": recent.get("outcome", "") if recent else "",
        "Next Action from Last Interaction": recent.get("next_action", "") if recent else "",
        "Follow-up Date": recent.get("follow_up_date", "") if recent else "",
        "AI Readiness Score": ai_summary.get("ai_readiness_score", "N/A") if ai_summary else "N/A",
        "Previous Drafts in Outbox": len(outbox_entries),
    }

    email = _build_email(org, interactions, ai_summary, email_type, recent)

    return {
        "email_type": email_type,
        "reason": reason,
        "detected_stage": detected_stage,
        "to": contact_email,
        "subject": email["subject"],
        "body": email["body"],
        "tone": "professional",
        "reasoning_summary": reason,
        "human_review_notes": [],
        "suggested_edits": [],
        "context_used": context_used,
        "follow_up_date": recent.get("follow_up_date", "") if recent else "",
        "next_action": recent.get("next_action", "Follow up on this email") if recent else "Send initial outreach and await response",
        "missing_context": missing_context,
        "organization_id": org_id,
    }


def _determine_email_type(org: Dict[str, Any], interactions: List[Dict[str, Any]]) -> tuple[str, str, str]:
    status = org.get("status", "").lower()
    num = len(interactions)

    if num == 0 and ("research" in status or "intake" in status):
        return (
            "Initial Outreach",
            f"{org['name']} was added through Research Intake/Discovery but has not been contacted yet. "
            "An initial outreach email introducing AI literacy support would be appropriate.",
            "Not Contacted (Research Intake)",
        )
    if num == 0:
        return (
            "Initial Outreach",
            f"No interactions recorded for {org['name']}. Start with a friendly introduction to explore AI literacy support opportunities.",
            "Not Contacted",
        )

    recent = _most_recent_interaction(interactions) or {}
    latest_type = (recent.get("interaction_type") or "").lower()
    latest_outcome = (recent.get("outcome") or "").lower()
    latest_notes = (recent.get("notes") or "").lower()

    if "pilot" in latest_notes or "pilot" in latest_outcome:
        return (
            "Pilot Proposal Follow-Up",
            f"The most recent interaction discussed a pilot program. Send a proposal summary or next-step email to keep momentum going.",
            "Pilot Discussion",
        )

    if latest_type == "meeting":
        return (
            "Meeting Recap and Next Steps",
            f"The most recent interaction was a Meeting on {recent.get('date')} about '{recent.get('title')}'. "
            "Send a recap email summarizing discussion points and agreed next actions.",
            "Meeting Completed",
        )
    if latest_type in ("call", "email"):
        return (
            "Follow-Up",
            f"The last touchpoint was a {recent.get('interaction_type')} on {recent.get('date')}. "
            "A follow-up email continues the conversation and checks on any pending items.",
            "Follow-Up Needed",
        )

    if "waiting" in status or "reply" in status:
        return (
            "Follow-Up",
            f"Status is '{status}'. The last interaction was a {recent.get('interaction_type')} on {recent.get('date')}. "
            "A polite follow-up would be appropriate.",
            "Awaiting Reply",
        )
    if "scheduled" in status or "confirm" in status:
        return (
            "Meeting Confirmation",
            f"A meeting is scheduled with {org['name']}. Send a confirmation with agenda and preparation details.",
            "Meeting Scheduled",
        )
    if "completed" in status:
        return (
            "Relationship Maintenance",
            f"Outreach with {org['name']} is marked as completed. A check-in to maintain the relationship and explore ongoing needs would be appropriate.",
            "Completed",
        )

    return (
        "Check-In / General Outreach",
        f"{org['name']} has {num} interaction(s). A general check-in keeps the conversation warm and opens the door for next steps.",
        "Active Conversation",
    )


def _most_recent_interaction(interactions: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    if not interactions:
        return None
    return max(interactions, key=lambda i: i.get("date", ""))


def _build_email(
    org: Dict[str, Any],
    interactions: List[Dict[str, Any]],
    ai_summary: Dict[str, Any] | None,
    email_type: str,
    recent: Dict[str, Any] | None,
) -> Dict[str, str]:
    org_name = org.get("name", "")
    contact_name = org.get("contact_name", "there")
    category = org.get("category", "")
    notes = org.get("mission_notes", "")
    score = ai_summary.get("ai_readiness_score", "") if ai_summary else ""

    if email_type == "Initial Outreach":
        subject = f"Exploring AI Literacy Support for {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

I am reaching out to explore whether {org_name} may benefit from practical AI literacy and workflow improvement support.

Based on your organization's profile as a {category} organization:
{notes}

A conversation could help identify small, useful opportunities to support your team's work while keeping human review at the center of every decision.

Would you be open to a brief introductory conversation?

Best regards,
Nobuki Matsui"""
        )
    elif email_type == "Follow-Up":
        last_title = recent.get("title", "our last conversation") if recent else "our last conversation"
        last_date = recent.get("date", "recently") if recent else "recently"
        next_action = recent.get("next_action", "") if recent else ""
        subject = f"Following Up — {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

I am following up on our conversation on {last_date} regarding "{last_title}".

{f'As discussed, my next action was: {next_action}.' if next_action else ''}
I wanted to check in and see if there are any updates or additional thoughts since we last spoke.

Please let me know if you would like to continue the conversation or schedule a follow-up.

Best regards,
Nobuki Matsui"""
        )
    elif email_type == "Meeting Recap and Next Steps":
        last_title = recent.get("title", "our meeting") if recent else "our meeting"
        last_date = recent.get("date", "") if recent else ""
        outcome = recent.get("outcome", "") if recent else ""
        next_action = recent.get("next_action", "") if recent else ""
        follow_up = recent.get("follow_up_date", "") if recent else ""
        subject = f"Recap — {last_title} — {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

Thank you for the productive conversation during our meeting on {last_date} regarding "{last_title}".

{f'Key outcome: {outcome}' if outcome else ''}

{f'As agreed, next steps include: {next_action}' if next_action else ''}
{f'We discussed following up around {follow_up}.' if follow_up else ''}

I have attached a summary of our discussion for your reference. Please let me know if anything was missed or if priorities have shifted.

Looking forward to continuing this work together.

Best regards,
Nobuki Matsui"""
        )
    elif email_type == "Pilot Proposal Follow-Up":
        last_title = recent.get("title", "our discussion") if recent else "our discussion"
        subject = f"Next Steps — AI Pilot Proposal for {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

Following up on our discussion about a potential AI literacy pilot for {org_name}.

Based on our conversation during "{last_title}", I have prepared a proposal outline for a small-scale pilot program. The pilot would focus on practical, low-risk applications with clear human oversight.

Would you be available for a brief meeting to walk through the proposal and discuss next steps?

I look forward to your thoughts.

Best regards,
Nobuki Matsui"""
        )
    elif email_type == "Meeting Confirmation":
        subject = f"Confirmation — Upcoming Meeting with {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

I am writing to confirm our upcoming meeting. I look forward to learning more about {org_name}'s work and exploring how AI literacy support could be helpful.

To make the most of our time, here are a few questions to consider beforehand:
- Which workflows or tasks take the most staff time?
- Are there any areas where documentation or follow-up could be improved?
- What would make a pilot program most valuable to your team?

Please let me know if you need to reschedule.

Best regards,
Nobuki Matsui"""
        )
    elif email_type == "Relationship Maintenance":
        subject = f"Checking In — {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

It has been a while since we last connected. I hope things are going well at {org_name}.

I wanted to check in and see if there are any new opportunities or challenges where AI literacy support might be helpful. We have new resources and program options available.

Would you be open to a brief update call?

Best regards,
Nobuki Matsui"""
        )
    else:
        subject = f"Checking In with {org_name}"
        body = _fmt(
            f"""Hello {contact_name},

I hope this message finds you well.

I am reaching out to continue our conversation about AI literacy and workflow support opportunities for {org_name}.

Please let me know if you have any questions or if there is interest in scheduling a follow-up discussion.

Best regards,
Nobuki Matsui"""
        )

    return {"subject": subject, "body": body}


def _fmt(text: str) -> str:
    import textwrap
    return textwrap.dedent(text).strip()


def derive_status_from_interactions(interactions: List[Dict[str, Any]], current_status: str = "") -> str:
    if not interactions:
        if "research" in current_status.lower() or "intake" in current_status.lower():
            return current_status or "Not Contacted"
        return "Not Contacted"

    recent = max(interactions, key=lambda i: i.get("date", ""))
    notes = (recent.get("notes") or "").lower()
    outcome = (recent.get("outcome") or "").lower()
    itype = (recent.get("interaction_type") or "").lower()

    if "pilot" in notes or "pilot" in outcome:
        return "Pilot Discussion"
    if itype == "meeting":
        return "Meeting Completed"
    if itype in ("call", "email"):
        return "Follow-Up Needed"
    return "Active Conversation"


def meeting_brief(org: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "brief": f"Prepare to discuss practical AI workflow opportunities with {org['name']}.",
        "discussion_topics": [
            "Current outreach and documentation workflows",
            "Repetitive staff tasks",
            "Knowledge sharing bottlenecks",
            "Pilot project options",
            "Human review and change management"
        ],
        "desired_outcome": "Identify one small, low-risk AI-assisted workflow pilot."
    }


def summarize_notes(notes: str) -> Dict[str, Any]:
    return {
        "decisions": ["Review potential AI-assisted workflow pilot."],
        "action_items": ["Send follow-up summary.", "Ask for examples of repetitive documentation tasks."],
        "risks": ["Avoid replacing human judgment or sending unreviewed communications."],
        "follow_up_recommendation": "Follow up within one week with a concise summary and one pilot proposal.",
        "source_notes": notes
    }


def _mock_extract_lessons(notes: str) -> List[Dict[str, str]]:
    notes_lower = notes.lower()
    lessons = []

    if "pilot" in notes_lower or "proposal" in notes_lower:
        lessons.append({
            "title": "Pilot proposals benefit from early staff input",
            "description": "Involving staff in pilot design early improves buy-in and surfaces practical constraints that would otherwise block adoption later.",
        })
    if "documentation" in notes_lower or "notes" in notes_lower or "repetitive" in notes_lower:
        lessons.append({
            "title": "Documentation pain points reveal automation opportunities",
            "description": "Staff who spend significant time on manual documentation are the strongest candidates for AI-assisted workflow pilots.",
        })
    if "training" in notes_lower or "literacy" in notes_lower or "workshop" in notes_lower:
        lessons.append({
            "title": "AI literacy builds confidence before tool adoption",
            "description": "Introducing AI concepts through workshops before deploying specific tools reduces anxiety and increases voluntary adoption.",
        })
    if "staff" in notes_lower and ("concern" in notes_lower or "capacity" in notes_lower or "readiness" in notes_lower):
        lessons.append({
            "title": "Staff capacity concerns must be addressed upfront",
            "description": "Any AI initiative must demonstrate it reduces burden, not adds to it. Frame pilots as time-saving tools from the start.",
        })
    if "meeting" in notes_lower or "follow" in notes_lower:
        lessons.append({
            "title": "Structured follow-up processes improve relationship continuity",
            "description": "Recording next actions and follow-up dates during meetings prevents relationship drift and ensures consistent outreach.",
        })
    if "budget" in notes_lower or "grant" in notes_lower or "funding" in notes_lower:
        lessons.append({
            "title": "Grant-funded initiatives need early alignment on outcomes",
            "description": "Clear outcome metrics agreed at the start make grant reporting easier and strengthen case for continued funding.",
        })

    if not lessons:
        lessons.append({
            "title": "Early conversations reveal organizational readiness patterns",
            "description": "Initial discussions help gauge digital maturity, staff openness, and pain point clarity before committing to a pilot direction.",
        })

    return lessons


def _mock_extract_insights(notes: str) -> List[str]:
    notes_lower = notes.lower()
    insights = []

    if "pilot" in notes_lower:
        insights.append("Organizations that proactively discuss pilots are typically more ready to experiment than those that need to be convinced.")
    if "documentation" in notes_lower:
        insights.append("Documentation-heavy workflows are ubiquitous in public-serving organizations and represent a low-barrier entry point for AI assistance.")
    if "staff" in notes_lower and "capacity" in notes_lower:
        insights.append("Staff capacity constraints are often a symptom of manual, repetitive processes — addressing the process reduces the constraint.")
    if "literacy" in notes_lower or "training" in notes_lower:
        insights.append("AI literacy training is most effective when delivered in the context of the learner's actual daily work, not as abstract concepts.")
    if "meeting" in notes_lower:
        insights.append("Meeting follow-up consistency is a leading indicator of relationship health — organizations with structured follow-ups progress faster.")
    if "grant" in notes_lower or "funding" in notes_lower:
        insights.append("Grant funding conversations are most productive when framed around measurable outcomes rather than technology features.")

    if not insights:
        insights.append("Initial conversations provide baseline data on organizational awareness and openness to AI adoption.")

    return insights


def _mock_extract_playbook_candidates(notes: str) -> List[Dict[str, Any]]:
    notes_lower = notes.lower()
    candidates = []

    if "pilot" in notes_lower or "proposal" in notes_lower:
        candidates.append({
            "title": "Pilot Proposal Development Process",
            "when_to_use": "When an organization expresses interest in exploring an AI-assisted workflow pilot during a meeting or call.",
            "suggested_process": "1. Schedule a scoping meeting within one week. 2. Map current workflow with staff input. 3. Draft a pilot proposal with clear success criteria. 4. Review proposal with organization lead. 5. Refine and confirm pilot scope.",
        })
    if "documentation" in notes_lower or "notes" in notes_lower or "repetitive" in notes_lower:
        candidates.append({
            "title": "Documentation Workflow Assessment",
            "when_to_use": "When an organization reports spending significant staff time on manual documentation, note-taking, or report generation.",
            "suggested_process": "1. Conduct a 30-minute workflow mapping session. 2. Identify top 3 documentation pain points. 3. Select one low-risk process for AI assistance. 4. Define human review steps. 5. Run a 2-week pilot with daily check-ins.",
        })
    if "meeting" in notes_lower or "follow" in notes_lower:
        candidates.append({
            "title": "Structured Follow-up Protocol",
            "when_to_use": "When an organization has multiple interactions but lacks a consistent follow-up process, leading to relationship drift.",
            "suggested_process": "1. After each interaction, record next action and follow-up date within 24 hours. 2. Set a weekly review of pending follow-ups. 3. Send recap emails within 48 hours of each meeting. 4. Track follow-up completion rate monthly.",
        })
    if "training" in notes_lower or "literacy" in notes_lower or "workshop" in notes_lower:
        candidates.append({
            "title": "AI Literacy Workshop Delivery",
            "when_to_use": "When an organization requests foundational AI literacy training before committing to specific tool pilots.",
            "suggested_process": "1. Assess current staff AI awareness through a brief survey. 2. Tailor workshop content to the organization's daily workflows. 3. Deliver a 90-minute interactive session with live demonstrations. 4. Collect feedback and identify pilot interest. 5. Schedule follow-up for interested teams.",
        })
    if "grant" in notes_lower or "funding" in notes_lower or "budget" in notes_lower:
        candidates.append({
            "title": "Grant-Funded Initiative Scoping",
            "when_to_use": "When an organization wants to explore AI adoption through grant-funded projects and needs help structuring the proposal.",
            "suggested_process": "1. Identify the grant program requirements and timeline. 2. Map proposed outcomes to the organization's pain points. 3. Draft measurable success indicators. 4. Outline the pilot timeline with human oversight checkpoints. 5. Review with the organization before submission.",
        })
    if "evaluation" in notes_lower or "outcome" in notes_lower or "impact" in notes_lower:
        candidates.append({
            "title": "Pilot Outcome Evaluation Framework",
            "when_to_use": "When a pilot is underway and the organization needs to track whether it is meeting its goals.",
            "suggested_process": "1. Define 2-3 measurable success indicators before pilot launch. 2. Collect baseline data on current process. 3. Track weekly progress against indicators. 4. Conduct a mid-pilot review with staff. 5. Document lessons learned and decide on next phase.",
        })

    if not candidates:
        candidates.append({
            "title": "Initial Engagement Playbook",
            "when_to_use": "When starting a new relationship with an organization that has no prior interaction history.",
            "suggested_process": "1. Research the organization's mission and programs. 2. Prepare a tailored introduction highlighting relevant AI use cases. 3. Schedule an introductory conversation. 4. Listen for pain points and pilot readiness signals. 5. Recommend one low-risk next step.",
        })

    return candidates


def _mock_extract_knowledge_sharing(notes: str) -> List[str]:
    notes_lower = notes.lower()
    opportunities = []

    if "pilot" in notes_lower:
        opportunities.append("Share pilot proposal template and lessons learned with other organizations exploring similar AI use cases.")
    if "documentation" in notes_lower or "notes" in notes_lower:
        opportunities.append("Documentation workflow insights from this engagement could inform a cross-organizational best-practice guide.")
    if "training" in notes_lower or "literacy" in notes_lower:
        opportunities.append("Workshop materials and curriculum developed for this organization could be adapted for similar organizations.")
    if "staff" in notes_lower and "concern" in notes_lower:
        opportunities.append("Staff concern patterns observed here may be valuable input for broader adoption readiness research.")

    if not opportunities:
        opportunities.append("Initial engagement insights may be useful as a baseline reference for future organizational comparisons.")

    return opportunities


def _mock_extract_human_judgment_points(notes: str) -> List[str]:
    notes_lower = notes.lower()
    points = []

    if "pilot" in notes_lower:
        points.append("All pilot-generated content requires human review before external use — never send AI-generated output without verification.")
    if "staff" in notes_lower or "training" in notes_lower:
        points.append("Staff readiness assessment should be conducted by a human program lead, not automated.")
    if "documentation" in notes_lower:
        points.append("AI-generated documentation summaries must be reviewed and approved by a designated staff member before saving to records.")
    if "grant" in notes_lower or "funding" in notes_lower:
        points.append("Grant applications and budget justifications must be written or substantially edited by a human grant writer.")

    points.append("AI recommendations are starting points — all relationship decisions require human judgment and context awareness.")

    return points


def _mock_suggest_tags(notes: str) -> List[str]:
    notes_lower = notes.lower()
    tags = set()

    if "pilot" in notes_lower or "proposal" in notes_lower:
        tags.add("pilot-idea")
    if "workflow" in notes_lower or "process" in notes_lower or "repetitive" in notes_lower:
        tags.add("workflow-improvement")
    if "staff" in notes_lower and ("concern" in notes_lower or "capacity" in notes_lower or "readiness" in notes_lower):
        tags.add("staff-concern")
    if "review" in notes_lower or "oversight" in notes_lower or "human" in notes_lower:
        tags.add("human-review")
    if "share" in notes_lower or "knowledge" in notes_lower or "collaborate" in notes_lower:
        tags.add("knowledge-sharing")
    if "training" in notes_lower or "literacy" in notes_lower or "workshop" in notes_lower:
        tags.add("training-need")
    if "evaluation" in notes_lower or "outcome" in notes_lower or "measure" in notes_lower:
        tags.add("evaluation-concern")
    if "documentation" in notes_lower or "notes" in notes_lower or "report" in notes_lower:
        tags.add("documentation")
    if "follow" in notes_lower or "next" in notes_lower:
        tags.add("follow-up")
    if "grant" in notes_lower or "funding" in notes_lower:
        tags.add("evaluation-concern")

    if not tags:
        tags.add("follow-up")

    return sorted(tags)


def _mock_extract_workflow_fields(notes: str) -> Dict[str, Any]:
    notes_lower = notes.lower()

    has_pilot = "pilot" in notes_lower
    has_doc = "documentation" in notes_lower or "notes" in notes_lower or "report" in notes_lower
    has_repetitive = "repetitive" in notes_lower or "repeated" in notes_lower or "manual" in notes_lower
    has_meeting = "meeting" in notes_lower
    has_training = "training" in notes_lower or "workshop" in notes_lower
    has_follow = "follow" in notes_lower
    has_pain = "pain" in notes_lower or "challenge" in notes_lower or "difficult" in notes_lower
    has_staff = "staff" in notes_lower
    has_data = "data" in notes_lower or "information" in notes_lower or "record" in notes_lower
    has_volunteer = "volunteer" in notes_lower
    has_community = "community" in notes_lower or "public" in notes_lower or "resident" in notes_lower
    has_email = "email" in notes_lower or "outreach" in notes_lower
    has_policy = "policy" in notes_lower or "compliance" in notes_lower or "privacy" in notes_lower

    # Current workflow described
    if has_meeting and has_doc:
        current_workflow = "Staff attend meetings, take manual notes, and later transcribe or summarize them into reports. Documentation is done post-hoc with no structured template."
    elif has_doc and has_repetitive:
        current_workflow = "Staff manually enter data into spreadsheets or forms, produce recurring reports, and store documents in shared folders. There is no automated workflow."
    elif has_volunteer or has_community:
        current_workflow = "Staff coordinate volunteer shifts, track community engagement manually, and produce program reports using spreadsheets and shared documents."
    elif has_email:
        current_workflow = "Outreach is conducted via individual emails. Staff manually track responses, schedule follow-ups, and maintain contact lists in spreadsheets."
    else:
        current_workflow = "Staff use a mix of email, shared documents, and in-person meetings to coordinate programs. Documentation practices are informal and vary by staff member."

    # Workflow pain points
    pain_points = []
    if has_doc:
        pain_points.append("Manual documentation is time-consuming and inconsistent across staff members.")
    if has_repetitive:
        pain_points.append("Repetitive data entry tasks consume staff time that could be spent on direct service.")
    if has_follow:
        pain_points.append("Follow-up tracking is ad-hoc — items are easily missed with no centralized system.")
    if has_pain:
        pain_points.append("Staff report frustration with the current process but lack time to redesign it.")
    if has_staff and ("capacity" in notes_lower or "stretch" in notes_lower or "overwhelm" in notes_lower):
        pain_points.append("Staff capacity is a recurring constraint — there is no buffer for process improvement work.")
    if has_community and not has_pain:
        pain_points.append("Community engagement tracking is fragmented — no single view of outreach activities.")
    if has_policy:
        pain_points.append("Policy compliance requirements add overhead to every step of the workflow.")
    if not pain_points:
        pain_points.append("No specific pain points documented — further discussion needed to identify workflow friction.")

    # Repetitive tasks identified
    repetitive_tasks = []
    if has_doc:
        repetitive_tasks.append("Transcribing or summarizing meeting notes")
        repetitive_tasks.append("Filling out recurring forms or reports")
    if has_email:
        repetitive_tasks.append("Composing and sending follow-up emails")
        repetitive_tasks.append("Manually tracking email responses and status")
    if has_volunteer:
        repetitive_tasks.append("Scheduling and confirming volunteer shifts")
    if has_data:
        repetitive_tasks.append("Data entry from paper or PDF sources into digital systems")
    if has_meeting:
        repetitive_tasks.append("Preparing meeting agendas and distributing minutes")
    if not repetitive_tasks:
        repetitive_tasks.append("General administrative coordination — further observation needed")

    # Information or documents used
    info_sources = []
    if has_doc:
        info_sources.append("Meeting notes and minutes")
        info_sources.append("Reports and program documentation")
    if has_policy:
        info_sources.append("Policy and compliance documents")
    if has_data:
        info_sources.append("Spreadsheets or databases with program data")
    if has_email:
        info_sources.append("Email correspondence and contact lists")
    if has_training:
        info_sources.append("Training materials and workshop guides")
    if has_volunteer:
        info_sources.append("Volunteer schedules and contact information")
    if not info_sources:
        info_sources.append("General organizational documentation — not yet inventoried")

    # Possible AI insertion point
    ai_insertion_points = []
    if has_doc:
        ai_insertion_points.append("AI-assisted meeting note summarization and action item extraction")
    if has_repetitive:
        ai_insertion_points.append("Automated data extraction and report generation from structured inputs")
    if has_email:
        ai_insertion_points.append("AI-drafted follow-up emails and outreach templates with human review")
    if has_follow:
        ai_insertion_points.append("Automated follow-up reminders and status tracking")
    if has_volunteer or has_community:
        ai_insertion_points.append("AI-assisted scheduling and engagement pattern analysis")
    if has_policy:
        ai_insertion_points.append("AI-assisted compliance checking against policy documents")
    if not ai_insertion_points:
        ai_insertion_points.append("General workflow mapping to identify highest-impact AI insertion points")

    # Required human review
    human_review_points = []
    human_review_points.append("All AI-generated summaries must be reviewed by a staff member before saving to records.")
    human_review_points.append("AI-drafted communications must be approved by a human before sending.")
    if has_policy:
        human_review_points.append("Policy compliance decisions require human judgment — AI suggestions are advisory only.")
    if has_staff:
        human_review_points.append("Staff capacity decisions must be made by program leads, not automated.")
    human_review_points.append("Final decisions on workflow changes require human approval.")

    # Missing knowledge or data
    missing_knowledge = []
    if not has_doc:
        missing_knowledge.append("Formal documentation of current workflows is not available — would benefit from a workflow mapping session.")
    if not has_data:
        missing_knowledge.append("Quantitative data on time spent per task is not yet available — time tracking observation could help.")
    if not has_policy:
        missing_knowledge.append("Policy and compliance requirements are not documented in accessible formats.")
    missing_knowledge.append("Staff training needs and digital literacy levels are not fully assessed.")
    if not missing_knowledge:
        missing_knowledge.append("No specific gaps identified — further discussion may reveal undocumented knowledge needs.")

    # Failure cases / exceptions
    failure_cases = []
    if has_follow:
        failure_cases.append({
            "what_failed": "Follow-ups are missed when staff are absent or overwhelmed",
            "why": "No centralized tracking system — relies on individual memory and email inbox",
            "missing_context": "No automated reminders or shared task list",
            "human_review_required": "Follow-up assignments need human judgment on priority and timing",
            "suggested_prevention": "Implement a shared follow-up tracking system with automated reminders and weekly review",
        })
    if has_doc:
        failure_cases.append({
            "what_failed": "Key information from meetings is lost or not shared with relevant staff",
            "why": "No standardized note-taking format or centralized documentation repository",
            "missing_context": "Meeting notes are stored in personal files or emailed to select individuals",
            "human_review_required": "Staff need to decide what information is relevant to share and with whom",
            "suggested_prevention": "Adopt a shared note-taking template and centralized documentation practice with distribution list",
        })
    if has_repetitive:
        failure_cases.append({
            "what_failed": "Manual data entry errors lead to incorrect reports and rework",
            "why": "No validation checks or automated data entry — entirely dependent on human accuracy",
            "missing_context": "No audit trail for data entry — errors are hard to trace",
            "human_review_required": "Data quality checks need human judgment to distinguish genuine errors from edge cases",
            "suggested_prevention": "Introduce input validation, automated data checks, and regular audit reviews",
        })
    if has_policy:
        failure_cases.append({
            "what_failed": "Policy updates are not consistently communicated or applied across the team",
            "why": "Policy changes are shared via email and rely on individual awareness",
            "missing_context": "No centralized policy repository or version control",
            "human_review_required": "Staff need to interpret how policy changes apply to their specific workflows",
            "suggested_prevention": "Maintain a centralized policy repository with change notifications and mandatory review checkpoints",
        })
    if has_staff and "burnout" in notes_lower:
        failure_cases.append({
            "what_failed": "Staff burnout caused by excessive manual administrative workload",
            "why": "No tools to reduce administrative burden — staff spend disproportionate time on documentation and follow-up",
            "missing_context": "Workload distribution across team not tracked",
            "human_review_required": "Workload rebalancing decisions need manager input and staff consultation",
            "suggested_prevention": "Conduct workload assessment and identify top administrative time drains for automation or simplification",
        })
    if not failure_cases:
        failure_cases.append({
            "what_failed": "No specific failure cases documented yet",
            "why": "Interaction notes do not describe past failures or exceptions",
            "missing_context": "Failure mode analysis has not been conducted",
            "human_review_required": "Staff should reflect on past challenges to identify recurring failure patterns",
            "suggested_prevention": "Schedule a retrospective session to document past workflow failures and contributing factors",
        })

    # Reusable workflow insight
    workflow_insights = []
    if has_doc:
        workflow_insights.append("Documentation workflows are a universal pain point across organizations and represent the lowest-barrier entry for AI assistance.")
    if has_repetitive:
        workflow_insights.append("Repetitive administrative tasks are often invisible to leadership — surfacing their time cost is a powerful motivator for change.")
    if has_follow:
        workflow_insights.append("Follow-up consistency is a leading indicator of relationship health — simple tracking improvements can yield outsized relationship benefits.")
    if has_policy:
        workflow_insights.append("Policy compliance workflows are high-risk and high-value targets for AI assistance — but require the most rigorous human oversight.")
    if has_volunteer or has_community:
        workflow_insights.append("Community-facing organizations typically have undocumented workflows that rely heavily on staff relationships — process documentation is a prerequisite for AI adoption.")
    if has_training:
        workflow_insights.append("Organizations that invest in staff training are more likely to adopt AI tools successfully, as they already value skill development.")
    if not workflow_insights:
        workflow_insights.append("Initial workflow mapping conversations reveal organizational readiness patterns that inform pilot design.")

    # Staff concerns about AI adoption
    staff_concerns = []
    if has_staff and ("concern" in notes_lower or "fear" in notes_lower or "worry" in notes_lower):
        staff_concerns.append("Staff may fear AI replaces rather than assists their work — emphasize augmentation, not automation.")
    if has_staff and ("capacity" in notes_lower or "overwhelm" in notes_lower or "workload" in notes_lower):
        staff_concerns.append("Staff already at capacity — any AI initiative must demonstrate time savings, not add overhead.")
    if has_policy:
        staff_concerns.append("Data privacy and confidentiality concerns must be resolved before any pilot begins.")
    if not staff_concerns:
        staff_concerns.append("No specific staff concerns raised — monitor during next interaction.")

    # Evaluation / recognition risks
    evaluation_risks = []
    if "evaluation" in notes_lower or "measure" in notes_lower or "metric" in notes_lower:
        evaluation_risks.append("Unclear how AI-assisted work would be evaluated against current performance criteria.")
    if "recognition" in notes_lower or "credit" in notes_lower or "reward" in notes_lower:
        evaluation_risks.append("Staff may feel AI-assisted outputs do not receive the same recognition as fully manual work.")
    if has_policy:
        evaluation_risks.append("Policy compliance may not account for AI-assisted workflows — evaluation criteria need updating.")
    if not evaluation_risks:
        evaluation_risks.append("No evaluation or recognition risks identified — further discussion may reveal concerns.")

    # Knowledge sharing opportunities
    ks_opportunities = []
    if has_pilot:
        ks_opportunities.append("Share pilot proposal template and lessons learned with other organizations exploring similar AI use cases.")
    if has_doc:
        ks_opportunities.append("Documentation workflow insights could inform a cross-organizational best-practice guide.")
    if has_training:
        ks_opportunities.append("Workshop materials and curriculum could be adapted for other similar organizations.")
    if not ks_opportunities:
        ks_opportunities.append("Initial engagement insights may be useful as a baseline reference for future comparisons.")

    # Training / follow-up needs
    training_needs = []
    if has_training:
        training_needs.append("Organization has expressed interest in AI literacy training — schedule foundational workshop.")
    if has_staff and ("ready" in notes_lower or "skill" in notes_lower or "digital" in notes_lower):
        training_needs.append("Staff digital literacy assessment recommended before deploying any AI tool.")
    if has_pilot:
        training_needs.append("Pilot participants will need workflow-specific training before launch.")
    if not training_needs:
        training_needs.append("No specific training needs identified — monitor as engagement deepens.")

    # Adoption safeguards
    adoption_safeguards = []
    if has_policy:
        adoption_safeguards.append("All AI-generated content must be reviewed by a designated staff member before use or distribution.")
    if has_staff:
        adoption_safeguards.append("Staff must be consulted before any workflow change — adoption is voluntary and human-led.")
    if has_pilot:
        adoption_safeguards.append("Pilots should start with a small, low-risk scope with clear success criteria and human oversight checkpoints.")
    adoption_safeguards.append("AI recommendations are advisory — all relationship and workflow decisions require human judgment.")
    if not [s for s in adoption_safeguards if s]:
        adoption_safeguards.append("Standard human oversight safeguards should be put in place before any AI tool deployment.")

    # Human system notes (overall assessment)
    human_system_notes_parts = []
    if has_staff:
        human_system_notes_parts.append("Staff engagement and capacity are key factors in adoption readiness.")
    if has_training:
        human_system_notes_parts.append("Training investment indicates organizational commitment to skill development.")
    if has_policy:
        human_system_notes_parts.append("Policy compliance requirements will shape how AI tools are integrated.")
    if has_pilot:
        human_system_notes_parts.append("Pilot interest suggests organizational openness to experimentation with appropriate safeguards.")
    human_system_notes = " ".join(human_system_notes_parts) if human_system_notes_parts else "Human system assessment not yet available — further interaction needed."

    suggested_wf_tags = set()
    if has_doc:
        suggested_wf_tags.add("documentation")
    if has_repetitive:
        suggested_wf_tags.add("workflow-improvement")
    if has_follow:
        suggested_wf_tags.add("follow-up")
    if has_policy:
        suggested_wf_tags.add("human-review")
    if has_training:
        suggested_wf_tags.add("training-need")
    if has_pain:
        suggested_wf_tags.add("evaluation-concern")
    if has_pilot:
        suggested_wf_tags.add("pilot-idea")
    if has_staff and ("concern" in notes_lower or "fear" in notes_lower):
        suggested_wf_tags.add("staff-concern")
    if "knowledge" in notes_lower or "share" in notes_lower:
        suggested_wf_tags.add("knowledge-sharing")
    if not suggested_wf_tags:
        suggested_wf_tags.add("follow-up")

    return {
        "current_workflow": current_workflow,
        "workflow_pain_points": pain_points,
        "repetitive_tasks_identified": repetitive_tasks,
        "information_or_documents_used": info_sources,
        "possible_ai_insertion_points": ai_insertion_points,
        "required_human_review": human_review_points,
        "missing_knowledge_or_data": missing_knowledge,
        "failure_cases_or_exceptions": failure_cases,
        "reusable_workflow_insights": workflow_insights,
        "workflow_tags": sorted(suggested_wf_tags),
        "staff_concerns": staff_concerns,
        "evaluation_or_recognition_risks": evaluation_risks,
        "knowledge_sharing_opportunities": ks_opportunities,
        "training_or_followup_needs": training_needs,
        "adoption_safeguards": adoption_safeguards,
        "human_system_notes": human_system_notes,
    }


def summarize_interaction_notes(notes: str, interaction_type: str) -> Dict[str, Any]:
    from datetime import date, timedelta
    from .tasks import suggest_tasks_from_interaction

    notes_lower = notes.lower()
    has_pilot = "pilot" in notes_lower
    has_follow_up = "follow-up" in notes_lower or "follow up" in notes_lower
    has_meeting = "meeting" in notes_lower
    has_workshop = "workshop" in notes_lower or "training" in notes_lower or "literacy" in notes_lower

    if has_pilot:
        suggested_email = "Pilot Proposal Follow-Up"
        follow_up = "Share pilot proposal and schedule review meeting."
    elif has_follow_up:
        suggested_email = "Follow-Up"
        follow_up = "Send follow-up summary and confirm next steps."
    elif has_meeting:
        suggested_email = "Meeting Recap"
        follow_up = "Send meeting recap and confirm action items."
    elif has_workshop:
        suggested_email = "Workshop Planning"
        follow_up = "Share workshop outline and confirm logistics."
    else:
        suggested_email = "General Check-In"
        follow_up = "Follow up within one week."

    today = date.today()
    suggested_follow_up_date = (today + timedelta(days=14)).isoformat()

    suggested_tasks = suggest_tasks_from_interaction(notes, interaction_type, 0, 0)

    workflow_fields = _mock_extract_workflow_fields(notes)

    return {
        "summary": f"Mock AI summary of {interaction_type.lower()} notes.",
        "key_discussion_points": [
            "AI workflow potential discussed",
            "Documentation challenges identified",
            "Follow-up timeline agreed upon",
        ],
        "decisions": [
            "Schedule follow-up meeting in two weeks",
            "Prepare a single pilot proposal for review",
        ],
        "action_items": [
            "Send meeting summary to stakeholders",
            "Prepare pilot proposal document",
            "Identify key staff for pilot participation",
        ],
        "risks_or_concerns": [
            "Staff readiness for new tools",
            "Data privacy considerations",
            "Change management effort may be underestimated",
        ],
        "lessons_learned": _mock_extract_lessons(notes),
        "reusable_insights": _mock_extract_insights(notes),
        "staff_concerns_or_adoption_concerns": [
            concern for concern in [
                "Staff may fear AI replaces rather than assists their work — emphasize augmentation, not automation.",
                "Data privacy and patron confidentiality must be addressed before any pilot begins.",
                "Change management effort is often underestimated — budget time for staff transition and training.",
            ] if any(kw in notes_lower for kw in ["staff", "concern", "ready", "adoption", "change"])
        ] or [
            "No specific adoption concerns raised — monitor during next interaction.",
        ],
        "human_judgment_points": _mock_extract_human_judgment_points(notes),
        "knowledge_sharing_opportunities": _mock_extract_knowledge_sharing(notes),
        "playbook_candidates": _mock_extract_playbook_candidates(notes),
        "recommended_follow_up": follow_up,
        "suggested_follow_up_date": suggested_follow_up_date,
        "suggested_next_email_type": suggested_email,
        "suggested_tags": _mock_suggest_tags(notes),
        "follow_up_tasks": suggested_tasks,
        "current_workflow": workflow_fields["current_workflow"],
        "workflow_pain_points": workflow_fields["workflow_pain_points"],
        "repetitive_tasks_identified": workflow_fields["repetitive_tasks_identified"],
        "information_or_documents_used": workflow_fields["information_or_documents_used"],
        "possible_ai_insertion_points": workflow_fields["possible_ai_insertion_points"],
        "required_human_review": workflow_fields["required_human_review"],
        "missing_knowledge_or_data": workflow_fields["missing_knowledge_or_data"],
        "failure_cases_or_exceptions": workflow_fields["failure_cases_or_exceptions"],
        "reusable_workflow_insights": workflow_fields["reusable_workflow_insights"],
        "workflow_tags": workflow_fields["workflow_tags"],
        "staff_concerns": workflow_fields["staff_concerns"],
        "evaluation_or_recognition_risks": workflow_fields["evaluation_or_recognition_risks"],
        "knowledge_sharing_opportunities": workflow_fields["knowledge_sharing_opportunities"],
        "training_or_followup_needs": workflow_fields["training_or_followup_needs"],
        "adoption_safeguards": workflow_fields["adoption_safeguards"],
        "human_system_notes": workflow_fields["human_system_notes"],
    }


def generate_knowledge_summary(org: Dict[str, Any], interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    from .tasks import get_tasks_for_org
    from .outbox import read_outbox
    from .interaction_summaries import get_summaries_for_org

    org_id = org["id"]
    tasks = get_tasks_for_org(org_id)
    all_drafts = read_outbox()
    org_drafts = [d for d in all_drafts if d.get("organization_id") == org_id]

    total_interactions = len(interactions)
    completed_tasks = [t for t in tasks if t.get("status") == "Completed"]
    open_tasks = [t for t in tasks if t.get("status") == "Open"]

    if not interactions:
        return {
            "relationship_status": "No recorded interactions yet. No relationship established.",
            "main_interests": "Not yet identified from interactions.",
            "known_concerns": "Not yet identified from interactions.",
            "previous_outreach_attempts": "None recorded.",
            "current_opportunities": "See AI Opportunity Analysis for detailed suggestions.",
            "active_opportunities": [],
            "completed_follow_ups": len(completed_tasks),
            "recommended_next_step": "Schedule an introductory conversation to learn about their needs.",
            "interaction_history": [],
            "follow_up_task_history": [],
            "draft_history": [],
            "timeline_events": [],
            "main_workflow_opportunities": [],
            "repeated_workflow_pain_points": [],
            "important_knowledge_sources": [],
            "known_failure_cases_or_exceptions": [],
            "human_review_requirements": [],
            "best_candidate_workflow_for_ai": "Not yet identified — run AI Note Summary on an interaction first.",
        }

    types = [i["interaction_type"] for i in interactions]

    interaction_hist = [
        f"{i.get('date','')} — {i.get('title','')} ({i.get('interaction_type','')})"
        for i in sorted(interactions, key=lambda x: x.get("date", ""), reverse=True)[:5]
    ]

    task_hist = [
        f"{'Completed' if t.get('status') == 'Completed' else 'Open'}: {t.get('title','')}"
        for t in tasks
    ]

    draft_hist = [
        f"Draft: {d.get('subject','')[:60]}"
        for d in sorted(org_drafts, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    ]

    timeline_events_list = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for t in sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:3]:
        timeline_events_list.append(
            f"{t.get('created_at','')} — {'Completed' if t.get('status') == 'Completed' else 'Open'} task: {t.get('title','')}"
        )
    for d in sorted(org_drafts, key=lambda x: x.get("created_at", ""), reverse=True)[:3]:
        timeline_events_list.append(
            f"{d.get('created_at','')} — Draft saved: {d.get('subject','')[:50]}"
        )

    summaries = get_summaries_for_org(org_id)
    all_lessons = []
    all_insights = []
    all_concerns = []
    all_playbooks = []
    all_knowledge_sharing = []
    all_workflows = []
    all_pain_points = []
    all_ai_points = []
    all_human_review_points = []
    all_failure_cases = []
    all_knowledge_sources_list = []
    all_staff_concerns = []
    all_eval_risks = []
    all_ks_opportunities = []
    all_training_needs = []
    all_adoption_safeguards = []
    all_human_system_notes = []
    for s in summaries:
        all_lessons.extend([li.get("title", "") for li in (s.get("lessons_learned") or [])])
        all_insights.extend(s.get("reusable_insights") or [])
        all_concerns.extend(s.get("staff_concerns_or_adoption_concerns") or [])
        all_playbooks.extend([pb.get("title", "") for pb in (s.get("playbook_candidates") or [])])
        all_knowledge_sharing.extend(s.get("knowledge_sharing_opportunities") or [])
        wf = s.get("current_workflow")
        if wf:
            all_workflows.append(wf)
        all_pain_points.extend(s.get("workflow_pain_points") or [])
        all_ai_points.extend(s.get("possible_ai_insertion_points") or [])
        all_human_review_points.extend(s.get("required_human_review") or [])
        all_failure_cases.extend(
            f"{f.get('what_failed','')} — {f.get('suggested_prevention','')}"
            for f in (s.get("failure_cases_or_exceptions") or [])
        )
        all_knowledge_sources_list.extend(s.get("information_or_documents_used") or [])
        all_staff_concerns.extend(s.get("staff_concerns") or [])
        all_eval_risks.extend(s.get("evaluation_or_recognition_risks") or [])
        all_ks_opportunities.extend(s.get("knowledge_sharing_opportunities") or [])
        all_training_needs.extend(s.get("training_or_followup_needs") or [])
        all_adoption_safeguards.extend(s.get("adoption_safeguards") or [])
        hn = s.get("human_system_notes")
        if hn:
            all_human_system_notes.append(hn)

    return {
        "relationship_status": f"{total_interactions} interaction(s) recorded. Types: {', '.join(sorted(set(types)))}.",
        "main_interests": "AI literacy support and workflow improvement based on interaction notes.",
        "known_concerns": "Staff readiness and data privacy considerations noted in discussions.",
        "previous_outreach_attempts": f"{total_interactions} interaction(s) on file including {', '.join(sorted(set(types)))}.",
        "current_opportunities": "See AI Opportunity Analysis for detailed suggestions.",
        "active_opportunities": [t.get("title", "") for t in open_tasks[:3]],
        "completed_follow_ups": len(completed_tasks),
        "recommended_next_step": "Follow up on action items from the most recent interaction." if interactions else "See AI Opportunity Analysis for suggestions.",
        "interaction_history": interaction_hist,
        "follow_up_task_history": task_hist,
        "draft_history": draft_hist,
        "timeline_events": timeline_events_list[:5],
        "main_lessons_learned": all_lessons[:5],
        "recurring_concerns": all_concerns[:5],
        "reusable_outreach_insights": all_insights[:5],
        "knowledge_sharing_opportunities": all_knowledge_sharing[:5],
        "playbook_candidates": all_playbooks[:5],
        "recommended_knowledge_item_to_preserve": all_lessons[0] if all_lessons else all_insights[0] if all_insights else "No knowledge items extracted yet — run AI Note Summary on an interaction first.",
        "main_workflow_opportunities": all_ai_points[:3],
        "repeated_workflow_pain_points": sorted(set(all_pain_points))[:5],
        "important_knowledge_sources": sorted(set(all_knowledge_sources_list))[:5],
        "known_failure_cases_or_exceptions": all_failure_cases[:3],
        "human_review_requirements": sorted(set(all_human_review_points))[:3],
        "best_candidate_workflow_for_ai": all_ai_points[0] if all_ai_points else "Not yet identified — run AI Note Summary on an interaction.",
        "staff_concerns": sorted(set(all_staff_concerns))[:5],
        "evaluation_or_recognition_risks": sorted(set(all_eval_risks))[:5],
        "knowledge_sharing_opportunities": sorted(set(all_ks_opportunities))[:5],
        "training_or_followup_needs": sorted(set(all_training_needs))[:5],
        "adoption_safeguards": sorted(set(all_adoption_safeguards))[:5],
        "human_system_notes": all_human_system_notes[0] if all_human_system_notes else "No human system assessment available.",
    }


def generate_readiness_assessment(
    org: Dict[str, Any],
    interactions: List[Dict[str, Any]],
    opportunities: Dict[str, Any] | None,
) -> Dict[str, Any]:
    name = org.get("name", "")
    category = org.get("category", "")
    notes = org.get("mission_notes", "")
    pain_points = org.get("pain_points", [])
    status = org.get("status", "")
    contact_email = org.get("contact_email", "")
    phone_number = org.get("phone_number", "")

    all_notes_text = " ".join([
        notes,
        *[i.get("notes", "") for i in interactions],
        *[i.get("outcome", "") for i in interactions],
    ]).lower()
    num_interactions = len(interactions)
    opp_count = len(opportunities.get("opportunities", [])) if opportunities else 0

    has_pilot_mention = "pilot" in all_notes_text
    has_documentation = any(
        w in all_notes_text for w in ["documentation", "docs", "notes", "records", "reports"]
    )
    has_repetitive = any(
        w in all_notes_text for w in ["repetitive", "repeated", "administrative", "routine", "manual"]
    )
    has_staff_concern = any(
        w in all_notes_text for w in ["staff capacity", "stretched", "overwhelmed", "staff readiness", "training"]
    )
    has_digital = any(
        w in all_notes_text for w in ["digital", "technology", "tech", "computer", "software", "online"]
    )

    # --- Category scores ---
    def _clamp(v: int) -> int:
        return max(0, min(20, v))

    # 1. Workflow Repetition (0-20)
    wr_score = 6
    wr_explain = "Limited evidence of repetitive workflows in available data."
    if has_repetitive:
        wr_score = 16
        wr_explain = "Interaction notes reference repetitive or administrative tasks — strong fit for AI-assisted workflow improvement."
    elif has_documentation:
        wr_score = 12
        wr_explain = "Documentation and note-taking appear to be part of their workflow. Some repetition likely."
    if num_interactions >= 3:
        wr_score = min(20, wr_score + 3)
        wr_explain += " Multiple interactions suggest ongoing engagement with recurring coordination needs."
    wr_score = _clamp(wr_score)

    # 2. Documentation Maturity (0-20)
    dm_score = 5
    dm_explain = "Limited information about documentation practices."
    if has_documentation:
        dm_score = 14
        dm_explain = "Documentation and notes are part of their workflow — a good foundation for AI-assisted summarization."
    if num_interactions >= 2:
        dm_score = min(20, dm_score + 3)
        dm_explain += " Interaction records show structured note-taking practices."
    if has_pilot_mention:
        dm_score = min(20, dm_score + 2)
    dm_score = _clamp(dm_score)

    # 3. Digital Maturity (0-20)
    di_score = 7
    di_explain = "Basic digital presence assumed based on organization type."
    if has_digital:
        di_score = 15
        di_explain = "Digital tools and technology mentioned in discussions — suggests moderate digital maturity."
    if category and any(t in category.lower() for t in ["technology", "digital", "innovation", "hub"]):
        di_score = 18
        di_explain = "Organization type indicates strong digital orientation."
    if num_interactions == 0:
        di_score = max(3, di_score - 3)
        di_explain += " No direct engagement yet to assess actual digital maturity."
    di_score = _clamp(di_score)

    # 4. Staff Capacity Benefit (0-20)
    sc_score = 8
    sc_explain = "Moderate potential for AI to support staff workflows."
    if has_staff_concern:
        sc_score = 17
        sc_explain = "Staff capacity concerns explicitly noted — AI could meaningfully reduce administrative burden."
    if pain_points and len(pain_points) >= 2:
        sc_score = min(20, sc_score + 3)
        sc_explain += " Multiple known pain points suggest high potential value from workflow improvements."
    sc_score = _clamp(sc_score)

    # 5. Low-Risk Pilot Suitability (0-10)
    lr_score = 4
    lr_explain = "Could identify a pilot area with further discussion."
    if has_pilot_mention:
        lr_score = 9
        lr_explain = "Pilot program is already being discussed — strong candidate for a low-risk pilot."
    if num_interactions >= 2 and not has_pilot_mention:
        lr_score = 6
        lr_explain = "Established relationship makes it easier to propose a focused pilot."
    lr_score = max(0, min(10, lr_score))

    # 6. Human Oversight Clarity (0-10)
    ho_score = 5
    ho_explain = "Human oversight requirements have not been explicitly discussed yet."
    if has_staff_concern:
        ho_score = 8
        ho_explain = "Staff readiness concerns have been raised — indicates awareness that change needs human-centered management."
    if "human review" in all_notes_text or "human oversight" in all_notes_text:
        ho_score = 9
        ho_explain = "Human review requirements have been explicitly discussed."
    ho_score = max(0, min(10, ho_score))

    categories = [
        {"name": "Workflow Repetition", "score": wr_score, "max": 20, "explanation": wr_explain},
        {"name": "Documentation Maturity", "score": dm_score, "max": 20, "explanation": dm_explain},
        {"name": "Digital Maturity", "score": di_score, "max": 20, "explanation": di_explain},
        {"name": "Staff Capacity Benefit", "score": sc_score, "max": 20, "explanation": sc_explain},
        {"name": "Low-Risk Pilot Suitability", "score": lr_score, "max": 10, "explanation": lr_explain},
        {"name": "Human Oversight Clarity", "score": ho_score, "max": 10, "explanation": ho_explain},
    ]

    total_score = wr_score + dm_score + di_score + sc_score + lr_score + ho_score

    if total_score >= 67:
        level = "High"
    elif total_score >= 34:
        level = "Moderate"
    else:
        level = "Low"

    # Context used
    context_used = {
        "Organization Name": name,
        "Category": category,
        "Contact Email": contact_email,
        "Phone Number": phone_number or "Not available",
        "Status": status,
        "Pain Points": pain_points,
        "Interaction Count": num_interactions,
        "Pilot Mentioned": has_pilot_mention,
        "Documentation Mentioned": has_documentation,
        "Repetitive Tasks Mentioned": has_repetitive,
        "Staff Capacity Concerns": has_staff_concern,
        "Digital Tools Mentioned": has_digital,
        "AI Opportunities Available": opp_count,
    }

    return {
        "overall_level": level,
        "total_score": total_score,
        "categories": categories,
        "best_starting_use_case": _best_use_case(categories, has_documentation, has_repetitive, has_pilot_mention),
        "why_ready": _why_ready(level, total_score, num_interactions, has_pilot_mention),
        "gaps": _gaps(categories, num_interactions, has_digital),
        "risks_or_concerns": _risks(has_staff_concern, has_pilot_mention, level),
        "recommended_pilot": _recommended_pilot(has_documentation, has_repetitive, has_pilot_mention),
        "human_oversight": _human_oversight(ho_score),
        "suggested_questions": _suggested_questions(has_staff_concern, has_pilot_mention, has_digital, num_interactions),
        "context_used": context_used,
    }


def _best_use_case(categories, has_documentation, has_repetitive, has_pilot_mention):
    if has_pilot_mention:
        return "AI-Assisted Meeting Notes & Follow-Up Automation"
    if has_documentation and has_repetitive:
        return "Documentation Workflow Assistant"
    if has_documentation:
        return "Meeting Notes Summarization & Action Item Extraction"
    return "Introductory AI Literacy Workshop for Staff"


def _why_ready(level, score, num_interactions, has_pilot_mention):
    parts = []
    if level == "High":
        parts.append(f"Overall readiness score of {score}/100 indicates strong alignment with AI adoption opportunities.")
    elif level == "Moderate":
        parts.append(f"Overall readiness score of {score}/100 suggests promising potential with some preparation needed.")
    else:
        parts.append(f"Overall readiness score of {score}/100 indicates foundational exploration is still needed.")

    if num_interactions >= 2:
        parts.append("Established engagement history provides a foundation for moving forward.")
    if has_pilot_mention:
        parts.append("Pilot program has already been discussed, indicating organizational openness.")
    return " ".join(parts)


def _gaps(categories, num_interactions, has_digital):
    gaps = []
    for c in categories:
        if c["score"] <= c["max"] * 0.4:
            gaps.append(f"Low {c['name'].lower()} ({c['score']}/{c['max']}) — {c['explanation']}")
    if num_interactions == 0:
        gaps.append("No direct engagement yet — first meeting needed to assess actual readiness.")
    if not has_digital:
        gaps.append("Digital tool usage not confirmed — understanding their current technology stack is needed.")
    return gaps if gaps else ["No significant gaps identified — organization appears ready for a pilot discussion."]


def _risks(has_staff_concern, has_pilot_mention, level):
    risks = [
        "AI tools must not replace human judgment in public-serving workflows.",
        "Data privacy and patron/staff confidentiality must be addressed before any pilot.",
        "Change management effort may be underestimated — staff need time to adopt new tools.",
    ]
    if has_staff_concern:
        risks.insert(0, "Staff capacity concerns already raised — any AI initiative must reduce burden, not add to it.")
    if level == "Low":
        risks.append("Low readiness suggests starting with awareness-building rather than tool implementation.")
    return risks


def _recommended_pilot(has_documentation, has_repetitive, has_pilot_mention):
    if has_pilot_mention:
        return "AI-Assisted Meeting Notes & Follow-Up Automation"
    if has_documentation and has_repetitive:
        return "Documentation Workflow Assistant"
    if has_documentation:
        return "Meeting Notes Summarization & Action Item Extraction"
    return "Introductory AI Literacy Workshop for Staff"


def _human_oversight(ho_score):
    if ho_score >= 8:
        return "Human oversight requirements are well understood. All AI-generated outputs should be reviewed by a designated staff member before external use. A review workflow should be established before pilot launch."
    return "Human oversight processes should be established before any pilot begins. Designate a staff reviewer for all AI-assisted outputs. Start with low-risk internal use cases only."


def _suggested_questions(has_staff_concern, has_pilot_mention, has_digital, num_interactions):
    questions = [
        "Which specific tasks take up the most staff time each week?",
        "What documentation or follow-up processes feel most repetitive?",
        "How does your team currently handle meeting notes and action items?",
    ]
    if not has_digital:
        questions.append("What digital tools does your team currently use for daily workflows?")
    if has_staff_concern:
        questions.append("If AI could save 5 hours of staff time per week, where would you reinvest that time?")
    if has_pilot_mention:
        questions.append("What would a successful pilot look like from your perspective?")
    return questions
