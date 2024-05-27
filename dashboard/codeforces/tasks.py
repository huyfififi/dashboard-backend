import logging
import time

import httpx
from celery import shared_task
from django.conf import settings

from .models import CodeforcesUser, CodeforcesSubmission
from .serializers import CodeforcesUserSerializer


@shared_task
def retrieve_codeforces_user_info(handle: str = settings.CODEFORCES_HANDLE) -> None:
    response = httpx.get(f"https://codeforces.com/api/user.info?handles={handle}")
    if response.status_code != 200:
        logging.error(f"received an error response from codeforces: {response.text=}")
        return None

    user_info = response.json()["result"][0]
    serializer = CodeforcesUserSerializer(
        data={
            "handle": handle,
            "rating": user_info["rating"],
            "max_rating": user_info["maxRating"],
        },
        instance=CodeforcesUser.objects.filter(handle=handle).first(),
    )
    if not serializer.is_valid():
        logging.error(f"failed to serialize codeforces user info: {serializer.errors=}")
        return None

    serializer.save()
    return None


@shared_task
def retrieve_codeforces_submissions(handle: str = settings.CODEFORCES_HANDLE) -> None:
    BATCH_SIZE = 100

    try:
        user = CodeforcesUser.objects.get(handle=handle)
    except CodeforcesUser.DoesNotExist:
        logging.error(
            f"user: {handle} record was not found. ",
            "that might be due to misconfiguration.",
        )
        return None

    page_i = 0
    while True:
        logging.info(f"fetching submissions for {handle} page: {page_i}")
        response = httpx.get(
            "https://codeforces.com/api/user.status?"
            f"handle={handle}&from={page_i * BATCH_SIZE}&count={BATCH_SIZE}"
        )
        if response.status_code != 200:
            logging.error(
                f"received an error response from codeforces: {response.text=}"
            )
            return None

        submissions = response.json()["result"]
        if not submissions:
            break

        submissions_to_create = []
        for submission in submissions:
            if CodeforcesSubmission.objects.filter(
                submission_id=submission["id"]
            ).exists():
                break

            submissions_to_create.append(
                CodeforcesSubmission(
                    contest_id=submission["contestId"],
                    problem_index=submission["problem"]["index"],
                    programming_language=submission["programmingLanguage"],
                    submission_id=submission["id"],
                    verdict=submission["verdict"],
                    user=user,
                )
            )

        CodeforcesSubmission.objects.bulk_create(submissions_to_create)
        page_i += 1
        # > API may be requested at most 1 time per two seconds
        time.sleep(3)
