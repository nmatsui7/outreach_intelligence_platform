import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

SUMMARIES_PATH = Path(__file__).resolve().parents[1] / "data" / "interaction_summaries.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read() -> List[Dict[str, Any]]:
    if not SUMMARIES_PATH.exists() or not SUMMARIES_PATH.read_text(encoding="utf-8").strip():
        return []
    return json.loads(SUMMARIES_PATH.read_text(encoding="utf-8"))


def _write(rows: List[Dict[str, Any]]) -> None:
    SUMMARIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARIES_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def save_summary(interaction_id: int, organization_id: int, summary: Dict[str, Any]) -> Dict[str, Any]:
    rows = _read()
    now = _now_iso()
    entry = {
        "summary_id": max((r.get("summary_id", 0) for r in rows), default=0) + 1,
        "interaction_id": interaction_id,
        "organization_id": organization_id,
        "created_at": now,
        "updated_at": now,
        **summary,
    }
    # Replace any existing summary for the same interaction
    rows = [r for r in rows if r.get("interaction_id") != interaction_id]
    rows.append(entry)
    _write(rows)
    return entry


def get_summary_for_interaction(interaction_id: int) -> Optional[Dict[str, Any]]:
    rows = _read()
    return next((r for r in rows if r.get("interaction_id") == interaction_id), None)


def get_summaries_for_org(organization_id: int) -> List[Dict[str, Any]]:
    return [r for r in _read() if r.get("organization_id") == organization_id]


def get_all_summaries() -> List[Dict[str, Any]]:
    return _read()
