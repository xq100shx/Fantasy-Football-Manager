from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import UpcomingMatch
from core.tasks import assign_points_to_user_squads

class Command(BaseCommand):
    help = 'Scrap match stats and assign points to user squads'

    def handle(self, *args, **kwargs):
        #get matches which date is < today

        # matches = UpcomingMatch.objects.filter(date__lt=datetime.now())
        # print(matches)
        call_command('get_stats')
        assign_points_to_user_squads()
        self.stdout.write(self.style.SUCCESS('Successfully scrapped match stats and assigned points'))