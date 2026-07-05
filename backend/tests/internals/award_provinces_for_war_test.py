import pytest

from rorapp.helpers.provinces import award_provinces_for_war
from rorapp.models import Game, Log, Province, War


def _create_war(game: Game, name: str) -> War:
    return War.objects.create(
        game=game,
        name=name,
        index=0,
        land_strength=5,
        fleet_support=0,
        naval_strength=0,
        disaster_numbers=[],
        standoff_numbers=[],
        spoils=10,
        famine=False,
        location="Italia",
        status=War.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_award_provinces_for_second_punic_war_creates_hispania_provinces(
    basic_game: Game,
):
    # Arrange
    war = _create_war(basic_game, "2nd Punic War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert {p.name for p in created} == {
        "Hispania Citerior",
        "Hispania Ulterior",
    }
    assert Province.objects.filter(game=basic_game).count() == 2
    for province in created:
        assert province.developed is False


@pytest.mark.django_db
def test_award_provinces_for_first_punic_war_creates_sicilia_and_sardinia(
    basic_game: Game,
):
    # Arrange
    war = _create_war(basic_game, "1st Punic War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert {p.name for p in created} == {"Sicilia", "Sardinia et Corsica"}


@pytest.mark.django_db
def test_award_provinces_for_war_skips_existing_provinces(basic_game: Game):
    # Arrange
    Province.objects.create(
        game=basic_game, name="Hispania Citerior", developed=False
    )
    war = _create_war(basic_game, "2nd Punic War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert [p.name for p in created] == ["Hispania Ulterior"]
    assert Province.objects.filter(game=basic_game).count() == 2


@pytest.mark.django_db
def test_award_provinces_for_unrelated_war_creates_nothing(basic_game: Game):
    # Arrange
    war = _create_war(basic_game, "Syrian War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert created == []
    assert Province.objects.filter(game=basic_game).count() == 0


@pytest.mark.django_db
def test_first_illyrian_war_does_not_award_illyricum_while_second_remains(
    basic_game: Game,
):
    # Arrange
    _create_war(basic_game, "2nd Illyrian War")
    war = _create_war(basic_game, "1st Illyrian War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert created == []
    assert not Province.objects.filter(game=basic_game, name="Illyricum").exists()


@pytest.mark.django_db
def test_second_illyrian_war_awards_illyricum_when_first_already_defeated(
    basic_game: Game,
):
    # Arrange
    war = _create_war(basic_game, "2nd Illyrian War")

    # Act
    created = award_provinces_for_war(basic_game, war)

    # Assert
    assert [p.name for p in created] == ["Illyricum"]


@pytest.mark.django_db
def test_award_provinces_for_war_logs_each_created_province(basic_game: Game):
    # Arrange
    war = _create_war(basic_game, "1st Punic War")

    # Act
    award_provinces_for_war(basic_game, war)

    # Assert
    log_texts = list(Log.objects.filter(game=basic_game).values_list("text", flat=True))
    assert "Sicilia was established as a province." in log_texts
    assert "Sardinia et Corsica was established as a province." in log_texts
