from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from pathlib import Path
import json

TASKS_PATH = Path(__file__).resolve().parents[1] / "data" / "tasks.json"


def _read() -> List[Dict[str, Any]]:
    try:
        with open(TASKS_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write(rows: List[Dict[str, Any]]) -> None:
    TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TASKS_PATH, "w") as f:
        json.dump(rows, f, indent=2)


def get_all_tasks() -> List[Dict[str, Any]]:
    return _read()


def get_tasks_for_org(organization_id: int) -> List[Dict[str, Any]]:
    return [t for t in _read() if t.get("organization_id") == organization_id]


def add_task(task: Dict[str, Any]) -> Dict[str, Any]:
    rows = _read()
    max_id = max((t.get("task_id", 0) for t in rows), default=0)
    now = date.today().isoformat()
    new_task = {
        "task_id": max_id + 1,
        "organization_id": task.get("organization_id"),
        "source_interaction_id": task.get("source_interaction_id"),
        "title": task.get("title", ""),
        "description": task.get("description", ""),
        "due_date": task.get("due_date", ""),
        "priority": task.get("priority", "Medium"),
        "status": "Open",
        "created_at": now,
        "updated_at": now,
    }
    rows.append(new_task)
    _write(rows)
    return new_task


def update_task(task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rows = _read()
    for task in rows:
        if task["task_id"] == task_id:
            allowed_keys = {"title", "description", "due_date", "priority", "status"}
            for k, v in updates.items():
                if k in allowed_keys:
                    task[k] = v
            task["updated_at"] = date.today().isoformat()
            _write(rows)
            return task
    return None


def delete_task(task_id: int) -> bool:
    rows = _read()
    new_rows = [t for t in rows if t["task_id"] != task_id]
    if len(new_rows) == len(rows):
        return False
    _write(new_rows)
    return True


def suggest_tasks_from_interaction(
    notes: str,
    interaction_type: str,
    org_id: int,
    interaction_id: int,
) -> List[Dict[str, Any]]:
    notes_lower = notes.lower()
    today = date.today()

    task_templates: List[Dict[str, Any]] = [
        {
            "keywords": ["pilot", "proposal", "workshop", "program"],
            "title": "Prepare pilot proposal document",
            "description": "Draft and share a pilot proposal based on the discussion.",
            "priority": "High",
            "due_days": 14,
        },
        {
            "keywords": ["follow-up", "follow up", "next steps", "recap", "summary"],
            "title": "Send follow-up summary",
            "description": "Compile and send a summary of the discussion with agreed next steps.",
            "priority": "High",
            "due_days": 3,
        },
        {
            "keywords": ["documentation", "docs", "records", "reports", "notes"],
            "title": "Review documentation workflow",
            "description": "Assess current documentation practices and identify areas for AI assistance.",
            "priority": "Medium",
            "due_days": 21,
        },
        {
            "keywords": ["meeting", "agenda", "schedule", "discuss"],
            "title": "Schedule follow-up meeting",
            "description": "Book a follow-up meeting to continue the discussion.",
            "priority": "Medium",
            "due_days": 14,
        },
        {
            "keywords": ["train", "workshop", "literacy", "education", "learning"],
            "title": "Prepare AI literacy workshop materials",
            "description": "Develop introductory AI literacy materials tailored to the organization's context.",
            "priority": "Medium",
            "due_days": 30,
        },
        {
            "keywords": ["grant", "funding", "proposal", "budget"],
            "title": "Research grant opportunities",
            "description": "Identify potential funding sources for AI adoption initiatives.",
            "priority": "Medium",
            "due_days": 30,
        },
        {
            "keywords": ["staff", "capacity", "training", "readiness"],
            "title": "Assess staff readiness for AI tools",
            "description": "Conduct a staff readiness assessment to identify training needs and concerns.",
            "priority": "High",
            "due_days": 14,
        },
        {
            "keywords": ["outreach", "community", "engagement", "public"],
            "title": "Plan community outreach strategy",
            "description": "Develop a plan for community-facing AI literacy or education initiatives.",
            "priority": "Medium",
            "due_days": 30,
        },
    ]

    suggested = []
    matched_indices = set()

    for i, tpl in enumerate(task_templates):
        if any(kw in notes_lower for kw in tpl["keywords"]):
            matched_indices.add(i)
            due = (today + timedelta(days=tpl["due_days"])).isoformat()
            suggested.append({
                "title": tpl["title"],
                "description": tpl["description"],
                "due_date": due,
                "priority": tpl["priority"],
            })

    if len(suggested) < 2:
        for i, tpl in enumerate(task_templates):
            if i not in matched_indices:
                due = (today + timedelta(days=tpl["due_days"])).isoformat()
                suggested.append({
                    "title": tpl["title"],
                    "description": tpl["description"],
                    "due_date": due,
                    "priority": tpl["priority"],
                })
                matched_indices.add(i)
                if len(suggested) >= 3:
                    break

    return suggested[:3]
