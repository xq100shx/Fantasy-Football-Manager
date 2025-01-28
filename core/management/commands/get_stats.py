# core/management/commands/check_matches.py
import os
import random
import re
import time

import requests
from django.core.management.base import BaseCommand
from django.db.models import QuerySet
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from core.models import UpcomingMatch, PlayerMatchStats, Player
from datetime import datetime
from bs4 import BeautifulSoup as bs


class Command(BaseCommand):
    help = 'Check upcoming matches and update played matches data'

    def handle(self, *args, **kwargs):
        # today = datetime.today().date()
        #27th of january 2025
        today = datetime(2025, 1, 27).date()
        today_matches = UpcomingMatch.objects.filter(date__lt=today)
        print(len('today_matches:'), today_matches)
        if not today_matches:
            print('No matches today')
            return
        else:
            self.scrap_match_stats(today_matches)

    # Funkcja wykonująca request z opóźnieniem
    def safe_request(self,url, min_delay=6, max_delay=8, retries=3):
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        try:
            response = session.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

        # delay = random.uniform(min_delay, max_delay)
        time.sleep(random.randint(min_delay, max_delay))
        return response

    def scrap_match_stats(self, today_matches: QuerySet[UpcomingMatch]):
        base_link = "https://fbref.com"
        for match in today_matches:
            print(f"Processing match: {match.home_team} vs {match.away_team} on {match.date}")
            url = match.league_link
            response = self.safe_request(url)
            if response is None:
                print(f"Failed to fetch league link: {url}")
                continue
            soup = bs(response.content, 'html.parser')
            table = soup.find('table')
            rows = table.find_all('tr')
            match_link = ''
            for row in rows:
                if row.has_attr('style'):
                    continue
                if (src := row.find('td', {'data-stat': 'score'})) is not None:
                    home_team_text = row.find('td', {'data-stat': 'home_team'}).a.text
                    away_team_text = row.find('td', {'data-stat': 'away_team'}).a.text
                    date_text = row.find('td', {'data-stat': 'date'}).a.text
                    print(f"Checking match: {home_team_text} vs {away_team_text} on {date_text}")
                    if home_team_text == match.home_team.name and away_team_text == match.away_team.name and date_text == str(match.date):
                        try:
                            match_link = src.a['href']
                            print(f"Match found: {match_link}")
                            break
                        except (AttributeError, KeyError) as e:
                            match_link = ''
                            # Optionally, log the error or handle it as needed
                            print(f"Error occurred: {e}")
            if match_link != '':
                response = self.safe_request(f'{base_link}{match_link}')
                if response is None:
                    print(f"Failed to fetch match link: {base_link}{match_link}")
                    continue
                soup = bs(response.content, 'html.parser')
                tables = soup.find_all('table', {'class': re.compile('^stats_table.*'),
                                                 'id': re.compile('(^stats.*_summary$)|(^keeper.*)')})
                players_stats = [tables[0], tables[2]]
                keepers_stats = [tables[1], tables[3]]
                player_stats_list = []
                for table in players_stats:
                    rows = table.find_all('tr')
                    for row in rows[2:-2]:
                        name = (row.find('th')).find('a').text
                        goals = (row.find('td', {'data-stat': 'goals'})).text
                        assists = (row.find('td', {'data-stat': 'assists'})).text
                        shots_on_target = (row.find('td', {'data-stat': 'shots_on_target'})).text
                        tackles = (row.find('td', {'data-stat': 'tackles'})).text
                        passes_completed = (row.find('td', {'data-stat': 'passes_completed'})).text
                        successful_dribbles = (row.find('td', {'data-stat': 'take_ons_won'})).text
                        yellow_cards = (row.find('td', {'data-stat': 'cards_yellow'})).text
                        red_cards = (row.find('td', {'data-stat': 'cards_red'})).text
                        player_stats_list.append(PlayerMatchStats(
                            #player has to be Player instance
                            player=Player.objects.get(name=name),
                            goals=goals,
                            assists=assists,
                            shots_on_target=shots_on_target,
                            tackles=tackles,
                            passes_completed=passes_completed,
                            successful_dribbles=successful_dribbles,
                            yellow_cards=yellow_cards,
                            red_cards=red_cards
                        ))
                        print(f"Collected stats for player: {name}")

                keeper_stats_list = []
                for table in keepers_stats:
                    rows = table.find_all('tr')
                    for row in rows[2:]:
                        gk = (row.find('th').find('a')).text
                        saves_percentage = (row.find('td', {'data-stat': 'gk_save_pct'})).text
                        keeper_stats_list.append(PlayerMatchStats(
                            player=Player.objects.get(name=gk),
                            saves_percentage=saves_percentage
                        ))
                        print(f"Collected stats for goalkeeper: {gk}")

                played_match = match.mark_as_played(date_played=datetime.today().date())
                for player_stats in player_stats_list:
                    player_stats.match = played_match
                    player_stats.save()
                    print(f"Saved stats for player: {player_stats.player}")
                for keeper_stats in keeper_stats_list:
                    keeper_stats.match = played_match
                    keeper_stats.save()
                    print(f"Saved stats for goalkeeper: {keeper_stats.player}")
            else:
                print(f"No match link found for {match.home_team} vs {match.away_team} on {match.date}")