# Project Salus Route Inventory

## Summary
- Source: `backend/main.py`
- Route count: 84
- Sprint marker count: 21
- Line count: 5269

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
- --- Sprint 15 Daily Driver Polish ---
- --- Sprint 16 Record Management Controls ---
- --- Sprint 17 Daily Workflow Automation ---
- --- Sprint 18 Navigation Unification and UX Cleanup ---
- --- Sprint 19 System Status and Readiness Scoring ---
- --- Sprint 20 Dashboard Index and Final Local MVP Checkpoint ---

## Routes

| Method | Path | Handler |
|---|---|---|
| GET | `/` | `home` |
| GET | `/` | `sprint14_home_page` |
| GET | `/agents` | `agents` |
| GET | `/api/aar` | `api_list_aars` |
| GET | `/api/aar` | `sprint04_list_aars` |
| POST | `/api/aar` | `api_create_aar` |
| POST | `/api/aar` | `sprint04_create_aar` |
| GET | `/api/aar/{aar_id}` | `api_get_aar` |
| GET | `/api/aar/{aar_id}` | `sprint04_get_aar` |
| GET | `/api/command/daily-driver-state` | `sprint15_daily_driver_state` |
| GET | `/api/command/dashboard-index` | `sprint20_dashboard_index` |
| GET | `/api/command/health` | `sprint14_command_health` |
| GET | `/api/command/integrated-state` | `sprint10_integrated_command_state` |
| GET | `/api/command/navigation` | `sprint18_command_navigation` |
| GET | `/api/command/readiness` | `sprint19_readiness` |
| GET | `/api/command/records` | `sprint16_record_management_state` |
| POST | `/api/command/records/archive` | `sprint16_archive_record` |
| POST | `/api/command/records/delete` | `sprint16_delete_record` |
| GET | `/api/command/review-state` | `sprint13_review_state` |
| GET | `/api/commander/brief` | `api_commander_brief` |
| GET | `/api/commander/next-action` | `api_commander_next_action` |
| GET | `/api/commander/today` | `api_commander_today` |
| GET | `/api/core/missions` | `sprint02_list_core_missions` |
| GET | `/api/daily-brief` | `sprint01_get_daily_brief` |
| POST | `/api/daily-brief` | `sprint01_create_daily_brief` |
| POST | `/api/daily-use/aar` | `sprint07_create_daily_use_aar` |
| POST | `/api/daily-use/brief` | `sprint07_create_daily_use_brief` |
| GET | `/api/daily-use/state` | `sprint07_daily_use_state` |
| POST | `/api/daily/closeout` | `api_daily_closeout` |
| GET | `/api/daily/history` | `api_daily_history` |
| POST | `/api/daily/start` | `api_daily_start` |
| GET | `/api/dashboard` | `sprint01_dashboard` |
| GET | `/api/dashboard/daily` | `api_dashboard_daily` |
| GET | `/api/dashboard/health` | `api_dashboard_health` |
| GET | `/api/dashboard/missions` | `api_dashboard_missions` |
| GET | `/api/dashboard/summary` | `api_dashboard_summary` |
| POST | `/api/dev/reset` | `sprint06_dev_reset` |
| POST | `/api/judgment` | `create_judgment` |
| GET | `/api/missions` | `sprint03_list_missions` |
| GET | `/api/missions` | `sprint05_list_missions` |
| POST | `/api/missions` | `sprint03_create_mission` |
| PATCH | `/api/missions/{mission_id}` | `sprint03_update_mission` |
| GET | `/api/mvp/status` | `api_mvp_status` |
| POST | `/api/schoolhouse/course` | `schoolhouse_create_course` |
| GET | `/api/schoolhouse/courses` | `schoolhouse_list_courses` |
| GET | `/api/schoolhouse/daily-brief` | `schoolhouse_daily_brief` |
| POST | `/api/schoolhouse/quiz` | `schoolhouse_quiz` |
| GET | `/api/schoolhouse/status` | `schoolhouse_status` |
| POST | `/api/schoolhouse/study-session` | `schoolhouse_study_session` |
| POST | `/api/schoolhouse/writing-task` | `schoolhouse_writing_task` |
| POST | `/api/schoolhouse/wrong-answer-review` | `schoolhouse_wrong_answer_review` |
| GET | `/api/sitrep` | `api_list_sitreps` |
| POST | `/api/sitrep` | `api_create_sitrep` |
| GET | `/api/sitrep/{sitrep_id}` | `api_get_sitrep` |
| GET | `/api/skills/charisma` | `charisma_status` |
| POST | `/api/skills/charisma/conversation-aar` | `charisma_conversation_aar` |
| GET | `/api/skills/charisma/daily-drill` | `charisma_daily_drill` |
| POST | `/api/skills/charisma/self-assessment` | `charisma_self_assessment` |
| GET | `/api/workflows/evening` | `sprint17_evening_workflow` |
| GET | `/api/workflows/morning` | `sprint17_morning_workflow` |
| GET | `/api/workflows/today` | `sprint17_today_workflows` |
| POST | `/auth` | `auth` |
| GET | `/command` | `sprint03_command_page` |
| GET | `/command/daily` | `sprint07_daily_command_page` |
| GET | `/command/daily-driver` | `sprint15_daily_driver_page` |
| GET | `/command/dashboard-index` | `sprint20_dashboard_index_page` |
| GET | `/command/home` | `sprint14_command_home_page` |
| GET | `/command/integrated` | `sprint10_integrated_command_dashboard` |
| GET | `/command/navigation` | `sprint18_navigation_page` |
| GET | `/command/ops` | `sprint11_operational_dashboard` |
| GET | `/command/readiness` | `sprint19_readiness_page` |
| GET | `/command/records` | `sprint16_record_management_page` |
| GET | `/command/review` | `sprint13_review_dashboard` |
| GET | `/command/workflows` | `sprint17_workflows_page` |
| GET | `/core/memory/status` | `core_memory_status` |
| GET | `/core/plugins/status` | `core_plugins_status` |
| GET | `/health` | `health` |
| GET | `/missions` | `missions` |
| POST | `/missions` | `sprint01_create_mission` |
| PATCH | `/missions/{mission_id}` | `sprint01_update_mission` |
| GET | `/sitreps` | `sitreps` |
| POST | `/sitreps` | `create_sitrep` |
| GET | `/status` | `mission_control_status` |
| GET | `/system/status` | `system_status` |

## Recommendation
Begin modular route extraction only after this inventory is committed and tests are green.
