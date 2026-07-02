from typing import Dict, List, Any
from datetime import date, timedelta
from pathlib import Path
import json

from .interactions import get_all_interactions, get_interactions_for_org
from .outbox import read_outbox
from .ai_mock import summarize_organization, generate_readiness_assessment, discover_opportunities
from .outreach_recommendation import compute_outreach_recommendation
from .tasks import get_all_tasks, get_tasks_for_org
from .knowledge import compute_knowledge_analytics

ATTACHMENTS_DIR = Path(__file__).resolve().parents[1] / "data" / "attachments"
ATTACHMENTS_INDEX = ATTACHMENTS_DIR / "_index.json"


def _read_attachment_index() -> Dict[str, List[Dict]]:
    try:
        with open(ATTACHMENTS_INDEX) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def compute_analytics_summary(crm) -> Dict[str, Any]:
    orgs = crm.list_organizations()
    interactions = get_all_interactions()
    drafts = read_outbox()
    today = date.today()
    today_str = today.isoformat()
    week_end = (today + timedelta(days=7)).isoformat()

    org_id_to_name = {o["id"]: o["name"] for o in orgs}

    total_orgs = len(orgs)
    total_interactions = len(interactions)
    total_drafts = len(drafts)

    follow_ups_due = sum(
        1 for i in interactions
        if i.get("follow_up_date") and i["follow_up_date"] >= today_str
    )

    readiness_entries: List[Dict] = []
    high_priority_count = 0
    priority_entries: List[Dict] = []
    priority_next_actions: Dict[str, int] = {}
    high_priority_without_follow_up = 0

    for org in orgs:
        org_id = org["id"]
        org_interactions = [
            i for i in interactions
            if i.get("organization_id") == org_id
        ]
        org_interactions.sort(key=lambda x: x.get("date", ""), reverse=True)

        ai_summary = summarize_organization(org)
        if ai_summary.get("outreach_priority") == "High":
            high_priority_count += 1

        opportunities = discover_opportunities(org)
        assessment = generate_readiness_assessment(org, org_interactions, opportunities)

        readiness_entries.append({
            "org_id": org_id,
            "org_name": org["name"],
            "score": assessment.get("total_score", 0),
            "level": assessment.get("overall_level", "Unknown"),
        })

        rec = compute_outreach_recommendation(org)
        priority_entries.append({
            "org_id": org_id,
            "org_name": org["name"],
            "priority": rec["outreach_priority"],
            "priority_score": rec["priority_score"],
            "next_action": rec["recommended_next_action"],
            "follow_up_date": rec["recommended_follow_up_date"],
        })
        action = rec["recommended_next_action"]
        priority_next_actions[action] = priority_next_actions.get(action, 0) + 1

        if rec["outreach_priority"] == "High" and not rec.get("recommended_follow_up_date"):
            high_priority_without_follow_up += 1

    avg_score = (
        round(sum(r["score"] for r in readiness_entries) / len(readiness_entries), 1)
        if readiness_entries else 0
    )

    low_count = sum(1 for r in readiness_entries if r["level"] == "Low")
    mod_count = sum(1 for r in readiness_entries if r["level"] == "Moderate")
    high_level_count = sum(1 for r in readiness_entries if r["level"] == "High")
    top_5 = sorted(readiness_entries, key=lambda r: r["score"], reverse=True)[:5]

    status_counts: Dict[str, int] = {}
    for org in orgs:
        s = org.get("status", "Not Contacted")
        status_counts[s] = status_counts.get(s, 0) + 1
    status_pipeline = dict(sorted(status_counts.items(), key=lambda x: -x[1]))

    type_counts: Dict[str, int] = {}
    program_counts: Dict[str, int] = {}
    for org in orgs:
        cat = org.get("category", "Unknown")
        type_counts[cat] = type_counts.get(cat, 0) + 1
        pa = org.get("program_area")
        if pa:
            program_counts[pa] = program_counts.get(pa, 0) + 1
    type_breakdown = dict(sorted(type_counts.items(), key=lambda x: -x[1]))
    program_breakdown = dict(sorted(program_counts.items(), key=lambda x: -x[1]))

    overdue: List[Dict] = []
    due_today_list: List[Dict] = []
    due_this_week_list: List[Dict] = []
    no_next_action_count = 0

    for i in interactions:
        fud = i.get("follow_up_date")
        if fud:
            if fud < today_str:
                overdue.append(i)
            elif fud == today_str:
                due_today_list.append(i)
            elif fud <= week_end:
                due_this_week_list.append(i)

        if not i.get("next_action"):
            no_next_action_count += 1

    drafts_by_org: Dict[str, int] = {}
    for d in drafts:
        oid = d.get("organization_id")
        oname = org_id_to_name.get(oid, "Unknown")
        drafts_by_org[oname] = drafts_by_org.get(oname, 0) + 1

    att_index = _read_attachment_index()
    drafts_with_attachments = sum(
        1 for d in drafts if str(d.get("id")) in att_index
    )

    most_recent = sorted(drafts, key=lambda d: d.get("id", 0), reverse=True)[:5]
    most_recent_safe = [
        {
            "id": d["id"],
            "to": d.get("to", ""),
            "subject": d.get("subject", ""),
            "organization_id": d.get("organization_id"),
        }
        for d in most_recent
    ]

    priority_by_level: Dict[str, int] = {}
    for p in priority_entries:
        lvl = p["priority"]
        priority_by_level[lvl] = priority_by_level.get(lvl, 0) + 1

    avg_priority_score = (
        round(sum(p["priority_score"] for p in priority_entries) / len(priority_entries), 1)
        if priority_entries else 0
    )

    top_next_actions = dict(sorted(priority_next_actions.items(), key=lambda x: -x[1])[:5])

    follow_ups_due_by_priority: Dict[str, int] = {}
    for p in priority_entries:
        if p.get("follow_up_date") and p["follow_up_date"] >= today_str:
            lvl = p["priority"]
            follow_ups_due_by_priority[lvl] = follow_ups_due_by_priority.get(lvl, 0) + 1

    all_tasks = get_all_tasks()
    open_tasks = [t for t in all_tasks if t.get("status") == "Open"]
    completed_tasks = [t for t in all_tasks if t.get("status") == "Completed"]
    overdue_tasks = [t for t in open_tasks if t.get("due_date") and t["due_date"] < today_str]
    tasks_due_this_week = [t for t in open_tasks if t.get("due_date") and today_str <= t["due_date"] <= week_end]
    high_priority_open_tasks = [t for t in open_tasks if t.get("priority") == "High"]

    phase3 = compute_knowledge_analytics(crm)

    return {
        "overview_metrics": {
            "total_organizations": total_orgs,
            "organizations_from_research_intake": None,
            "organizations_from_discovery": None,
            "total_interactions": total_interactions,
            "drafts_in_outbox": total_drafts,
            "follow_ups_due": follow_ups_due,
            "average_readiness_score": avg_score,
            "high_priority_targets": high_priority_count,
            "average_priority_score": avg_priority_score,
        },
        "outreach_pipeline": status_pipeline,
        "organization_breakdown": {
            "by_type": type_breakdown,
            "by_program_area": program_breakdown,
        },
        "ai_readiness": {
            "average_score": avg_score,
            "low_count": low_count,
            "moderate_count": mod_count,
            "high_count": high_level_count,
            "top_5": top_5,
            "organizations_missing_readiness": [],
        },
        "follow_up_workload": {
            "due_today": len(due_today_list),
            "due_this_week": len(due_this_week_list),
            "overdue": len(overdue),
            "orgs_with_no_next_action": no_next_action_count,
            "open_tasks": len(open_tasks),
            "completed_tasks": len(completed_tasks),
            "overdue_tasks": len(overdue_tasks),
            "tasks_due_this_week": len(tasks_due_this_week),
            "high_priority_open_tasks": len(high_priority_open_tasks),
        },
        "draft_activity": {
            "total_drafts": total_drafts,
            "drafts_by_organization": drafts_by_org,
            "drafts_with_attachments_count": drafts_with_attachments,
            "most_recent_drafts": most_recent_safe,
        },
        "priority_analytics": {
            "by_priority": priority_by_level,
            "high_priority_without_follow_up": high_priority_without_follow_up,
            "average_priority_score": avg_priority_score,
            "top_next_actions": top_next_actions,
            "follow_ups_due_by_priority": follow_ups_due_by_priority,
        },
        "organizational_knowledge": {
            "total_knowledge_items": phase3["total_knowledge_items"],
            "organizations_with_interaction_history": phase3["organizations_with_interaction_history"],
            "organizations_without_interaction_history": phase3["organizations_without_interaction_history"],
            "most_common_tags": phase3["most_common_tags"],
            "recent_knowledge_activity": phase3["recent_knowledge_activity"],
            "workflow_opportunities_identified": phase3.get("workflow_opportunities_identified", 0),
            "organizations_with_workflow_opportunities": phase3.get("organizations_with_workflow_opportunities", 0),
            "organizations_missing_knowledge_source_notes": phase3.get("organizations_missing_knowledge_source_notes", 0),
            "failure_cases_recorded": phase3.get("failure_cases_recorded", 0),
            "candidate_pilot_workflows": phase3.get("candidate_pilot_workflows", 0),
            "adoption_risk_notes_recorded": phase3.get("adoption_risk_notes_recorded", 0),
            "organizations_with_adoption_risk_notes": phase3.get("organizations_with_adoption_risk_notes", 0),
            "staff_concern_notes": phase3.get("staff_concern_notes", 0),
            "evaluation_risk_notes": phase3.get("evaluation_risk_notes", 0),
            "high_severity_adoption_risks": phase3.get("high_severity_adoption_risks", 0),
            "workflow_opps_with_human_review": phase3.get("workflow_opps_with_human_review", 0),
        },
    }
