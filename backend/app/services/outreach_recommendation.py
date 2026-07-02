from typing import Dict, List, Any, Optional
from datetime import date, timedelta

from .ai_mock import (
    summarize_organization,
    generate_next_best_email,
    generate_readiness_assessment,
    discover_opportunities,
)
from .interactions import get_all_interactions
from .outbox import read_outbox
from .tasks import get_tasks_for_org


def _priority_level(score: int) -> str:
    if score >= 67:
        return "High"
    if score >= 34:
        return "Medium"
    return "Low"


def _compute_priority_score(
    org: Dict,
    org_interactions: List[Dict],
    readiness_score: int,
    ai_summary_score: int,
) -> int:
    base = round(readiness_score * 0.30)
    status = org.get("status", "")
    status_scores = {
        "Pilot Discussion": 20,
        "Draft Ready": 18,
        "Meeting Scheduled": 16,
        "After Meeting": 14,
        "Waiting Reply": 14,
        "Active Conversation": 12,
        "Follow-Up Needed": 12,
        "Not Contacted": 10,
        "Researching": 8,
        "Research Approved": 8,
        "Completed": 6,
    }
    status_score = status_scores.get(status, 10)

    recent = org_interactions[0] if org_interactions else None
    if recent:
        try:
            d = recent.get("date", "")
            parts = d.split("-")
            d_obj = date(int(parts[0]), int(parts[1]), int(parts[2]))
            days_ago = (date.today() - d_obj).days
            if days_ago <= 7:
                recency_score = 25
            elif days_ago <= 30:
                recency_score = 20
            elif days_ago <= 90:
                recency_score = 12
            else:
                recency_score = 5
        except (IndexError, ValueError, KeyError):
            recency_score = 10
    else:
        recency_score = 0

    pain_points = org.get("pain_points", [])
    pain_score = min(15, len(pain_points) * 5)

    data_score = 0
    if org.get("contact_email"):
        data_score += 3
    if org.get("contact_name"):
        data_score += 2
    if org.get("phone_number"):
        data_score += 2
    if org.get("mission_notes"):
        data_score += 3

    score = base + status_score + recency_score + pain_score + data_score
    return min(100, max(0, score))


def _determine_next_action(org: Dict, org_interactions: List[Dict]) -> str:
    status = org.get("status", "")
    m = status.lower()

    if "not contacted" in m:
        return "Prepare initial outreach email"
    if "draft ready" in m:
        return "Review draft and save final version to outbox"
    if "waiting reply" in m or "follow-up needed" in m:
        if org_interactions:
            recent = org_interactions[0]
            try:
                d = recent.get("date", "")
                parts = d.split("-")
                d_obj = date(int(parts[0]), int(parts[1]), int(parts[2]))
                if (date.today() - d_obj).days >= 5:
                    return "Send polite follow-up — enough time has passed since last contact"
                else:
                    return "Wait a few more days before sending follow-up"
            except (IndexError, ValueError, KeyError):
                pass
        return "Send polite follow-up"
    if "meeting scheduled" in m:
        return "Prepare meeting agenda and talking points"
    if "after meeting" in m or "meeting completed" in m:
        return "Send recap email and confirm next steps"
    if "pilot" in m:
        return "Draft pilot proposal outline and share with organization"
    if "completed" in m:
        return "Schedule relationship check-in for next quarter"
    if "research" in m:
        return "Complete research and prepare outreach strategy"
    recent = org_interactions[0] if org_interactions else None
    if recent and recent.get("next_action"):
        return recent["next_action"]
    return "Review organization status and determine next step"


def _get_follow_up_date(org_interactions: List[Dict], next_action: str) -> str:
    recent = org_interactions[0] if org_interactions else None
    if recent and recent.get("follow_up_date"):
        return recent["follow_up_date"]
    today = date.today()
    if "pilot" in next_action.lower():
        return (today + timedelta(days=14)).isoformat()
    if "agenda" in next_action.lower() or "recap" in next_action.lower():
        return (today + timedelta(days=7)).isoformat()
    if "follow-up" in next_action.lower():
        return (today + timedelta(days=5)).isoformat()
    if "check-in" in next_action.lower():
        return (today + timedelta(days=90)).isoformat()
    return (today + timedelta(days=14)).isoformat()


