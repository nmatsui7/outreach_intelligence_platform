"""
Field Mapping Documentation and Helpers
========================================

The MVP uses a lightweight local data model (JSON files). Some internal field
names differ from user-facing CSV / API labels and are mapped at import/export
boundaries.

┌─────────────────────────┬────────────────────────┬──────────────────────────────┐
│ User-facing label       │ Internal key           │ Notes                        │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ organization_type       │ category               │ Mapped on import (CSV,       │
│                         │                        │ Research Intake, Discovery). │
│                         │                        │ Exported as organization_type│
│                         │                        │ in CSV and JSON.             │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ program_area            │ program_area (optional)│ Stored as a top-level key    │
│                         │                        │ only on CSV import. Research │
│                         │                        │ Intake / Discovery embed it   │
│                         │                        │ in mission_notes.            │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ notes / description /   │ mission_notes          │ All free-text fields         │
│ why_relevant /          │                        │ (description, program_area,  │
│ suggested_outreach_angle│                        │ why_relevant,                │
│ / source_url            │                        │ suggested_outreach_angle,    │
│                         │                        │ source_url, notes) are       │
│                         │                        │ concatenated into a single    │
│                         │                        │ mission_notes string on      │
│                         │                        │ import.                      │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ last_interaction        │ last_interaction       │ Auto-generated from          │
│                         │                        │ interactions or import.      │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ pain_points             │ pain_points            │ Array of strings, same in    │
│                         │                        │ both layers.                 │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ status / name / website │ (same)                 │ Used identically in both     │
│ / contact_name /        │                        │ layers.                      │
│ contact_email /         │                        │                              │
│ phone_number / id       │                        │                              │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ created_at              │ created_at             │ Auto-set by                  │
│                         │                        │ LocalJsonCRMConnector on     │
│                         │                        │ creation.  Existing records  │
│                         │                        │ without this field get a     │
│                         │                        │ backfilled value marked      │
│                         │                        │ "(backfilled)".              │
├─────────────────────────┼────────────────────────┼──────────────────────────────┤
│ updated_at              │ updated_at             │ Auto-set on every            │
│                         │                        │ add_organization,            │
│                         │                        │ update_org, or               │
│                         │                        │ update_status call.          │
└─────────────────────────┴────────────────────────┴──────────────────────────────┘

Because program_area, description, why_relevant, suggested_outreach_angle,
source_url, and notes are not stored as individual fields in the internal
model, CSV/JSON export recovers them only when they were stored separately.
For organizations added through Research Intake or Organization Discovery,
these values are embedded in mission_notes and are not individually
recoverable. This is a known limitation of the lightweight data model.
"""

from typing import Dict, Any, Set


# Fields that are shared identically between internal and external layers
_SHARED_FIELDS: Set[str] = {
    "id", "name", "website", "contact_name", "contact_email",
    "phone_number", "status", "pain_points", "last_interaction",
}

# Fields where the external label differs from the internal key
_EXTERNAL_TO_INTERNAL: Dict[str, str] = {
    "organization_type": "category",
}

_INTERNAL_TO_EXTERNAL: Dict[str, str] = {
    "category": "organization_type",
}


def to_internal(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a user-facing / import record to the internal storage format.

    Preserves all shared fields as-is, renames 'organization_type' to
    'category', and keeps any extra fields (e.g. program_area) so they
    survive a round-trip through export.
    """
    result: Dict[str, Any] = {}
    for k, v in record.items():
        internal_key = _EXTERNAL_TO_INTERNAL.get(k, k)
        result[internal_key] = v
    return result


def to_display(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an internal organization record to a display / export record.

    Renames 'category' back to 'organization_type'.  Exports 'notes' as a
    copy of 'mission_notes' for user-facing contexts.  Keeps all other
    fields (including optional extras like program_area) as-is.
    """
    result: Dict[str, Any] = {}
    for k, v in record.items():
        external_key = _INTERNAL_TO_EXTERNAL.get(k, k)
        result[external_key] = v
    # Provide a user-facing 'notes' alias for mission_notes
    if "mission_notes" in record and "notes" not in result:
        result["notes"] = record["mission_notes"]
    return result
