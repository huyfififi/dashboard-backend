import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from codeforces.models import CodeforcesUser, CodeforcesSubmission


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
class TestCodeforcesSubmissionModel:
    def test_submission_creation(self):
        user = CodeforcesUser.objects.create(
            handle="test_handle", rating=1500, max_rating=1600
        )
        submission: CodeforcesSubmission = user.codeforcessubmission_set.create(
            contest_id=1,
            problem_index="A",
            programming_language="Python",
            submission_id=1,
            verdict="AC",
        )
        assert submission.contest_id == 1
        assert submission.problem_index == "A"
        assert submission.programming_language == "Python"
        assert submission.submission_id == 1
        assert submission.verdict == "AC"

    def test_verdict_choices(self):
        user = CodeforcesUser.objects.create(
            handle="test_handle", rating=1500, max_rating=1600
        )
        submission: CodeforcesSubmission = user.codeforcessubmission_set.create(
            contest_id=1,
            problem_index="A",
            programming_language="Python",
            submission_id=1,
            verdict="WA",
        )
        assert submission.verdict == "WA"

        submission.verdict = "AC"  # valid choice 
        submission.full_clean()
        submission.save()

        submission.verdict = "AAA"  # not a valid choice
        submission.save()  # choices are not enforced at the database level

        with pytest.raises(ValidationError):
            submission.full_clean()
            submission.save()


@pytest.mark.django_db
class TestCodeforcesUserAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_handle_in_setting_is_required(self, client, settings):
        settings.CODEFORCES_HANDLE = None
        response = client.get(reverse("codeforces-user-info"))
        assert response.status_code == 500
        assert response.json() == {
            "error": (
                "user record was not found. " "that might be due to misconfiguration."
            )
        }

    def test_retrieve_user_info(self, client, mocker, settings):
        settings.CODEFORCES_HANDLE = "dotted_seal"

        CodeforcesUser.objects.create(
            handle="dotted_seal",
            rating=1000,
            max_rating=1050,
        )
        response = client.get(reverse("codeforces-user-info"))
        assert response.status_code == 200
        assert response.json() == {
            "handle": "dotted_seal",
            "rating": 1000,
            "max_rating": 1050,
            "last_updated": mocker.ANY,
        }
