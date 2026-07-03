import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "workflow_knowledge.json"

_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "this", "that", "these", "those", "i", "it", "its",
    "we", "you", "they", "he", "she", "not", "no", "nor", "up", "down",
    "out", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such",
    "only", "own", "same", "so", "than", "too", "very", "just",
    "because", "as", "until", "while", "about", "between", "through",
    "during", "before", "after", "above", "below", "into", "onto",
    "upon", "ai", "assisted",
})

SIMILARITY_THRESHOLD = 0.45


def _read() -> Dict[str, Any]:
    if not DATA_PATH.exists() or not DATA_PATH.read_text(encoding="utf-8").strip():
        return {"workflow_opportunities": [], "knowledge_sources": [], "failure_cases": []}
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _write(data: Dict[str, Any]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_key(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    words = text.split()
    words = [w for w in words if w not in _STOP_WORDS]
    return ' '.join(words)


def _word_overlap(a: str, b: str) -> float:
    words_a = set(_normalize_key(a).split())
    words_b = set(_normalize_key(b).split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def _merge_lists_unique(*lists: List[Any]) -> List[Any]:
    seen = set()
    result = []
    for lst in lists:
        for item in lst:
            key = item if isinstance(item, str) else json.dumps(item, sort_keys=True)
            if key not in seen:
                seen.add(key)
                result.append(item)
    return result


def _merge_strings_nonempty(existing: str, new: str) -> str:
    return existing if existing else new


# ---- Workflow Opportunities ----

def _find_or_create_workflow_opportunity(
    organization_id: int,
    title: str,
    possible_ai_support: str,
) -> tuple[Optional[Dict[str, Any]], bool]:
    data = _read()
    existing = [o for o in data["workflow_opportunities"]
                if o.get("organization_id") == organization_id]
    norm_candidate = _normalize_key(possible_ai_support)

    for opp in existing:
        norm_existing = _normalize_key(opp.get("possible_ai_support", opp.get("title", "")))
        if norm_candidate == norm_existing:
            return opp, True
        overlap = _word_overlap(possible_ai_support, opp.get("possible_ai_support", opp.get("title", "")))
        if overlap >= SIMILARITY_THRESHOLD:
            return opp, True
    return None, False


def _merge_into_workflow_opportunity(
    opp: Dict[str, Any],
    source_interaction_id: int,
    source_interaction_title: str,
    title: str,
    current_process: str,
    pain_point: str,
    possible_ai_support: str,
    knowledge_sources_needed: List[str],
    human_review_points: List[str],
    risks_or_exceptions: List[str],
    tags: Optional[List[str]] = None,
    staff_impact: str = "",
    adoption_risk_level: str = "Unknown",
    next_discovery_questions: Optional[List[str]] = None,
    human_review_required: str = "",
    required_knowledge_sources: Optional[List[str]] = None,
    known_failure_cases: Optional[List[str]] = None,
) -> Dict[str, Any]:
    source_ids = opp.get("source_interaction_ids") or [opp.get("source_interaction_id")]
    if source_interaction_id not in source_ids:
        source_ids.append(source_interaction_id)
    evidence_excerpts = opp.get("evidence_excerpts") or []
    excerpt = possible_ai_support[:200]
    if excerpt not in evidence_excerpts:
        evidence_excerpts.append(excerpt)

    opp["source_interaction_ids"] = source_ids
    opp["source_interaction_title"] = source_interaction_title
    opp["evidence_count"] = len(source_ids)
    opp["evidence_excerpts"] = evidence_excerpts
    opp["last_seen_at"] = _now_iso()
    opp["title"] = _merge_strings_nonempty(opp.get("title", ""), title)
    opp["current_process"] = _merge_strings_nonempty(opp.get("current_process", ""), current_process)
    opp["pain_point"] = _merge_strings_nonempty(opp.get("pain_point", ""), pain_point)
    opp["possible_ai_support"] = _merge_strings_nonempty(opp.get("possible_ai_support", ""), possible_ai_support)
    opp["knowledge_sources_needed"] = _merge_lists_unique(opp.get("knowledge_sources_needed", []), knowledge_sources_needed)
    opp["human_review_points"] = _merge_lists_unique(opp.get("human_review_points", []), human_review_points)
    opp["risks_or_exceptions"] = _merge_lists_unique(opp.get("risks_or_exceptions", []), risks_or_exceptions)
    opp["tags"] = _merge_lists_unique(opp.get("tags", []), tags or [])
    opp["staff_impact"] = _merge_strings_nonempty(opp.get("staff_impact", ""), staff_impact)
    opp["adoption_risk_level"] = _merge_strings_nonempty(opp.get("adoption_risk_level", "Unknown"), adoption_risk_level)
    opp["next_discovery_questions"] = _merge_lists_unique(opp.get("next_discovery_questions", []), next_discovery_questions or [])
    opp["human_review_required"] = _merge_strings_nonempty(opp.get("human_review_required", ""), human_review_required)
    opp["required_knowledge_sources"] = _merge_lists_unique(opp.get("required_knowledge_sources", []), required_knowledge_sources or [])
    opp["known_failure_cases"] = _merge_lists_unique(opp.get("known_failure_cases", []), known_failure_cases or [])
    opp["updated_at"] = _now_iso()
    return opp


def save_workflow_opportunity(
    organization_id: int,
    source_interaction_id: int,
    source_interaction_title: str,
    title: str,
    current_process: str,
    pain_point: str,
    possible_ai_support: str,
    knowledge_sources_needed: List[str],
    human_review_points: List[str],
    risks_or_exceptions: List[str],
    tags: Optional[List[str]] = None,
    status: str = "Identified",
    staff_impact: str = "",
    adoption_risk_level: str = "Unknown",
    next_discovery_questions: Optional[List[str]] = None,
    human_review_required: str = "",
    required_knowledge_sources: Optional[List[str]] = None,
    known_failure_cases: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data = _read()
    existing, found = _find_or_create_workflow_opportunity(
        organization_id, title, possible_ai_support,
    )
    if found and existing is not None:
        merged = _merge_into_workflow_opportunity(
            existing, source_interaction_id, source_interaction_title,
            title, current_process, pain_point, possible_ai_support,
            knowledge_sources_needed, human_review_points, risks_or_exceptions,
            tags, staff_impact, adoption_risk_level, next_discovery_questions,
            human_review_required, required_knowledge_sources, known_failure_cases,
        )
        _write(data)
        return merged

    wf_id = max([o.get("id", 0) for o in data["workflow_opportunities"]], default=0) + 1
    canonical_title = re.sub(r'^AI Support:\s*', '', title).strip()
    entry = {
        "id": wf_id,
        "organization_id": organization_id,
        "source_interaction_ids": [source_interaction_id],
        "source_interaction_title": source_interaction_title,
        "canonical_title": canonical_title,
        "normalized_key": _normalize_key(possible_ai_support),
        "title": title,
        "current_process": current_process,
        "pain_point": pain_point,
        "possible_ai_support": possible_ai_support,
        "knowledge_sources_needed": knowledge_sources_needed,
        "human_review_points": human_review_points,
        "risks_or_exceptions": risks_or_exceptions,
        "tags": tags or [],
        "status": status,
        "staff_impact": staff_impact,
        "adoption_risk_level": adoption_risk_level,
        "next_discovery_questions": next_discovery_questions or [],
        "human_review_required": human_review_required,
        "required_knowledge_sources": required_knowledge_sources or [],
        "known_failure_cases": known_failure_cases or [],
        "evidence_count": 1,
        "evidence_excerpts": [possible_ai_support[:200]],
        "last_seen_at": _now_iso(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    data["workflow_opportunities"].append(entry)
    _write(data)
    return entry


def get_workflow_opportunities_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [o for o in data["workflow_opportunities"] if o.get("organization_id") == organization_id]


def get_all_workflow_opportunities() -> List[Dict[str, Any]]:
    return _read()["workflow_opportunities"]


def update_workflow_opportunity(opp_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for o in data["workflow_opportunities"]:
        if o["id"] == opp_id:
            o.update(updates)
            o["updated_at"] = _now_iso()
            _write(data)
            return o
    return None


# ---- Knowledge Sources ----

def _find_or_create_knowledge_source(
    organization_id: int,
    name: str,
) -> tuple[Optional[Dict[str, Any]], bool]:
    data = _read()
    existing = [k for k in data["knowledge_sources"]
                if k.get("organization_id") == organization_id]
    norm_candidate = _normalize_key(name)
    for ks in existing:
        norm_existing = _normalize_key(ks.get("name", ""))
        if norm_candidate == norm_existing:
            return ks, True
    for ks in existing:
        overlap = _word_overlap(name, ks.get("name", ""))
        if overlap >= SIMILARITY_THRESHOLD:
            return ks, True
    return None, False


def _merge_into_knowledge_source(
    ks: Dict[str, Any],
    name: str,
    description: str,
) -> Dict[str, Any]:
    evidence_count = ks.get("evidence_count", 1)
    ks["evidence_count"] = evidence_count + 1
    ks["last_seen_at"] = _now_iso()
    ks["name"] = _merge_strings_nonempty(ks.get("name", ""), name)
    ks["description"] = _merge_strings_nonempty(ks.get("description", ""), description)
    ks["updated_at"] = _now_iso()
    return ks


def save_knowledge_source(
    organization_id: int,
    source_type: str,
    name: str,
    description: str = "",
    location_note: str = "",
) -> Dict[str, Any]:
    data = _read()
    existing, found = _find_or_create_knowledge_source(organization_id, name)
    if found and existing is not None:
        merged = _merge_into_knowledge_source(existing, name, description)
        _write(data)
        return merged

    ks_id = max([k.get("id", 0) for k in data["knowledge_sources"]], default=0) + 1
    entry = {
        "id": ks_id,
        "organization_id": organization_id,
        "source_type": source_type,
        "name": name,
        "normalized_key": _normalize_key(name),
        "description": description,
        "location_note": location_note,
        "evidence_count": 1,
        "last_seen_at": _now_iso(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    data["knowledge_sources"].append(entry)
    _write(data)
    return entry


def get_knowledge_sources_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [k for k in data["knowledge_sources"] if k.get("organization_id") == organization_id]


def get_all_knowledge_sources() -> List[Dict[str, Any]]:
    return _read()["knowledge_sources"]


def update_knowledge_source(ks_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for k in data["knowledge_sources"]:
        if k["id"] == ks_id:
            k.update(updates)
            k["updated_at"] = _now_iso()
            _write(data)
            return k
    return None


def delete_knowledge_source(ks_id: int) -> bool:
    data = _read()
    before = len(data["knowledge_sources"])
    data["knowledge_sources"] = [k for k in data["knowledge_sources"] if k["id"] != ks_id]
    if len(data["knowledge_sources"]) < before:
        _write(data)
        return True
    return False


# ---- Failure Cases / Exceptions ----

def _find_or_create_failure_case(
    organization_id: int,
    what_failed: str,
) -> tuple[Optional[Dict[str, Any]], bool]:
    data = _read()
    existing = [f for f in data["failure_cases"]
                if f.get("organization_id") == organization_id]
    norm_candidate = _normalize_key(what_failed)
    for fc in existing:
        norm_existing = _normalize_key(fc.get("what_failed", ""))
        if norm_candidate == norm_existing:
            return fc, True
    for fc in existing:
        overlap = _word_overlap(what_failed, fc.get("what_failed", ""))
        if overlap >= SIMILARITY_THRESHOLD:
            return fc, True
    return None, False


def _merge_into_failure_case(
    fc: Dict[str, Any],
    source_interaction_id: int,
    source_interaction_title: str,
    what_failed: str,
    why_it_failed: str,
    suggested_prevention: str,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    source_ids = fc.get("source_interaction_ids") or [fc.get("source_interaction_id")]
    if source_interaction_id not in source_ids:
        source_ids.append(source_interaction_id)
    evidence_excerpts = fc.get("evidence_excerpts") or []
    excerpt = what_failed[:200]
    if excerpt not in evidence_excerpts:
        evidence_excerpts.append(excerpt)

    fc["source_interaction_ids"] = source_ids
    fc["source_interaction_title"] = source_interaction_title
    fc["evidence_count"] = len(source_ids)
    fc["evidence_excerpts"] = evidence_excerpts
    fc["last_seen_at"] = _now_iso()
    fc["what_failed"] = _merge_strings_nonempty(fc.get("what_failed", ""), what_failed)
    fc["why_it_failed"] = _merge_strings_nonempty(fc.get("why_it_failed", ""), why_it_failed)
    fc["suggested_prevention"] = _merge_strings_nonempty(fc.get("suggested_prevention", ""), suggested_prevention)
    fc["tags"] = _merge_lists_unique(fc.get("tags", []), tags or [])
    fc["updated_at"] = _now_iso()
    return fc


def save_failure_case(
    organization_id: int,
    source_interaction_id: int,
    source_interaction_title: str,
    what_failed: str,
    why_it_failed: str,
    missing_context: str,
    human_review_required: str,
    suggested_prevention: str,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data = _read()
    existing, found = _find_or_create_failure_case(organization_id, what_failed)
    if found and existing is not None:
        merged = _merge_into_failure_case(
            existing, source_interaction_id, source_interaction_title,
            what_failed, why_it_failed, suggested_prevention, tags,
        )
        _write(data)
        return merged

    fc_id = max([f.get("id", 0) for f in data["failure_cases"]], default=0) + 1
    entry = {
        "id": fc_id,
        "organization_id": organization_id,
        "source_interaction_ids": [source_interaction_id],
        "source_interaction_title": source_interaction_title,
        "what_failed": what_failed,
        "normalized_key": _normalize_key(what_failed),
        "why_it_failed": why_it_failed,
        "missing_context": missing_context,
        "human_review_required": human_review_required,
        "suggested_prevention": suggested_prevention,
        "tags": tags or [],
        "status": "Identified",
        "evidence_count": 1,
        "evidence_excerpts": [what_failed[:200]],
        "last_seen_at": _now_iso(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    data["failure_cases"].append(entry)
    _write(data)
    return entry


def get_failure_cases_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [f for f in data["failure_cases"] if f.get("organization_id") == organization_id]


def get_all_failure_cases() -> List[Dict[str, Any]]:
    return _read()["failure_cases"]


def update_failure_case(fc_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for f in data["failure_cases"]:
        if f["id"] == fc_id:
            f.update(updates)
            f["updated_at"] = _now_iso()
            _write(data)
            return f
    return None


# ---- Adoption Risk Notes / Human System Notes ----

def _find_or_create_adoption_risk_note(
    organization_id: int,
    risk_type: str,
    description: str,
) -> tuple[Optional[Dict[str, Any]], bool]:
    data = _read()
    notes = data.get("adoption_risk_notes") or []
    existing = [a for a in notes if a.get("organization_id") == organization_id]
    norm_candidate = _normalize_key(f"{risk_type} {description}")
    for ar in existing:
        norm_existing = _normalize_key(f"{ar.get('risk_type', '')} {ar.get('description', '')}")
        if norm_candidate == norm_existing:
            return ar, True
    for ar in existing:
        combined = f"{ar.get('risk_type', '')} {ar.get('description', '')}"
        overlap = _word_overlap(f"{risk_type} {description}", combined)
        if overlap >= SIMILARITY_THRESHOLD:
            return ar, True
    return None, False


def _merge_into_adoption_risk_note(
    ar: Dict[str, Any],
    source_interaction_id: int,
    source_interaction_title: str,
    risk_type: str,
    description: str,
    severity: str,
    related_staff_role: str,
    suggested_mitigation: str,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    source_ids = ar.get("source_interaction_ids") or [ar.get("source_interaction_id")]
    if source_interaction_id not in source_ids:
        source_ids.append(source_interaction_id)
    evidence_excerpts = ar.get("evidence_excerpts") or []
    excerpt = description[:200]
    if excerpt not in evidence_excerpts:
        evidence_excerpts.append(excerpt)

    ar["source_interaction_ids"] = source_ids
    ar["source_interaction_title"] = source_interaction_title
    ar["evidence_count"] = len(source_ids)
    ar["evidence_excerpts"] = evidence_excerpts
    ar["last_seen_at"] = _now_iso()
    ar["risk_type"] = _merge_strings_nonempty(ar.get("risk_type", ""), risk_type)
    ar["description"] = _merge_strings_nonempty(ar.get("description", ""), description)
    ar["severity"] = severity if severity != "Low" else ar.get("severity", "Low")
    ar["related_staff_role"] = _merge_strings_nonempty(ar.get("related_staff_role", ""), related_staff_role)
    ar["suggested_mitigation"] = _merge_strings_nonempty(ar.get("suggested_mitigation", ""), suggested_mitigation)
    ar["tags"] = _merge_lists_unique(ar.get("tags", []), tags or [])
    ar["updated_at"] = _now_iso()
    return ar


def save_adoption_risk_note(
    organization_id: int,
    source_interaction_id: int,
    source_interaction_title: str,
    risk_type: str,
    description: str,
    severity: str = "Low",
    related_staff_role: str = "",
    suggested_mitigation: str = "",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data = _read()
    existing, found = _find_or_create_adoption_risk_note(organization_id, risk_type, description)
    if found and existing is not None:
        merged = _merge_into_adoption_risk_note(
            existing, source_interaction_id, source_interaction_title,
            risk_type, description, severity, related_staff_role,
            suggested_mitigation, tags,
        )
        _write(data)
        return merged

    if "adoption_risk_notes" not in data:
        data["adoption_risk_notes"] = []
    ar_id = max([a.get("id", 0) for a in data["adoption_risk_notes"]], default=0) + 1
    entry = {
        "id": ar_id,
        "organization_id": organization_id,
        "source_interaction_ids": [source_interaction_id],
        "source_interaction_title": source_interaction_title,
        "risk_type": risk_type,
        "description": description,
        "normalized_key": _normalize_key(f"{risk_type} {description}"),
        "severity": severity,
        "related_staff_role": related_staff_role,
        "suggested_mitigation": suggested_mitigation,
        "tags": tags or [],
        "evidence_count": 1,
        "evidence_excerpts": [description[:200]],
        "last_seen_at": _now_iso(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    data["adoption_risk_notes"].append(entry)
    _write(data)
    return entry


def get_adoption_risk_notes_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    notes = data.get("adoption_risk_notes") or []
    return [a for a in notes if a.get("organization_id") == organization_id]


def get_all_adoption_risk_notes() -> List[Dict[str, Any]]:
    data = _read()
    return data.get("adoption_risk_notes") or []


def update_adoption_risk_note(ar_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    notes = data.get("adoption_risk_notes") or []
    for a in notes:
        if a["id"] == ar_id:
            a.update(updates)
            a["updated_at"] = _now_iso()
            _write(data)
            return a
    return None


def delete_adoption_risk_note(ar_id: int) -> bool:
    data = _read()
    notes = data.get("adoption_risk_notes") or []
    before = len(notes)
    data["adoption_risk_notes"] = [a for a in notes if a["id"] != ar_id]
    if len(data["adoption_risk_notes"]) < before:
        _write(data)
        return True
    return False


# ---- Auto-save from interaction summary ----

KNOWN_SOURCE_TYPES = [
    "FAQ documents", "Past meeting notes", "Past emails or drafts",
    "Policies", "Templates", "Q&A records", "Training materials",
    "Reports", "Public website content", "Other",
]


def auto_save_workflow_opportunity_from_summary(
    organization_id: int,
    interaction_id: int,
    interaction_title: str,
    summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    saved = []
    ai_points = summary.get("possible_ai_insertion_points") or []
    pain_points = summary.get("workflow_pain_points") or []
    staff_concerns = summary.get("staff_concerns") or []
    eval_risks = summary.get("evaluation_or_recognition_risks") or []
    training_needs = summary.get("training_or_followup_needs") or []
    safeguards = summary.get("adoption_safeguards") or []
    for i, ap in enumerate(ai_points):
        staff_impact_text = ""
        if staff_concerns:
            staff_impact_text = staff_concerns[0][:200]
        elif training_needs:
            staff_impact_text = training_needs[0][:200]
        risk_level = "Unknown"
        if eval_risks:
            risk_level = "Medium" if "unclear" in eval_risks[0].lower() else "Low"
        if staff_concerns and any("fear" in c.lower() for c in staff_concerns):
            risk_level = "Medium"
        questions = []
        if summary.get("missing_knowledge_or_data"):
            questions.append(summary["missing_knowledge_or_data"][0][:150])
        opp = save_workflow_opportunity(
            organization_id=organization_id,
            source_interaction_id=interaction_id,
            source_interaction_title=interaction_title,
            title=f"AI Support: {ap[:80]}",
            current_process=summary.get("current_workflow", "Not documented"),
            pain_point=pain_points[i] if i < len(pain_points) else "Not specified",
            possible_ai_support=ap,
            knowledge_sources_needed=summary.get("information_or_documents_used") or [],
            human_review_points=summary.get("required_human_review") or [],
            risks_or_exceptions=[
                f.get("what_failed", "") for f in (summary.get("failure_cases_or_exceptions") or [])
            ],
            tags=summary.get("workflow_tags") or [],
            status="Identified",
            staff_impact=staff_impact_text,
            adoption_risk_level=risk_level,
            next_discovery_questions=questions,
            human_review_required=", ".join(summary.get("required_human_review") or [])[:300],
            required_knowledge_sources=summary.get("information_or_documents_used") or [],
            known_failure_cases=[
                f.get("what_failed", "") for f in (summary.get("failure_cases_or_exceptions") or [])
            ],
        )
        saved.append(opp)
    return saved


def auto_save_adoption_risk_notes_from_summary(
    organization_id: int,
    interaction_id: int,
    interaction_title: str,
    summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    saved = []
    notes_data = summary.get("adoption_safeguards") or []
    for safeguard in notes_data:
        note = save_adoption_risk_note(
            organization_id=organization_id,
            source_interaction_id=interaction_id,
            source_interaction_title=interaction_title,
            risk_type="Adoption Safeguard",
            description=safeguard[:300],
            severity="Low",
            related_staff_role="All staff",
            suggested_mitigation=safeguard[:200],
            tags=summary.get("workflow_tags") or [],
        )
        saved.append(note)
    staff_concerns = summary.get("staff_concerns") or []
    for concern in staff_concerns:
        risk_type = "Staff Concern"
        severity = "Medium" if "fear" in concern.lower() or "replace" in concern.lower() else "Low"
        note = save_adoption_risk_note(
            organization_id=organization_id,
            source_interaction_id=interaction_id,
            source_interaction_title=interaction_title,
            risk_type=risk_type,
            description=concern[:300],
            severity=severity,
            related_staff_role="All staff",
            suggested_mitigation=concern[:200],
            tags=summary.get("workflow_tags") or [],
        )
        saved.append(note)
    eval_risks = summary.get("evaluation_or_recognition_risks") or []
    for risk in eval_risks:
        note = save_adoption_risk_note(
            organization_id=organization_id,
            source_interaction_id=interaction_id,
            source_interaction_title=interaction_title,
            risk_type="Evaluation Risk",
            description=risk[:300],
            severity="Medium",
            related_staff_role="Program leads",
            suggested_mitigation="Review evaluation criteria to include AI-assisted workflows.",
            tags=summary.get("workflow_tags") or [],
        )
        saved.append(note)
    return saved


def auto_save_failure_cases_from_summary(
    organization_id: int,
    interaction_id: int,
    interaction_title: str,
    summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    saved = []
    for fc in summary.get("failure_cases_or_exceptions") or []:
        case = save_failure_case(
            organization_id=organization_id,
            source_interaction_id=interaction_id,
            source_interaction_title=interaction_title,
            what_failed=fc.get("what_failed", ""),
            why_it_failed=fc.get("why", ""),
            missing_context=fc.get("missing_context", ""),
            human_review_required=fc.get("human_review_required", ""),
            suggested_prevention=fc.get("suggested_prevention", ""),
            tags=summary.get("workflow_tags") or [],
        )
        saved.append(case)
    return saved


def auto_save_knowledge_sources_from_summary(
    organization_id: int,
    summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    saved = []
    info_sources = summary.get("information_or_documents_used") or []
    for src_name in info_sources:
        matched_type = "Other"
        for kt in KNOWN_SOURCE_TYPES:
            if any(kw in src_name.lower() for kw in kt.lower().replace("/", " ").split()):
                matched_type = kt
                break
        ks = save_knowledge_source(
            organization_id=organization_id,
            source_type=matched_type,
            name=src_name,
            description=f"Automatically identified from interaction notes — organized as '{matched_type}'",
            location_note="Local — no external storage accessed",
        )
        saved.append(ks)
    return saved
