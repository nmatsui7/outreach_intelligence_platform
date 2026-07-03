import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "adoption_planning.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read() -> Dict[str, Any]:
    if not DATA_PATH.exists() or not DATA_PATH.read_text(encoding="utf-8").strip():
        return {"adoption_plans": [], "pilot_plans": [], "success_metrics": []}
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _write(data: Dict[str, Any]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---- Adoption Plans ----

def get_adoption_plan_for_org(organization_id: int) -> Optional[Dict[str, Any]]:
    data = _read()
    plans = [p for p in data["adoption_plans"] if p.get("organization_id") == organization_id]
    if plans:
        plans.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        return plans[0]
    return None


def save_adoption_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    data = _read()
    plan_id = max([p.get("plan_id", 0) for p in data["adoption_plans"]], default=0) + 1
    now = _now_iso()
    plan["plan_id"] = plan_id
    plan.setdefault("status", "Draft")
    plan["created_at"] = now
    plan["updated_at"] = now
    data["adoption_plans"].append(plan)
    _write(data)
    return plan


def update_adoption_plan(plan_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for p in data["adoption_plans"]:
        if p["plan_id"] == plan_id:
            p.update(updates)
            p["updated_at"] = _now_iso()
            _write(data)
            return p
    return None


def get_all_adoption_plans() -> List[Dict[str, Any]]:
    return _read()["adoption_plans"]


def delete_adoption_plan(plan_id: int) -> bool:
    data = _read()
    before = len(data["adoption_plans"])
    data["adoption_plans"] = [p for p in data["adoption_plans"] if p["plan_id"] != plan_id]
    if len(data["adoption_plans"]) < before:
        _write(data)
        return True
    return False


# ---- Pilot Plans ----

def get_pilot_plans_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [p for p in data["pilot_plans"] if p.get("organization_id") == organization_id]


def get_pilot_plan(pilot_id: int) -> Optional[Dict[str, Any]]:
    data = _read()
    for p in data["pilot_plans"]:
        if p["pilot_id"] == pilot_id:
            return p
    return None


def get_all_pilot_plans() -> List[Dict[str, Any]]:
    return _read()["pilot_plans"]


def save_pilot_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    data = _read()
    pilot_id = max([p.get("pilot_id", 0) for p in data["pilot_plans"]], default=0) + 1
    now = _now_iso()
    plan["pilot_id"] = pilot_id
    plan.setdefault("status", "Draft")
    plan["created_at"] = now
    plan["updated_at"] = now
    data["pilot_plans"].append(plan)
    _write(data)
    return plan


def update_pilot_plan(pilot_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for p in data["pilot_plans"]:
        if p["pilot_id"] == pilot_id:
            p.update(updates)
            p["updated_at"] = _now_iso()
            _write(data)
            return p
    return None


def delete_pilot_plan(pilot_id: int) -> bool:
    data = _read()
    before = len(data["pilot_plans"])
    data["pilot_plans"] = [p for p in data["pilot_plans"] if p["pilot_id"] != pilot_id]
    if len(data["pilot_plans"]) < before:
        _write(data)
        return True
    return False


# ---- Success Metrics ----

def get_success_metrics_for_org(organization_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [m for m in data["success_metrics"] if m.get("organization_id") == organization_id]


def get_all_success_metrics() -> List[Dict[str, Any]]:
    return _read()["success_metrics"]


def get_success_metrics_for_pilot(pilot_id: int) -> List[Dict[str, Any]]:
    data = _read()
    return [m for m in data["success_metrics"] if m.get("pilot_id") == pilot_id]


def save_success_metric(metric: Dict[str, Any]) -> Dict[str, Any]:
    data = _read()
    metric_id = max([m.get("metric_id", 0) for m in data["success_metrics"]], default=0) + 1
    now = _now_iso()
    metric["metric_id"] = metric_id
    metric.setdefault("status", "Proposed")
    metric["created_at"] = now
    metric["updated_at"] = now
    data["success_metrics"].append(metric)
    _write(data)
    return metric


def update_success_metric(metric_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    data = _read()
    for m in data["success_metrics"]:
        if m["metric_id"] == metric_id:
            m.update(updates)
            m["updated_at"] = _now_iso()
            _write(data)
            return m
    return None


def delete_success_metric(metric_id: int) -> bool:
    data = _read()
    before = len(data["success_metrics"])
    data["success_metrics"] = [m for m in data["success_metrics"] if m["metric_id"] != metric_id]
    if len(data["success_metrics"]) < before:
        _write(data)
        return True
    return False
