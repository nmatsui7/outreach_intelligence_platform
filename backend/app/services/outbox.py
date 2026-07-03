import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

OUTBOX_PATH = Path(__file__).resolve().parents[1] / "data" / "outbox.json"
VALID_STATUSES = {"draft", "needs_review", "approved", "sent_manually", "archived"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_outbox() -> List[Dict[str, Any]]:
    if not OUTBOX_PATH.exists() or not OUTBOX_PATH.read_text(encoding="utf-8").strip():
        return []
    return [_normalize_draft(row) for row in json.loads(OUTBOX_PATH.read_text(encoding="utf-8"))]


def _normalize_status(status: str | None) -> str:
    if status in VALID_STATUSES:
        return status
    return "needs_review"


def _normalize_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    recipient_email = draft.get("recipient_email_optional") or draft.get("to") or ""
    normalized = {
        **draft,
        "recipient_name": draft.get("recipient_name") or "",
        "recipient_role": draft.get("recipient_role") or "",
        "recipient_email_optional": recipient_email,
        "to": draft.get("to") or recipient_email,
        "draft_type": draft.get("draft_type") or "follow_up",
        "source_interaction_id": draft.get("source_interaction_id"),
        "source_note_summary_id": draft.get("source_note_summary_id"),
        "status": _normalize_status(draft.get("status")),
        "human_review_notes": draft.get("human_review_notes") or "",
        "created_at": draft.get("created_at") or "",
        "updated_at": draft.get("updated_at") or draft.get("created_at") or "",
    }
    return normalized


def save_demo_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    rows = read_outbox()
    now = _now_iso()
    item = {
        "id": max((row.get("id", 0) for row in rows), default=0) + 1,
        **draft,
        "status": _normalize_status(draft.get("status") or "needs_review"),
        "human_review_notes": draft.get("human_review_notes") or "",
        "created_at": now,
        "updated_at": now,
    }
    item = _normalize_draft(item)
    rows.append(item)
    OUTBOX_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return item


def update_demo_draft(draft_id: int, updates: Dict[str, Any]) -> Dict[str, Any] | None:
    rows = read_outbox()
    for row in rows:
        if row.get("id") != draft_id:
            continue
        allowed = {
            "status",
            "human_review_notes",
            "recipient_name",
            "recipient_role",
            "recipient_email_optional",
            "draft_type",
        }
        for key, value in updates.items():
            if key in allowed:
                row[key] = value
        row["status"] = _normalize_status(row.get("status"))
        row["updated_at"] = _now_iso()
        OUTBOX_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return _normalize_draft(row)
    return None
