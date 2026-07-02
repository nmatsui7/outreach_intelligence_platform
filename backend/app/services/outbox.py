import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

OUTBOX_PATH = Path(__file__).resolve().parents[1] / "data" / "outbox.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_outbox() -> List[Dict[str, Any]]:
    if not OUTBOX_PATH.exists() or not OUTBOX_PATH.read_text(encoding="utf-8").strip():
        return []
    return json.loads(OUTBOX_PATH.read_text(encoding="utf-8"))


def save_demo_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    rows = read_outbox()
    item = {
        "id": max((row.get("id", 0) for row in rows), default=0) + 1,
        **draft,
        "status": "Saved to Demo Outbox - Not Sent",
        "created_at": _now_iso(),
    }
    rows.append(item)
    OUTBOX_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return item
