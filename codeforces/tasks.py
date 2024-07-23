import logging
import time

import httpx
from celery import shared_task
from django.conf import settings

from .models import CodeforcesUser, CodeforcesSubmission
from .serializers import CodeforcesUserSerializer


logger = logging.getLogger(__name__)


@shared_task
def retrieve_codeforces_user_info(handle: str = settings.CODEFORCES_HANDLE) -> None:
    request_url = f"https://codeforces.com/api/user.info?handles={handle}"
    # default timeout=5.0 is too short for Codeforces API
    response = httpx.get(request_url, timeout=15.0)
    if response.status_code != 200:
        logger.error(
            "received an error response from codeforces. ",
            f"{response.text=} {request_url=}",
        )
        return None
    user_info: dict = response.json()["result"][0]

    time.sleep(3)

    request_url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = httpx.get(request_url, timeout=15.0)
    if response.status_code != 200:
        logger.error(
            "received an error response from codeforces. ",
            f"{response.text=} {request_url=}",
        )
        return None
    participated_contests_count: int = len(response.json()["result"])

    serializer = CodeforcesUserSerializer(
        data={
            "handle": handle,
            "rating": user_info["rating"],
            "max_rating": user_info["maxRating"],
            "participated_contests_count": participated_contests_count,
        },
        instance=CodeforcesUser.objects.filter(handle=handle).first(),
    )
    if not serializer.is_valid():
        logger.error(f"failed to serialize codeforces user info: {serializer.errors=}")
        return None

    serializer.save()
    return None


@shared_task
def retrieve_codeforces_user_submissions(
    handle: str = settings.CODEFORCES_HANDLE,
) -> None:
    BATCH_SIZE = 100

    try:
        user = CodeforcesUser.objects.get(handle=handle)
    except CodeforcesUser.DoesNotExist:
        logger.error(
            f"user: {handle} record was not found. ",
            "that might be due to misconfiguration.",
        )
        return None

    page_i: int = 0
    up_to_date: bool = False
    while not up_to_date:
        logger.info(f"fetching submissions for {handle} page: {page_i}")
        print(f"fetching submissions for {handle} page: {page_i}")
        response = httpx.get(
            (
                "https://codeforces.com/api/user.status?"
                f"handle={handle}&from={page_i * BATCH_SIZE + 1}&count={BATCH_SIZE}"
            ),
            timeout=15.0,
        )
        if response.status_code != 200:
            logger.error(
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
                up_to_date = True
                break

            submissions_to_create.append(
                CodeforcesSubmission(
                    contest_id=submission["contestId"],
                    problem_index=submission["problem"]["index"],
                    # rating is not present for contest submissions
                    problem_rating=submission["problem"].get("rating"),
                    programming_language=submission["programmingLanguage"],
                    submission_id=submission["id"],
                    verdict=CodeforcesSubmission.VERDICT_CHOICES[submission["verdict"]],
                    user=user,
                )
            )

        CodeforcesSubmission.objects.bulk_create(submissions_to_create)
        page_i += 1
        # > API may be requested at most 1 time per two seconds
        time.sleep(3)
