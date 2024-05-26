from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import CodeforcesUser
from .serializers import CodeforcesUserSerializer


@api_view(["GET"])
def user_info(request):
    handle = settings.CODEFORCES_HANDLE
    try:
        user = CodeforcesUser.objects.get(handle=handle)
    except CodeforcesUser.DoesNotExist:
        return Response(
            {
                "error": (
                    "user record was not found. "
                    "that might be due to misconfiguration."
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    serializer = CodeforcesUserSerializer(instance=user)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
