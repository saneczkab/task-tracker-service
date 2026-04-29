from app.crud.tag import create_tag, delete_tag, get_tag_by_id, get_team_tags


def test_get_tag_by_id_returns_tag(db_session, tag_obj):
    result = get_tag_by_id(db_session, tag_obj.id)

    assert result is not None
    assert result.id == tag_obj.id
    assert result.name == tag_obj.name
    assert result.color == tag_obj.color
    assert result.team_id == tag_obj.team_id


def test_get_tag_by_id_returns_none_when_not_found(db_session):
    result = get_tag_by_id(db_session, tag_id=999)

    assert result is None


def test_get_team_tags_returns_list_for_team(db_session, tag_obj):
    second_tag = create_tag(
        db_session,
        team_id=tag_obj.team_id,
        name="Frontend",
        color="#10B981",
    )

    result = get_team_tags(db_session, tag_obj.team_id)

    assert len(result) == 2
    assert {item.id for item in result} == {tag_obj.id, second_tag.id}


def test_get_team_tags_returns_empty_list_when_team_has_no_tags(db_session, team_obj):
    missing_team_id = team_obj.id + 1000

    result = get_team_tags(db_session, missing_team_id)

    assert result == []


def test_create_tag_creates_and_returns_tag(db_session, team_obj):
    name = "Urgent"
    color = "#EF4444"

    result = create_tag(db_session, team_id=team_obj.id, name=name, color=color)

    assert result.id is not None
    assert result.team_id == team_obj.id
    assert result.name == name
    assert result.color == color


def test_delete_tag_removes_tag(db_session, tag_obj):
    delete_tag(db_session, tag_obj)

    assert get_tag_by_id(db_session, tag_obj.id) is None


def test_delete_tag_does_not_remove_other_tags(db_session, tag_obj):
    second_tag = create_tag(
        db_session,
        team_id=tag_obj.team_id,
        name="Design",
        color="#8B5CF6",
    )

    delete_tag(db_session, tag_obj)

    assert get_tag_by_id(db_session, tag_obj.id) is None
    assert get_tag_by_id(db_session, second_tag.id) is not None
