import json
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

try:
    from app.connectors.local_json import LocalJsonCRMConnector
    from app.models import (
        DraftRequest,
        DraftEmail,
        InteractionCreate,
        InteractionUpdate,
        MeetingNotesRequest,
        OrgUpdate,
        OutboxUpdate,
        ResearchApproveRequest,
        ResearchDiscoverRequest,
        ResearchIntakeRequest,
        StatusUpdate,
    )
    from app.services.ai_provider import get_ai_provider
    from app.services.attachments import (
        save_attachment,
        list_attachments,
        delete_attachment,
    )
    from app.services.interactions import (
        add_interaction,
        delete_interaction,
        get_interactions_for_org,
        update_interaction,
    )
    from app.services.outbox import read_outbox, save_demo_draft, update_demo_draft
    from app.services.research_mock import discover_research_candidates
    from app.services.data_tools import (
        export_csv as export_csv_service,
        export_json as export_json_service,
        parse_csv,
        import_rows,
        stage_import,
        get_staged_rows,
        CSV_FIELDS,
        CSV_TEMPLATE,
    )
    from app.services.analytics import compute_analytics_summary
    from app.services.outreach_recommendation import (
        compute_outreach_recommendation,
        compute_priority_queue,
    )
    from app.services.tasks import (
        get_all_tasks,
        get_tasks_for_org,
        add_task,
        update_task,
        delete_task,
        suggest_tasks_from_interaction,
    )
    from app.services.knowledge import (
        build_timeline_for_org,
        search_knowledge,
        get_lessons_for_org,
        get_playbook_candidates_for_org,
    )
    from app.services.interaction_summaries import save_summary, get_summaries_for_org as get_summaries
    from app.services.workflow import (
        get_workflow_opportunities_for_org,
        save_workflow_opportunity,
        update_workflow_opportunity,
        get_knowledge_sources_for_org,
        save_knowledge_source,
        update_knowledge_source,
        delete_knowledge_source,
        get_failure_cases_for_org,
        save_failure_case,
        update_failure_case,
        auto_save_workflow_opportunity_from_summary,
        auto_save_failure_cases_from_summary,
        auto_save_knowledge_sources_from_summary,
        get_adoption_risk_notes_for_org,
        save_adoption_risk_note,
        update_adoption_risk_note,
        delete_adoption_risk_note,
        auto_save_adoption_risk_notes_from_summary,
    )
    from app.services.adoption_principles import (
        get_all as get_principles_all,
        get_by_id as get_principles_by_id,
        get_by_category as get_principles_by_category,
    )
except ModuleNotFoundError:
    from backend.app.connectors.local_json import LocalJsonCRMConnector
    from backend.app.models import (
        DraftRequest,
        DraftEmail,
        InteractionCreate,
        InteractionUpdate,
        MeetingNotesRequest,
        OrgUpdate,
        OutboxUpdate,
        ResearchApproveRequest,
        ResearchDiscoverRequest,
        ResearchIntakeRequest,
        StatusUpdate,
    )
    from backend.app.services.ai_provider import get_ai_provider
    from backend.app.services.attachments import (
        save_attachment,
        list_attachments,
        delete_attachment,
    )
    from backend.app.services.interactions import (
        add_interaction,
        delete_interaction,
        get_interactions_for_org,
        update_interaction,
    )
    from backend.app.services.outbox import read_outbox, save_demo_draft, update_demo_draft
    from backend.app.services.research_mock import discover_research_candidates
    from backend.app.services.data_tools import (
        export_csv as export_csv_service,
        export_json as export_json_service,
        parse_csv,
        import_rows,
        stage_import,
        get_staged_rows,
        CSV_FIELDS,
        CSV_TEMPLATE,
    )
    from backend.app.services.analytics import compute_analytics_summary
    from backend.app.services.outreach_recommendation import (
        compute_outreach_recommendation,
        compute_priority_queue,
    )
    from backend.app.services.tasks import (
        get_all_tasks,
        get_tasks_for_org,
        add_task,
        update_task,
        delete_task,
        suggest_tasks_from_interaction,
    )
    from backend.app.connectors.local_json import backfill_timestamps
    from backend.app.services.knowledge import (
        build_timeline_for_org,
        search_knowledge,
        get_lessons_for_org,
        get_playbook_candidates_for_org,
    )
    from backend.app.services.interaction_summaries import save_summary, get_summaries_for_org as get_summaries
    from backend.app.services.workflow import (
        get_workflow_opportunities_for_org,
        save_workflow_opportunity,
        update_workflow_opportunity,
        get_knowledge_sources_for_org,
        save_knowledge_source,
        update_knowledge_source,
        delete_knowledge_source,
        get_failure_cases_for_org,
        save_failure_case,
        update_failure_case,
        auto_save_workflow_opportunity_from_summary,
        auto_save_failure_cases_from_summary,
        auto_save_knowledge_sources_from_summary,
        get_adoption_risk_notes_for_org,
        save_adoption_risk_note,
        update_adoption_risk_note,
        delete_adoption_risk_note,
        auto_save_adoption_risk_notes_from_summary,
    )
    from backend.app.services.adoption_principles import (
        get_all as get_principles_all,
        get_by_id as get_principles_by_id,
        get_by_category as get_principles_by_category,
    )

