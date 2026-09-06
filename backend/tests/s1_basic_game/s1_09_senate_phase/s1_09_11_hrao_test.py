import pytest
from rorapp.helpers.hrao import set_hrao
from rorapp.models import Game, Senator


# The order of officials given in 1.09.11, most senior first. A senator holding
# no office at all comes last, ranked only by influence.
HRAO_ORDER = [
    Senator.Title.DICTATOR,
    Senator.Title.ROME_CONSUL,
    Senator.Title.FIELD_CONSUL,
    Senator.Title.CENSOR,
    Senator.Title.MASTER_OF_HORSE,
    None,
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "senior_title, junior_title", list(zip(HRAO_ORDER, HRAO_ORDER[1:]))
)
def test_hrao_follows_the_order_of_offices(
    basic_game: Game,
    senior_title: Senator.Title,
    junior_title: Senator.Title | None,
):
    # Arrange
    game = basic_game
    senior = Senator.objects.get(game=game, family_name="Aurelius")
    senior.add_title(senior_title)
    senior.save()
    junior = Senator.objects.get(game=game, family_name="Junius")
    if junior_title:
        junior.add_title(junior_title)
    junior.influence = 20
    junior.save()

    # Act
    set_hrao(game.id)

    # Assert
    senior.refresh_from_db()
    assert senior.has_title(Senator.Title.HRAO)
