import time
from datetime import timedelta

import pytest
from django.conf import settings
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

    def test_handle_is_required(self, client, settings):
        settings.CODEFORCES_HANDLE = None
        response = client.get(reverse("codeforces-user-info"))
        assert response.status_code == 500
        assert response.json() == {"error": "handle is not set in the server"}

    def test_retrieve_user_info(self, client):
        # This test actually sends a request to Codeforces servers
        # TODO: Research the advantages and disadvantages of tests
        # that send requests to external services

        # https://codeforces.com/apiHelp
        # API may be requested at most 1 time per two seconds.
        sleep = 2

        assert CodeforcesUser.objects.count() == 0

        time.sleep(sleep)
        response = client.get(f"{reverse('codeforces-user-info')}")
        assert response.status_code == 200
        response_payload = response.json()
        assert response_payload["handle"] == settings.CODEFORCES_HANDLE
        assert isinstance(response_payload["rating"], int)
        assert isinstance(response_payload["max_rating"], int)
        assert response_payload["last_updated"] is not None
        assert CodeforcesUser.objects.count() == 1

        last_updated: str = response_payload["last_updated"]

        # record won't be updated within 1 hour time slot
        response = client.get(f"{reverse('codeforces-user-info')}")
        assert response.status_code == 200
        assert response.json()["last_updated"] == last_updated  # not updated
        assert CodeforcesUser.objects.count() == 1

        user = CodeforcesUser.objects.first()

        # record can be updated after 1 hour
        last_updated_before = user.last_updated
        user.last_udpated = user.last_updated - timedelta(hours=1, minutes=1)
        user.save()
        time.sleep(sleep)
        response = client.get(f"{reverse('codeforces-user-info')}")
        assert response.status_code == 200
        assert CodeforcesUser.objects.count() == 1
        user.refresh_from_db()
        assert user.last_updated != last_updated_before