app = FastAPI(title="Outreach Intelligence Platform")
crm = LocalJsonCRMConnector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "email_sending": False, "mode": "demo"}


@app.post("/api/admin/backfill-timestamps")
def admin_backfill_timestamps():
    updated = backfill_timestamps()
    return {"backfilled": updated, "message": f"{updated} record(s) updated."}


@app.post("/api/data/import/csv")
async def import_csv(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8-sig")
    valid_rows, parse_errors = parse_csv(content)
    upload_id = str(uuid.uuid4())
    stage_import(upload_id, valid_rows)
    return {
        "upload_id": upload_id,
        "imported": len(valid_rows),
        "duplicates_skipped": 0,
        "parse_errors": parse_errors,
        "rows_read": len(valid_rows) + len(parse_errors),
    }


@app.post("/api/data/import/csv/confirm")
def confirm_csv_import(payload: dict):
    upload_id = payload.get("upload_id", "")
    rows = get_staged_rows(upload_id)
    if not rows:
        raise HTTPException(status_code=400, detail="No staged CSV data found. Upload first.")
    result = import_rows(rows)
    return result


@app.get("/api/data/export/csv")
def export_csv():
    orgs = crm.list_organizations()
    csv_data = export_csv_service(orgs)
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=organizations_export.csv"},
    )


@app.get("/api/data/export/json")
def export_json():
    data = export_json_service()
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=outreach_intelligence_export.json"},
    )


@app.get("/api/analytics/summary")
def analytics_summary():
    return compute_analytics_summary(crm)


@app.get("/api/analytics/priority-queue")
def priority_queue():
    orgs = crm.list_organizations()
    return compute_priority_queue(orgs)


@app.get("/api/organizations")
def list_organizations():
    return crm.list_organizations()


