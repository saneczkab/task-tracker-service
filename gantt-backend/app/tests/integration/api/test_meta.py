def test_get_task_statuses_success(client, status_obj):
    response = client.get("/api/taskStatuses")

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == status_obj.id and fields["name"] == status_obj.name
        for fields in data
    )


def test_get_priorities_success(client, priority_obj):
    response = client.get("/api/priorities")

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == priority_obj.id and fields["name"] == priority_obj.name
        for fields in data
    )


def test_get_connection_types_success(client, connection_type_obj):
    response = client.get("/api/connectionTypes")

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == connection_type_obj.id
        and fields["name"] == connection_type_obj.name
        for fields in data
    )