def _generate_collaboration_angles(
    org: Dict,
    opportunities: Dict,
) -> List[Dict]:
    category = (org.get("category") or "").lower()
    pain_points = [p.lower() for p in org.get("pain_points", [])]

    all_angles = [
        {
            "title": "Practical AI Literacy Workshop",
            "description": "Hands-on workshop introducing staff to practical AI concepts, prompting skills, and responsible use guidelines tailored to their daily work.",
            "estimated_effort": "Low",
            "expected_value": "High — builds foundational AI awareness across the team",
            "human_oversight": "Workshop facilitator reviews all materials before delivery",
        },
        {
            "title": "Workflow Mapping Session",
            "description": "Collaborative session to map current outreach and documentation workflows, identifying bottlenecks where AI assistance could reduce manual effort.",
            "estimated_effort": "Medium",
            "expected_value": "High — surfaces concrete automation opportunities",
            "human_oversight": "Program lead reviews workflow maps and proposed changes",
        },
        {
            "title": "Staff Documentation Improvement Pilot",
            "description": "Test an AI-assisted documentation workflow where staff dictation or rough notes are turned into structured records with human review before saving.",
            "estimated_effort": "Medium",
            "expected_value": "High — reduces documentation time while maintaining quality",
            "human_oversight": "Supervisor reviews all AI-generated documentation before acceptance",
        },
        {
            "title": "Meeting Summary Workflow Pilot",
            "description": "Pilot an automated meeting summary system that converts rough notes into action items, decisions, and follow-ups with coordinator review.",
            "estimated_effort": "Low",
            "expected_value": "Medium — saves time on note-taking and follow-up tracking",
            "human_oversight": "Meeting coordinator reviews summaries before distribution",
        },
        {
            "title": "Responsible AI Training Session",
            "description": "Training session covering AI risks, bias awareness, privacy considerations, and when human oversight is required for AI-assisted decisions.",
            "estimated_effort": "Medium",
            "expected_value": "Medium — builds responsible AI culture and risk awareness",
            "human_oversight": "Training content reviewed by ethics or compliance team",
        },
        {
            "title": "Community Education Session",
            "description": "Design and deliver a community-facing session on AI literacy tailored to the organization's audience, covering practical uses and limitations.",
            "estimated_effort": "High",
            "expected_value": "High — extends AI literacy to the broader community",
            "human_oversight": "Program manager reviews all public-facing content",
        },
        {
            "title": "Internal Knowledge Base Pilot",
            "description": "Build a small AI-powered internal knowledge base that helps staff find approved policies, program information, and answers to common questions.",
            "estimated_effort": "Medium",
            "expected_value": "High — reduces repetitive questions and search time",
            "human_oversight": "Content owner reviews and approves all knowledge base entries",
        },
        {
            "title": "AI-Assisted Grant Writing Support",
            "description": "Use AI to help draft grant proposals, compile supporting data, and track submission deadlines with human oversight of all final content.",
            "estimated_effort": "Medium",
            "expected_value": "High — accelerates grant writing while maintaining quality",
            "human_oversight": "Grant writer reviews and edits all AI-generated content before submission",
        },
    ]

    if "library" in category or "literacy" in category or "education" in category:
        preferred_indices = [0, 5, 6]
    elif "nonprofit" in category or "community" in category or "support" in category:
        preferred_indices = [0, 1, 7]
    elif "technology" in category or "business" in category or "digital" in category:
        preferred_indices = [0, 3, 6]
    else:
        preferred_indices = [0, 1, 2]

    pain_keywords = {
        "literacy": 0,
        "workshop": 5,
        "documentation": 2,
        "notes": 3,
        "knowledge": 6,
        "training": 4,
        "grant": 7,
        "administrative": 1,
        "repetitive": 1,
    }

    scored = []
    for idx, angle in enumerate(all_angles):
        score = 0
        if idx in preferred_indices:
            score += 3
        for kw, pidx in pain_keywords.items():
            if any(kw in pp for pp in pain_points):
                if pidx == idx:
                    score += 2
        if "High" in angle["expected_value"]:
            score += 1
        scored.append((score, idx, angle))

    scored.sort(key=lambda x: -x[0])
    return [angle for _, _, angle in scored[:3]]


def _generate_reasoning(org: Dict, priority_score: int, next_action: str) -> str:
    status = org.get("status", "")
    pain_count = len(org.get("pain_points", []))
    has_contact = bool(org.get("contact_email"))
    has_interactions = bool(org.get("last_interaction"))

    parts = []
    parts.append(
        f"{org['name']} is currently in '{status}' status "
        f"with a priority score of {priority_score}/100."
    )

    if pain_count > 0:
        parts.append(
            f"The organization has {pain_count} identified pain point(s) "
            f"suggesting readiness for AI-assisted workflow improvements."
        )
    else:
        parts.append("No specific pain points have been recorded yet.")

    if not has_contact:
        parts.append("A contact email is missing — outreach may require alternative channels.")
    if has_interactions:
        parts.append("Previous interactions have been recorded, providing context for personalized outreach.")

    parts.append(f"The recommended next action is: {next_action.lower()}")

    return " ".join(parts)


def _get_risks(org: Dict, readiness: Dict) -> List[str]:
    risks = list(readiness.get("risks_or_concerns", []))
    if not org.get("contact_email"):
        risks.append("No direct contact email available for outreach")
    if not org.get("pain_points"):
        risks.append("No pain points identified — collaboration angle may not resonate")
    if readiness.get("total_score", 0) < 40:
        risks.append("Low AI readiness score suggests the organization may need more foundational preparation")
    return risks