@app.get("/api/organizations/{organization_id}")
def get_organization(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@app.patch("/api/organizations/{organization_id}/status")
def update_status(organization_id: int, payload: StatusUpdate):
    org = crm.update_status(organization_id, payload.status)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@app.patch("/api/organizations/{organization_id}")
def update_organization(organization_id: int, payload: OrgUpdate):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        return org
    result = crm.update_org(organization_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")
    return result


@app.get("/api/organizations/{organization_id}/summary")
def organization_summary(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_ai_provider().summarize_organization(org)


@app.get("/api/organizations/{organization_id}/opportunities")
def organization_opportunities(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_ai_provider().discover_opportunities(org)


@app.post("/api/drafts/generate")
def create_draft(payload: DraftRequest):
    org = crm.get_organization(payload.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    provider = get_ai_provider()
    interactions = get_interactions_for_org(payload.organization_id)
    ai_summary = provider.summarize_organization(org)
    all_outbox = read_outbox()
    org_outbox = [d for d in all_outbox if d.get("organization_id") == payload.organization_id]

    opportunities = provider.discover_opportunities(org)
    outreach_rec = compute_outreach_recommendation(org)
    workflow_summaries = get_summaries(payload.organization_id)
    follow_up_tasks = get_tasks_for_org(payload.organization_id)
    adoption_risks = get_adoption_risk_notes_for_org(payload.organization_id)

    extra_context = {
        "readiness_level": outreach_rec.get("context_used", {}).get("AI Readiness Level"),
        "outreach_priority": outreach_rec.get("outreach_priority"),
        "recommended_next_action": outreach_rec.get("recommended_next_action"),
        "recommended_follow_up_date": outreach_rec.get("recommended_follow_up_date"),
        "collaboration_angles": outreach_rec.get("recommended_collaboration_angles", []),
        "risks_or_concerns": outreach_rec.get("risks_or_concerns", []),
        "missing_information": outreach_rec.get("missing_information", []),
        "workflow_summaries": [
            {
                "summary_id": s.get("summary_id"),
                "summary": s.get("summary", "")[:500],
                "workflow_fields": s.get("workflow_fields", {}),
                "tags": s.get("suggested_tags", []),
                "human_judgment_points": s.get("human_judgment_points", []),
            }
            for s in workflow_summaries[-5:]
        ],
        "opportunities": [
            {
                "name": o.get("name"),
                "benefit": o.get("benefit"),
                "effort": o.get("effort"),
            }
            for o in opportunities.get("opportunities", [])
        ],
        "follow_up_tasks": [
            {
                "title": t.get("title"),
                "description": t.get("description", ""),
                "due_date": t.get("due_date"),
                "priority": t.get("priority"),
                "status": t.get("status"),
            }
            for t in follow_up_tasks
        ],
        "adoption_risks": [
            {
                "risk_type": r.get("risk_type"),
                "description": r.get("description"),
                "severity": r.get("severity"),
                "related_staff_role": r.get("related_staff_role"),
                "suggested_mitigation": r.get("suggested_mitigation"),
            }
            for r in adoption_risks
        ],
        "candidate_source_notes": {
            "program_area": org.get("mission_notes", ""),
            "pain_points": org.get("pain_points", []),
            "outreach_goal": payload.outreach_goal,
        },
    }

    draft = provider.generate_next_best_email(
        org, interactions, ai_summary, org_outbox,
        extra_context=extra_context,
    )
    draft["organization_id"] = payload.organization_id
    draft["ai_generated"] = True
    draft["human_review_required"] = True
    draft["status"] = "needs_review"
    draft["draft_type"] = "ai_assisted"
    draft.setdefault("to", org.get("contact_email", ""))
    draft.setdefault("subject", "")
    draft.setdefault("body", "")
    draft.setdefault("tone", "professional")
    draft.setdefault("reasoning_summary", "")
    draft.setdefault("human_review_notes", [])
    draft.setdefault("missing_context", [])
    draft.setdefault("suggested_edits", [])

    saved = save_demo_draft(draft)
    return saved


@app.post("/api/outbox")
def save_to_outbox(payload: DraftEmail):
    return save_demo_draft(payload.model_dump())


@app.get("/api/outbox")
def get_outbox():
    rows = read_outbox()
    for row in rows:
        org = crm.get_organization(row.get("organization_id"))
        row["organization_name"] = org.get("name", f"Org #{row.get('organization_id')}") if org else f"Org #{row.get('organization_id')}"
    return rows


@app.patch("/api/outbox/{draft_id}")
def update_outbox_draft(draft_id: int, payload: OutboxUpdate):
    updated = update_demo_draft(draft_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Draft not found")
    org = crm.get_organization(updated.get("organization_id"))
    updated["organization_name"] = org.get("name", f"Org #{updated.get('organization_id')}") if org else f"Org #{updated.get('organization_id')}"
    return updated


@app.post("/api/outbox/{draft_id}/attachments")
async def upload_attachment(draft_id: int, file: UploadFile = File(...)):
    outbox = read_outbox()
    if not any(d.get("id") == draft_id for d in outbox):
        raise HTTPException(status_code=404, detail="Draft not found")
    return await save_attachment(draft_id, file)


@app.get("/api/outbox/{draft_id}/attachments")
def get_attachments(draft_id: int):
    return list_attachments(draft_id)


@app.delete("/api/outbox/{draft_id}/attachments/{attachment_id}")
def remove_attachment(draft_id: int, attachment_id: str):
    outbox = read_outbox()
    if not any(d.get("id") == draft_id for d in outbox):
        raise HTTPException(status_code=404, detail="Draft not found")
    if not delete_attachment(draft_id, attachment_id):
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"deleted": True}


@app.get("/api/organizations/{organization_id}/meeting-brief")
def get_meeting_brief(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_ai_provider().meeting_brief(org)


@app.post("/api/meeting-notes/summarize")
def summarize_meeting_notes(payload: MeetingNotesRequest):
    return get_ai_provider().summarize_notes(payload.notes)


@app.post("/api/research/discover")
def discover_organizations(payload: ResearchDiscoverRequest):
    if not payload.research_theme.strip():
        raise HTTPException(status_code=400, detail="Research theme is required")
    return discover_research_candidates(payload.research_theme)


@app.post("/api/research/intake")
def save_research_intake(payload: ResearchIntakeRequest):
    if not payload.organization_name.strip():
        raise HTTPException(status_code=400, detail="Organization name is required")

    # Field mapping note (see app/services/field_mapper.py):
    #   payload.organization_type → internal "category"
    #   payload.program_area      embedded in mission_notes below
    notes = [
        payload.description,
        f"Program area: {payload.program_area}" if payload.program_area else "",
        (
            f"Why it may benefit from AI literacy or workflow improvement: "
            f"{payload.why_it_may_benefit}"
            if payload.why_it_may_benefit
            else ""
        ),
        (
            f"Suggested outreach angle: {payload.suggested_outreach_angle}"
            if payload.suggested_outreach_angle
            else ""
        ),
        f"Source URL: {payload.source_url}" if payload.source_url else "",
        f"Notes: {payload.notes}" if payload.notes else "",
    ]
    organization = {
        "name": payload.organization_name,
        "category": payload.organization_type or "Research intake",
        "website": payload.website,
        "contact_name": "General Inquiries",
        "contact_email": payload.general_contact_email or "",
        "phone_number": payload.phone_number or "",
        "status": "Research Intake",
        "mission_notes": " ".join(note for note in notes if note).strip()
        or "Added through manual Research Intake.",
        "pain_points": [
            "AI literacy support",
            "Workflow improvement",
            "Human-reviewed outreach planning",
        ],
        "last_interaction": "Added from manual Research Intake.",
    }
    return crm.add_organization(organization)


@app.post("/api/research/approve")
def approve_research_candidate(payload: ResearchApproveRequest):
    candidate = payload.candidate
    normalized_name = candidate.organization_name.strip().lower()
    existing = next(
        (
            org
            for org in crm.list_organizations()
            if org.get("name", "").strip().lower() == normalized_name
        ),
        None,
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"{candidate.organization_name} already exists in the CRM.",
        )

    source_parts = [
        f"Source type: {candidate.source_type}" if candidate.source_type else "",
        f"Source name: {candidate.source_name}" if candidate.source_name else "",
        f"Source URL: {candidate.source_url}" if candidate.source_url else "",
        f"Source notes: {candidate.source_notes}" if candidate.source_notes else "",
        f"Source note: {candidate.source_note}" if candidate.source_note else "",
    ]
    workflow_parts = [
        (
            "Likely workflow pain points: "
            + "; ".join(candidate.likely_workflow_pain_points)
            if candidate.likely_workflow_pain_points
            else ""
        ),
        (
            "Possible AI support areas: "
            + "; ".join(candidate.possible_ai_support_areas)
            if candidate.possible_ai_support_areas
            else ""
        ),
        (
            "Required human review: "
            + "; ".join(candidate.required_human_review)
            if candidate.required_human_review
            else ""
        ),
        (
            "Required knowledge sources: "
            + "; ".join(candidate.required_knowledge_sources)
            if candidate.required_knowledge_sources
            else ""
        ),
        (
            "Adoption risk notes: "
            + "; ".join(candidate.adoption_risk_notes)
            if candidate.adoption_risk_notes
            else ""
        ),
        (
            "Suggested discovery questions: "
            + "; ".join(candidate.suggested_discovery_questions)
            if candidate.suggested_discovery_questions
            else ""
        ),
        (
            f"Suggested first discovery question: "
            f"{candidate.suggested_first_discovery_question}"
            if candidate.suggested_first_discovery_question
            else ""
        ),
    ]
    mission_notes = " ".join(
        note
        for note in [
            candidate.program_area,
            candidate.why_it_may_be_relevant,
            (
                f"Why selected: {candidate.why_user_selected_this_candidate}"
                if candidate.why_user_selected_this_candidate
                else ""
            ),
            (
                f"Suggested outreach angle: {candidate.suggested_outreach_angle}"
                if candidate.suggested_outreach_angle
                else ""
            ),
            *workflow_parts,
            *source_parts,
        ]
        if note
    ).strip()
    # Field mapping note (see app/services/field_mapper.py):
    #   candidate.organization_type → internal "category"
    #   candidate.program_area      embedded in mission_notes below
    organization = {
        "name": candidate.organization_name,
        "category": candidate.organization_type or "Research approved",
        "website": candidate.website,
        "contact_name": "General Inquiries",
        "contact_email": candidate.general_contact_email or "",
        "phone_number": candidate.phone_number or "",
        "status": "Research Approved",
        "mission_notes": mission_notes or "Added from Organization Discovery.",
        "pain_points": candidate.likely_workflow_pain_points
        or [
            "Program planning",
            "Documentation support",
            "Follow-up coordination",
        ],
        "last_interaction": (
            "Added from Organization Discovery. "
            + " ".join(note for note in source_parts if note)
        ),
    }
    return crm.add_organization(organization)


def _sync_org_metadata(organization_id: int) -> None:
    org = crm.get_organization(organization_id)
    if not org:
        return
    interactions = get_interactions_for_org(organization_id)

    updates = {}
    new_status = get_ai_provider().derive_status_from_interactions(interactions, org.get("status", ""))
    if org["status"] != new_status:
        updates["status"] = new_status

    if interactions:
        recent = max(interactions, key=lambda i: i.get("date", ""))
        new_last = f"{recent.get('date','')} — {recent.get('title','')} ({recent.get('interaction_type','')})"
    else:
        new_last = "No previous interaction recorded."
    if org.get("last_interaction") != new_last:
        updates["last_interaction"] = new_last

    if updates:
        crm.update_org(organization_id, updates)


@app.get("/api/organizations/{organization_id}/interactions")
def list_interactions(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    rows = get_interactions_for_org(organization_id)
    rows.sort(key=lambda r: r.get("date", ""), reverse=True)
    return rows


@app.post("/api/organizations/{organization_id}/interactions")
def create_interaction(organization_id: int, payload: InteractionCreate):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    result = add_interaction(payload.model_dump())
    _sync_org_metadata(organization_id)
    return result


@app.patch("/api/organizations/{organization_id}/interactions/{interaction_id}")
def edit_interaction(organization_id: int, interaction_id: int, payload: InteractionUpdate):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    result = update_interaction(interaction_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Interaction not found")
    _sync_org_metadata(organization_id)
    return result


@app.delete("/api/organizations/{organization_id}/interactions/{interaction_id}")
def remove_interaction(organization_id: int, interaction_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not delete_interaction(interaction_id):
        raise HTTPException(status_code=404, detail="Interaction not found")
    _sync_org_metadata(organization_id)
    return {"deleted": True}


@app.post("/api/organizations/{organization_id}/interactions/{interaction_id}/summarize")
def summarize_interaction(organization_id: int, interaction_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    interactions = get_interactions_for_org(organization_id)
    interaction = next((i for i in interactions if i["id"] == interaction_id), None)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    result = get_ai_provider().summarize_interaction_notes(interaction.get("notes", ""), interaction.get("interaction_type", ""))
    # Attach suggested tasks with org/interaction context for frontend review
    if "follow_up_tasks" in result:
        for t in result["follow_up_tasks"]:
            t["organization_id"] = organization_id
            t["source_interaction_id"] = interaction_id
    # Persist the enriched summary
    save_summary(interaction_id, organization_id, result)
    # Auto-save workflow opportunities, failure cases, and knowledge sources
    intx_title = interaction.get("title", f"Interaction #{interaction_id}")
    auto_save_workflow_opportunity_from_summary(organization_id, interaction_id, intx_title, result)
    auto_save_failure_cases_from_summary(organization_id, interaction_id, intx_title, result)
    auto_save_knowledge_sources_from_summary(organization_id, result)
    auto_save_adoption_risk_notes_from_summary(organization_id, interaction_id, intx_title, result)
    return result


@app.get("/api/organizations/{organization_id}/lessons-learned")
def organization_lessons(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_lessons_for_org(organization_id)


@app.get("/api/organizations/{organization_id}/playbook-candidates")
def organization_playbooks(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_playbook_candidates_for_org(organization_id)


@app.get("/api/organizations/{organization_id}/knowledge-summary")
def knowledge_summary(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    interactions = get_interactions_for_org(organization_id)
    interactions.sort(key=lambda r: r.get("date", ""), reverse=True)
    return get_ai_provider().generate_knowledge_summary(org, interactions)


@app.get("/api/organizations/{organization_id}/timeline")
def organization_timeline(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return build_timeline_for_org(org)


@app.get("/api/knowledge/search")
def knowledge_search(
    q: str = "",
    org_id: int = None,
    content_type: str = None,
    date_from: str = None,
    date_to: str = None,
):
    return search_knowledge(crm, q, org_id, content_type, date_from, date_to)


@app.get("/api/organizations/{organization_id}/workflow-opportunities")
def organization_workflow_opportunities(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_workflow_opportunities_for_org(organization_id)


@app.post("/api/organizations/{organization_id}/workflow-opportunities")
def create_workflow_opportunity(organization_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return save_workflow_opportunity(
        organization_id=organization_id,
        source_interaction_id=payload.get("source_interaction_id", 0),
        source_interaction_title=payload.get("source_interaction_title", ""),
        title=payload.get("title", ""),
        current_process=payload.get("current_process", ""),
        pain_point=payload.get("pain_point", ""),
        possible_ai_support=payload.get("possible_ai_support", ""),
        knowledge_sources_needed=payload.get("knowledge_sources_needed", []),
        human_review_points=payload.get("human_review_points", []),
        risks_or_exceptions=payload.get("risks_or_exceptions", []),
        tags=payload.get("tags"),
        status=payload.get("status", "Identified"),
        staff_impact=payload.get("staff_impact", ""),
        adoption_risk_level=payload.get("adoption_risk_level", "Unknown"),
        next_discovery_questions=payload.get("next_discovery_questions"),
        human_review_required=payload.get("human_review_required", ""),
        required_knowledge_sources=payload.get("required_knowledge_sources"),
        known_failure_cases=payload.get("known_failure_cases"),
    )


@app.patch("/api/organizations/{organization_id}/workflow-opportunities/{opp_id}")
def edit_workflow_opportunity(organization_id: int, opp_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    result = update_workflow_opportunity(opp_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow opportunity not found")
    return result


@app.get("/api/organizations/{organization_id}/knowledge-sources")
def organization_knowledge_sources(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_knowledge_sources_for_org(organization_id)


@app.post("/api/organizations/{organization_id}/knowledge-sources")
def create_knowledge_source(organization_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return save_knowledge_source(
        organization_id=organization_id,
        source_type=payload.get("source_type", "Other"),
        name=payload.get("name", ""),
        description=payload.get("description", ""),
        location_note=payload.get("location_note", ""),
    )


@app.patch("/api/organizations/{organization_id}/knowledge-sources/{ks_id}")
def edit_knowledge_source(organization_id: int, ks_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    result = update_knowledge_source(ks_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return result


@app.delete("/api/organizations/{organization_id}/knowledge-sources/{ks_id}")
def remove_knowledge_source(organization_id: int, ks_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not delete_knowledge_source(ks_id):
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    return {"deleted": True}


@app.get("/api/organizations/{organization_id}/failure-cases")
def organization_failure_cases(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_failure_cases_for_org(organization_id)


@app.post("/api/organizations/{organization_id}/failure-cases")
def create_failure_case(organization_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return save_failure_case(
        organization_id=organization_id,
        source_interaction_id=payload.get("source_interaction_id", 0),
        source_interaction_title=payload.get("source_interaction_title", ""),
        what_failed=payload.get("what_failed", ""),
        why_it_failed=payload.get("why_it_failed", ""),
        missing_context=payload.get("missing_context", ""),
        human_review_required=payload.get("human_review_required", ""),
        suggested_prevention=payload.get("suggested_prevention", ""),
        tags=payload.get("tags"),
    )


@app.patch("/api/organizations/{organization_id}/failure-cases/{fc_id}")
def edit_failure_case(organization_id: int, fc_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    result = update_failure_case(fc_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Failure case not found")
    return result


@app.get("/api/organizations/{organization_id}/adoption-risk-notes")
def organization_adoption_risk_notes(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return get_adoption_risk_notes_for_org(organization_id)


@app.post("/api/organizations/{organization_id}/adoption-risk-notes")
def create_adoption_risk_note(organization_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return save_adoption_risk_note(
        organization_id=organization_id,
        source_interaction_id=payload.get("source_interaction_id", 0),
        source_interaction_title=payload.get("source_interaction_title", ""),
        risk_type=payload.get("risk_type", "General"),
        description=payload.get("description", ""),
        severity=payload.get("severity", "Low"),
        related_staff_role=payload.get("related_staff_role", ""),
        suggested_mitigation=payload.get("suggested_mitigation", ""),
        tags=payload.get("tags"),
    )


@app.patch("/api/organizations/{organization_id}/adoption-risk-notes/{ar_id}")
def edit_adoption_risk_note(organization_id: int, ar_id: int, payload: dict):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    result = update_adoption_risk_note(ar_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Adoption risk note not found")
    return result


@app.delete("/api/organizations/{organization_id}/adoption-risk-notes/{ar_id}")
def remove_adoption_risk_note(organization_id: int, ar_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not delete_adoption_risk_note(ar_id):
        raise HTTPException(status_code=404, detail="Adoption risk note not found")
    return {"deleted": True}


@app.post("/api/organizations/{organization_id}/readiness-assessment")
def readiness_assessment(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    interactions = get_interactions_for_org(organization_id)
    opportunities = get_ai_provider().discover_opportunities(org)
    return get_ai_provider().generate_readiness_assessment(org, interactions, opportunities)


@app.get("/api/organizations/{organization_id}/outreach-recommendation")
def outreach_recommendation(organization_id: int):
    org = crm.get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return compute_outreach_recommendation(org)


@app.get("/api/adoption-principles")
def list_principles(category: str = None):
    if category:
        return get_principles_by_category(category)
    return get_principles_all()


@app.get("/api/adoption-principles/{principle_id}")
def get_principle(principle_id: int):
    p = get_principles_by_id(principle_id)
    if not p:
        raise HTTPException(status_code=404, detail="Principle not found")
    return p


@app.get("/api/tasks")
def list_tasks(organization_id: int = None, status: str = None):
    if organization_id:
        tasks = get_tasks_for_org(organization_id)
    else:
        tasks = get_all_tasks()
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    tasks.sort(key=lambda t: t.get("task_id", 0), reverse=True)
    return tasks


@app.post("/api/tasks")
def create_task(payload: dict):
    return add_task(payload)


@app.patch("/api/tasks/{task_id}")
def edit_task(task_id: int, payload: dict):
    result = update_task(task_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@app.delete("/api/tasks/{task_id}")
def remove_task(task_id: int):
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"


@app.get("/")
@app.get("/research-intake")
@app.get("/organization-discovery")
@app.get("/integrations")
@app.get("/data-tools")
@app.get("/analytics")
@app.get("/priority-queue")
@app.get("/workflow-opportunities")
@app.get("/follow-ups")
@app.get("/knowledge-search")
@app.get("/demo-outbox")
def serve_frontend_page():
    return FileResponse(INDEX_FILE, headers={"Cache-Control": "no-cache"})


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
