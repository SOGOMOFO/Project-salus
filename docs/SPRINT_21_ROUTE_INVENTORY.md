# Project Salus Route Inventory

## Summary
- Source: `backend/main.py`
- Route count: 84
- Sprint marker count: 18
- Line count: 4029
- Route source count: 7

## Sprint Markers
- --- Sprint 01 Core Loop compatibility endpoints ---
- --- Sprint 04 Local JSON Persistence ---
- --- Sprint 02 Commander UI ---
- --- Sprint 04 Persistent AAR Override ---
- --- Sprint 05 Mission/Data Contract compatibility endpoints ---
- --- Sprint compatibility JSON helpers ---
- --- Sprint 05 route priority fix ---
- --- Sprint 06 Data Hygiene and Reset Controls ---
- --- Sprint 07 Real Daily Use Mode ---
- --- Sprint 08 Schoolhouse Learning Coach Module ---
- --- Sprint 09 Charisma and Communication Skill Module ---
- --- Sprint 10 Command Dashboard Integration ---
- --- Sprint 11 Operational Dashboard Controls ---
- --- Sprint 13 Operational Review and History Dashboard ---
- --- Sprint 14 Command Launcher and Navigation System ---
- --- Sprint 23 Wire Extracted Dashboard and Readiness Routers ---
- --- Sprint 24 Extract Navigation and Workflow Routers ---
- --- Sprint 26 Wire Records and Daily Driver Routers ---

## Routes

