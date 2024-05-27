from rest_framework import serializers

from .models import CodeforcesUser, CodeforcesSubmission


class CodeforcesUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("handle", "rating", "max_rating", "last_updated")
        model = CodeforcesUser


class CodeforcesSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "contest_id",
            "problem_index",
            "programming_language",
            "submission_id",
            "verdict",
            "user",
        )
        model = CodeforcesSubmission
