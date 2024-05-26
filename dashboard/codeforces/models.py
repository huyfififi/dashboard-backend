from django.db import models


class CodeforcesUser(models.Model):
    handle = models.CharField(max_length=50, unique=True)
    rating = models.IntegerField(blank=True, null=True)
    max_rating = models.IntegerField(blank=True, null=True)

    last_updated = models.DateTimeField(auto_now=True, editable=False)
