import pytest
from django.db.utils import IntegrityError

from codeforces.models import CodeforcesUser


@pytest.mark.django_db
class TestCodeforcesUserModel:
    def test_user_creation(self):
        user = CodeforcesUser.objects.create(
            handle="test_handle",
            rating=1500,
            max_rating=1600
        )
        retrieved_user = CodeforcesUser.objects.get(handle="test_handle")
        assert retrieved_user.handle == "test_handle"
        assert retrieved_user.rating == 1500
        assert retrieved_user.max_rating == 1600
        assert retrieved_user.last_updated is not None

    def test_handle_is_unique(self):
        CodeforcesUser.objects.create(
            handle="test_handle",
            rating=1500,
            max_rating=1600
        )
        with pytest.raises(IntegrityError):
            CodeforcesUser.objects.create(
                handle="test_handle",
                rating=1400,
                max_rating=1500
            )

    def test_blank_fields(self):
        user = CodeforcesUser.objects.create(
            handle="new_handle"
        )
        assert user.rating is None
        assert user.max_rating is None
