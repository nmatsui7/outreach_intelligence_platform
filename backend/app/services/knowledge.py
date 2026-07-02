from typing import Dict, List, Any, Optional
from .interactions import get_all_interactions, get_interactions_for_org
from .outbox import read_outbox
from .tasks import get_all_tasks, get_tasks_for_org
from .interaction_summaries import get_summaries_for_org, get_all_summaries
from .workflow import (
    get_workflow_opportunities_for_org,
    get_all_workflow_opportunities,
    get_knowledge_sources_for_org,
    get_all_knowledge_sources,
    get_failure_cases_for_org,
    get_all_failure_cases,
    get_adoption_risk_notes_for_org,
    get_all_adoption_risk_notes,
)


def _safe_date(val: Any) -> str:
    if not val:
        return ""
    if isinstance(val, str):
        return val
    return str(val)


def build_timeline_for_org(org: Dict[str, Any]) -> List[Dict[str, Any]]:
    org_id = org["id"]
    events = []

    created = org.get("created_at", "")
    if created:
        created_display = created.replace(" (backfilled)", "")
        events.append({
            "date": created_display,
            "date_sort": created_display,
            "event_type": "organization_created",
            "title": f"Organization added to CRM",
            "description": f"Status: {org.get('status', 'New')}",
            "source": None,
        })

    interactions = get_interactions_for_org(org_id)
    for intx in interactions:
        events.append({
            "date": _safe_date(intx.get("date", "")),
            "date_sort": _safe_date(intx.get("date", "")),
            "event_type": "interaction",
            "title": intx.get("title", "Untitled interaction"),
            "description": (intx.get("notes", "") or "")[:200],
            "source": f"interaction-{intx.get('id')}",
        })

    tasks = get_tasks_for_org(org_id)
    for task in tasks:
        created_date = task.get("created_at", "")
        if created_date:
            events.append({
                "date": created_date,
                "date_sort": created_date,
                "event_type": "task_created",
                "title": f"Task: {task.get('title', '')}",
                "description": (task.get("description", "") or "")[:200],
                "source": f"task-{task.get('task_id')}",
            })
        if task.get("status") == "Completed" and task.get("updated_at"):
            events.append({
                "date": _safe_date(task.get("updated_at", "")),
                "date_sort": _safe_date(task.get("updated_at", "")),
                "event_type": "task_completed",
                "title": f"Completed: {task.get('title', '')}",
                "description": "",
                "source": f"task-{task.get('task_id')}",
            })

    all_drafts = read_outbox()
    org_drafts = [d for d in all_drafts if d.get("organization_id") == org_id]
    for draft in org_drafts:
        draft_date = draft.get("created_at", "")
        if draft_date:
            events.append({
                "date": _safe_date(draft_date),
                "date_sort": _safe_date(draft_date),
                "event_type": "draft_saved",
                "title": f"Draft: {draft.get('subject', '')[:80]}",
                "description": f"To: {draft.get('to', '')}",
                "source": f"draft-{draft.get('id')}",
            })

    events.sort(key=lambda e: e.get("date_sort", ""))
    return events


