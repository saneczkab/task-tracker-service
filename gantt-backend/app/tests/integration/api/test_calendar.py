def test_export_calendar(
    client,
    auth_headers,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    task_obj,
):
    payload = {"scope": "all", "target": "all"}
    response = client.post("/api/calendar/export", json=payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    assert "Content-Disposition" in response.headers

    body = response.text
    assert "BEGIN:VCALENDAR" in body
    assert task_obj.name in body
