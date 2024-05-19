from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def user_info(request):
    handle = request.query_params.get("handle")
    if not handle:
        return Response(
            {"error": "handle is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    return {"test": "this is a test"}
