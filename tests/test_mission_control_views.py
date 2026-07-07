from backend import mission_control_views as views


def test_render_operator_queue_table_empty():
    html = views.render_operator_queue_table([])
    assert "No operator queue items" in html


def test_render_operator_queue_table_with_actions():
    html = views.render_operator_queue_table(
        [
            {
                "id": 7,
                "title": "View Test Item",
                "description": "Render this queue item",
                "queue_type": "task",
                "status": "open",
                "priority": "high",
            }
        ]
    )

    assert "View Test Item" in html
    assert "Render this queue item" in html
    assert "/mission-control/operator-item/7/status/in_progress" in html
    assert "/mission-control/operator-item/7/convert-to-mission" in html
    assert "Convert to Mission" in html


def test_render_queue_controls():
    html = views.render_queue_controls()
    assert "Generate Missions from Queue" in html
    assert "Cleanup Done Items" in html


def test_render_live_status_script():
    html = views.render_live_status_script()
    assert "/api/mission-control/live-status" in html
    assert "refreshLiveStatus" in html


def test_render_operator_inbox_panel():
    html = views.render_operator_inbox_panel()
    assert "Operator Inbox" in html
    assert "/mission-control/operator-item" in html
