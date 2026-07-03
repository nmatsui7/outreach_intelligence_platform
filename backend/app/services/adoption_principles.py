import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "adoption_principles.json"
SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "adoption_principles_seed.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed_if_empty() -> None:
    if DATA_PATH.exists() and DATA_PATH.read_text(encoding="utf-8").strip():
        return
    if not SEED_PATH.exists():
        return
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    records = []
    for i, item in enumerate(seed):
        records.append({
            "id": i + 1,
            "title": item["title"],
            "summary": item["summary"],
            "category": item["category"],
            "source_note_id": item.get("source_note_id"),
            "source_note_title": item.get("source_note_title", ""),
            "evidence_excerpt": item.get("evidence_excerpt", ""),
            "applies_to": item.get("applies_to", []),
            "recommended_use": item.get("recommended_use", ""),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        })
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _read() -> List[Dict[str, Any]]:
    _seed_if_empty()
    if not DATA_PATH.exists() or not DATA_PATH.read_text(encoding="utf-8").strip():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def get_all() -> List[Dict[str, Any]]:
    return _read()


def get_by_id(principle_id: int) -> Optional[Dict[str, Any]]:
    for p in _read():
        if p["id"] == principle_id:
            return p
    return None


def get_by_category(category: str) -> List[Dict[str, Any]]:
    return [p for p in _read() if p.get("category") == category]


def get_categories() -> List[str]:
    cats: set = set()
    for p in _read():
        c = p.get("category")
        if c:
            cats.add(c)
    return sorted(cats)


def find_by_applies_to(area: str) -> List[Dict[str, Any]]:
    return [p for p in _read() if area in p.get("applies_to", [])]


CATEGORY_LABELS: Dict[str, str] = {
    "workflow_analysis": "Workflow Analysis",
    "human_system": "Human System",
    "incentives_and_evaluation": "Incentives & Evaluation",
    "knowledge_sources": "Knowledge Sources",
    "failure_cases": "Failure Cases",
    "pilot_selection": "Pilot Selection",
    "training_design": "Training Design",
    "tool_selection": "Tool Selection",
    "human_review": "Human Review",
}
