"""Basic test to verify pytest setup is working."""
import pytest


def test_basic_assertion():
    """Simple test to verify pytest is running correctly."""
    assert True


def test_basic_math():
    """Test basic Python functionality."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


@pytest.mark.django_db
def test_django_db_access():
    """Test that Django database access works in tests."""
    from rorapp.models import Game

    # This should work without errors even if no games exist
    count = Game.objects.count()
    assert count >= 0
