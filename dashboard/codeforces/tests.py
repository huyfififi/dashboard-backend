import time

import pytest
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from codeforces.models import CodeforcesUser


@pytest.mark.django_db
class TestCodeforcesUserModel:
    # Generated by Chat-GPT4o
    def test_user_creation(self):
        CodeforcesUser.objects.create(
            handle="test_handle", rating=1500, max_rating=1600
        )
        retrieved_user = CodeforcesUser.objects.get(handle="test_handle")
        assert retrieved_user.handle == "test_handle"
        assert retrieved_user.rating == 1500
        assert retrieved_user.max_rating == 1600
        assert retrieved_user.last_updated is not None

    def test_handle_is_unique(self):
        CodeforcesUser.objects.create(
            handle="test_handle", rating=1500, max_rating=1600
        )
        with pytest.raises(IntegrityError):
            CodeforcesUser.objects.create(
                handle="test_handle", rating=1400, max_rating=1500
            )

    def test_blank_fields(self):
        user = CodeforcesUser.objects.create(handle="new_handle")
        assert user.rating is None
        assert user.max_rating is None


@pytest.mark.django_db
class TestCodeforcesUserAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_handle_is_required(self, client):
        response = client.get(reverse("codeforces-user-info"))
        assert response.status_code == 400
        assert response.json() == {"error": "handle is required"}

    def test_retrieve_user_info(self, client):
        # https://codeforces.com/apiHelp
        # API may be requested at most 1 time per two seconds.
        sleep = 2

        # This test actually sends a request to Codeforces servers
        # TODO: Research the advantages and disadvantages of tests
        # that send requests to external services
        handle = "utsu_boy"  # Kazuki's handle

        assert CodeforcesUser.objects.count() == 0

        time.sleep(sleep)

        response = client.get(f"{reverse('codeforces-user-info')}?handle={handle}")
        assert response.status_code == 200
        response_payload = response.json()
        assert response_payload["handle"] == handle
        assert isinstance(response_payload["rating"], int)
        assert isinstance(response_payload["max_rating"], int)
        assert response_payload["last_updated"] is not None
        assert CodeforcesUser.objects.count() == 1

        last_updated: str = response_payload["last_updated"]

        response = client.get(f"{reverse('codeforces-user-info')}?handle={handle}")
        assert response.status_code == 200
        assert response.json()["last_updated"] == last_updated
        assert CodeforcesUser.objects.count() == 1