def _get_missing_info(org: Dict) -> List[str]:
    missing = []
    if not org.get("contact_name"):
        missing.append("Contact person name")
    if not org.get("contact_email"):
        missing.append("Contact email address")
    if not org.get("phone_number"):
        missing.append("Phone number")
    if not org.get("mission_notes"):
        missing.append("Organization mission or description notes")
    if len(org.get("pain_points", [])) < 2:
        missing.append("Sufficient pain points or needs documentation")
    return missing


def compute_outreach_recommendation(org: Dict) -> Dict[str, Any]:
    org_id = org["id"]
    org_interactions = [
        i for i in get_all_interactions()
        if i.get("organization_id") == org_id
    ]
    org_interactions.sort(key=lambda x: x.get("date", ""), reverse=True)

    org_outbox = [
        d for d in read_outbox()
        if d.get("organization_id") == org_id
    ]

    tasks = get_tasks_for_org(org_id)
    open_tasks = [t for t in tasks if t.get("status") == "Open"]
    overdue_tasks = [
        t for t in tasks
        if t.get("status") == "Open" and t.get("due_date") and t["due_date"] < date.today().isoformat()
    ]

    ai_summary = summarize_organization(org)
    opportunities = discover_opportunities(org)
    readiness = generate_readiness_assessment(org, org_interactions, opportunities)
    next_best_email = generate_next_best_email(org, org_interactions, ai_summary, org_outbox)

    readiness_score = readiness.get("total_score", 50)
    ai_summary_score = ai_summary.get("ai_readiness_score", 50)

    priority_score = _compute_priority_score(org, org_interactions, readiness_score, ai_summary_score)
    priority = _priority_level(priority_score)

    next_action = _determine_next_action(org, org_interactions)
    if overdue_tasks:
        next_action = f"Attention needed: {overdue_tasks[0]['title']} is overdue. {next_action}"
    elif open_tasks:
        next_action = f"Complete open task: {open_tasks[0]['title']}. {next_action}"
    follow_up_date = _get_follow_up_date(org_interactions, next_action)
    collaboration_angles = _generate_collaboration_angles(org, opportunities)
    reasoning = _generate_reasoning(org, priority_score, next_action)
    risks = _get_risks(org, readiness)
    missing_info = _get_missing_info(org)

    email_type = next_best_email.get("email_type", "General Outreach")
    detected_stage = next_best_email.get("detected_stage", "")

    recent = org_interactions[0] if org_interactions else None
    context_used = {
        "Organization Name": org["name"],
        "Category": org.get("category", ""),
        "CRM Status": org.get("status", ""),
        "Contact Email": org.get("contact_email", "") or "Not available",
        "Phone Number": org.get("phone_number", "") or "Not available",
        "Pain Points": org.get("pain_points", []),
        "Total Interactions": len(org_interactions),
        "Detected Relationship Stage": detected_stage,
        "Most Recent Interaction": f"{recent.get('date','')} — {recent.get('title','')}" if recent else "None",
        "Recent Outcome": recent.get("outcome", "") if recent else "",
        "Next Action from Last Interaction": recent.get("next_action", "") if recent else "",
        "Follow-up Date from Last Interaction": recent.get("follow_up_date", "") if recent else "",
        "AI Readiness Score": readiness_score,
        "AI Readiness Level": readiness.get("overall_level", "N/A"),
        "AI Summary Readiness Score": ai_summary_score,
        "Outreach Priority (AI Summary)": ai_summary.get("outreach_priority", "N/A"),
        "Drafts in Outbox for This Org": len(org_outbox),
        "Detected Email Type": email_type,
        "Open Follow-up Tasks": len(open_tasks),
        "Overdue Follow-up Tasks": len(overdue_tasks),
    }

    return {
        "organization_id": org_id,
        "organization_name": org["name"],
        "outreach_priority": priority,
        "priority_score": priority_score,
        "recommended_next_action": next_action,
        "recommended_follow_up_date": follow_up_date,
        "recommended_email_type": email_type,
        "recommended_collaboration_angles": collaboration_angles,
        "reasoning": reasoning,
        "risks_or_concerns": risks,
        "missing_information": missing_info,
        "context_used": context_used,
    }


def compute_priority_queue(orgs: List[Dict]) -> List[Dict]:
    results = []
    for org in orgs:
        rec = compute_outreach_recommendation(org)
        results.append({
            "id": org["id"],
            "name": org["name"],
            "category": org.get("category", ""),
            "status": org.get("status", ""),
            "outreach_priority": rec["outreach_priority"],
            "priority_score": rec["priority_score"],
            "readiness_score": rec["context_used"]["AI Readiness Score"],
            "readiness_level": rec["context_used"]["AI Readiness Level"],
            "recommended_next_action": rec["recommended_next_action"],
            "recommended_follow_up_date": rec["recommended_follow_up_date"],
            "reasoning": rec["reasoning"],
        })
    results.sort(key=lambda r: r["priority_score"], reverse=True)
    return results
