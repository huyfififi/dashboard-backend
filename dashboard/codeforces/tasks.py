import logging

import httpx
from celery import shared_task
from django.conf import settings

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
        }
    )
    if not serializer.is_valid():
        logging.error(f"failed to serialize codeforces user info: {serializer.errors=}")
        return None

    serializer.save()
    return None
