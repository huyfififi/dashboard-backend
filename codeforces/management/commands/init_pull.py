import time

from django.core.management.base import BaseCommand

from codeforces.tasks import (
    retrieve_codeforces_user_info,
    retrieve_codeforces_user_submissions,
)


class Command(BaseCommand):
    help = "pull user information and his/her submissions"

    def handle(self, *args, **options):
        retrieve_codeforces_user_info()
        time.sleep(3)
        retrieve_codeforces_user_submissions()
