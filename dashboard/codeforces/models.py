from django.db import models


class CodeforcesUser(models.Model):
    handle = models.CharField(max_length=50, unique=True)
    rating = models.IntegerField(blank=True, null=True)
    max_rating = models.IntegerField(blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)


class CodeforcesSubmission(models.Model):
    class VERDICT_CHOICES(models.TextChoices):
        FAILED = "FL"
        OK = "AC"
        PARTIAL = "PT"
        COMPILATION_ERROR = "CE"
        RUNTIME_ERROR = "RE"
        WRONG_ANSWER = "WA"
        PRESENTATION_ERROR = "PE"
        TIME_LIMIT_EXCEEDED = "TLE"
        MEMORY_LIMIT_EXCEEDED = "MLE"
        IDLENESS_LIMIT_EXCEEDED = "ILE"
        SECURITY_VIOLATED = "SV"
        CRASHED = "CR"
        INPUT_PREPARATION_CRASHED = "IPC"
        CHALLENGED = "CH"
        SKIPPED = "SK"
        TESTING = "TE"
        REJECTED = "RJ"

    contest_id = models.IntegerField()
    problem_index = models.CharField(max_length=2)
    programming_language = models.CharField(max_length=25)
    # codeforces submission id, auto-incremented
    submission_id = models.IntegerField(unique=True)
    user = models.ForeignKey(CodeforcesUser, on_delete=models.CASCADE)
    verdict = models.CharField(
        max_length=3,
        choices=VERDICT_CHOICES,
        blank=True,
        null=True,
    )  # can be absent

    class Meta:
        ordering = ["-submission_id"]