| Method | Path | Handler | Source | Owner |
|---|---|---|---|---|
| GET | `/` | `home` | `backend/main.py` | `app` |
| GET | `/` | `sprint14_home_page` | `backend/main.py` | `app` |
| GET | `/agents` | `agents` | `backend/main.py` | `app` |
| GET | `/api/aar` | `api_list_aars` | `backend/main.py` | `app` |
| GET | `/api/aar` | `sprint04_list_aars` | `backend/main.py` | `app` |
| POST | `/api/aar` | `api_create_aar` | `backend/main.py` | `app` |
| POST | `/api/aar` | `sprint04_create_aar` | `backend/main.py` | `app` |
| GET | `/api/aar/{aar_id}` | `api_get_aar` | `backend/main.py` | `app` |
| GET | `/api/aar/{aar_id}` | `sprint04_get_aar` | `backend/main.py` | `app` |
| GET | `/api/command/daily-driver-state` | `sprint26_daily_driver_sprint15_daily_driver_state_bridge` | `backend/routes/daily_driver.py` | `router` |
| GET | `/api/command/dashboard-index` | `dashboard_index_api` | `backend/routes/dashboard_index.py` | `router` |
| GET | `/api/command/health` | `sprint14_command_health` | `backend/main.py` | `app` |
| GET | `/api/command/integrated-state` | `sprint10_integrated_command_state` | `backend/main.py` | `app` |
| GET | `/api/command/navigation` | `navigation_api` | `backend/routes/navigation.py` | `router` |
| GET | `/api/command/readiness` | `readiness_api` | `backend/routes/readiness.py` | `router` |
| GET | `/api/command/records` | `sprint26_records_sprint16_record_management_state_bridge` | `backend/routes/records.py` | `router` |
| POST | `/api/command/records/archive` | `sprint26_records_sprint16_archive_record_bridge` | `backend/routes/records.py` | `router` |
| POST | `/api/command/records/delete` | `sprint26_records_sprint16_delete_record_bridge` | `backend/routes/records.py` | `router` |
| GET | `/api/command/review-state` | `sprint13_review_state` | `backend/main.py` | `app` |
| GET | `/api/commander/brief` | `api_commander_brief` | `backend/main.py` | `app` |
| GET | `/api/commander/next-action` | `api_commander_next_action` | `backend/main.py` | `app` |
| GET | `/api/commander/today` | `api_commander_today` | `backend/main.py` | `app` |
| GET | `/api/core/missions` | `sprint02_list_core_missions` | `backend/main.py` | `app` |
| GET | `/api/daily-brief` | `sprint01_get_daily_brief` | `backend/main.py` | `app` |
| POST | `/api/daily-brief` | `sprint01_create_daily_brief` | `backend/main.py` | `app` |
| POST | `/api/daily-use/aar` | `sprint07_create_daily_use_aar` | `backend/main.py` | `app` |
| POST | `/api/daily-use/brief` | `sprint07_create_daily_use_brief` | `backend/main.py` | `app` |
| GET | `/api/daily-use/state` | `sprint07_daily_use_state` | `backend/main.py` | `app` |
| POST | `/api/daily/closeout` | `api_daily_closeout` | `backend/main.py` | `app` |
| GET | `/api/daily/history` | `api_daily_history` | `backend/main.py` | `app` |
| POST | `/api/daily/start` | `api_daily_start` | `backend/main.py` | `app` |
| GET | `/api/dashboard` | `sprint01_dashboard` | `backend/main.py` | `app` |
| GET | `/api/dashboard/daily` | `api_dashboard_daily` | `backend/main.py` | `app` |
| GET | `/api/dashboard/health` | `api_dashboard_health` | `backend/main.py` | `app` |
| GET | `/api/dashboard/missions` | `api_dashboard_missions` | `backend/main.py` | `app` |
| GET | `/api/dashboard/summary` | `api_dashboard_summary` | `backend/main.py` | `app` |
| POST | `/api/dev/reset` | `sprint06_dev_reset` | `backend/main.py` | `app` |
| POST | `/api/judgment` | `create_judgment` | `backend/main.py` | `app` |
| GET | `/api/missions` | `sprint03_list_missions` | `backend/main.py` | `app` |
| GET | `/api/missions` | `sprint05_list_missions` | `backend/main.py` | `app` |
| POST | `/api/missions` | `sprint03_create_mission` | `backend/main.py` | `app` |
| PATCH | `/api/missions/{mission_id}` | `sprint03_update_mission` | `backend/main.py` | `app` |
| GET | `/api/mvp/status` | `api_mvp_status` | `backend/main.py` | `app` |
| POST | `/api/schoolhouse/course` | `schoolhouse_create_course` | `backend/main.py` | `app` |
| GET | `/api/schoolhouse/courses` | `schoolhouse_list_courses` | `backend/main.py` | `app` |
| GET | `/api/schoolhouse/daily-brief` | `schoolhouse_daily_brief` | `backend/main.py` | `app` |
| POST | `/api/schoolhouse/quiz` | `schoolhouse_quiz` | `backend/main.py` | `app` |
| GET | `/api/schoolhouse/status` | `schoolhouse_status` | `backend/main.py` | `app` |
| POST | `/api/schoolhouse/study-session` | `schoolhouse_study_session` | `backend/main.py` | `app` |
| POST | `/api/schoolhouse/writing-task` | `schoolhouse_writing_task` | `backend/main.py` | `app` |
| POST | `/api/schoolhouse/wrong-answer-review` | `schoolhouse_wrong_answer_review` | `backend/main.py` | `app` |
| GET | `/api/sitrep` | `api_list_sitreps` | `backend/main.py` | `app` |
| POST | `/api/sitrep` | `api_create_sitrep` | `backend/main.py` | `app` |
| GET | `/api/sitrep/{sitrep_id}` | `api_get_sitrep` | `backend/main.py` | `app` |
| GET | `/api/skills/charisma` | `charisma_status` | `backend/main.py` | `app` |
| POST | `/api/skills/charisma/conversation-aar` | `charisma_conversation_aar` | `backend/main.py` | `app` |
| GET | `/api/skills/charisma/daily-drill` | `charisma_daily_drill` | `backend/main.py` | `app` |
| POST | `/api/skills/charisma/self-assessment` | `charisma_self_assessment` | `backend/main.py` | `app` |
| GET | `/api/workflows/evening` | `evening_workflow_api` | `backend/routes/workflows.py` | `router` |
| GET | `/api/workflows/morning` | `morning_workflow_api` | `backend/routes/workflows.py` | `router` |
| GET | `/api/workflows/today` | `today_workflows_api` | `backend/routes/workflows.py` | `router` |
| POST | `/auth` | `auth` | `backend/main.py` | `app` |
| GET | `/command` | `sprint03_command_page` | `backend/main.py` | `app` |
| GET | `/command/daily` | `sprint07_daily_command_page` | `backend/main.py` | `app` |
| GET | `/command/daily-driver` | `sprint26_daily_driver_sprint15_daily_driver_page_bridge` | `backend/routes/daily_driver.py` | `router` |
| GET | `/command/dashboard-index` | `dashboard_index_page` | `backend/routes/dashboard_index.py` | `router` |
| GET | `/command/home` | `sprint14_command_home_page` | `backend/main.py` | `app` |
| GET | `/command/integrated` | `sprint10_integrated_command_dashboard` | `backend/main.py` | `app` |
| GET | `/command/navigation` | `navigation_page` | `backend/routes/navigation.py` | `router` |
| GET | `/command/ops` | `sprint11_operational_dashboard` | `backend/main.py` | `app` |
| GET | `/command/readiness` | `readiness_page` | `backend/routes/readiness.py` | `router` |
| GET | `/command/records` | `sprint26_records_sprint16_record_management_page_bridge` | `backend/routes/records.py` | `router` |
| GET | `/command/review` | `sprint13_review_dashboard` | `backend/main.py` | `app` |
| GET | `/command/workflows` | `workflows_page` | `backend/routes/workflows.py` | `router` |
| GET | `/core/memory/status` | `core_memory_status` | `backend/main.py` | `app` |
| GET | `/core/plugins/status` | `core_plugins_status` | `backend/main.py` | `app` |
| GET | `/health` | `health` | `backend/main.py` | `app` |
| GET | `/missions` | `missions` | `backend/main.py` | `app` |
| POST | `/missions` | `sprint01_create_mission` | `backend/main.py` | `app` |
| PATCH | `/missions/{mission_id}` | `sprint01_update_mission` | `backend/main.py` | `app` |
| GET | `/sitreps` | `sitreps` | `backend/main.py` | `app` |
| POST | `/sitreps` | `create_sitrep` | `backend/main.py` | `app` |
| GET | `/status` | `mission_control_status` | `backend/main.py` | `app` |
| GET | `/system/status` | `system_status` | `backend/main.py` | `app` |

## Recommendation
Continue modular route extraction one route group at a time with tests green after every extraction.
