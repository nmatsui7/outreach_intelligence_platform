import csv
import io
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    from app.connectors.local_json import LocalJsonCRMConnector
    from app.services.outbox import read_outbox
    from app.services.attachments import _read_index as read_attachment_index
    from app.services.interactions import get_all_interactions
    from app.services.field_mapper import to_display, to_internal
except ModuleNotFoundError:
    from backend.app.connectors.local_json import LocalJsonCRMConnector
    from backend.app.services.outbox import read_outbox
    from backend.app.services.attachments import _read_index as read_attachment_index
    from backend.app.services.interactions import get_all_interactions
    from backend.app.services.field_mapper import to_display, to_internal

CSV_FIELDS = [
    "name", "website", "contact_name", "contact_email", "phone_number",
    "organization_type", "program_area", "description", "why_relevant",
    "suggested_outreach_angle", "source_url", "notes", "status",
]

EXPORT_CSV_FIELDS = [
    "id", "name", "website", "contact_name", "contact_email", "phone_number",
    "organization_type", "program_area", "description", "why_relevant",
    "suggested_outreach_angle", "source_url", "notes", "status",
    "created_at", "updated_at",
]

CSV_TEMPLATE = """name,website,contact_name,contact_email,phone_number,organization_type,program_area,description,why_relevant,suggested_outreach_angle,source_url,notes,status
Waterloo Community Arts Council,https://example-arts.org,Jane Smith,jane@example-arts.org,519-555-1234,Community nonprofit,Arts and culture programming,Local arts council serving the region,Strong community reach and existing programs,Propose AI-assisted program planning workshop,https://example-arts.org/about,Interested in digital skills development,Not Contacted"""


def _normalize_org_name(name: str) -> str:
    return name.strip().lower()


def _map_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    mapped = {
        "name": row.get("name", "").strip(),
        "website": row.get("website", "").strip(),
        "contact_name": row.get("contact_name", "").strip() or "General Inquiries",
        "contact_email": row.get("contact_email", "").strip(),
        "phone_number": row.get("phone_number", "").strip(),
        "organization_type": row.get("organization_type", "").strip(),
        "program_area": row.get("program_area", "").strip(),
        "description": row.get("description", "").strip(),
        "why_relevant": row.get("why_relevant", "").strip(),
        "suggested_outreach_angle": row.get("suggested_outreach_angle", "").strip(),
        "source_url": row.get("source_url", "").strip(),
        "notes": row.get("notes", "").strip(),
        "status": row.get("status", "").strip() or "Not Contacted",
    }
    return mapped


def _build_mapped_notes(mapped: Dict[str, Any]) -> str:
    parts = []
    if mapped.get("description"):
        parts.append(mapped["description"])
    if mapped.get("program_area"):
        parts.append(f"Program area: {mapped['program_area']}")
    if mapped.get("why_relevant"):
        parts.append(f"Why relevant: {mapped['why_relevant']}")
    if mapped.get("suggested_outreach_angle"):
        parts.append(f"Suggested outreach angle: {mapped['suggested_outreach_angle']}")
    if mapped.get("source_url"):
        parts.append(f"Source URL: {mapped['source_url']}")
    if mapped.get("notes"):
        parts.append(f"Notes: {mapped['notes']}")
    return " ".join(parts).strip() or "Imported via CSV upload."


def parse_csv(content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    rows = []
    errors = []
    reader = csv.DictReader(io.StringIO(content))
    line_num = 2  # header is line 1
    for row in reader:
        mapped = _map_csv_row(row)
        row_errors = _validate_row(mapped)
        if row_errors:
            errors.append(f"Row {line_num}: {row_errors}")
        else:
            rows.append(mapped)
        line_num += 1
    return rows, errors


def _validate_row(mapped: Dict[str, Any]) -> str:
    if not mapped.get("name"):
        return "Missing required field 'name'."
    return ""


def check_duplicate(mapped: Dict[str, Any], existing_orgs: List[Dict[str, Any]]) -> bool:
    name = _normalize_org_name(mapped.get("name", ""))
    website = mapped.get("website", "").strip().lower()
    for org in existing_orgs:
        if _normalize_org_name(org.get("name", "")) == name:
            if not website or not org.get("website"):
                return True
            if org.get("website", "").strip().lower() == website:
                return True
    return False


_staged_imports: Dict[str, List[Dict[str, Any]]] = {}


def stage_import(upload_id: str, rows: List[Dict[str, Any]]):
    _staged_imports[upload_id] = rows


def get_staged_rows(upload_id: str) -> List[Dict[str, Any]]:
    return _staged_imports.pop(upload_id, [])


def import_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    crm = LocalJsonCRMConnector()
    existing = crm.list_organizations()

    imported = 0
    duplicates = 0
    for mapped in rows:
        if check_duplicate(mapped, existing):
            duplicates += 1
            continue
        notes = _build_mapped_notes(mapped)
        pain_points = ["Imported via CSV upload", "Workflow improvement", "Human-reviewed outreach planning"]
        # Use the field mapper to convert user-facing names to internal keys
        org = to_internal({
            "name": mapped["name"],
            "organization_type": mapped.get("organization_type") or "Imported",
            "website": mapped.get("website", ""),
            "contact_name": mapped.get("contact_name", "General Inquiries"),
            "contact_email": mapped.get("contact_email", ""),
            "phone_number": mapped.get("phone_number", ""),
            "status": mapped.get("status", "Not Contacted"),
            "mission_notes": notes,
            "pain_points": pain_points,
            "last_interaction": "Imported from CSV.",
            # Store program_area separately so export can recover it
            "program_area": mapped.get("program_area", ""),
        })
        crm.add_organization(org)
        imported += 1
        existing = crm.list_organizations()

    return {
        "imported": imported,
        "duplicates_skipped": duplicates,
        "total_rows_read": len(rows),
    }


def export_csv(orgs: List[Dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(EXPORT_CSV_FIELDS)
    for org in orgs:
        # Convert internal field names to user-facing labels via the mapper
        display = to_display(org)
        writer.writerow([
            display.get("id", ""),
            display.get("name", ""),
            display.get("website", ""),
            display.get("contact_name", ""),
            display.get("contact_email", ""),
            display.get("phone_number", ""),
            display.get("organization_type", ""),
            display.get("program_area", ""),
            display.get("mission_notes", ""),
            display.get("why_relevant", ""),
            display.get("suggested_outreach_angle", ""),
            display.get("source_url", ""),
            display.get("notes", ""),
            display.get("status", ""),
            display.get("created_at", ""),
            display.get("updated_at", ""),
        ])
    return output.getvalue()


def export_json() -> Dict[str, Any]:
    crm = LocalJsonCRMConnector()
    orgs = crm.list_organizations()
    outbox = read_outbox()
    interactions = get_all_interactions()
    attachment_index = read_attachment_index()

    # Collect attachment metadata without file contents
    attachment_meta = {}
    for draft_id_str, atts in attachment_index.items():
        attachment_meta[draft_id_str] = atts

    return {
        "schema_version": "1.0",
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "organizations": orgs,
        "interactions": interactions,
        "demo_outbox": outbox,
        "attachment_metadata": attachment_meta,
    }
