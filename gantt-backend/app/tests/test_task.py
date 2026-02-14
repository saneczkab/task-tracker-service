from unittest.mock import Mock

import fastapi
import pytest

from app.api import task as task_api
from app.models import task as task_model


class TestTask:

    def setup_mocks(self):
        self.db = Mock()
        self.current_user = Mock()
        self.current_user.id = 10

        self.mock_project = Mock()
        self.mock_stream = Mock()
        self.mock_stream.id = 5
        self.mock_stream.project_id = 1

        self.mock_user_team = Mock()
        self.mock_user_team.role_id = 2

        self.mock_task = Mock()
        self.mock_task.id = 99
        self.mock_task.stream_id = 5

    def test_get_project_tasks_success(self):
        self.setup_mocks()

        self.mock_project.streams = [Mock(tasks=[self.mock_task])]

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        result = task_api.get_project_tasks(1, self.current_user, self.db)
        assert result == [self.mock_task]

    def test_get_project_tasks_not_found(self):
        self.setup_mocks()
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.get_project_tasks(1, self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_get_project_tasks_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.get_project_tasks(1, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_get_stream_tasks_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        self.db.query.return_value.filter.return_value.all.return_value = [self.mock_task]

        result = task_api.get_stream_tasks(5, self.current_user, self.db)
        assert result == [self.mock_task]

    def test_get_stream_tasks_not_found(self):
        self.setup_mocks()
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.get_stream_tasks(5, self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_get_stream_tasks_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.get_stream_tasks(5, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_create_task_success(self, monkeypatch):
        self.setup_mocks()
        task_data = Mock()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        mock_task_class = Mock()
        monkeypatch.setattr(task_model, "Task", mock_task_class)

        task_api.create_task(5, task_data, self.current_user, self.db)

        mock_task_class.assert_called_once()
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    def test_create_task_stream_not_found(self):
        self.setup_mocks()
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.create_task(5, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_create_task_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.create_task(5, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_create_task_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.create_task(5, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_update_task_not_found(self):
        self.setup_mocks()
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.update_task(99, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_update_task_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.update_task(99, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_update_task_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.update_task(99, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_update_task_success(self):
        self.setup_mocks()

        data = Mock()
        data.name = "new"
        data.description = None
        data.status_id = None
        data.priority_id = None
        data.start_date = None
        data.deadline = None
        data.assignee_email = None

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        result = task_api.update_task(99, data, self.current_user, self.db)

        assert result == self.mock_task
        assert self.mock_task.name == "new"
        self.db.commit.assert_called_once()

    def test_delete_task_not_found(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.delete_task(99, self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_delete_task_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.delete_task(99, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_delete_task_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            task_api.delete_task(99, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_delete_task_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_task,
            self.mock_stream,
            self.mock_project,
            self.mock_user_team,
            None
        ]

        result = task_api.delete_task(99, self.current_user, self.db)

        assert result is None
        self.db.delete.assert_called()
        self.db.commit.assert_called_once()
