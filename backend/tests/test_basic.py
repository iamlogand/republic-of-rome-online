import pytest
from rorapp.models import Game


@pytest.mark.django_db
def test_django_db_access():
    count = Game.objects.count()
    assert count >= 0