def search_knowledge(
    crm,
    q: str = "",
    org_id: Optional[int] = None,
    content_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if not q:
        return []

    q_lower = q.lower().strip()
    results: List[Dict[str, Any]] = []
    orgs = crm.list_organizations()

    for org in orgs:
        if org_id is not None and org["id"] != org_id:
            continue
        oid = org["id"]
        oname = org.get("name", "")

        if content_type in (None, "", "organization"):
            combined = " ".join([
                oname,
                org.get("mission_notes", ""),
                org.get("category", ""),
                org.get("status", ""),
            ]).lower()
            if q_lower in combined:
                excerpt = org.get("mission_notes", "") or org.get("category", "") or ""
                results.append({
                    "content_type": "organization",
                    "organization_id": oid,
                    "organization_name": oname,
                    "title": oname,
                    "excerpt": excerpt[:300],
                    "date": org.get("created_at", "").replace(" (backfilled)", ""),
                    "link": f"/?org={oid}",
                })
                if content_type == "organization":
                    continue

        if content_type in (None, "", "interaction"):
            for intx in get_interactions_for_org(oid):
                combined = " ".join([
                    intx.get("title", ""),
                    intx.get("notes", ""),
                    intx.get("outcome", ""),
                    intx.get("next_action", ""),
                ]).lower()
                if q_lower in combined:
                    excerpt = intx.get("notes", "") or intx.get("outcome", "") or ""
                    results.append({
                        "content_type": "interaction",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Interaction: {intx.get('title', '')} ({intx.get('interaction_type', '')})",
                        "excerpt": excerpt[:300],
                        "date": _safe_date(intx.get("date", "")),
                        "link": f"/?org={oid}",
                    })

        if content_type in (None, "", "task"):
            for task in get_tasks_for_org(oid):
                combined = f"{task.get('title', '')} {task.get('description', '')}"
                if q_lower in combined.lower():
                    results.append({
                        "content_type": "task",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Task: {task.get('title', '')}",
                        "excerpt": (task.get("description", "") or "")[:300],
                        "date": _safe_date(task.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

        if content_type in (None, "", "draft"):
            all_drafts = read_outbox()
            for draft in all_drafts:
                if draft.get("organization_id") != oid:
                    continue
                combined = f"{draft.get('subject', '')} {draft.get('body', '')}"
                if q_lower in combined.lower():
                    results.append({
                        "content_type": "draft",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Draft: {draft.get('subject', '')[:100]}",
                        "excerpt": (draft.get("body", "") or "")[:300],
                        "date": _safe_date(draft.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

        # Search interaction summary content (lessons, insights, playbooks, etc.)
        if content_type in (None, "", "lesson", "insight", "playbook"):
            for s in get_summaries_for_org(oid):
                intx = next((i for i in get_interactions_for_org(oid) if i["id"] == s.get("interaction_id")), None)
                intx_title = intx.get("title", "") if intx else ""
                intx_date = _safe_date(intx.get("date", "")) if intx else ""
                summary_text = " ".join([
                    str(s.get("lessons_learned", "")),
                    str(s.get("reusable_insights", "")),
                    str(s.get("staff_concerns_or_adoption_concerns", "")),
                    str(s.get("human_judgment_points", "")),
                    str(s.get("knowledge_sharing_opportunities", "")),
                    str(s.get("playbook_candidates", "")),
                    " ".join(s.get("suggested_tags") or []),
                ]).lower()
                if not summary_text or q_lower not in summary_text:
                    continue

                ct = content_type if content_type and content_type in ("lesson", "insight", "playbook") else "lesson"

                excerpt_parts = []
                for lesson in (s.get("lessons_learned") or []):
                    if q_lower in (lesson.get("title", "") + lesson.get("description", "")).lower():
                        excerpt_parts.append(lesson.get("description", ""))
                for insight in (s.get("reusable_insights") or []):
                    if q_lower in insight.lower():
                        excerpt_parts.append(insight)
                for pb in (s.get("playbook_candidates") or []):
                    if q_lower in (pb.get("title", "") + pb.get("suggested_process", "")).lower():
                        excerpt_parts.append(pb.get("suggested_process", ""))

                excerpt = excerpt_parts[0][:300] if excerpt_parts else summary_text[:300]

                label_map = {"lesson": "Lesson Learned", "insight": "Reusable Insight", "playbook": "Playbook Candidate"}
                results.append({
                    "content_type": ct,
                    "organization_id": oid,
                    "organization_name": oname,
                    "title": f"{label_map.get(ct, 'Knowledge')}: {intx_title}",
                    "excerpt": excerpt,
                    "date": intx_date,
                    "link": f"/?org={oid}",
                })

        # Search workflow opportunities
        if content_type in (None, "", "workflow-opportunity", "workflow"):
            for opp in get_workflow_opportunities_for_org(oid):
                combined = " ".join([
                    opp.get("title", ""),
                    opp.get("current_process", ""),
                    opp.get("pain_point", ""),
                    opp.get("possible_ai_support", ""),
                ]).lower()
                if q_lower in combined:
                    excerpt = opp.get("pain_point", "") or opp.get("current_process", "") or ""
                    results.append({
                        "content_type": "workflow-opportunity",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Workflow Opp: {opp.get('title', '')[:80]}",
                        "excerpt": excerpt[:300],
                        "date": _safe_date(opp.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

        # Search knowledge sources
        if content_type in (None, "", "knowledge-source", "source"):
            for ks in get_knowledge_sources_for_org(oid):
                combined = " ".join([
                    ks.get("name", ""),
                    ks.get("source_type", ""),
                    ks.get("description", ""),
                ]).lower()
                if q_lower in combined:
                    results.append({
                        "content_type": "knowledge-source",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Knowledge Source: {ks.get('name', '')[:80]}",
                        "excerpt": ks.get("description", "")[:300],
                        "date": _safe_date(ks.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

        # Search failure cases
        if content_type in (None, "", "failure-case", "exception"):
            for fc in get_failure_cases_for_org(oid):
                combined = " ".join([
                    fc.get("what_failed", ""),
                    fc.get("why_it_failed", ""),
                    fc.get("suggested_prevention", ""),
                ]).lower()
                if q_lower in combined:
                    results.append({
                        "content_type": "failure-case",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Failure Case: {fc.get('what_failed', '')[:80]}",
                        "excerpt": fc.get("why_it_failed", "")[:300],
                        "date": _safe_date(fc.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

        # Search adoption risk notes
        if content_type in (None, "", "adoption-risk", "risk"):
            for ar in get_adoption_risk_notes_for_org(oid):
                combined = " ".join([
                    ar.get("risk_type", ""),
                    ar.get("description", ""),
                    ar.get("suggested_mitigation", ""),
                ]).lower()
                if q_lower in combined:
                    results.append({
                        "content_type": "adoption-risk",
                        "organization_id": oid,
                        "organization_name": oname,
                        "title": f"Adoption Risk: {ar.get('risk_type', '')} — {ar.get('description', '')[:60]}",
                        "excerpt": ar.get("description", "")[:300],
                        "date": _safe_date(ar.get("created_at", "")),
                        "link": f"/?org={oid}",
                    })

    if date_from:
        results = [r for r in results if r.get("date", "") >= date_from]
    if date_to:
        results = [r for r in results if r.get("date", "") <= date_to]

    results.sort(key=lambda r: r.get("date", ""), reverse=True)
    return results


def compute_knowledge_analytics(crm) -> Dict[str, Any]:
    orgs = crm.list_organizations()
    all_interactions = get_all_interactions()
    all_tasks = get_all_tasks()
    all_drafts = read_outbox()

    orgs_with_interactions = 0
    orgs_without_interactions = 0
    all_tags: List[str] = []

    for org in orgs:
        org_ints = get_interactions_for_org(org["id"])
        if org_ints:
            orgs_with_interactions += 1
            for intx in org_ints:
                tags = intx.get("tags") or []
                all_tags.extend(tags)
        else:
            orgs_without_interactions += 1

    tag_counts: Dict[str, int] = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    most_common_tags = dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:10])

    recent_events: List[Dict[str, Any]] = []
    for org in orgs:
        oid = org["id"]
        oname = org["name"]
        for intx in get_interactions_for_org(oid):
            recent_events.append({
                "date": _safe_date(intx.get("date", "")),
                "description": f"Interaction: {intx.get('title', '')} — {oname}",
            })
        for task in get_tasks_for_org(oid):
            if task.get("created_at"):
                recent_events.append({
                    "date": _safe_date(task["created_at"]),
                    "description": f"Task created: {task.get('title', '')} — {oname}",
                })
    for draft in all_drafts:
        if draft.get("created_at"):
            org_name = next(
                (o["name"] for o in orgs if o["id"] == draft.get("organization_id")),
                "Unknown",
            )
            recent_events.append({
                "date": _safe_date(draft["created_at"]),
                "description": f"Draft saved: {draft.get('subject', '')[:60]} — {org_name}",
            })

    recent_events.sort(key=lambda e: e.get("date", ""), reverse=True)
    recent_events = recent_events[:5]

    total_knowledge_items = (
        len(orgs)
        + len(all_interactions)
        + len(all_tasks)
        + len(all_drafts)
    )

    # Include summary tags in analytics
    all_summaries = get_all_summaries()
    for s in all_summaries:
        summary_tags = s.get("suggested_tags") or []
        for tag in summary_tags:
            all_tags.append(tag)

    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    most_common_tags = dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:10])

    # Workflow analytics
    all_workflow_opps = get_all_workflow_opportunities()
    all_failure_cases = get_all_failure_cases()
    all_knowledge_sources = get_all_knowledge_sources()

    orgs_with_workflow_opps = len(set(o.get("organization_id") for o in all_workflow_opps))
    orgs_missing_knowledge_sources = 0
    for org in orgs:
        if not get_knowledge_sources_for_org(org["id"]):
            orgs_missing_knowledge_sources += 1

    candidate_pilot_workflows = [
        o for o in all_workflow_opps if o.get("status") in ("Candidate for Pilot", "Needs Validation")
    ]

    all_adoption_risk_notes = get_all_adoption_risk_notes()
    orgs_with_adoption_risks = len(set(a.get("organization_id") for a in all_adoption_risk_notes))
    staff_concern_notes = [a for a in all_adoption_risk_notes if a.get("risk_type") == "Staff Concern"]
    eval_risk_notes = [a for a in all_adoption_risk_notes if a.get("risk_type") == "Evaluation Risk"]
    high_severity_risks = [a for a in all_adoption_risk_notes if a.get("severity") in ("Medium", "High")]
    workflow_opps_with_human_review = [
        o for o in all_workflow_opps if o.get("human_review_required") or o.get("human_review_points")
    ]

    return {
        "total_knowledge_items": total_knowledge_items,
        "organizations_with_interaction_history": orgs_with_interactions,
        "organizations_without_interaction_history": orgs_without_interactions,
        "most_common_tags": most_common_tags,
        "recent_knowledge_activity": recent_events,
        "workflow_opportunities_identified": len(all_workflow_opps),
        "organizations_with_workflow_opportunities": orgs_with_workflow_opps,
        "organizations_missing_knowledge_source_notes": orgs_missing_knowledge_sources,
        "failure_cases_recorded": len(all_failure_cases),
        "candidate_pilot_workflows": len(candidate_pilot_workflows),
        "adoption_risk_notes_recorded": len(all_adoption_risk_notes),
        "organizations_with_adoption_risk_notes": orgs_with_adoption_risks,
        "staff_concern_notes": len(staff_concern_notes),
        "evaluation_risk_notes": len(eval_risk_notes),
        "high_severity_adoption_risks": len(high_severity_risks),
        "workflow_opps_with_human_review": len(workflow_opps_with_human_review),
    }


def get_lessons_for_org(organization_id: int) -> List[Dict[str, Any]]:
    summaries = get_summaries_for_org(organization_id)
    interactions = get_interactions_for_org(organization_id)
    intx_map = {i["id"]: i for i in interactions}

    lessons = []
    for s in summaries:
        lesson_items = s.get("lessons_learned") or []
        intx = intx_map.get(s.get("interaction_id"))
        for li in lesson_items:
            lessons.append({
                "title": li.get("title", ""),
                "description": li.get("description", ""),
                "source_interaction": intx.get("title", f"Interaction #{s.get('interaction_id')}") if intx else f"Interaction #{s.get('interaction_id')}",
                "date": _safe_date(intx.get("date", "")) if intx else "",
                "tags": s.get("suggested_tags") or [],
                "interaction_id": s.get("interaction_id"),
            })

    lessons.sort(key=lambda x: x.get("date", ""), reverse=True)
    return lessons


def get_playbook_candidates_for_org(organization_id: int) -> List[Dict[str, Any]]:
    summaries = get_summaries_for_org(organization_id)
    interactions = get_interactions_for_org(organization_id)
    intx_map = {i["id"]: i for i in interactions}

    candidates = []
    for s in summaries:
        playbook_items = s.get("playbook_candidates") or []
        intx = intx_map.get(s.get("interaction_id"))
        for pb in playbook_items:
            candidates.append({
                "title": pb.get("title", ""),
                "when_to_use": pb.get("when_to_use", ""),
                "suggested_process": pb.get("suggested_process", ""),
                "source_interaction": intx.get("title", f"Interaction #{s.get('interaction_id')}") if intx else f"Interaction #{s.get('interaction_id')}",
                "tags": s.get("suggested_tags") or [],
                "date": _safe_date(intx.get("date", "")) if intx else "",
                "interaction_id": s.get("interaction_id"),
            })

    candidates.sort(key=lambda x: x.get("date", ""), reverse=True)
    return candidates
