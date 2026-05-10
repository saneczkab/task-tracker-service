from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.services.push_service import (
    create_push_subscription_service,
    delete_push_subscription_service,
    get_user_subscriptions_service,
    send_push,
)


@patch("app.services.push_service.push_crud.create_subscription")
def test_create_push_subscription_service_success(
    mock_create_subscription, mock_db, ids
):
    created = Mock(id=ids.goal_id, user_id=ids.user_id)
    mock_create_subscription.return_value = created

    result = create_push_subscription_service(
        mock_db,
        user_id=ids.user_id,
        endpoint="https://example.com/push/new",
        p256dh="p256dh-key",
        auth="auth-key",
    )

    mock_create_subscription.assert_called_once_with(
        mock_db,
        user_id=ids.user_id,
        endpoint="https://example.com/push/new",
        p256dh="p256dh-key",
        auth="auth-key",
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(created)
    assert result is created


@patch("app.services.push_service.push_crud.get_subscriptions_by_user")
def test_get_user_subscriptions_service_success(
    mock_get_subscriptions_by_user, mock_db, ids
):
    expected = [Mock(), Mock()]
    mock_get_subscriptions_by_user.return_value = expected

    result = get_user_subscriptions_service(mock_db, ids.user_id)

    mock_get_subscriptions_by_user.assert_called_once_with(mock_db, ids.user_id)
    assert result is expected


@patch("app.services.push_service.push_crud.delete_subscription")
@patch("app.services.push_service.push_crud.get_subscription_by_id")
def test_delete_push_subscription_service_success(
    mock_get_subscription_by_id, mock_delete_subscription, mock_db, ids
):
    subscription = Mock(id=ids.goal_id, user_id=ids.user_id)
    mock_get_subscription_by_id.return_value = subscription

    delete_push_subscription_service(mock_db, subscription.id, ids.user_id)

    mock_get_subscription_by_id.assert_called_once_with(mock_db, subscription.id)
    mock_delete_subscription.assert_called_once_with(mock_db, subscription)


@patch("app.services.push_service.push_crud.delete_subscription")
@patch("app.services.push_service.push_crud.get_subscription_by_id")
def test_delete_push_subscription_service_not_found(
    mock_get_subscription_by_id, mock_delete_subscription, mock_db, ids
):
    mock_get_subscription_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_push_subscription_service(mock_db, ids.goal_id, ids.user_id)

    mock_delete_subscription.assert_not_called()


@patch("app.services.push_service.push_crud.delete_subscription")
@patch("app.services.push_service.push_crud.get_subscription_by_id")
def test_delete_push_subscription_service_forbidden(
    mock_get_subscription_by_id, mock_delete_subscription, mock_db, ids
):
    subscription = Mock(id=ids.goal_id, user_id=ids.second_user_id)
    mock_get_subscription_by_id.return_value = subscription

    with pytest.raises(exception.ForbiddenError):
        delete_push_subscription_service(mock_db, subscription.id, ids.user_id)

    mock_delete_subscription.assert_not_called()


@patch("app.services.push_service.webpush")
@patch.multiple(
    "app.services.push_service",
    SessionLocal=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.team_crud",
    get_team_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.project_crud",
    get_project_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.stream_crud",
    get_stream_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.task_crud",
    get_task_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.push_crud",
    get_subscriptions_by_user=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.reminder_crud",
    get_reminder_by_id=DEFAULT,
    mark_as_sent=DEFAULT,
)
def test_send_push_returns_early_when_reminder_not_found(
    mock_webpush,
    **mocks,
):
    db = Mock()
    mocks["SessionLocal"].return_value = db
    mocks["get_reminder_by_id"].return_value = None

    send_push(1001)

    mocks["get_subscriptions_by_user"].assert_not_called()
    mocks["mark_as_sent"].assert_not_called()
    mock_webpush.assert_not_called()
    db.close.assert_called_once()


@patch("app.services.push_service.webpush")
@patch.multiple(
    "app.services.push_service",
    SessionLocal=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.reminder_crud",
    get_reminder_by_id=DEFAULT,
    mark_as_sent=DEFAULT,
)
def test_send_push_returns_early_when_reminder_already_sent(
    mock_webpush,
    **mocks,
):
    db = Mock()
    reminder = Mock(sent=True)
    mocks["SessionLocal"].return_value = db
    mocks["get_reminder_by_id"].return_value = reminder

    send_push(1002)

    mocks["mark_as_sent"].assert_not_called()
    mock_webpush.assert_not_called()
    db.close.assert_called_once()


@patch("app.services.push_service.webpush")
@patch.multiple(
    "app.services.push_service",
    SessionLocal=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.team_crud",
    get_team_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.project_crud",
    get_project_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.stream_crud",
    get_stream_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.task_crud",
    get_task_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.push_crud",
    get_subscriptions_by_user=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.reminder_crud",
    get_reminder_by_id=DEFAULT,
    mark_as_sent=DEFAULT,
)
def test_send_push_returns_when_task_hierarchy_missing(
    mock_webpush,
    **mocks,
):
    db = Mock()
    reminder = Mock(id=10, user_id=20, task_id=30, sent=False)
    mocks["SessionLocal"].return_value = db
    mocks["get_reminder_by_id"].return_value = reminder
    mocks["get_subscriptions_by_user"].return_value = [Mock()]
    mocks["get_task_by_id"].return_value = None

    send_push(reminder.id)

    mocks["mark_as_sent"].assert_not_called()
    mock_webpush.assert_not_called()
    db.close.assert_called_once()


@patch("app.services.push_service.webpush")
@patch.multiple(
    "app.services.push_service",
    SessionLocal=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.team_crud",
    get_team_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.project_crud",
    get_project_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.stream_crud",
    get_stream_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.task_crud",
    get_task_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.push_crud",
    get_subscriptions_by_user=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.reminder_crud",
    get_reminder_by_id=DEFAULT,
    mark_as_sent=DEFAULT,
)
def test_send_push_sends_notifications_and_marks_sent(
    mock_webpush,
    **mocks,
):
    db = Mock()
    reminder = Mock(id=10, user_id=20, task_id=30, sent=False)
    task_obj = Mock(name="Task A", stream_id=40)
    stream_obj = Mock(id=40, project_id=50)
    project_obj = Mock(team_id=60)
    team_obj = Mock(id=60)
    sub_1 = Mock(endpoint="https://example.com/1", p256dh="p1", auth="a1")
    sub_2 = Mock(endpoint="https://example.com/2", p256dh="p2", auth="a2")

    mocks["SessionLocal"].return_value = db
    mocks["get_reminder_by_id"].return_value = reminder
    mocks["get_subscriptions_by_user"].return_value = [sub_1, sub_2]
    mocks["get_task_by_id"].return_value = task_obj
    mocks["get_stream_by_id"].return_value = stream_obj
    mocks["get_project_by_id"].return_value = project_obj
    mocks["get_team_by_id"].return_value = team_obj

    send_push(reminder.id)

    assert mock_webpush.call_count == 2
    mocks["mark_as_sent"].assert_called_once_with(db, reminder)
    db.close.assert_called_once()


@patch("app.services.push_service.webpush")
@patch.multiple(
    "app.services.push_service",
    SessionLocal=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.team_crud",
    get_team_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.project_crud",
    get_project_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.stream_crud",
    get_stream_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.task_crud",
    get_task_by_id=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.push_crud",
    get_subscriptions_by_user=DEFAULT,
)
@patch.multiple(
    "app.services.push_service.reminder_crud",
    get_reminder_by_id=DEFAULT,
    mark_as_sent=DEFAULT,
)
def test_send_push_marks_sent_even_if_webpush_fails(
    mock_webpush,
    **mocks,
):
    db = Mock()
    reminder = Mock(id=10, user_id=20, task_id=30, sent=False)
    task_obj = Mock(name="Task A", stream_id=40)
    stream_obj = Mock(id=40, project_id=50)
    project_obj = Mock(team_id=60)
    team_obj = Mock(id=60)
    sub_1 = Mock(endpoint="https://example.com/1", p256dh="p1", auth="a1")

    mocks["SessionLocal"].return_value = db
    mocks["get_reminder_by_id"].return_value = reminder
    mocks["get_subscriptions_by_user"].return_value = [sub_1]
    mocks["get_task_by_id"].return_value = task_obj
    mocks["get_stream_by_id"].return_value = stream_obj
    mocks["get_project_by_id"].return_value = project_obj
    mocks["get_team_by_id"].return_value = team_obj
    mock_webpush.side_effect = Exception("push failed")

    send_push(reminder.id)

    mocks["mark_as_sent"].assert_called_once_with(db, reminder)
    db.close.assert_called_once()
