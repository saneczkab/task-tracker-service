def test_subscribe_to_push_success(client, auth_headers, user_obj):
    payload = {"endpoint": "https://example.com/", "p256dh": "key1", "auth": "key2"}
    response = client.post("/api/push/subscribe", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_obj.id
    assert data["endpoint"] == payload["endpoint"]


def test_get_subscriptions_success(client, auth_headers, push_subscription_obj):
    response = client.get("/api/push/subscriptions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(fields["id"] == push_subscription_obj.id for fields in data)


def test_delete_subscription_success(client, auth_headers, push_subscription_obj):
    response = client.delete(
        f"/api/push/subscriptions/{push_subscription_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


def test_delete_subscription_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/push/subscriptions/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_subscription_forbidden(
    client, auth_headers, second_push_subscription_obj, user_obj
):
    response = client.delete(
        f"/api/push/subscriptions/{second_push_subscription_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
