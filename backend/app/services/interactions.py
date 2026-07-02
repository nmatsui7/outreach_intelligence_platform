import json
from pathlib import Path
from typing import Dict, Any, List

INTERACTIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "interactions.json"


def read_interactions() -> List[Dict[str, Any]]:
    if not INTERACTIONS_PATH.exists() or not INTERACTIONS_PATH.read_text(encoding="utf-8").strip():
        return []
    return json.loads(INTERACTIONS_PATH.read_text(encoding="utf-8"))


def write_interactions(rows: List[Dict[str, Any]]) -> None:
    INTERACTIONS_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def get_interactions_for_org(organization_id: int) -> List[Dict[str, Any]]:
    return [i for i in read_interactions() if i["organization_id"] == organization_id]


def get_all_interactions() -> List[Dict[str, Any]]:
    return read_interactions()


def add_interaction(interaction: Dict[str, Any]) -> Dict[str, Any]:
    rows = read_interactions()
    item = {
        "id": max((row.get("id", 0) for row in rows), default=0) + 1,
        **interaction,
    }
    rows.append(item)
    write_interactions(rows)
    return item


def update_interaction(interaction_id: int, updates: Dict[str, Any]) -> Dict[str, Any] | None:
    rows = read_interactions()
    for row in rows:
        if row["id"] == interaction_id:
            row.update(updates)
            write_interactions(rows)
            return row
    return None


def delete_interaction(interaction_id: int) -> bool:
    rows = read_interactions()
    new_rows = [row for row in rows if row["id"] != interaction_id]
    if len(new_rows) == len(rows):
        return False
    write_interactions(new_rows)
    return True
