from __future__ import annotations

import inspect
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from backend.services.storage_registry import sync_legacy_globals


class Sprint16RecordMutationRequest(BaseModel):
    group: str
    id: str
    confirmation: str | None = None


def _build_record_mutation_request(payload: dict[str, Any]) -> Sprint16RecordMutationRequest:
    data = dict(payload or {})

    # Compatibility with earlier smoke tests that used record_type/record_id.
    if "group" not in data and "record_type" in data:
        data["group"] = data["record_type"]

    if "id" not in data and "record_id" in data:
        data["id"] = data["record_id"]

    return Sprint16RecordMutationRequest(**data)


def _normalize_record_mutation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload or {})

    # Compatibility with earlier smoke tests that used record_type/record_id.
    if "group" not in data and "record_type" in data:
        data["group"] = data["record_type"]

    if "id" not in data and "record_id" in data:
        data["id"] = data["record_id"]

    # Validate shape when the model exists, then pass a plain dict to legacy logic.
    if "Sprint16RecordMutationRequest" in globals():
        validated = Sprint16RecordMutationRequest(**data)
        return validated.model_dump()

    return data


def _sync_legacy_globals() -> None:
    """Load shared stores/helpers through the storage registry."""
    sync_legacy_globals(globals())


async def _resolve_result(result: Any) -> Any:
    if inspect.isawaitable(result):
        return await result
    return result


from fastapi.responses import HTMLResponse as _Sprint16HTMLResponse
from fastapi import HTTPException as _Sprint16HTTPException


def _sprint16_record_groups() -> Dict[str, Any]:
    return {
        "missions": globals().get("_sprint01_missions", {}),
        "daily_briefs": globals().get("_sprint01_daily_briefs", []),
        "aars": globals().get("_sprint04_aars", []),
        "schoolhouse_courses": globals().get("_schoolhouse_courses", []),
        "schoolhouse_study_sessions": globals().get("_schoolhouse_study_sessions", []),
        "schoolhouse_wrong_answer_reviews": globals().get("_schoolhouse_wrong_answer_reviews", []),
        "schoolhouse_writing_tasks": globals().get("_schoolhouse_writing_tasks", []),
        "charisma_self_assessments": globals().get("_charisma_self_assessments", []),
        "charisma_conversation_aars": globals().get("_charisma_conversation_aars", []),
    }


def _sprint16_records_as_list(group: str) -> list:
    groups = _sprint16_record_groups()
    if group not in groups:
        raise _Sprint16HTTPException(status_code=404, detail=f"Unknown record group: {group}")

    records = groups[group]

    if isinstance(records, dict):
        return list(records.values())

    if isinstance(records, list):
        return records

    return []


def _sprint16_find_record(group: str, record_id: str):
    groups = _sprint16_record_groups()
    if group not in groups:
        raise _Sprint16HTTPException(status_code=404, detail=f"Unknown record group: {group}")

    records = groups[group]

    if isinstance(records, dict):
        if record_id in records:
            return records, record_id, records[record_id]

        for key, value in records.items():
            if isinstance(value, dict) and str(value.get("id")) == str(record_id):
                return records, key, value

    if isinstance(records, list):
        for index, value in enumerate(records):
            if isinstance(value, dict) and str(value.get("id")) == str(record_id):
                return records, index, value

    raise _Sprint16HTTPException(status_code=404, detail=f"Record not found: {record_id}")


def _sprint16_save_group(group: str) -> None:
    save_json = globals().get("_sprint01_save_json")

    try:
        if group == "daily_briefs" and save_json:
            save_json("sprint01_daily_briefs.json", globals().get("_sprint01_daily_briefs", []))
        elif group == "missions" and save_json:
            save_json("sprint01_missions.json", globals().get("_sprint01_missions", {}))
        elif group == "aars" and save_json:
            filename = globals().get("_SPRINT01_AARS_FILE", "sprint04_aars.json")
            save_json(filename, globals().get("_sprint04_aars", []))
        elif group.startswith("schoolhouse") or group.startswith("charisma"):
            saver = globals().get("_sprint12_save_capability_data")
            if saver:
                saver()
    except Exception:
        pass


async def sprint16_record_management_state() -> Dict[str, Any]:
    groups = _sprint16_record_groups()
    counts = {}
    archived_counts = {}

    for group_name in groups:
        records = _sprint16_records_as_list(group_name)
        counts[group_name] = len(records)
        archived_counts[group_name] = len([
            item for item in records
            if isinstance(item, dict) and item.get("archived") is True
        ])

    return {
        "status": "ok",
        "module": "record_management_controls",
        "groups": list(groups.keys()),
        "counts": counts,
        "archived_counts": archived_counts,
        "data": {
            group_name: _sprint16_records_as_list(group_name)
            for group_name in groups
        },
        "actions": [
            "archive",
            "delete",
        ],
        "warning": "Delete removes records from local runtime/persistent JSON where supported. Archive is safer for real records.",
    }


async def sprint16_archive_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    group = payload.get("group")
    record_id = payload.get("id")

    if not group or not record_id:
        raise _Sprint16HTTPException(status_code=400, detail="group and id are required")

    records, key, record = _sprint16_find_record(group, record_id)

    if not isinstance(record, dict):
        raise _Sprint16HTTPException(status_code=400, detail="record is not archiveable")

    record["archived"] = True
    record["archived_at"] = _sprint01_now() if "_sprint01_now" in globals() else datetime.now(timezone.utc).isoformat()

    if "status" in record:
        record["previous_status"] = record.get("status")
        record["status"] = "archived"

    _sprint16_save_group(group)

    return {
        "status": "ok",
        "action": "archive",
        "group": group,
        "id": record_id,
        "record": record,
    }


