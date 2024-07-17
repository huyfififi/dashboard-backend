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

    solved_problems = (
        user.codeforcessubmission_set.filter(
            verdict=CodeforcesSubmission.VERDICT_CHOICES.OK
        )
        .order_by("contest_id", "problem_index")
        .distinct("contest_id", "problem_index")
    )

    return Response(
        data={
            "solved_count": solved_problems.count(),
            "-1000": solved_problems.filter(problem_rating__lt=1000).count(),
            "1000-1200": solved_problems.filter(
                problem_rating__gte=1000, problem_rating__lt=1200
            ).count(),
            "1200-1400": solved_problems.filter(
                problem_rating__gte=1200, problem_rating__lt=1400
            ).count(),
            "total_count": user.codeforcessubmission_set.count(),
        },
        status=status.HTTP_200_OK,
    )
