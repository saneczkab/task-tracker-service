from unittest.mock import patch


@patch("app.crud.meta.get_team_statuses")
def test_get_statuses_success(mock_crud, status, client):
    mock_crud.return_value = [status]

    response = client.get("/api/taskStatuses")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == status.id
    assert data[0]["name"] == status.name


@patch("app.crud.meta.get_team_statuses")
def test_get_statuses_empty(mock_crud, client):
    mock_crud.return_value = []

    response = client.get("/api/taskStatuses")

    assert response.status_code == 200
    assert response.json() == []


@patch("app.crud.meta.get_team_priorities")
def test_get_priorities_success(mock_crud, priority, client):
    mock_crud.return_value = [priority]

    response = client.get("/api/priorities")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == priority.id
    assert data[0]["name"] == priority.name


@patch("app.crud.meta.get_team_priorities")
def test_get_priorities_empty(mock_crud, client):
    mock_crud.return_value = []

    response = client.get("/api/priorities")

    assert response.status_code == 200
    assert response.json() == []


@patch("app.crud.meta.get_connection_types")
def test_get_connection_types_success(mock_crud, connection, client):
    mock_crud.return_value = [connection]

    response = client.get("/api/connectionTypes")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == connection.id
    assert data[0]["name"] == connection.name


@patch("app.crud.meta.get_connection_types")
def test_get_connection_types_empty(mock_crud, client):
    mock_crud.return_value = []

    response = client.get("/api/connectionTypes")

    assert response.status_code == 200
    assert response.json() == []
