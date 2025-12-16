from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api import project
from app.models import project as project_models


class TestProject:

    def setup_mocks(self):
        self.mock_db = Mock()
        self.mock_user = Mock()
        self.mock_user.id = 1

        self.mock_team = Mock()
        self.mock_user_team = Mock()
        self.mock_project = Mock(spec=project_models.Project)

    def test_get_team_projects_success(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        self.mock_db.query.return_value.filter.return_value.all.return_value = [self.mock_project]

        result = project.get_team_projects(1, self.mock_user, self.mock_db)

        assert result == [self.mock_project]

    def test_get_team_projects_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            project.get_team_projects(999, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_get_team_projects_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            None
        ]

        with pytest.raises(HTTPException) as exc:
            project.get_team_projects(1, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_create_project_success(self, monkeypatch):
        self.setup_mocks()

        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        mock_project_class = Mock()
        monkeypatch.setattr(project_models, "Project", mock_project_class)

        project_data = Mock()
        project_data.name = "New Project"

        project.create_project(1, project_data, self.mock_user, self.mock_db)

        mock_project_class.assert_called_once_with(name="New Project", team_id=1)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    def test_create_project_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        project_data = Mock()

        with pytest.raises(HTTPException) as exc:
            project.create_project(999, project_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_create_project_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            None
        ]

        project_data = Mock()

        with pytest.raises(HTTPException) as exc:
            project.create_project(1, project_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_create_project_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        project_data = Mock()

        with pytest.raises(HTTPException) as exc:
            project.create_project(1, project_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_update_project_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            project.update_project(999, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_update_project_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            None
        ]

        with pytest.raises(HTTPException) as exc:
            project.update_project(1, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_update_project_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(HTTPException) as exc:
            project.update_project(1, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_update_project_success(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 2
        self.mock_project.name = "old"

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        update_data = Mock()
        update_data.name = "new"

        result = project.update_project(1, update_data, self.mock_user, self.mock_db)

        assert result == self.mock_project
        assert self.mock_project.name == "new"

    def test_delete_project_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            project.delete_project(999, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_delete_project_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            None
        ]

        with pytest.raises(HTTPException) as exc:
            project.delete_project(1, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_delete_project_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(HTTPException) as exc:
            project.delete_project(1, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_delete_project_success(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        result = project.delete_project(1, self.mock_user, self.mock_db)

        assert result is None
        self.mock_db.delete.assert_called_once_with(self.mock_project)
        self.mock_db.commit.assert_called_once()
