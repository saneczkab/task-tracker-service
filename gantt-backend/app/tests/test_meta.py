from unittest.mock import Mock
from app.api import meta
from app.models import meta as meta_models


class TestMeta:

    def setup_mocks(self):
        self.mock_db = Mock()

    def test_get_team_statuses_success(self):
        self.setup_mocks()

        mock_status1 = Mock(spec=meta_models.Status)
        mock_status2 = Mock(spec=meta_models.Status)

        self.mock_db.query.return_value.all.return_value = [mock_status1, mock_status2]

        result = meta.get_team_statuses(self.mock_db)

        assert result == [mock_status1, mock_status2]

    def test_get_team_priorities_success(self):
        self.setup_mocks()

        mock_p1 = Mock(spec=meta_models.Priority)
        mock_p2 = Mock(spec=meta_models.Priority)

        self.mock_db.query.return_value.all.return_value = [mock_p1, mock_p2]

        result = meta.get_team_priorities(self.mock_db)

        assert result == [mock_p1, mock_p2]

    def test_get_connection_types_success(self):
        self.setup_mocks()

        mock_c1 = Mock(spec=meta_models.ConnectionType)
        mock_c2 = Mock(spec=meta_models.ConnectionType)

        self.mock_db.query.return_value.all.return_value = [mock_c1, mock_c2]

        result = meta.get_connection_types(self.mock_db)

        assert result == [mock_c1, mock_c2]
