from app.crud.push import (
    create_subscription,
    delete_subscription,
    get_subscription_by_id,
    get_subscriptions_by_user,
)


def test_get_subscription_by_id_returns_subscription(db_session, push_subscription_obj):
    result = get_subscription_by_id(db_session, push_subscription_obj.id)

    assert result.id == push_subscription_obj.id
    assert result.user_id == push_subscription_obj.user_id


def test_get_subscription_by_id_returns_none_when_not_found(db_session):
    result = get_subscription_by_id(db_session, 999)

    assert result is None


def test_get_subscriptions_by_user_returns_list(db_session, push_subscription_obj):
    result = get_subscriptions_by_user(db_session, push_subscription_obj.user_id)

    assert len(result) == 1
    assert result[0].id == push_subscription_obj.id


def test_get_subscriptions_by_user_filters_by_user(
    db_session, push_subscription_obj, second_push_subscription_obj
):
    result = get_subscriptions_by_user(db_session, push_subscription_obj.user_id)

    assert len(result) == 1
    assert result[0].id == push_subscription_obj.id
    assert second_push_subscription_obj.id not in {item.id for item in result}


def test_get_subscriptions_by_user_returns_empty_list_when_not_found(db_session):
    result = get_subscriptions_by_user(db_session, 999)

    assert result == []


def test_create_subscription_persists_subscription(db_session, user_obj):
    result = create_subscription(
        db_session,
        user_id=user_obj.id,
        endpoint="https://example.com/push/new",
        p256dh="new-p256dh",
        auth="new-auth",
    )

    assert result.id is not None
    assert result.user_id == user_obj.id
    assert result.endpoint == "https://example.com/push/new"
    assert result.p256dh == "new-p256dh"
    assert result.auth == "new-auth"


def test_delete_subscription_removes_record(db_session, push_subscription_obj):
    delete_subscription(db_session, push_subscription_obj)

    assert get_subscription_by_id(db_session, push_subscription_obj.id) is None
    assert get_subscriptions_by_user(db_session, push_subscription_obj.user_id) == []
