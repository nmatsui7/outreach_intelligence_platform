import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List
from fastapi import UploadFile, HTTPException

ATTACHMENTS_DIR = Path(__file__).resolve().parents[1] / "data" / "attachments"
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/png",
    "image/jpeg",
    "text/csv",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".csv"}
MAX_SIZE_BYTES = 5 * 1024 * 1024


def _attachments_index_path() -> Path:
    return ATTACHMENTS_DIR / "_index.json"


def _ensure_dir():
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)


def _read_index() -> Dict[str, List[Dict[str, Any]]]:
    _ensure_dir()
    path = _attachments_index_path()
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_index(index: Dict[str, List[Dict[str, Any]]]):
    _ensure_dir()
    _attachments_index_path().write_text(json.dumps(index, indent=2), encoding="utf-8")


async def save_attachment(draft_id: int, file: UploadFile) -> Dict[str, Any]:
    _ensure_dir()

    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(content)} bytes). Maximum is {MAX_SIZE_BYTES} bytes (5 MB).",
        )

    mime_type = file.content_type or "application/octet-stream"
    timestamp = int(time.time() * 1000)
    attachment_id = f"att_{timestamp}_{os.urandom(4).hex()}"
    stored_filename = f"{attachment_id}{ext}"

    stored_path = ATTACHMENTS_DIR / stored_filename
    stored_path.write_bytes(content)

    meta = {
        "attachment_id": attachment_id,
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "mime_type": mime_type,
        "size_bytes": len(content),
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    index = _read_index()
    key = str(draft_id)
    if key not in index:
        index[key] = []
    index[key].append(meta)
    _write_index(index)

    return meta


def list_attachments(draft_id: int) -> List[Dict[str, Any]]:
    index = _read_index()
    return index.get(str(draft_id), [])


def delete_attachment(draft_id: int, attachment_id: str) -> bool:
    index = _read_index()
    key = str(draft_id)
    attachments = index.get(key, [])
    meta = next((a for a in attachments if a["attachment_id"] == attachment_id), None)
    if not meta:
        return False

    stored_path = ATTACHMENTS_DIR / meta["stored_filename"]
    if stored_path.exists():
        stored_path.unlink()

    index[key] = [a for a in attachments if a["attachment_id"] != attachment_id]
    if not index[key]:
        del index[key]
    _write_index(index)
    return True
