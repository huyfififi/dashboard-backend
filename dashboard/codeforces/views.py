from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import CodeforcesUser, CodeforcesSubmission
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


@api_view(["GET"])
def user_statistics(request):
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

    return Response(
        data={
            "solved_count": user.codeforcessubmission_set.filter(
                verdict=CodeforcesSubmission.VERDICT_CHOICES.OK
            )
            .order_by("contest_id", "problem_index")
            .distinct("contest_id", "problem_index")
            .count(),
            "total_count": user.codeforcessubmission_set.count(),
        },
        status=status.HTTP_200_OK,
    )
