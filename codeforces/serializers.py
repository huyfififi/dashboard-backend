from rest_framework import serializers

from .models import CodeforcesUser


class CodeforcesUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "handle",
            "rating",
            "max_rating",
            "participated_contests_count",
            "last_updated",
        )
        model = CodeforcesUser
