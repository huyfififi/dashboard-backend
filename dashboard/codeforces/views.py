from datetime import timedelta
from typing import Optional

import httpx
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import CodeforcesUser
from .serializers import CodeforcesUserSerializer


def create_codeforces_user(handle: str) -> Optional[CodeforcesUser]:
    response = httpx.get(f"https://codeforces.com/api/user.info?handles={handle}")
    if response.status_code != 200:
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
        return None
    serializer.save()
    return serializer.instance


@api_view(["GET"])
def user_info(request):
    handle = settings.CODEFORCES_HANDLE
    if not handle:
        return Response(
            {"error": "handle is not set in the server"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        user = CodeforcesUser.objects.get(handle=handle)
    except CodeforcesUser.DoesNotExist:
        user = create_codeforces_user(handle=handle)
        if not user:
            return Response(
                {"error": "server error occurred while retrieving user information"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    if timezone.now() - user.last_updated > timedelta(hours=1):
        user = update_codeforces_user(handle=handle)

    serializer = CodeforcesUserSerializer(instance=user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
