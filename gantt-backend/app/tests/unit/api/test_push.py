from unittest.mock import patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.push_service.create_push_subscription_service")
def test_subscribe_to_push_success(
    mock_service, mock_user, current_user, push_subscription_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = push_subscription_obj

    response = client.post(
        "/api/push/subscribe",
        json={
            "endpoint": push_subscription_obj.endpoint,
            "p256dh": push_subscription_obj.p256dh,
            "auth": push_subscription_obj.auth,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == push_subscription_obj.id
    assert data["user_id"] == push_subscription_obj.user_id
    assert data["endpoint"] == push_subscription_obj.endpoint


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.push_service.get_user_subscriptions_service")
def test_get_subscriptions_success(
    mock_service, mock_user, current_user, push_subscription_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [push_subscription_obj]

    response = client.get("/api/push/subscriptions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == push_subscription_obj.id
    assert data[0]["user_id"] == push_subscription_obj.user_id
    assert data[0]["endpoint"] == push_subscription_obj.endpoint


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.push_service.delete_push_subscription_service")
def test_delete_subscription_success(
    mock_service, mock_user, current_user, push_subscription_obj, auth_headers, client
):
    mock_user.return_value = current_user

    response = client.delete(
        f"/api/push/subscriptions/{push_subscription_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    mock_service.assert_called_once()


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.push_service.delete_push_subscription_service")
def test_delete_subscription_not_found(
    mock_service, mock_user, current_user, push_subscription_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/push/subscriptions/{push_subscription_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.push_service.delete_push_subscription_service")
def test_delete_subscription_forbidden(
    mock_service, mock_user, current_user, push_subscription_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/push/subscriptions/{push_subscription_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403
