import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import CRMConnector

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "organizations.json"


def _now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format (second precision)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def backfill_timestamps() -> int:
    """
    Safe backfill: assign created_at / updated_at to any existing records
    that are missing them.  Uses the current timestamp (with a comment marker)
    so it is obvious these are backfilled rather than original creation dates.

    Returns the number of records updated.
    """
    rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    now = _now_iso()
    updated = 0
    for row in rows:
        changed = False
        if "created_at" not in row:
            row["created_at"] = f"{now} (backfilled)"
            changed = True
        if "updated_at" not in row:
            row["updated_at"] = f"{now} (backfilled)"
            changed = True
        if changed:
            updated += 1
    if updated:
        DATA_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return updated


class LocalJsonCRMConnector(CRMConnector):
    """Local demo CRM connector. Replace with Salesforce/HubSpot later."""

    def _read(self) -> List[Dict[str, Any]]:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))

    def _write(self, rows: List[Dict[str, Any]]) -> None:
        DATA_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def list_organizations(self) -> List[Dict[str, Any]]:
        return self._read()

    def get_organization(self, organization_id: int) -> Optional[Dict[str, Any]]:
        return next((row for row in self._read() if row["id"] == organization_id), None)

    def update_status(self, organization_id: int, status: str) -> Optional[Dict[str, Any]]:
        rows = self._read()
        for row in rows:
            if row["id"] == organization_id:
                row["status"] = status
                row["updated_at"] = _now_iso()
                self._write(rows)
                return row
        return None

    def add_organization(self, organization: Dict[str, Any]) -> Dict[str, Any]:
        rows = self._read()
        normalized_name = organization["name"].strip().lower()
        existing = next(
            (row for row in rows if row["name"].strip().lower() == normalized_name),
            None,
        )
        if existing:
            return existing

        now = _now_iso()
        item = {
            "id": max((row.get("id", 0) for row in rows), default=0) + 1,
            "created_at": now,
            "updated_at": now,
            **organization,
        }
        rows.append(item)
        self._write(rows)
        return item

    def update_org(self, organization_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rows = self._read()
        for row in rows:
            if row["id"] == organization_id:
                row.update(updates)
                row["updated_at"] = _now_iso()
                self._write(rows)
                return row
        return None