async def sprint16_delete_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    group = payload.get("group")
    record_id = payload.get("id")
    confirmation = payload.get("confirmation", "")

    if not group or not record_id:
        raise _Sprint16HTTPException(status_code=400, detail="group and id are required")

    if confirmation != "DELETE_PROJECT_SALUS_RECORD":
        raise _Sprint16HTTPException(status_code=400, detail="confirmation phrase required")

    records, key, record = _sprint16_find_record(group, record_id)

    if isinstance(records, dict):
        deleted = records.pop(key)
    elif isinstance(records, list):
        deleted = records.pop(key)
    else:
        raise _Sprint16HTTPException(status_code=400, detail="record group is not deleteable")

    _sprint16_save_group(group)

    return {
        "status": "ok",
        "action": "delete",
        "group": group,
        "id": record_id,
        "deleted": deleted,
    }


async def sprint16_record_management_page() -> _Sprint16HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Record Management</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 18px;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
            margin-bottom: 18px;
          }
          input, select {
            width: 100%;
            box-sizing: border-box;
            margin: 6px 0 12px 0;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #28405f;
            background: #081525;
            color: #f4f7fb;
          }
          button, a.button {
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 11px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 5px 5px 5px 0;
          }
          button.danger {
            background: #d66;
            color: #111;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 420px;
            overflow: auto;
          }
          .muted {
            color: #aab7c7;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Record Management</h1>
        <p class="muted">Archive or delete selected records. Archive is safer for real records.</p>

        <div class="panel">
          <h2>Navigation</h2>
          <a class="button" href="/command/daily-driver">Daily Driver</a>
          <a class="button" href="/command/ops">Ops Dashboard</a>
          <a class="button" href="/command/review">Review Dashboard</a>
          <button onclick="refreshRecords()">Refresh Records</button>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Archive Record</h2>
            <select id="archive_group">
              <option>missions</option>
              <option>daily_briefs</option>
              <option>aars</option>
              <option>schoolhouse_courses</option>
              <option>schoolhouse_study_sessions</option>
              <option>schoolhouse_wrong_answer_reviews</option>
              <option>schoolhouse_writing_tasks</option>
              <option>charisma_self_assessments</option>
              <option>charisma_conversation_aars</option>
            </select>
            <input id="archive_id" placeholder="Record ID">
            <button onclick="archiveRecord()">Archive Record</button>
          </div>

          <div class="panel">
            <h2>Delete Record</h2>
            <p class="muted">Requires exact confirmation phrase.</p>
            <select id="delete_group">
              <option>missions</option>
              <option>daily_briefs</option>
              <option>aars</option>
              <option>schoolhouse_courses</option>
              <option>schoolhouse_study_sessions</option>
              <option>schoolhouse_wrong_answer_reviews</option>
              <option>schoolhouse_writing_tasks</option>
              <option>charisma_self_assessments</option>
              <option>charisma_conversation_aars</option>
            </select>
            <input id="delete_id" placeholder="Record ID">
            <input id="delete_confirmation" placeholder="DELETE_PROJECT_SALUS_RECORD">
            <button class="danger" onclick="deleteRecord()">Delete Record</button>
          </div>
        </div>

        <div class="panel">
          <h2>Last Result</h2>
          <pre id="result">No action yet.</pre>
        </div>

        <div class="panel">
          <h2>Record State</h2>
          <pre id="records">Loading...</pre>
        </div>

        <script>
          async function api(path, options = {}) {
            const res = await fetch(path, {
              headers: { "Content-Type": "application/json" },
              ...options
            });
            return await res.json();
          }

          function value(id) {
            return document.getElementById(id).value;
          }

          function show(id, data) {
            document.getElementById(id).textContent = JSON.stringify(data, null, 2);
          }

          async function refreshRecords() {
            show("records", await api("/api/command/records"));
          }

          async function archiveRecord() {
            const result = await api("/api/command/records/archive", {
              method: "POST",
              body: JSON.stringify({
                group: value("archive_group"),
                id: value("archive_id")
              })
            });
            show("result", result);
            await refreshRecords();
          }

          async function deleteRecord() {
            const result = await api("/api/command/records/delete", {
              method: "POST",
              body: JSON.stringify({
                group: value("delete_group"),
                id: value("delete_id"),
                confirmation: value("delete_confirmation")
              })
            });
            show("result", result);
            await refreshRecords();
          }

          refreshRecords();
        </script>
      </body>
    </html>
    """
    return _Sprint16HTMLResponse(content=html)



async def get_records_state() -> Any:
    _sync_legacy_globals()
    return await _resolve_result(sprint16_record_management_state())


async def archive_record(request: Request) -> Any:
    _sync_legacy_globals()
    payload = _normalize_record_mutation_payload(await request.json())
    return await _resolve_result(sprint16_archive_record(payload))


async def delete_record(request: Request) -> Any:
    _sync_legacy_globals()
    payload = _normalize_record_mutation_payload(await request.json())
    return await _resolve_result(sprint16_delete_record(payload))


async def get_records_page() -> Any:
    _sync_legacy_globals()
    return await _resolve_result(sprint16_record_management_page())
