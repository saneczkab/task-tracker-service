from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app import models
from app.api import goal


class TestGoals:

    def setup_mocks(self):
        self.mock_db = Mock()
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_stream = Mock()
        self.mock_project = Mock()
        self.mock_project.team = Mock()
        self.mock_user_team = Mock()
        self.mock_goal = Mock()
        self.mock_goal.stream = Mock()

    def test_get_stream_goals_success(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream, self.mock_project, self.mock_user_team
        ]
        self.mock_db.query.return_value.filter.return_value.all.return_value = [self.mock_goal]

        result = goal.get_stream_goals(1, self.mock_user, self.mock_db)
        assert result == [self.mock_goal]

    def test_get_stream_goals_not_found(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            goal.get_stream_goals(999, self.mock_user, self.mock_db)
        assert exc.value.status_code == 404

    def test_get_stream_goals_no_access(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream, self.mock_project, None
        ]

        with pytest.raises(HTTPException) as exc:
            goal.get_stream_goals(1, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_create_goal_success(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream, self.mock_project, self.mock_user_team, None
        ]

        goal_data = Mock()
        goal_data.name = "test"
        goal_data.description = "descr"
        goal_data.deadline = None

        result = goal.create_goal(1, goal_data, self.mock_user, self.mock_db)

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
        assert isinstance(result, models.goal.Goal)

    def test_create_goal_duplicate(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream, self.mock_project, self.mock_user_team, Mock()
        ]

        goal_data = Mock()

        with pytest.raises(HTTPException) as exc:
            goal.create_goal(1, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 409

    def test_create_goal_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream, self.mock_project, self.mock_user_team
        ]

        goal_data = Mock()

        with pytest.raises(HTTPException) as exc:
            goal.create_goal(1, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_update_goal_not_found(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        goal_data = Mock()

        with pytest.raises(HTTPException) as exc:
            goal.update_goal(999, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 404

    def test_update_goal_no_access(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, None
        ]

        goal_data = Mock()

        with pytest.raises(HTTPException) as exc:
            goal.update_goal(1, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_update_goal_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, self.mock_user_team
        ]

        goal_data = Mock()

        with pytest.raises(HTTPException) as exc:
            goal.update_goal(1, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_update_goal_name_conflict(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 2
        self.mock_goal.name = "old"

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, self.mock_user_team, Mock()
        ]

        goal_data = Mock()
        goal_data.name = "name_conflict"

        with pytest.raises(HTTPException) as exc:
            goal.update_goal(1, goal_data, self.mock_user, self.mock_db)
        assert exc.value.status_code == 409

    def test_update_goal_success(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 2
        self.mock_goal.name = "old"

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, self.mock_user_team, None
        ]

        goal_data = Mock()
        goal_data.name = "new"
        goal_data.description = None
        goal_data.deadline = None

        result = goal.update_goal(1, goal_data, self.mock_user, self.mock_db)
        assert result == self.mock_goal

    def test_delete_goal_not_found(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            goal.delete_goal(999, self.mock_user, self.mock_db)
        assert exc.value.status_code == 404

    def test_delete_goal_no_access(self):
        self.setup_mocks()
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, None
        ]

        with pytest.raises(HTTPException) as exc:
            goal.delete_goal(1, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_delete_goal_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, self.mock_user_team
        ]

        with pytest.raises(HTTPException) as exc:
            goal.delete_goal(1, self.mock_user, self.mock_db)
        assert exc.value.status_code == 403

    def test_delete_goal_success(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_goal, self.mock_stream, self.mock_project, self.mock_user_team
        ]

        result = goal.delete_goal(1, self.mock_user, self.mock_db)
        assert result is None
        self.mock_db.delete.assert_called_once_with(self.mock_goal)