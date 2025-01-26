import os
import re
from pprint import pprint

import requests
from django.core.management.base import BaseCommand
from core.models import UpcomingMatch, Team
from datetime import datetime
from bs4 import BeautifulSoup as bs

class Command(BaseCommand):
    help = 'Scrap upcoming matches directly to the database'

    def handle(self, *args, **kwargs):
        main_url = 'https://fbref.com'
        url_comps = f'{main_url}/en/comps/'

        response = requests.get(url_comps)
        
        soup = bs(response.text, 'html.parser')
        table = soup.find('table', {'id': 'comps_club'})
        rows = table.find_all('tr')
        leagues = {}
        
        for row in rows[1:len(rows) - 1]:
            league_name = ''
            league_link = ''
            links = row.find_all('a')
            for link in links:
                if 'history' in link['href']:
                    league_name = link.text
                if f'{datetime.now().year}' in link.text:
                    league_link = link['href']
                    break
            leagues[league_name] = {'link': league_link}

        #i want to change link so he has pattern: /en/comps/number/schedule/league-name-Scores-and-Fixtures
        for league in leagues.keys():
            league_link = leagues[league]['link']
            league_link = league_link.split('/')
            #add 'schedule' to the link
            league_link = f'{main_url}/en/comps/{league_link[3]}/schedule/{league_link[4]}-Scores-and-Fixtures'
            leagues[league]['link'] = league_link
        
        for league in leagues.keys():
            league_link = leagues[league]['link']
            response = requests.get(league_link)

            soup = bs(response.content, 'html.parser')
            table = soup.find('table')
            #we seek only for rows where in td data-stat='score' is empty
            rows = table.find_all('tr')
            for row in rows:
                if row.has_attr('style'):
                    continue
                if (scr := row.find('td', {'data-stat': 'score'})) is not None:
                    if scr.a is None:
                        game_week = row.find('th', {'data-stat': 'gameweek'}).text
                        date = row.find('td', {'data-stat': 'date'}).a.text
                        #change date to datetime.date
                        date = datetime.strptime(date, '%Y-%m-%d').date()
                        home_team = row.find('td', {'data-stat': 'home_team'}).a.text
                        away_team = row.find('td', {'data-stat': 'away_team'}).a.text
                        # print(f"{game_week} {date} {home_team} - {away_team}")

                        UpcomingMatch.objects.get_or_create(
                            game_week=game_week, 
                            date=date, 
                            home_team=Team.objects.get(name=home_team),
                            away_team=Team.objects.get(name=away_team)
                            )
            



