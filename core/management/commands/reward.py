from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command
from accounts.models import CustomUser
from core.models import UpcomingMatch, UserSquadPlayer, PlayerMatchStats, UserSquad, PlayedMatch

class Command(BaseCommand):
    help = 'Scrap match stats and assign points to user squads'

    def handle(self, *args, **kwargs):
        #get matches which date is < today

        # day = datetime(2025, 1, 27).date()
        day = datetime.now().date()
        matches = UpcomingMatch.objects.filter(date__lt=day)
        print("Matches which data can be scrapped: ", matches)
        print("Do you want to continue? [y/n]")
        answer = input()
        if answer.lower() != 'y':
            return
        call_command('get_stats')
        self.assign_points_to_user_squads()
        self.stdout.write(self.style.SUCCESS('Successfully scrapped match stats and assigned points'))


    def assign_points_to_user_squads(self):
        played_matches = PlayedMatch.objects.filter(points_awarded=False)
        for played_match in played_matches:
            player_stats = PlayerMatchStats.objects.filter(match=played_match)
            for user_squad in UserSquad.objects.filter(date__lte=played_match.date_played):
                total_points = 0
                for user_squad_player in UserSquadPlayer.objects.filter(user_squad=user_squad):
                    for stat in player_stats:
                        if stat.player == user_squad_player.player:
                            if user_squad_player.position == 'GK':
                                points = (
                                    stat.saves_percentage
                                )
                            elif user_squad_player.position == 'DF':
                                points = (
                                        stat.goals * 6 +
                                        stat.assists * 4 +
                                        stat.shots_on_target * 1 +
                                        stat.tackles * 2 +
                                        stat.passes_completed * 1 +
                                        stat.successful_dribbles * 1 +
                                        stat.yellow_cards * -1 +
                                        stat.red_cards * -3
                                )
                            elif user_squad_player.position == 'MF':
                                points = (
                                        stat.goals * 5 +
                                        stat.assists * 4 +
                                        stat.shots_on_target * 1.5 +
                                        stat.tackles * 1.5 +
                                        stat.passes_completed * 2 +
                                        stat.successful_dribbles * 2 +
                                        stat.yellow_cards * -1 +
                                        stat.red_cards * -3
                                )
                            else:  # 'FW'
                                points = (
                                        stat.goals * 7 +
                                        stat.assists * 5 +
                                        stat.shots_on_target * 2 +
                                        stat.tackles * 1 +
                                        stat.passes_completed * 0.5 +
                                        stat.successful_dribbles * 2 +
                                        stat.yellow_cards * -1 +
                                        stat.red_cards * -3
                                )
                            user_squad_player.points += int(points)
                            user_squad_player.save()
                            total_points += int(user_squad_player.points)
                user_squad.score = int(total_points)
                user_squad.save()
                CustomUser.objects.filter(id=user_squad.user.id).update(
                    score=CustomUser.objects.get(id=user_squad.user.id).score + total_points)
            played_match.points_awarded = True
            played_match.save()