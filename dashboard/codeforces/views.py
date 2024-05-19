from typing import Optional

import httpx
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
    handle = request.query_params.get("handle")
    if not handle:
        return Response(
            {"error": "handle is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = CodeforcesUser.objects.get(handle=handle)
    except CodeforcesUser.DoesNotExist:
        user = create_codeforces_user(handle=handle)
        if not user:
            return Response(
                {"error": "server error occurred while retrieving user information"}
            )

    # curr tiem -  user.last_updated > 1 hour
    # update user information

    serializer = CodeforcesUserSerializer(instance=user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
