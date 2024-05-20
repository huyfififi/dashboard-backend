from rest_framework import serializers

from .models import CodeforcesUser


class CodeforcesUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("handle", "rating", "max_rating", "last_updated")
        model = CodeforcesUser
